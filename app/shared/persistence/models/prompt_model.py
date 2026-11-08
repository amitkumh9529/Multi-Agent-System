from sqlalchemy import String, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.shared.persistence.models import Base
from typing import TYPE_CHECKING

# Import per type checking (evita circular imports: le due classi per funzionare devono importarsi a vicenda)
if TYPE_CHECKING:
    from app.shared.persistence.models import AgentModel



class PromptModel(Base):
    __tablename__ = "prompts"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    description: Mapped[str] = mapped_column(String, nullable=True)
    system_prompt: Mapped[str] = mapped_column(String, nullable=False)

    # Relationship: un prompt può essere usato da molti agenti
    agents: Mapped[list["AgentModel"]] = relationship(
        "AgentModel",
        back_populates="prompt"
    )