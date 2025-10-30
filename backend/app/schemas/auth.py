from pydantic import BaseModel

class ConnectionRequest(BaseModel):
    username: str