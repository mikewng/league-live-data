from pydantic import BaseModel

class ConnectionRequest(BaseModel):
    token: str
    username: str