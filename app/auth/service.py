from urllib.parse import urlencode

import httpx
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.redis import redis_client
from app.core.security import create_access_token, hash_password, make_refresh_token, verify_password
from app.db.models import User

REFRESH_PREFIX = "refresh:"


def _save_refresh_session(user_id: int, refresh_token: str) -> None:
    ttl_seconds = settings.refresh_token_expire_days * 24 * 60 * 60
    redis_client.setex(f"{REFRESH_PREFIX}{refresh_token}", ttl_seconds, str(user_id))


def issue_tokens(user_id: int) -> dict[str, str]:
    access_token = create_access_token(user_id)
    refresh_token = make_refresh_token()
    _save_refresh_session(user_id, refresh_token)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


def register_user(db: Session, login: str, password: str) -> User:
    existing = db.query(User).filter(User.login == login).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="login already exists")

    user = User(login=login, hashed_password=hash_password(password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, login: str, password: str) -> User:
    user = db.query(User).filter(User.login == login).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid login or password")
    return user


def refresh_tokens(refresh_token: str) -> dict[str, str]:
    user_id = redis_client.get(f"{REFRESH_PREFIX}{refresh_token}")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid refresh token")

    redis_client.delete(f"{REFRESH_PREFIX}{refresh_token}")
    return issue_tokens(int(user_id))


def logout(refresh_token: str) -> None:
    redis_client.delete(f"{REFRESH_PREFIX}{refresh_token}")


def github_login_url() -> str:
    if not settings.github_client_id:
        raise HTTPException(status_code=500, detail="github oauth is not configured")

    params = urlencode({
        "client_id": settings.github_client_id,
        "redirect_uri": settings.github_callback_url,
        "scope": "read:user user:email",
    })
    return f"https://github.com/login/oauth/authorize?{params}"


async def github_callback(db: Session, code: str) -> dict[str, str]:
    if not settings.github_client_id or not settings.github_client_secret:
        raise HTTPException(status_code=500, detail="github oauth is not configured")

    async with httpx.AsyncClient(timeout=10) as client:
        token_response = await client.post(
            "https://github.com/login/oauth/access_token",
            headers={"Accept": "application/json"},
            data={
                "client_id": settings.github_client_id,
                "client_secret": settings.github_client_secret,
                "code": code,
                "redirect_uri": settings.github_callback_url,
            },
        )
        token_response.raise_for_status()
        github_token = token_response.json().get("access_token")

        if not github_token:
            raise HTTPException(status_code=401, detail="github did not return access token")

        user_response = await client.get(
            "https://api.github.com/user",
            headers={"Authorization": f"Bearer {github_token}", "Accept": "application/json"},
        )
        user_response.raise_for_status()
        github_user = user_response.json()

    github_id = str(github_user["id"])
    login = github_user.get("login") or f"github_{github_id}"

    user = db.query(User).filter(User.github_id == github_id).first()
    if not user:
        base_login = login
        candidate = base_login
        counter = 1
        while db.query(User).filter(User.login == candidate).first():
            counter += 1
            candidate = f"{base_login}_{counter}"

        user = User(login=candidate, github_id=github_id)
        db.add(user)
        db.commit()
        db.refresh(user)

    return issue_tokens(user.id)
