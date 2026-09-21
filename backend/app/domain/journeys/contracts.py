from datetime import datetime
from pydantic import BaseModel, Field

class JourneySnapshot(BaseModel):
    identifier: str = Field(min_length=1, max_length=150)
    status: str = Field(min_length=1, max_length=40)
    user_id: int | None = None
    correlation_id: str | None = None
    updated_at: datetime | None = None

class JourneyPage(BaseModel):
    items: list[JourneySnapshot] = Field(default_factory=list)
    next_cursor: str | None = None
