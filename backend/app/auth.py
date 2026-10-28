"""Very small admin login. Demo defaults are for local use only: set ADMIN_USER, ADMIN_PASSWORD
and SECRET_KEY as environment variables for anything real."""
import hmac
import os
import time
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me-use-a-long-random-value-in-real-use")
ADMIN_USER = os.getenv("ADMIN_USER", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
TOKEN_SECONDS = 2 * 60 * 60
bearer = HTTPBearer(auto_error=False)


def check_login(username: str, password: str) -> bool:
    ok_user = hmac.compare_digest(username.encode(), ADMIN_USER.encode())
    ok_pass = hmac.compare_digest(password.encode(), ADMIN_PASSWORD.encode())
    return ok_user and ok_pass


def make_token(username: str) -> str:
    now = int(time.time())
    return jwt.encode({"sub": username, "iat": now, "exp": now + TOKEN_SECONDS}, SECRET_KEY, algorithm="HS256")


def require_admin(creds: HTTPAuthorizationCredentials = Depends(bearer)) -> str:
    if creds is None:
        raise HTTPException(status_code=401, detail="Admin login required")
    try:
        data = jwt.decode(creds.credentials, SECRET_KEY, algorithms=["HS256"])
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return data["sub"]
