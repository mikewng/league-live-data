from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import Response
from datetime import datetime, timezone
from pydantic import BaseModel

from app.schemas.auth import ConnectionRequest
from app.schemas.session import Session
from app.schemas.game_data import GameDataPayload
import app.core.memory_data as memory
from app.core.auth import validate_secret_token, validate_active_session
from app.services.formatting_service import format_league_data
from app.services.change_detection_service import change_detector
from app.services.openai_service import handle_game_changes, text_to_speech

router = APIRouter()


class TTSRequest(BaseModel):
    text: str
    voice: str = "onyx"  # default voice

# Checks if there is no active user, and then sets up a session for a user
@router.post("/connection/establish")
async def check_connection(
    payload: ConnectionRequest,
    token: str = Depends(validate_secret_token)
):
    if memory.current_session is not None and memory.current_session.isActive:
        raise HTTPException(
            status_code=409,
            detail=f"User '{memory.current_session.user}' is already connected. Please disconnect first."
        )

    memory.current_session = Session(
        user=payload.username,
        token=token,
        isActive=True,
        created_at=datetime.now(timezone.utc),
        last_activity=datetime.now(timezone.utc)
    )

    return {
        "status": "connected",
        "message": f"Session established for user: {payload.username}",
        "user": payload.username
    }


# Checks username and auth token and sets isActive to False if true
# Should also clear the game session data
@router.post("/connection/disconnect")
async def disconnect(
    payload: ConnectionRequest,
    session: Session = Depends(validate_active_session)
):
    if session.user != payload.username:
        raise HTTPException(
            status_code=403,
            detail=f"Username mismatch. Current session belongs to: {session.user}"
        )

    memory.current_session.isActive = False
    memory.game_data = None
    change_detector.reset()

    return {
        "status": "disconnected",
        "message": f"Session ended successfully for user: {payload.username}",
        "user": payload.username
    }
    
# Regularly called endpoint that gets live league game data and updates to the storage
@router.post("/ingest", status_code=201)
async def ingest_game_json(
    payload: GameDataPayload,
    session: Session = Depends(validate_active_session)
):
    game_data = format_league_data(payload)

    changes = await change_detector.detect_changes(game_data)

    if changes:
        await handle_game_changes(changes)

    memory.game_data = game_data

    response = {
        "status": "success",
        "message": "Data ingested successfully",
        "user": session.user,
        "game_status": game_data.game_status,
        "changes_detected": len(changes),
    }

    return response

# Text-to-speech endpoint
@router.post("/tts")
async def generate_speech(
    payload: TTSRequest,
    session: Session = Depends(validate_active_session)
):
    try:
        audio_content = await text_to_speech(payload.text, payload.voice)

        return Response(
            content=audio_content,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "inline; filename=speech.mp3"
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate speech: {str(e)}"
        )