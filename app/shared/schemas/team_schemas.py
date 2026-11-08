from pydantic import BaseModel, Field, field_validator
from typing import List, Optional

from app.shared.schemas.agent_schemas import AgentRead

# Schema base con campi comuni
class TeamBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Nome del team")   # il valore puntato (...) indica che il campo è obbligatorio
    description: Optional[str] = Field(None, description="Descrizione del team")    # uso None che è il valore di default in quanto è un campo opzionale


# Schema per la creazione di un team
class TeamCreate(TeamBase):
    supervisor_id: int = Field(..., gt=0, description="ID dell'agente supervisor")    # gt=0 : greater than 0
    worker_ids: List[int] = Field(default_factory=list, description="Lista degli ID dei worker")

    @field_validator('worker_ids')
    @classmethod
    def validate_worker_ids(cls, v):
        """Valida che non ci siano ID duplicati"""
        if len(v) != len(set(v)):
            raise ValueError("worker_ids contiene duplicati")
        return v

    @field_validator('worker_ids')          #decoratore che registra questa funzione come validatore per il campo 'worker_ids'
    @classmethod                            # specifica che si tratta di un metodo di classe e non di istanza
    def validate_supervisor_not_in_workers(cls, v, info):          # cls: classe stessa (TeamCreate); v: valore del campo (ossia worker_ids); info: oggetto ValidationInfo che contiene informazioni sulla validazione in corso
        """Valida che il supervisor non sia anche nella lista dei worker"""
        supervisor_id = info.data.get('supervisor_id')            # info.data: dizionario contenente tutti i campi già validati fino a questo punto; la get restituisce il campo o None in modo sicuro.
        if supervisor_id and supervisor_id in v:                  # controllo se il valore esiste (non è None) e se non è presente nella lista dei workers
            raise ValueError("Il supervisor non può essere anche un worker dello stesso team")
        return v


class TeamRead(TeamBase):
    id: int

    class Config:
        from_attributes: True


class TeamReadFull(TeamBase):
    id: int
    supervisor: AgentRead
    workers: List[AgentRead]

    class Config:
        from_attributes: True