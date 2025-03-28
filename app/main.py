from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
# from starlette.requests import Request

from app.routers import books
from app.database.base import Base
from app.database.session import engine

from app.models import Book


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
