# Logica per validare/creare config agenti

from sqlalchemy.orm import Session
from app.shared.schemas.agent_schemas import AgentCreate
from app.shared.persistence import agent_db, prompt_db, tool_db, kb_db
from app.shared.persistence.models import AgentModel, LLMModel


def create_agent(db: Session, agent_data: AgentCreate) -> AgentModel:
    """
    Logica di business per creare un agente.
    """

    # 1. Controllo nome agente univoco
    if agent_db.get_agent_by_name(db, agent_data.name):
        raise ValueError(f"Un agente con nome {agent_data.name} esiste già")

    # 2. Controllo se prompt inserito esiste
    if agent_data.prompt_id is not None:
        prompt = prompt_db.get_prompt_by_id(db, agent_data.prompt_id)
        if not prompt:
            raise ValueError(f"Prompt con ID {agent_data.prompt_id} non trovato")

    # 3. Controllo llm_model valido
    llm_model = db.query(LLMModel).filter(LLMModel.id == agent_data.llm_model_id).first()
    if not llm_model:
        raise ValueError(f"Modello LLM con id={agent_data.llm_model_id} non trovato")

    # 4. Controllo tools esistenti
    filtered_tools = None
    if agent_data.tool_ids:
        filtered_tools = tool_db.filter_tools(db, agent_data.tool_ids)

    # 5. Controllo Knowledge Base
    filtered_kbs = None
    if agent_data.kb_ids:
        print(f"KB_IDS ricevuti: {agent_data.kb_ids}")
        filtered_kbs = kb_db.filter_kbs(db, agent_data.kb_ids)
        print(f"KB filtrate: {len(filtered_kbs)}")

    print(f"Servizio: Creo l'agente '{agent_data.name}'...")
    db_agent = agent_db.create_agent(db=db, agent_schema=agent_data, tools=filtered_tools, kbs=filtered_kbs)

    return db_agent


def get_all_agents(db: Session) -> list[AgentModel]:
    """
    Logica di business per ottenere la lista di tutti gli agenti.
    """
    agents = agent_db.get_all_agents(db=db)

    return agents


def update_agent(db: Session, agent_id: int, agent_data: AgentCreate) -> AgentModel:
    """
    Logica di business per aggiornare un agente.
    """

    # Controllo id agent esistente
    db_agent = agent_db.get_agent_by_id(db, agent_id)
    if not db_agent:
        raise ValueError(f"Agente con id='{agent_id}' non trovato")

    # Verifico che il nome non sia già usato da un altro agente
    if agent_data.name != db_agent.name:
        existing_agent = agent_db.get_other_agent_with_name(db, agent_data.name, agent_id)
        if existing_agent:
            raise ValueError(f"Un agente con nome '{agent_data.name}' esiste già")

    # Controllo se prompt inserito esiste
    if agent_data.prompt_id is not None:
        prompt = prompt_db.get_prompt_by_id(db, agent_data.prompt_id)
        if not prompt:
            raise ValueError(f"Prompt con ID {agent_data.prompt_id} non trovato")

    # Controllo llm_model valido
    llm_model = db.query(LLMModel).filter(LLMModel.id == agent_data.llm_model_id).first()
    if not llm_model:
        raise ValueError(f"Modello LLM con id={agent_data.llm_model_id} non trovato")


    # Controllo tools esistenti
    filtered_tools = None
    if agent_data.tool_ids:
        filtered_tools = tool_db.filter_tools(db, agent_data.tool_ids)

    # Controllo Knowledge Base
    filtered_kbs = None
    if agent_data.kb_ids:
        print(f"KB_IDS ricevuti: {agent_data.kb_ids}")
        filtered_kbs = kb_db.filter_kbs(db, agent_data.kb_ids)
        print(f"KB filtrate: {len(filtered_kbs)}")

    print(f"Servizio: Aggiorno l'agente con id='{agent_id}' e nome='{agent_data.name}'...")
    updated_agent = agent_db.update_agent(
        db=db,
        agent_id=agent_id,
        agent_schema=agent_data,
        tools=filtered_tools,
        kbs=filtered_kbs
    )
    return updated_agent


def get_agent(db: Session, agent_id: int) -> AgentModel:
    db_agent = agent_db.get_agent_by_id(db, agent_id)
    if not db_agent:
        raise ValueError(f"Agente con id='{agent_id}' non trovato")
    return db_agent


def delete_agent(db: Session, agent_id: int) -> None:
    db_agent = agent_db.get_agent_by_id(db, agent_id)
    if db_agent is None:
        raise ValueError(f"Agente con id='{agent_id}' non trovato")

    if len(db_agent.managed_teams) > 0:
        raise ValueError(f"L'agente selezionato è impiegato come Supervisor in un Team")
    agent_db.delete_agent(db=db, db_agent=db_agent)
    return