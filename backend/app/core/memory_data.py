from typing import Optional
from app.schemas.session import Session
from app.schemas.game_data import GameData

# In-memory storage for single session and game data
current_session: Optional[Session] = None
game_data: Optional[GameData] = None
