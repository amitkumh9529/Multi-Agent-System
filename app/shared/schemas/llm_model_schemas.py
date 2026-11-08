from typing import List
from pydantic import BaseModel, Field

class LLMModelBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Nome del modello LLM")
    api_model_name: str = Field(..., min_length=1, max_length=255, description="Nome del deployment")
    provider: str = Field(..., min_length=1, max_length=255, description="Nome del provider")

class LLMModelRead(LLMModelBase):
    id: int

    class Config:
        from_attributes = True