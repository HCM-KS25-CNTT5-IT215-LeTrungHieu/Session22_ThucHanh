from datetime import UTC, datetime, timedelta

import bcrypt
import jwt

from app.core.config import settings


def hash_password(password: str):
    salt = bcrypt.gensalt()
    byte_password = password.encode("utf-8")

    hashed_password = bcrypt.hashpw(password=byte_password, salt=salt)

    return hashed_password.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    byte_password = plain_password.encode("utf-8")
    byte_hashed_password = hashed_password.encode("utf-8")

    return bcrypt.checkpw(password=byte_password, hashed_password=byte_hashed_password)


def generate_token(username: str, duration: int) -> str:
    now = datetime.now(UTC)
    payload = {
        "sub": username,
        "iat": now,
        "exp": now + timedelta(minutes=duration),
    }

    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")
