# API: /api/v1/agents (CRUD)

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

# Importa tutti i pezzi
from app.shared.schemas.agent_schemas import AgentCreate, AgentRead, AgentReadFull
from app.control_plane.services import agent_service
from app.shared.persistence.db_client import get_db

router = APIRouter()

@router.post("", response_model=AgentRead, status_code=status.HTTP_201_CREATED)     #specifichiamo che come output vogliamo un oggetto AgentRead; pydantic si occuperà di convertire l'AgentModel in AgentRead
def create_agent(
        agent_data: AgentCreate,  # 1. FastAPI valida il JSON in entrata usando AgentCreate
        db: Session = Depends(get_db)  # 2. FastAPI inietta una sessione DB
        ):
    """
    Crea un nuovo agente nel sistema.
    """
    try:
        # 3. Chiama il "Manager" (service)
        created_agent = agent_service.create_agent(db=db, agent_data=agent_data)

        # 4. FastAPI converte il 'created_agent' (modello SQLAlchemy)
        #    nello schema 'AgentRead' (JSON) grazie a response_model e from_attributes
        return created_agent

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=list[AgentRead])
def read_all_agents(db: Session = Depends(get_db)):
    """
    Restituisce la lista di agenti creati
    """
    try:
        return agent_service.get_all_agents(db=db)

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{agent_id}", response_model=AgentReadFull)
def read_agent(agent_id: int,
               db: Session = Depends(get_db)
               ):
    """
    Restituisce l'agente con id specificato
    """
    try:
        return agent_service.get_agent(db=db, agent_id=agent_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{agent_id}", response_model=AgentReadFull)
def update_agent(agent_data: AgentCreate,
                 agent_id: int,
                 db: Session = Depends(get_db)
                 ):
    """
    Aggiorna l'agente nel sistema con i nuovi valori
    """
    try:
        updated_agent = agent_service.update_agent(db=db, agent_id=agent_id, agent_data=agent_data)

        return updated_agent

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_agent(agent_id: int,
                 db: Session = Depends(get_db)):
    """
    Cancella l'agente con id specificato dal sistema
    """
    try:
        agent_service.delete_agent(db=db, agent_id=agent_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))