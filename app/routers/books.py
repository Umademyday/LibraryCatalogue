from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.database.deps import get_db
from app import crud

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
def list_books(request: Request, db: Session = Depends(get_db)):
    books = crud.get_all_books(db)
    return templates.TemplateResponse("index.html", {"request": request, "books": books})
