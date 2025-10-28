from schemas.game_data import GameDataPayload
import core.memory_data as memory

def format_league_data(data: GameDataPayload):
    current_session = memory.current_session
    game_data = memory.game_data

    return