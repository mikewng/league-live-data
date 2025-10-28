from fastapi import APIRouter, HTTPException, Header
from typing import Optional

from schemas.auth import ConnectionRequest
from schemas.session import Session
from schemas.game_data import GameDataPayload
import core.memory_data as memory

router = APIRouter()

# Checks if there is no active user, and then sets up a session for a user
@router.post("/connection/establish")
async def check_connection(
    payload: ConnectionRequest,
    authorization: Optional[str] = Header(None)
):
    if authorization:
        token_from_header = authorization.replace("Bearer ", "")
        if token_from_header != payload.token:
            raise HTTPException(status_code=401, detail="Token mismatch")

    if memory.current_session is not None and memory.current_session.isActive:
        raise HTTPException(status_code=500, detail="Another user is using this session right now.")

    memory.current_session = Session()
    memory.current_session.user = payload.username
    memory.current_session.isActive = True

    return {"status": "connected", "message": "Token verified"}


# Checks username and auth token and sets isActive to False if true
# Should also clear the game session data
@router.post("/connection/disconnect")
async def disconnect(
    payload: ConnectionRequest,
    authorization: Optional[str] = Header(None)
):
    if authorization:
        token_from_header = authorization.replace("Bearer ", "")
        if token_from_header != payload.token:
            raise HTTPException(status_code=401, detail="Token mismatch")

    if memory.current_session is None:
        raise HTTPException(status_code=404, detail="No active session")

    if memory.current_session.user != payload.username:
        raise HTTPException(status_code=401, detail="Session user mismatch")

    if memory.current_session.isActive:
        memory.current_session.isActive = False
        memory.game_data = None
    else:
        raise HTTPException(status_code=500, detail="Session already inactive.")

    return {"status": "disconnected", "message": "Session ended successfully"}
    
# Regularly called endpoint that gets live league game data and updates to the storage
@router.post("/ingest", status_code=201)
async def ingest_game_json(payload: GameDataPayload):
    if memory.current_session is None:
        raise HTTPException(status_code=404, detail="No active session")

    if not memory.current_session.isActive:
        raise HTTPException(status_code=403, detail="Session is not active")

    return {
        "message": "Data ingested successfully",
        "user": memory.current_session.user,
        "data_received": True
    }