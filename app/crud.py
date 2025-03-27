from sqlalchemy.orm import Session
from app import models

def get_all_books(db: Session):
    return db.query(models.Book).order_by(models.Book.created_at.desc()).all()
