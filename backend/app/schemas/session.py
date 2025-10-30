from pydantic import BaseModel

class Session(BaseModel):
    user: str
    isActive: bool