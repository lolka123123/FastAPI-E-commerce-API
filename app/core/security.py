import jwt
from datetime import datetime, timezone, timedelta
from pwdlib import PasswordHash
import secrets
import hashlib

from app.core.config import settings


def create_access_token(user_id: str) -> str:
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=settings.access_token_expire_minutes)

    payload = {
        'sub': str(user_id),
        'iat': now,
        'exp': expire
    }
    token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return token

def decode_access_token(token: str) -> dict:
    payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    return payload




password_hash = PasswordHash.recommended()

def hash_password(password: str) -> str:
    return password_hash.hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
    return  password_hash.verify(password, hashed_password)




def generate_secure_token() -> str:
    return secrets.token_urlsafe(64)

def hash_secure_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()