from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_admin_from_request
from app.models.user import User
from app.schema.response import UserAdminResponse
from app.service.admin import get_all_users as srv_get_all_users

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/users", response_model=UserAdminResponse)
def get_all_users(
    request: Request,
    db: Session = Depends(get_db),
):
    current_admin = get_admin_from_request(request, db)
    return srv_get_all_users(db)
