from fastapi import FastAPI

from app.core.database import engine
from app.models.base import Base

app = FastAPI()

Base.metadata.create_all(bind=engine)
