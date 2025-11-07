from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from typing import Optional, Type
from sqlalchemy.orm import Session

from app.database.deps import get_db
from app import crud
from app import models
from app.models import Book

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


class BookRepository:
    def __init__(self, session: Session):
        self.session = session

    # Reads
    def list(self) -> list[Type[Book]]:
        return (self.session.query(models.Book)
                .order_by(models.Book.created_at.desc())
                .all())

    def get(self, book_id: int) -> Optional[models.Book]:
        return self.session.query(models.Book).get(book_id)

    # Writes (no commit here—leave that to UoW)
    def add(self, book: models.Book) -> None:
        self.session.add(book)

    def delete(self, book: models.Book) -> None:
        self.session.delete(book)
