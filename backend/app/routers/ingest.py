from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from typing import Optional, Dict, Any

from schemas.auth import ConnectionRequest
from schemas.session import Session
from schemas.game_data import GameData

router = APIRouter()

current_session: Optional[Session] = None
game_data: Optional[GameData] = None

# Live Game Data of Any JSON Format to be used for updating game data
class GameDataPayload(BaseModel):
    data: Dict[str, Any]

# Checks if there is no active user, and then sets up a session for a user
@router.post("/connection/establish")
async def check_connection(
    payload: ConnectionRequest,
    authorization: Optional[str] = Header(None)
):
    global current_session
    global game_data

    if authorization:
        token_from_header = authorization.replace("Bearer ", "")
        if token_from_header != payload.token:
            raise HTTPException(status_code=401, detail="Token mismatch")

    if current_session is not None and current_session.isActive:
        raise HTTPException(status_code=500, detail="Another user is using this session right now.")

    current_session = Session()
    current_session.user = payload.username
    current_session.isActive = True

    return {"status": "connected", "message": "Token verified"}


# Checks username and auth token and sets isActive to False if true
# Should also clear the game session data
@router.post("/connection/disconnect")
async def disconnect(
    payload: ConnectionRequest,
    authorization: Optional[str] = Header(None)
):
    global current_session
    global game_data

    if authorization:
        token_from_header = authorization.replace("Bearer ", "")
        if token_from_header != payload.token:
            raise HTTPException(status_code=401, detail="Token mismatch")

    if current_session is None:
        raise HTTPException(status_code=404, detail="No active session")

    if current_session.user != payload.username:
        raise HTTPException(status_code=401, detail="Session user mismatch")

    if current_session.isActive:
        current_session.isActive = False
        game_data = None
    else:
        raise HTTPException(status_code=500, detail="Session already inactive.")

    return {"status": "disconnected", "message": "Session ended successfully"}
    
# Regularly called endpoint that gets live league game data and updates to the storage
@router.post("/ingest", status_code=201)
async def ingest_game_json(payload: GameDataPayload):
    global current_session
    global game_data

    if current_session is None:
        raise HTTPException(status_code=404, detail="No active session")

    if not current_session.isActive:
        raise HTTPException(status_code=403, detail="Session is not active")
    
    # Update in-memory data of league game with payload

    return {
        "message": "Data ingested successfully",
        "user": current_session.user,
        "data_received": True
    }