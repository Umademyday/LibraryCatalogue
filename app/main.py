from fastapi import FastAPI, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from fastapi import Depends

from app.routers import books
from app.database.base import Base
from app.database.deps import get_db
from app.database.session import engine
from . import models, crud



# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Mount static folder (e.g. images, css)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
# app.mount("/images", StaticFiles(directory="book_images"), name="book_images")


# Include routers
app.include_router(books.router)

# Templates directory
templates = Jinja2Templates(directory="app/templates")

# GET: upload form
@app.get("/upload")
async def upload_form(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})

# POST: handle form
@app.post("/upload")
async def upload_book(
    title: str = Form(...),
    author: str = Form(...),
    genre: str = Form(...),
    location: str = Form(...),
    db: Session = Depends(get_db)
):
    new_book = models.Book(
        title=title,
        author=author,
        genre=genre,
        location=location
    )
    db.add(new_book)
    db.commit()
    return RedirectResponse("/", status_code=303)