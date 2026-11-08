from pydantic import BaseModel, Field
from typing import Optional


# Schema di base (campi comuni)
class PromptBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Nome del prompt")
    description: Optional[str] = Field(None, description="Descrizione del prompt")
    system_prompt: str = Field(..., description="Contenuto del system prompt")


# Schema per la CREAZIONE (ciò che riceviamo dal frontend)
class PromptCreate(PromptBase):
    pass  # Per ora, è uguale alla base

# Schema per la LETTURA (ciò che restituiamo, include l'ID del DB)
class PromptRead(PromptBase):
    id: int

    class Config:
        from_attributes = True