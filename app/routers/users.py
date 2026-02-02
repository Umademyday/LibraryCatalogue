from typing import Optional
from sqlalchemy.orm import Session

from app.models import User


class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def get(self, user_id: int) -> Optional[User]:
        return self.session.query(User).get(user_id)

    def get_by_username(self, username: str) -> Optional[User]:
        return self.session.query(User).filter(User.username == username).first()

    def list(self) -> list[User]:
        return self.session.query(User).order_by(User.created_at.desc()).all()

    def add(self, user: User) -> None:
        self.session.add(user)
