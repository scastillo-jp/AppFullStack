import jwt
from datetime import datetime, timezone, timedelta
from app.core.config import (
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()

def hash_password(password:str):
    return password_hash.hash(password)

def verify_password(password: str, hashed_password: str):
    return password_hash.verify(password, hashed_password)

def create_access_token(claims: dict):
    token_claims = claims.copy()

    expires_at = datetime.now(timezone.utc) + timedelta(
        minutes = ACCESS_TOKEN_EXPIRE_MINUTES
    )

    token_claims.update({"exp": expires_at})

    return jwt.encode(
        token_claims,
        SECRET_KEY,
        algorithm=ALGORITHM
    ) 