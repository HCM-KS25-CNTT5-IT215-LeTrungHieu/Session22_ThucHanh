from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User
from app.schema.response import UserAdminResponse, UserResponse


def get_all_users(db: Session) -> UserAdminResponse:
    users = db.scalars(select(User)).all()
    user_responses = [
        UserResponse(
            id=user.id,
            username=user.username,
            role=user.role,
            balance=user.balance,
            created_at=user.created_at,
        )
        for user in users
    ]
    return UserAdminResponse(users=user_responses)
