from datetime import UTC, datetime, timedelta

import bcrypt
import jwt
from fastapi import Request
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import AppException
from app.models.token import RevokedToken
from app.models.user import User, UserRole


def hash_password(password: str):
    salt = bcrypt.gensalt()
    byte_password = password.encode("utf-8")

    hashed_password = bcrypt.hashpw(password=byte_password, salt=salt)

    return hashed_password.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    byte_password = plain_password.encode("utf-8")
    byte_hashed_password = hashed_password.encode("utf-8")

    return bcrypt.checkpw(password=byte_password, hashed_password=byte_hashed_password)


def generate_token(username: str, role: str, token_type: str, duration: int) -> str:
    now = datetime.now(UTC)
    payload = {
        "sub": username,
        "role": role,
        "token_type": token_type,
        "iat": now,
        "exp": now + timedelta(minutes=duration),
    }

    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


def verify_token(token: str) -> dict:
    return jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])


def get_token_from_request(request: Request) -> str:
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise AppException(
            status_code=401,
            error_code="INVALID_TOKEN",
            detail="Không tìm thấy token xác thực",
        )
    return auth_header.split(" ")[1]


def get_user_from_request(request: Request, db: Session) -> User:
    token = get_token_from_request(request)

    revoked = db.scalar(select(RevokedToken).where(RevokedToken.token == token))
    if revoked:
        raise AppException(
            status_code=401,
            error_code="TOKEN_REVOKED",
            detail="Token đã bị thu hồi do người dùng đã đăng xuất",
        )

    try:
        payload = verify_token(token)
        username = payload.get("sub")
        token_type = payload.get("token_type")

        if not username or token_type != "access":
            raise AppException(
                status_code=401,
                error_code="INVALID_TOKEN",
                detail="Token không hợp lệ",
            )
            
    except ExpiredSignatureError:
        raise AppException(
            status_code=401,
            error_code="INVALID_TOKEN",
            detail="Token đã hết hạn",
        )
    except InvalidTokenError:
        raise AppException(
            status_code=401,
            error_code="INVALID_TOKEN",
            detail="Token không hợp lệ",
        )

    user = db.scalar(select(User).where(User.username == username))
    if not user:
        raise AppException(
            status_code=401,
            error_code="INVALID_TOKEN",
            detail="Người dùng không tồn tại",
        )

    return user


def get_admin_from_request(request: Request, db: Session) -> User:
    current_user = get_user_from_request(request, db)
    if current_user.role != UserRole.ADMIN:
        raise AppException(
            status_code=403,
            error_code="PERMISSION_DENIED",
            detail="Không có quyền truy cập",
        )
    return current_user
