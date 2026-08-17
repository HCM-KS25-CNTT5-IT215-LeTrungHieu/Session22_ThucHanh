from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.database import engine
from app.core.exceptions import AppException
from app.models.base import Base
from app.models.user import User  # To ensure models are loaded
from app.models.token import RevokedToken # To ensure models are loaded
from app.routes.account import router as account_router
from app.routes.admin import router as admin_router
from app.routes.auth import router as auth_router

app = FastAPI(title="TrustBank Digital API")

Base.metadata.create_all(bind=engine)

app.include_router(auth_router)
app.include_router(account_router)
app.include_router(admin_router)


@app.exception_handler(AppException)
def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.error_code, "detail": exc.detail},
    )


@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"error": "VALIDATION_ERROR", "detail": "Dữ liệu đầu vào sai định dạng"},
    )


@app.exception_handler(Exception)
def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "INTERNAL_SERVER_ERROR", "detail": "Lỗi máy chủ không xác định trước"},
    )
