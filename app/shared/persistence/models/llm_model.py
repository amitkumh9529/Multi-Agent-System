from sqlalchemy import String, Integer, Boolean, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from typing import TYPE_CHECKING
from ..db_client import Base

if TYPE_CHECKING:
    from app.shared.persistence.models import AgentModel

class LLMModel(Base):
    __tablename__ = "llm_models"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Identificativi
    name: Mapped[str] = mapped_column(String, unique=True)  # es. "GPT-4 Turbo" (da mostrare in UI)
    api_model_name: Mapped[str] = mapped_column(String)  # es. "gpt-4-0125-preview" (da mandare all'API)
    provider: Mapped[str] = mapped_column(String)  # es. "openai", "aws", "azure"

    # Relationship: un modello può essere usato da molti agenti
    agents: Mapped["AgentModel"] = relationship(
        "AgentModel",
        back_populates="llm_model"
    )
