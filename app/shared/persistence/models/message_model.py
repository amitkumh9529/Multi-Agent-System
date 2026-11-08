import enum
import uuid

from sqlalchemy import String, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column
from ..db_client import Base
from sqlalchemy.dialects.postgresql import UUID


class MessageType(str, enum.Enum):
    HUMAN = "human"
    AI = "ai"

class ChatMessageModel(Base):
    __tablename__ = "chat_messages"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)

    thread_id: Mapped[str] = mapped_column(ForeignKey("chat_threads.thread_id", ondelete="CASCADE"), index=True)
    # thread_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("chat_threads.thread_id", ondelete="CASCADE"),index=True)  # ForeignKey alla chat # TODO: Questa è la foreign key
    type: Mapped[MessageType] = mapped_column(
        SQLEnum(MessageType, native_enum=False),
        default=MessageType.AI
    )
    content: Mapped[str] = mapped_column(Text)  # contenuto del messaggio
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True) # per ordinamento temporale