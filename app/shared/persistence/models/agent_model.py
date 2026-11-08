from typing import Optional, List
from sqlalchemy import Integer, String, Float, ForeignKey, Enum as SQLEnum, Column, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import ARRAY
from app.shared.persistence.models import Base
import enum
from typing import TYPE_CHECKING

from app.shared.schemas.agent_schemas import AgentType

if TYPE_CHECKING:
    from app.shared.persistence.models import PromptModel, TeamModel, LLMModel, ToolModel, KnowledgeBaseModel


# Tabella di unione Agenti <-> Tools
agent_tools = Table(
    "agent_tools",
    Base.metadata,
    Column("agent_id", ForeignKey("agents.id", ondelete="CASCADE"), primary_key=True),
    Column("tool_id", ForeignKey("tools.id", ondelete="CASCADE"), primary_key=True),
)


# Tabella di unione Agenti <-> Knowledge Bases
agent_kbs = Table(
    "agent_kbs",
    Base.metadata,
    Column("agent_id", ForeignKey("agents.id", ondelete="CASCADE"), primary_key=True),
    Column("kb_id", ForeignKey("knowledge_bases.id", ondelete="CASCADE"), primary_key=True),
)


class AgentModel(Base):
    __tablename__ = "agents"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    description: Mapped[str] = mapped_column(String, nullable=True)
    temperature: Mapped[float] = mapped_column(Float, default=0.0)
    agent_type: Mapped[AgentType] = mapped_column(
        SQLEnum(AgentType, native_enum=False),
        default=AgentType.WORKER
    )

    # Foreign Key verso Prompt
    prompt_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("prompts.id", ondelete="RESTRICT"),
        nullable=True
    )

    # Relationship: un agente ha un prompt.
    prompt: Mapped["PromptModel"] = relationship( #Serve a mappare e navigare le relazioni tra i modelli (tabelle) a livello di Python.
        "PromptModel",                  # Non aggiunge colonne al DB (quello lo fa la ForeignKey),
        back_populates="agents"        # permettono di accedere agli oggetti correlati in modo diretto (es. prompt.agents), senza scrivere query SQL esplicite.
                                        # back_populates permette di sincronizzare il campo automaticamente (es. alla creazione di un nuovo agente con questo prompt)
    )

    # Foreign Key verso llm_Model
    llm_model_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("llm_models.id", ondelete="RESTRICT"),
        nullable=False
    )

    # Relationship: un agente usa un Modello llm
    llm_model: Mapped["LLMModel"] = relationship(
        "LLMModel",
        back_populates="agents"
    )

    # Relationship per i team dove questo agent è SUPERVISOR (one to many)
    managed_teams: Mapped[List["TeamModel"]] = relationship(
        "TeamModel",
        foreign_keys="[TeamModel.supervisor_id]",
        back_populates="supervisor"
    )

    # Relationship per i team dove questo agent è WORKER (one to many)
    worker_teams: Mapped[List["TeamModel"]] = relationship(
        "TeamModel",
        secondary="team_workers",
        back_populates="workers"
    )

    # Relationship per i tool usati dall'agente (one to many: un agente ha più tool)
    tools: Mapped[List["ToolModel"]] = relationship(
        "ToolModel",
        secondary="agent_tools",
        back_populates="agents"
    )

    # 2. Knowledge Bases
    knowledge_bases: Mapped[List["KnowledgeBaseModel"]] = relationship(
        "KnowledgeBaseModel",
        secondary="agent_kbs",
        back_populates="agents"
    )