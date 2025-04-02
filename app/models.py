from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.database import base


class Book(base.Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    author = Column(String, index=True, nullable=False)
    genre = Column(String, index=True, nullable=False)
    location = Column(String, nullable=False)
    cover_image = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
