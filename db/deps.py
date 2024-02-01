from utils.database import SessionLocal
from typing import Generator
from sqlalchemy.orm import Session
from models import User

# def get_db() -> Generator:
#     db = DBConnection().getSession()
#     try:
#         yield db
#     finally:
#         db.close()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
