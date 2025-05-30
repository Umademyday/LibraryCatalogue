from fastapi import FastAPI, Request, Form, Depends, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from uuid import uuid4
import shutil
import os
import cv2
import pytesseract

from app.routers import books
from app.database.base import Base
from app.database.deps import get_db
from app.database.session import engine
from . import models, crud

# Move it to config file
GENRES = ["Child book", "Just book", "Other"]
LOCATIONS = ["Madrid", "Moscow", "St. Peterbourg", "London", "Lebedyan"]
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Mount static folder (e.g. images, css)
app.mount("/media", StaticFiles(directory=r"G:\book_images"), name="media")

# Include routers
app.include_router(books.router)

# Templates directory
templates = Jinja2Templates(directory="app/templates")


@app.get("/upload")
async def upload_form(request: Request):
    return templates.TemplateResponse("upload.html", {
        "request": request,
        "genres": GENRES,
        "locations": LOCATIONS
    })


@app.post("/upload/cover")
async def upload_cover_only(
    request: Request,
    cover_image: UploadFile = File(...),
):
    image_path = None
    raw_text = None

    if cover_image:
        UPLOAD_DIR = r"G:\book_images"
        os.makedirs(UPLOAD_DIR, exist_ok=True)

        filename = f"{uuid4().hex}_{cover_image.filename}"
        file_path = os.path.join(UPLOAD_DIR, filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(cover_image.file, buffer)

        image_path = f"/media/{filename}"

        # OCR
        try:
            image = cv2.imread(file_path)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
            raw_text = pytesseract.image_to_string(thresh, lang="eng+spa+rus")
        except Exception as e:
            raw_text = f"OCR failed: {str(e)}"

    return templates.TemplateResponse("upload.html", {
        "request": request,
        "genres": GENRES,
        "locations": LOCATIONS,
        "image_url": image_path,
        "raw_text": raw_text,
        "title": "",
        "author": ""
    })

# POST: Save final book to DB
@app.post("/upload")
async def upload_book(
    title: str = Form(...),
    author: str = Form(...),
    genre: str = Form(...),
    location: str = Form(...),
    cover_image_path: str = Form(None),
    db: Session = Depends(get_db)
):


    new_book = models.Book(
        title=title,
        author=author,
        genre=genre,
        location=location,
        cover_image=cover_image_path
    )
    print('cover_image_path:', cover_image_path)
    db.add(new_book)
    db.commit()

    return RedirectResponse("/", status_code=303)


@app.get("/edit/{book_id}")
def edit_book_form(book_id: int, request: Request, db: Session = Depends(get_db)):
    book = db.query(models.Book).get(book_id)
    if not book:
        return RedirectResponse("/", status_code=302)
    return templates.TemplateResponse("edit.html", {
        "request": request,
        "book": book,
        "genres": GENRES,
        "locations": LOCATIONS
    })


@app.post("/edit/{book_id}")
def update_book(
        book_id: int,
        title: str = Form(...),
        author: str = Form(...),
        genre: str = Form(...),
        location: str = Form(...),
        db: Session = Depends(get_db)
):
    book = db.query(models.Book).get(book_id)
    if not book:
        return RedirectResponse("/", status_code=302)

    book.title = title
    book.author = author
    book.genre = genre
    book.location = location

    db.commit()
    return RedirectResponse("/", status_code=303)


@app.post("/delete/{book_id}")
def delete_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(models.Book).get(book_id)
    if book:
        db.delete(book)
        db.commit()
    return RedirectResponse("/", status_code=303)
