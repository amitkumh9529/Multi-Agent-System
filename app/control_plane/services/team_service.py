from app.shared.persistence.models import TeamModel
from app.shared.schemas.team_schemas import TeamCreate
from app.shared.persistence import team_db, agent_db
from sqlalchemy.orm import Session
from app.shared.schemas.agent_schemas import AgentType


def create_team(db: Session, team_data: TeamCreate) -> TeamModel:

    # Controllo nome team univoco
    if team_db.get_team_by_name(db, team_data.name):
        raise ValueError(f"Un team con nome {team_data.name} esiste già")

    # Controllo: agent supervisor esiste
    supervisor = agent_db.get_agent_by_id(db, team_data.supervisor_id)
    if not supervisor or supervisor.agent_type != AgentType.SUPERVISOR:
        raise ValueError(f"Agente supervisor con ID {team_data.supervisor_id} non trovato")

    # Controllo che i workers esistano
    workers = []
    if team_data.worker_ids:
        workers = agent_db.get_agents_by_ids(db, team_data.worker_ids)

        # Verifico tutti gli ID esistano
        if len(workers) != len(team_data.worker_ids):
            found_ids = {w.id for w in workers}
            missing_ids = set(team_data.worker_ids) - found_ids
            raise ValueError(f"Worker con ID {missing_ids} non trovati")

        # Verifica che siano tutti di tipo WORKER
        for worker in workers:
            if worker.agent_type != AgentType.WORKER:
                raise ValueError(f"L'agente con id={worker.id} non è di tipo WORKER")

    # Salvataggio nel db
    print(f"Servizio: Creo il team '{team_data.name}'...")
    db_team = team_db.create_team(db=db, team_schema=team_data, workers=workers)

    return db_team


def get_all_teams(db: Session) -> list[TeamModel]:
    return team_db.get_all_teams(db=db)


def get_team(db: Session, team_id: int) -> TeamModel:
    db_team = team_db.get_team_by_id(db=db, team_id=team_id)
    if not db_team:
        raise ValueError(f"Team con id='{team_id}' non trovato")
    return db_team


def update_team(db: Session, team_id: int, team_data: TeamCreate) -> TeamModel:
    """
    Logica di business per aggiornare un team.
     """

    # Controllo id team esistente
    db_team = team_db.get_team_by_id(db=db, team_id=team_id)
    if not db_team:
        raise ValueError(f"Team con id='{team_id}' non trovato")

    # Verifico che il nome non sia già usato da un altro team
    if team_data.name != db_team.name:
        existing_team = team_db.get_other_team_with_name(db, name=team_data.name, team_id=team_id)
        if existing_team:
            raise ValueError(f"Un team con nome '{team_data.name}' esiste già")

    # Controllo: agent supervisor esiste
    supervisor = agent_db.get_agent_by_id(db, team_data.supervisor_id)
    if not supervisor:
        raise ValueError(f"Supervisor con id='{team_data.supervisor_id}' non trovato")
    if supervisor.agent_type != AgentType.SUPERVISOR:
        raise ValueError(f"Agente con id='{team_data.supervisor_id}' non è di tipo supervisor")

    # Controllo che i workers esistano
    workers = []
    if team_data.worker_ids:
        workers = agent_db.get_agents_by_ids(db, team_data.worker_ids)

        # Verifico tutti gli ID esistano
        if len(workers) != len(team_data.worker_ids):
            found_ids = {w.id for w in workers}
            missing_ids = set(team_data.worker_ids) - found_ids
            raise ValueError(f"Worker con ID {missing_ids} non trovati")

        # Verifica che siano tutti di tipo WORKER
        for worker in workers:
            if worker.agent_type != AgentType.WORKER:
                raise ValueError(f"L'agente con id={worker.id} non è di tipo WORKER")


    print(f"Servizio: Agiorno il team con id='{team_id}'...")
    updated_team = team_db.update_team(db=db, team_id=team_id, team_schema=team_data, workers=workers)
    return updated_team


def delete_team(db: Session, team_id: int) -> None:
    db_team = team_db.get_team_by_id(db=db, team_id=team_id)
    if db_team is None:
        raise ValueError(f"Team con id='{team_id}' non trovato")
    team_db.delete_team(db=db, team_model=db_team)
    return