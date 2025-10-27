from pydantic import BaseModel

class ConnectionRequest(BaseModel):
    player_username: str