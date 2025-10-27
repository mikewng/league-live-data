from typing import List
from player_data import PlayerData

class GameData:
    game_status: str
    main_player: PlayerData
    ally_players: List[PlayerData]
    enemy_players: List[PlayerData]