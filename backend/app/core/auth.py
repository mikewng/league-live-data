from fastapi import Header, HTTPException, Depends
from typing import Optional
from datetime import datetime, timezone

from app.core.config import Settings
import app.core.memory_data as memory
from app.schemas.session import Session

_settings: Optional[Settings] = None

def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def extract_bearer_token(authorization: Optional[str] = Header(None, alias="Authorization")) -> str:
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Missing Authorization header",
            headers={"WWW-Authenticate": "Bearer"}
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid Authorization header format. Expected: Bearer <token>",
            headers={"WWW-Authenticate": "Bearer"}
        )

    token = authorization.replace("Bearer ", "", 1).strip()
    if not token:
        raise HTTPException(
            status_code=401,
            detail="Token is empty",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return token


def validate_secret_token(
    token: str = Depends(extract_bearer_token),
    settings: Settings = Depends(get_settings)
) -> str:
    if token != settings.SECRET_TOKEN:
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return token


def validate_active_session(
    token: str = Depends(validate_secret_token)
) -> Session:
    if memory.current_session is None:
        raise HTTPException(
            status_code=404,
            detail="No active session. Please establish a connection first."
        )

    if not memory.current_session.isActive:
        raise HTTPException(
            status_code=403,
            detail="Session is inactive. Please establish a new connection."
        )

    if memory.current_session.token != token:
        raise HTTPException(
            status_code=401,
            detail="Token does not match the active session"
        )

    memory.current_session.last_activity = datetime.now(timezone.utc)

    return memory.current_session

RequireToken = Depends(validate_secret_token)
RequireSession = Depends(validate_active_session)
