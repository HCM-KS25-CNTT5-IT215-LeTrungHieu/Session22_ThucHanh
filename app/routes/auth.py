from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_token_from_request, get_user_from_request
from app.models.user import User
from app.schema.request import (
    ChangePasswordRequest,
    RefreshTokenRequest,
    UserLoginRequest,
    UserRegisterRequest,
)
from app.schema.response import TokenResponse, UserResponse
from app.service.auth import change_password as srv_change_password
from app.service.auth import login as srv_login
from app.service.auth import logout as srv_logout
from app.service.auth import refresh as srv_refresh
from app.service.auth import register as srv_register

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(request: UserRegisterRequest, db: Session = Depends(get_db)):
    return srv_register(request, db)


@router.post("/login", response_model=TokenResponse)
def login(request: UserLoginRequest, db: Session = Depends(get_db)):
    return srv_login(request, db)


@router.post("/refresh", response_model=TokenResponse)
def refresh(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    return srv_refresh(request, db)


@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(
    request: Request,
    db: Session = Depends(get_db),
):
    token = get_token_from_request(request)
    srv_logout(token, db)
    return {"message": "Đăng xuất thành công"}


@router.post("/change-password", status_code=status.HTTP_200_OK)
def change_password(
    req_body: ChangePasswordRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    current_user = get_user_from_request(request, db)
    srv_change_password(req_body, current_user, db)
    return {"message": "Đổi mật khẩu thành công"}
