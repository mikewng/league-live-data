from typing import List, Dict, Any
from pydantic import BaseModel
from app.schemas.player_data import PlayerData

class GameDataPayload(BaseModel):
    data: Dict[str, Any]
    
class GameData(BaseModel):
    game_status: str
    main_player: PlayerData
    ally_players: List[PlayerData]
    enemy_players: List[PlayerData]