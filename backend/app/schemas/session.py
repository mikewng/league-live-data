from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Session(BaseModel):
    user: str
    token: str
    isActive: bool
    created_at: datetime
    last_activity: Optional[datetime] = None