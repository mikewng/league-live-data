from typing import Optional
from schemas.session import Session
from schemas.game_data import GameData

# In-memory storage for single session and game data
current_session: Optional[Session] = None
game_data: Optional[GameData] = None
