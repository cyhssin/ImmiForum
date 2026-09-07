from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

class TagResponse(BaseModel):
    id: UUID
    name: str
    created_at: datetime

    class Config:
        from_attributes = True