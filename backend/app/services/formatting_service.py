from schemas.game_data import GameDataPayload, GameData
from schemas.player_data import PlayerData
import core.memory_data as memory

# Takes in payload, formats it into a game object
def format_league_data(data: GameDataPayload):
    game_data = GameData()
    mc_player = PlayerData()

    mc_player.name = data["allPlayers"][0]["riotIdGameName"]
    mc_player.kills = data["allPlayers"][0]["scores"]["kills"]
    mc_player.deaths = data["allPlayers"][0]["scores"]["deaths"]
    mc_player.assists = data["allPlayers"][0]["scores"]["assists"]
    mc_player.creep_score = data["allPlayers"][0]["scores"]["creepScore"]

    game_data.main_player = mc_player
    update_game_data(game_data)

# Helper method to extract players from json and append it to list 
def extract_players(players_data: GameDataPayload):
    return

# Finally update in-memory game data with new object
def update_game_data(data: GameData):
    game_data = memory.game_data
    return