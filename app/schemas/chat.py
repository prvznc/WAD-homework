from datetime import datetime

from pydantic import BaseModel, Field


class MessageOut(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatOut(BaseModel):
    id: int
    title: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatDetail(ChatOut):
    messages: list[MessageOut]


class ChatCreate(BaseModel):
    title: str = Field(default="new chat", max_length=255)


class MessageCreate(BaseModel):
    content: str = Field(min_length=1)
