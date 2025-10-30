from typing import Optional, Dict, Any, List, Callable, Awaitable
from dataclasses import dataclass, field
from enum import Enum
from app.schemas.game_data import GameData
from app.schemas.player_data import PlayerData
import asyncio


class ChangeType(Enum):
    KILL = "kill"
    DEATH = "death"
    ASSIST = "assist"
    ITEM_PURCHASE = "item_purchase"
    GOLD_MILESTONE = "gold_milestone"
    CS_MILESTONE = "cs_milestone"
    GAME_STATUS = "game_status"


@dataclass
class ChangeEvent:
    change_type: ChangeType
    player_name: str
    old_value: Any
    new_value: Any
    context: Dict[str, Any] = field(default_factory=dict)

    def to_prompt(self) -> str:
        if self.change_type == ChangeType.KILL:
            return (f"{self.player_name} just got a kill! "
                   f"They now have {self.new_value} kills (was {self.old_value}). "
                   f"Current stats: {self.context.get('deaths', 0)} deaths, "
                   f"{self.context.get('assists', 0)} assists, "
                   f"{self.context.get('cs', 0)} CS, "
                   f"{self.context.get('gold', 0)} gold.")

        elif self.change_type == ChangeType.DEATH:
            return (f"{self.player_name} just died! "
                   f"They now have {self.new_value} deaths (was {self.old_value}). "
                   f"Current stats: {self.context.get('kills', 0)} kills, "
                   f"{self.context.get('assists', 0)} assists, "
                   f"{self.context.get('cs', 0)} CS.")

        elif self.change_type == ChangeType.ASSIST:
            return (f"{self.player_name} got an assist! "
                   f"They now have {self.new_value} assists. "
                   f"Current KDA: {self.context.get('kills', 0)}/{self.context.get('deaths', 0)}/{self.new_value}")

        elif self.change_type == ChangeType.ITEM_PURCHASE:
            new_items = set(self.new_value) - set(self.old_value)
            return (f"{self.player_name} just purchased new items: {', '.join(new_items)}! "
                   f"They now have: {', '.join(self.new_value)}. "
                   f"Current gold: {self.context.get('gold', 0)}")

        elif self.change_type == ChangeType.GOLD_MILESTONE:
            return (f"{self.player_name} reached {self.new_value} gold! "
                   f"Current stats: {self.context.get('kills', 0)}/{self.context.get('deaths', 0)}/{self.context.get('assists', 0)} KDA, "
                   f"{self.context.get('cs', 0)} CS.")

        elif self.change_type == ChangeType.CS_MILESTONE:
            return (f"{self.player_name} reached {self.new_value} CS! "
                   f"Current gold: {self.context.get('gold', 0)}")

        elif self.change_type == ChangeType.GAME_STATUS:
            return (f"Game status changed from '{self.old_value}' to '{self.new_value}'")

        return f"{self.change_type.value} changed for {self.player_name}"


class ChangeDetector:
    def __init__(self):
        self.previous_data: Optional[GameData] = None
        self.callbacks: List[Callable[[List[ChangeEvent]], Awaitable[None]]] = []
        self.track_kills = True
        self.track_deaths = True
        self.track_assists = True
        self.track_items = True
        self.track_game_status = True
        self.gold_milestones = [1000, 2000, 3000, 5000, 7500, 10000, 15000]
        self.cs_milestones = [50, 100, 150, 200, 250, 300]

    def register_callback(self, callback: Callable[[List[ChangeEvent]], Awaitable[None]]):
        self.callbacks.append(callback)

    async def detect_changes(self, current_data: GameData) -> List[ChangeEvent]:
        if self.previous_data is None:
            self.previous_data = current_data
            return []

        changes: List[ChangeEvent] = []

        if self.track_game_status and self.previous_data.game_status != current_data.game_status:
            changes.append(ChangeEvent(
                change_type=ChangeType.GAME_STATUS,
                player_name="System",
                old_value=self.previous_data.game_status,
                new_value=current_data.game_status
            ))

        main_player_changes = self._detect_player_changes(
            self.previous_data.main_player,
            current_data.main_player,
            is_main_player=True
        )
        changes.extend(main_player_changes)

        for prev_ally in self.previous_data.ally_players:
            curr_ally = self._find_player_by_name(current_data.ally_players, prev_ally.name)
            if curr_ally:
                ally_changes = self._detect_player_changes(prev_ally, curr_ally, is_main_player=False)
                changes.extend(ally_changes)

        for prev_enemy in self.previous_data.enemy_players:
            curr_enemy = self._find_player_by_name(current_data.enemy_players, prev_enemy.name)
            if curr_enemy:
                enemy_changes = self._detect_player_changes(prev_enemy, curr_enemy, is_main_player=False)
                changes.extend(enemy_changes)

        self.previous_data = current_data

        if changes:
            await self._fire_callbacks(changes)

        return changes

    def _detect_player_changes(
        self,
        prev_player: PlayerData,
        curr_player: PlayerData,
        is_main_player: bool = False
    ) -> List[ChangeEvent]:
        changes: List[ChangeEvent] = []

        context = {
            "kills": curr_player.kills,
            "deaths": curr_player.deaths,
            "assists": curr_player.assists,
            "cs": curr_player.creep_score,
            "gold": curr_player.current_gold,
            "champion": curr_player.champion,
            "is_main_player": is_main_player
        }

        if self.track_kills and curr_player.kills > prev_player.kills:
            changes.append(ChangeEvent(
                change_type=ChangeType.KILL,
                player_name=curr_player.name,
                old_value=prev_player.kills,
                new_value=curr_player.kills,
                context=context
            ))

        if self.track_deaths and curr_player.deaths > prev_player.deaths:
            changes.append(ChangeEvent(
                change_type=ChangeType.DEATH,
                player_name=curr_player.name,
                old_value=prev_player.deaths,
                new_value=curr_player.deaths,
                context=context
            ))

        if self.track_assists and curr_player.assists > prev_player.assists:
            changes.append(ChangeEvent(
                change_type=ChangeType.ASSIST,
                player_name=curr_player.name,
                old_value=prev_player.assists,
                new_value=curr_player.assists,
                context=context
            ))

        if self.track_items and set(curr_player.current_items) != set(prev_player.current_items):
            # Only fire if new items were added (not removed/sold)
            if len(curr_player.current_items) >= len(prev_player.current_items):
                changes.append(ChangeEvent(
                    change_type=ChangeType.ITEM_PURCHASE,
                    player_name=curr_player.name,
                    old_value=prev_player.current_items,
                    new_value=curr_player.current_items,
                    context=context
                ))

        if is_main_player:
            for milestone in self.gold_milestones:
                if prev_player.current_gold < milestone <= curr_player.current_gold:
                    changes.append(ChangeEvent(
                        change_type=ChangeType.GOLD_MILESTONE,
                        player_name=curr_player.name,
                        old_value=prev_player.current_gold,
                        new_value=milestone,
                        context=context
                    ))

        if is_main_player:
            for milestone in self.cs_milestones:
                if prev_player.creep_score < milestone <= curr_player.creep_score:
                    changes.append(ChangeEvent(
                        change_type=ChangeType.CS_MILESTONE,
                        player_name=curr_player.name,
                        old_value=prev_player.creep_score,
                        new_value=milestone,
                        context=context
                    ))

        return changes

    def _find_player_by_name(self, players: List[PlayerData], name: str) -> Optional[PlayerData]:
        for player in players:
            if player.name == name:
                return player
        return None

    async def _fire_callbacks(self, changes: List[ChangeEvent]):
        for callback in self.callbacks:
            try:
                await callback(changes)
            except Exception as e:
                print(f"Error in change detection callback: {e}")

    def reset(self):
        self.previous_data = None

change_detector = ChangeDetector()
