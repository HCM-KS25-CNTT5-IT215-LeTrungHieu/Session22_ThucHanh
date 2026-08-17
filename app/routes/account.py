from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_user_from_request
from app.models.user import User
from app.schema.request import TransferRequest
from app.schema.response import BalanceResponse, TransferResponse
from app.service.account import get_balance as srv_get_balance
from app.service.account import transfer as srv_transfer

router = APIRouter(prefix="/api/account", tags=["account"])


@router.get("/balance", response_model=BalanceResponse)
def get_balance(request: Request, db: Session = Depends(get_db)):
    current_user = get_user_from_request(request, db)
    return srv_get_balance(current_user)


@router.post("/transfer", response_model=TransferResponse)
def transfer(
    req_body: TransferRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    current_user = get_user_from_request(request, db)
    return srv_transfer(req_body, current_user, db)
