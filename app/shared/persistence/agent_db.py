# Funzioni di interazione con db per agenti tramite ORM offerto da sqlalchemy

from typing import Optional
from sqlalchemy.orm import Session

from app.shared.persistence.models import AgentModel, ToolModel, KnowledgeBaseModel
from app.shared.schemas.agent_schemas import AgentCreate, AgentRead


def create_agent(db: Session, agent_schema: AgentCreate, tools: list[ToolModel], kbs: list[KnowledgeBaseModel]) -> AgentModel:
    """
    Salva un nuovo agente nel DB.
    """
    # 1. Converte lo schema Pydantic (AgentCreate) in un dizionario Python e successivamente in un modello SQLAlchemy (AgentModel)
    db_agent = AgentModel(**agent_schema.model_dump(exclude={'tool_ids','kb_ids'}))

    if tools:
        db_agent.tools = tools

    if kbs:
        db_agent.knowledge_bases = kbs

    # 2. Aggiunge alla sessione, fa il commit e aggiorna
    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)  # Obbligatorio per ottenere l'ID generato dal DB

    return db_agent


def get_agent_by_id(db: Session, agent_id: int) -> Optional[AgentModel]:
    """
    Query per ottenere (e verificare) esistenza dell'agente con id specificato
    """
    return db.query(AgentModel).filter(AgentModel.id == agent_id).first()


def get_agents_by_ids(db: Session, agent_ids: list[int]) -> list[AgentModel]:
    """
    Query per ottenere una lista di Agenti salvati nel DB a partire da una lista di IDs.
    """
    return (db.query(AgentModel).filter(
        AgentModel.id.in_(agent_ids))
            .all())


def get_agent_by_name(db: Session, name: str) -> Optional[AgentModel]:
    """
    Query sqlAlchemy per ottenere l'agente nel DB con nome specificato
    """
    return db.query(AgentModel).filter(AgentModel.name == name).first()


def get_other_agent_with_name(db: Session, name: str, prompt_id: int) -> Optional[AgentModel]:
    """
    Funzione che verifica se sia presente un ALTRO agente (ossia altro id) con stesso nome
    """
    existing_agent = db.query(AgentModel).filter(
        AgentModel.name == name,
        AgentModel.id != prompt_id  # Esclude l'agente corrente
    ).first()
    return existing_agent


def get_all_agents(db: Session) -> list[AgentModel]:
    """
    Query per ottenere la lista di Agenti salvati nel DB
    """
    return db.query(AgentModel).all()


def update_agent(db: Session, agent_schema: AgentCreate, agent_id: int, tools: list[ToolModel], kbs: list[KnowledgeBaseModel]) -> Optional[AgentModel]:
    """
    Aggiorna un agente esistente nel DB.
    """
    # 1. Recupera l'agente esistente
    db_agent = db.query(AgentModel).filter(AgentModel.id == agent_id).first()

    # 2. Aggiorna i campi usando model_dump()
    for key, value in agent_schema.model_dump(exclude_unset=True).items():
        setattr(db_agent, key, value)

    # 3. Assegna tool e KBs
    if tools:
        db_agent.tools = tools

    if kbs:
        db_agent.knowledge_bases = kbs

    # 4. Commit e refresh
    db.commit()
    db.refresh(db_agent)

    return db_agent


def delete_agent(db: Session, db_agent: AgentModel) -> None:
    """
    Elimina un agente dal DB.
    """

    db.delete(db_agent)
    db.commit()
    return
