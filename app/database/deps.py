from app.database.session import SessionLocal
from app.database.uow import UnitOfWork


def get_uow():
    return UnitOfWork(SessionLocal)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
