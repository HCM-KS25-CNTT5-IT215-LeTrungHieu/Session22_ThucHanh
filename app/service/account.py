from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import AppException
from app.models.user import User
from app.schema.request import TransferRequest
from app.schema.response import BalanceResponse, TransferResponse


def get_balance(current_user: User) -> BalanceResponse:
    return BalanceResponse(
        balance=current_user.balance, message="Chào mừng bạn đến với TrustBank Digital"
    )

def transfer(request: TransferRequest, current_user: User, db: Session) -> TransferResponse:
    if request.amount <= 0:
        raise AppException(
            status_code=422,
            error_code="VALIDATION_ERROR",
            detail="Số tiền chuyển phải lớn hơn 0",
        )

    if current_user.username == request.to_username:
        raise AppException(
            status_code=400,
            error_code="INVALID_TRANSFER",
            detail="Không thể tự chuyển tiền cho chính mình",
        )

    if current_user.balance < request.amount:
        raise AppException(
            status_code=400,
            error_code="INSUFFICIENT_BALANCE",
            detail="Số dư không đủ để thực hiện giao dịch",
        )

    recipient = db.scalar(select(User).where(User.username == request.to_username))
    if not recipient:
        raise AppException(
            status_code=404,
            error_code="RECIPIENT_NOT_FOUND",
            detail="Không tìm thấy tài khoản người nhận",
        )

    try:
        current_user.balance -= request.amount
        recipient.balance += request.amount
        db.commit()
    except Exception:
        db.rollback()
        raise AppException(
            status_code=500,
            error_code="INTERNAL_SERVER_ERROR",
            detail="Lỗi hệ thống khi thực hiện giao dịch",
        )

    return TransferResponse(
        message="Chuyển tiền thành công",
        from_user=current_user.username,
        to_user=recipient.username,
        amount=request.amount,
        note=request.note,
    )
