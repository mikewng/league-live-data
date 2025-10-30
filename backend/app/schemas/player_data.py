from typing import List
from pydantic import BaseModel

class PlayerData(BaseModel):
    name: str
    kills: int
    deaths: int
    assists: int
    creep_score: int
    current_gold: float
    current_items: List[str]