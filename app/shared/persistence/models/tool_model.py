import uuid
from typing import List

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from . import AgentModel
from ..db_client import Base


class ToolModel(Base):
    __tablename__ = "tools"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Nome tecnico usato nel codice (es. "web_search")
    name: Mapped[str] = mapped_column(String(50), unique=True, index=True)

    # Nome visualizzato nella UI (es. "Ricerca Web Avanzata")
    display_name: Mapped[str] = mapped_column(String(100))

    # Descrizione per l'utente (UI) e per l'Agent (System Prompt)
    description: Mapped[str] = mapped_column(Text, nullable=True)

    # Relazione one to many: un tool è usato da più agenti
    agents: Mapped[List["AgentModel"]] = relationship(
        "AgentModel",
        secondary="agent_tools",
        back_populates="tools"
    )