import time
import uuid
import jwt
from passlib.context import CryptContext
from typing import Literal
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGORITHM = "HS256"


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)


class TokenType:
    ACCESS: Literal["access"] = "access"
    REFRESH: Literal["refresh"] = "refresh"


def _make_token(
    sub: int, token_version: int, token_type: str, expires_in_seconds: int
) -> str:
    now = int(time.time())
    payload = {
        "sub": str(sub),
        "iat": now,
        "nbf": now,
        "exp": now + expires_in_seconds,
        "jti": str(uuid.uuid4()),
        "type": token_type,
        "tv": token_version,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)


def create_access_token(user_id: int, token_version: int) -> str:
    return _make_token(
        sub=user_id,
        token_version=token_version,
        token_type=TokenType.ACCESS,
        expires_in_seconds=settings.ACCESS_TOKEN_EXPIRES_MIN * 60,
    )


def create_refresh_token(user_id: int, token_version: int) -> str:
    return _make_token(
        sub=user_id,
        token_version=token_version,
        token_type=TokenType.REFRESH,
        expires_in_seconds=settings.REFRESH_TOKEN_EXPIRES_DAYS * 86400,
    )


def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
