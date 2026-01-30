from fastapi import FastAPI, Request, Form, Depends, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from uuid import uuid4
import shutil
import os
import cv2
import pytesseract

from app.routers import books
from app.database.base import Base
from app.database.session import engine
from . import models
from app.database.deps import get_uow

# Move it to config file
GENRES = ["Child book", "Just book", "Other"]
LOCATIONS = ["Madrid", "Moscow", "St. Peterbourg", "London", "Lebedyan"]

# Allowed image extensions and MIME types for cover uploads
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Mount static folder (e.g. images, css)
app.mount("/media", StaticFiles(directory=r"G:\book_images"), name="media")

# Include routers
app.include_router(books.router)

# Templates directory
templates = Jinja2Templates(directory="app/templates")


def validate_image_file(file: UploadFile) -> tuple[bool, str]:
    """
    Validate that an uploaded file is a safe image.
    Returns (is_valid, error_message).
    """
    if not file.filename:
        return False, "No filename provided"
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return False, "Unsupported file extension"
    if file.content_type not in ALLOWED_MIME_TYPES:
        return False, "Unsupported file type"

    return True, ""


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
        # Validate the uploaded file is a safe image
        is_valid, error_msg = validate_image_file(cover_image)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)

        UPLOAD_DIR = r"G:\book_images"
        os.makedirs(UPLOAD_DIR, exist_ok=True)

        # Security: Use basename to prevent path traversal attacks
        safe_filename = os.path.basename(cover_image.filename or "image")
        filename = f"{uuid4().hex}_{safe_filename}"
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


# POST: Save final book to DB (UoW handles commit/rollback)
@app.post("/upload")
def upload_book(
        title: str = Form(...),
        author: str = Form(...),
        genre: str = Form(...),
        location: str = Form(...),
        cover_image_path: str = Form(None),
        uow = Depends(get_uow),
):
    with uow.start():
        new_book = models.Book(
            title=title, author=author, genre=genre,
            location=location, cover_image=cover_image_path
        )
        # Prefer going through the repository:
        uow.books.add(new_book)
    return RedirectResponse("/", status_code=303)


@app.get("/edit/{book_id}")
def edit_book_form(book_id: int, request: Request, uow = Depends(get_uow)):
    with uow.start():
        book = uow.books.get(book_id)
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
        uow = Depends(get_uow),
):
    with uow.start():
        book = uow.books.get(book_id)
        if not book:
            # no changes to commit; UoW will just close
            return RedirectResponse("/", status_code=302)
        book.title = title
        book.author = author
        book.genre = genre
        book.location = location
        # No explicit commit—handled by UoW
    return RedirectResponse("/", status_code=303)


@app.post("/delete/{book_id}")
def delete_book(book_id: int, uow = Depends(get_uow)):
    with uow.start():
        book = uow.books.get(book_id)
        if book:
            uow.books.delete(book)
        # Commit/rollback handled by UoW
    return RedirectResponse("/", status_code=303)
