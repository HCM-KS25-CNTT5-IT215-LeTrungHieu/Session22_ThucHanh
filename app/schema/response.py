from datetime import datetime

from pydantic import BaseModel

from app.models.user import UserRole


class UserResponse(BaseModel):
    id: int
    username: str
    role: UserRole
    balance: float
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class BalanceResponse(BaseModel):
    balance: float
    message: str


class TransferResponse(BaseModel):
    message: str
    from_user: str
    to_user: str
    amount: float
    note: str | None


class UserAdminResponse(BaseModel):
    users: list[UserResponse]


class ErrorResponse(BaseModel):
    error: str
    detail: str

