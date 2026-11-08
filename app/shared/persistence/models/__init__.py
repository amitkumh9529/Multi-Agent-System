from app.shared.persistence.db_client import Base

from app.shared.persistence.models.prompt_model import PromptModel  # registriamo i modelli così SQLAlchemy crea tutte le tabelle con Base.metadata.create_all()
from app.shared.persistence.models.agent_model import AgentModel
from app.shared.persistence.models.team_model import TeamModel
from app.shared.persistence.models.llm_model import LLMModel
from app.shared.persistence.models.thread_model import ChatThreadModel
from app.shared.persistence.models.message_model import ChatMessageModel
from app.shared.persistence.models.tool_model import ToolModel
from app.shared.persistence.models.kb_model import KnowledgeBaseModel, DocumentModel

__all__ = ["Base", "PromptModel", "AgentModel", "TeamModel", "LLMModel", "ChatThreadModel",
           "ChatMessageModel", "ToolModel", "KnowledgeBaseModel", "DocumentModel"]     # tramite questo ogni classe può importare questi oggetti direttamente da shared.persistence.models