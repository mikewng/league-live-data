from pydantic import BaseModel

class Session():
    user: str
    isActive: bool