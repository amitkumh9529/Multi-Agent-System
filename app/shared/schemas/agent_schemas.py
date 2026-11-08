import uuid

from pydantic import BaseModel, Field

from app.shared.schemas.kb_schemas import KnowledgeBaseRead
from app.shared.schemas.llm_model_schemas import LLMModelRead
from app.shared.schemas.prompt_schemas import PromptRead
from typing import Optional, List
import enum

from app.shared.schemas.tool_schemas import ToolRead


class AgentType(str, enum.Enum):
    SUPERVISOR = "supervisor"
    WORKER = "worker"


# Schema di base (campi comuni)
class AgentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Nome dell'agent")
    description: str = Field(..., description="Descrizione del team")
    prompt_id: Optional[int] = Field(default=None, gt=0, description="ID del prompt da associare")  # non lo rendo obbligatorio
    llm_model_id: int = Field(..., gt=0, description="ID del modello LLM da associare")
    temperature: float = Field(0.0, ge=0.0, le=1.0, description="Temperatura del modello LLM")
    agent_type: AgentType = AgentType.WORKER


# Schema per la CREAZIONE (ciò che riceviamo dal frontend)
class AgentCreate(AgentBase):
    tool_ids: List[int] = Field(default_factory=list)   # in fase di creazione il frontend manda id dei tool e delle kb a cui agente ha accesso
    kb_ids: Optional[List[uuid.UUID]] = Field(default=None)


# Schema per la LETTURA (ciò che restituiamo, include l'ID del DB)
class AgentReadFull(AgentBase):
    id: int
    prompt_id: Optional[int] = Field(default=None, exclude=True)    # Lo escludo così non lo visualizzo in output, in quanto ho l'intero 'prompt'
    prompt: Optional[PromptRead]  # Include i dettagli del prompt
    llm_model: LLMModelRead  # Include i dettagli del LLM utilizzato
    tools : List[ToolRead]  # Include i dettagli dei tool utilizzati
    knowledge_bases: List[KnowledgeBaseRead]    # include i dettagli delle knowledge base utilizzate

    class Config:
        from_attributes = True  # Questo dice a Pydantic di leggere i dati da un modello SQLAlchemy
        # quindi pydantic per il campo id di AgentRead, legge created_agent.id etc. e crea AgentRead


class AgentRead(AgentBase):
    id: int

    class Config:
        from_attributes = True
