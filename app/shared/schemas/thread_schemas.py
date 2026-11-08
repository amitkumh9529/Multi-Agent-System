import uuid

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class ChatThreadBase(BaseModel):
    # thread_id: uuid.UUID = Field(..., description="UUID generato dal client") #TODO: questa è la primary key
    thread_id: str = Field(..., description="UUID generato dal client")
    title: Optional[str] = Field(None, description="Titolo della conversazione")

class ChatThreadCreate(ChatThreadBase):
    # Possiamo dare un default al titolo se il frontend non lo manda
    title: str = "Nuova Chat"

class ChatThreadRead(ChatThreadBase):
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True