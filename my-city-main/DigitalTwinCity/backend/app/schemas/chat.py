from datetime import datetime

from pydantic import BaseModel, Field


class ChatMessageCreate(BaseModel):
    sender: str = Field(min_length=1, max_length=120)
    text: str = Field(min_length=1, max_length=2000)


class ChatMessageResponse(BaseModel):
    id: int
    sender: str
    text: str
    created_at: datetime
