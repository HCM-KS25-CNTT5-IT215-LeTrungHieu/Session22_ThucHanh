from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import create_database, database_exists

from app.core.config import settings

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(bind=engine)

if not database_exists(settings.database_url):
    create_database(settings.database_url)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
