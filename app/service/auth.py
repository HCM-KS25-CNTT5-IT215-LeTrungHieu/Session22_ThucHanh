from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import AppException
from app.core.security import generate_token, hash_password, verify_password, verify_token
from app.models.token import RevokedToken
from app.models.user import User
from app.schema.request import (
    ChangePasswordRequest,
    RefreshTokenRequest,
    UserLoginRequest,
    UserRegisterRequest,
)
from app.schema.response import TokenResponse, UserResponse


def register(request: UserRegisterRequest, db: Session) -> UserResponse:
    if db.scalar(select(User).where(User.username == request.username)):
        raise AppException(
            status_code=409,
            error_code="USER_ALREADY_EXISTS",
            detail="Tài khoản đã tồn tại",
        )

    hashed = hash_password(request.password)
    new_user = User(
        username=request.username,
        hashed_password=hashed,
        role=request.role,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return UserResponse(
        id=new_user.id,
        username=new_user.username,
        role=new_user.role,
        balance=new_user.balance,
        created_at=new_user.created_at,
    )

def login(request: UserLoginRequest, db: Session) -> TokenResponse:
    user = db.scalar(select(User).where(User.username == request.username))
    if not user or not verify_password(request.password, user.hashed_password):
        raise AppException(
            status_code=401,
            error_code="INVALID_CREDENTIALS",
            detail="Sai tên đăng nhập hoặc mật khẩu",
        )

    access_token = generate_token(
        username=user.username, role=user.role, token_type="access", duration=10
    )
    refresh_token = generate_token(
        username=user.username, role=user.role, token_type="refresh", duration=7 * 24 * 60
    )

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)

def refresh(request: RefreshTokenRequest, db: Session) -> TokenResponse:
    try:
        payload = verify_token(request.refresh_token)
        if payload.get("token_type") != "refresh":
            raise AppException(
                status_code=401,
                error_code="INVALID_REFRESH_TOKEN",
                detail="Token không hợp lệ",
            )

        username = payload.get("sub")
        role = payload.get("role")
        
        # Additional check if user exists
        user = db.scalar(select(User).where(User.username == username))
        if not user:
             raise AppException(
                status_code=401,
                error_code="INVALID_REFRESH_TOKEN",
                detail="Người dùng không tồn tại",
            )

        access_token = generate_token(
            username=username, role=role, token_type="access", duration=10
        )
        return TokenResponse(
            access_token=access_token, refresh_token=request.refresh_token
        )

    except (ExpiredSignatureError, InvalidTokenError):
        raise AppException(
            status_code=401,
            error_code="INVALID_REFRESH_TOKEN",
            detail="Token không hợp lệ hoặc đã hết hạn",
        )

def logout(token: str, db: Session):
    revoked_token = RevokedToken(token=token)
    db.add(revoked_token)
    db.commit()

def change_password(request: ChangePasswordRequest, current_user: User, db: Session):
    if not verify_password(request.old_password, current_user.hashed_password):
        raise AppException(
            status_code=401,
            error_code="INVALID_CREDENTIALS",
            detail="Mật khẩu cũ không chính xác",
        )

    if request.old_password == request.new_password:
        raise AppException(
            status_code=400,
            error_code="VALIDATION_ERROR",
            detail="Mật khẩu mới không được trùng mật khẩu cũ",
        )

    current_user.hashed_password = hash_password(request.new_password)
    db.commit()
