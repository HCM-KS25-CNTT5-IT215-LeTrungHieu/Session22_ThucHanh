from pydantic import BaseModel, Field

from app.models.user import UserRole


class UserRegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=8, max_length=72)
    role: UserRole = UserRole.CUSTOMER


class UserLoginRequest(BaseModel):
    username: str
    password: str


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


class TransferRequest(BaseModel):
    to_username: str
    amount: float = Field(gt=0)
