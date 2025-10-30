from typing import List, Dict, Any, Optional
from app.schemas.game_data import GameDataPayload, GameData
from app.schemas.player_data import PlayerData
import app.core.memory_data as memory


def format_league_data(payload: GameDataPayload) -> GameData:
    raw_data = payload.data

    active_player_data = raw_data.get("activePlayer")
    game_data_obj = raw_data.get("gameData")
    all_players_data = raw_data.get("allPlayers")

    if not all_players_data:
        return GameData(
            game_status="UNKNOWN",
            main_player=PlayerData(
                name="Unknown", champion="Unknown", kills=0, deaths=0,
                assists=0, creep_score=0, current_gold=0.0,
                current_items=[], main_rune="Unknown"
            ),
            ally_players=[],
            enemy_players=[]
        )

    active_player_riot_id = active_player_data.get("riotId", "") if active_player_data else ""
    game_status = game_data_obj.get("gameMode", "UNKNOWN") if game_data_obj else "UNKNOWN"

    main_player = None
    main_player_team = None
    temp_players = []

    for player_data in all_players_data:
        player_riot_id = player_data.get("riotId")

        if player_riot_id == active_player_riot_id:
            main_player = _create_player_from_data(player_data, active_player_data)
            main_player_team = player_data.get("team")
        else:
            temp_players.append((player_data, player_data.get("team")))

    if main_player is None:
        main_player = _create_player_from_data(all_players_data[0], active_player_data)
        main_player_team = all_players_data[0].get("team")
        temp_players = temp_players[1:] if len(temp_players) > 0 else []

    ally_players = []
    enemy_players = []
    for player_data, player_team in temp_players:
        player = _create_player_from_data(player_data)
        if player_team == main_player_team:
            ally_players.append(player)
        else:
            enemy_players.append(player)

    game_data = GameData(
        game_status=game_status,
        main_player=main_player,
        ally_players=ally_players,
        enemy_players=enemy_players
    )

    update_game_data(game_data)

    return game_data

def _create_player_from_data(player_data: Dict[str, Any], active_player_data: Optional[Dict[str, Any]] = None) -> PlayerData:
    scores = player_data.get("scores")
    items_data = player_data.get("items")

    if items_data:
        item_names = [item["displayName"] for item in items_data if "displayName" in item]
    else:
        item_names = []

    current_gold = active_player_data.get("currentGold", 0.0) if active_player_data else 0.0

    main_rune = "Unknown"
    if active_player_data:
        full_runes = active_player_data.get("fullRunes")
        if full_runes:
            general_runes = full_runes.get("generalRunes")
            if general_runes:
                main_rune = general_runes[0].get("displayName", "Unknown")
    else:
        runes = player_data.get("runes")
        if runes:
            keystone = runes.get("keystone")
            if keystone:
                main_rune = keystone.get("displayName", "Unknown")

    return PlayerData(
        name=player_data.get("riotIdGameName", "Unknown"),
        champion=player_data.get("championName", "Unknown"),
        kills=scores.get("kills", 0) if scores else 0,
        deaths=scores.get("deaths", 0) if scores else 0,
        assists=scores.get("assists", 0) if scores else 0,
        creep_score=scores.get("creepScore", 0) if scores else 0,
        current_gold=current_gold,
        current_items=item_names,
        main_rune=main_rune
    )

def extract_players(all_players_data: List[Dict[str, Any]], main_player_team: str) -> tuple[List[PlayerData], List[PlayerData]]:
    ally_players = []
    enemy_players = []

    for player_data in all_players_data:
        player = _create_player_from_data(player_data)

        if player_data.get("team") == main_player_team:
            ally_players.append(player)
        else:
            enemy_players.append(player)

    return ally_players, enemy_players

def update_game_data(data: GameData) -> None:
    memory.game_data = data