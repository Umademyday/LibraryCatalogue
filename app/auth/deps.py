from fastapi import Request, Depends, HTTPException

from app.auth.session import verify_session_token
from app.database.deps import get_uow
from app.models import User

COOKIE_NAME = "session_token"


class AuthRequired(HTTPException):
    """Raised when authentication is required but user is not logged in."""
    def __init__(self):
        super().__init__(status_code=401, detail="Authentication required")


def get_current_user(request: Request, uow=Depends(get_uow)) -> User:
    """
    Extract and verify the session token from cookies.
    Returns the User if authenticated, raises AuthRequired otherwise.
    """
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        raise AuthRequired()

    user_id = verify_session_token(token)
    if not user_id:
        raise AuthRequired()

    with uow.start():
        user = uow.users.get(user_id)
        if not user or not user.is_active:
            raise AuthRequired()
        uow.session.expunge(user)
        return user
