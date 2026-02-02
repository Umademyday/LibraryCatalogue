from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from app.config import settings

SESSION_MAX_AGE = 7 * 24 * 60 * 60  # 7 days in seconds

_serializer = URLSafeTimedSerializer(settings.SECRET_KEY)


def create_session_token(user_id: int) -> str:
    """Create a signed session token containing the user ID."""
    return _serializer.dumps({"user_id": user_id})


def verify_session_token(token: str) -> int | None:
    """
    Verify a session token and return the user_id if valid.
    Returns None if the token is invalid or expired.
    """
    try:
        data = _serializer.loads(token, max_age=SESSION_MAX_AGE)
        return data.get("user_id")
    except (BadSignature, SignatureExpired):
        return None
