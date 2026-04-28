from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    login: str = Field(min_length=3, max_length=128)
    password: str = Field(min_length=6, max_length=128)


class LoginRequest(BaseModel):
    login: str
    password: str


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
