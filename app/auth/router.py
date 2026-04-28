from fastapi import APIRouter, Depends, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.auth.service import (
    authenticate_user,
    github_callback,
    github_login_url,
    issue_tokens,
    logout,
    refresh_tokens,
    register_user,
)
from app.db.session import get_db
from app.schemas.auth import LoginRequest, RegisterRequest, TokenPair

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenPair)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    user = register_user(db, payload.login, payload.password)
    return issue_tokens(user.id)


@router.post("/login", response_model=TokenPair)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, payload.login, payload.password)
    return issue_tokens(user.id)


@router.post("/refresh", response_model=TokenPair)
def refresh(refresh_token: str = Query(...)):
    return refresh_tokens(refresh_token)


@router.post("/logout")
def logout_route(refresh_token: str = Query(...)):
    logout(refresh_token)
    return {"status": "ok"}


@router.get("/github/login")
def github_login():
    return RedirectResponse(github_login_url())


@router.get("/github/callback")
async def github_oauth_callback(code: str, db: Session = Depends(get_db)):
    tokens = await github_callback(db, code)
    url = (
        f"/?access_token={tokens['access_token']}"
        f"&refresh_token={tokens['refresh_token']}"
    )
    return RedirectResponse(url)
