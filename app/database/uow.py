from contextlib import contextmanager
from app.routers.books import BookRepository
from app.routers.users import UserRepository
from app.database.session import SessionLocal


class UnitOfWork:
    def __init__(self, session_factory=SessionLocal):
        self._sf = session_factory
        self.session = None
        self.books: BookRepository | None = None
        self.users: UserRepository | None = None

    @contextmanager
    def start(self):
        self.session = self._sf()
        self.books = BookRepository(self.session)
        self.users = UserRepository(self.session)
        try:
            yield self
            self.session.commit()
        except:
            self.session.rollback()
            raise
        finally:
            self.session.close()