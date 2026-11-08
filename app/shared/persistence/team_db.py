# Funzioni di interazione con db per Team:
from typing import Optional

from sqlalchemy.orm import Session

from app.shared.persistence.models import TeamModel, AgentModel
from app.shared.schemas.team_schemas import TeamCreate


def create_team(db: Session, team_schema: TeamCreate, workers: list[AgentModel]) -> TeamModel:
    """
    Salva un nuovo team nel DB.
    """
    db_team = TeamModel(**team_schema.model_dump(exclude={'worker_ids'}))   # escludo i valori di 'worker_ids' dallo schema pydantic TeamCreate. Questo perchè non mi servono nella table Team nel db, ma andranno in 'team_workers'

    if workers is not None:  # Controllo se è stato passato
        db_team.workers = workers


    db.add(db_team)
    db.commit()
    db.refresh(db_team)

    return db_team

def get_team_by_name(db: Session, name: str) -> Optional[TeamModel]:
    """
    Query sqlAlchemy per ottenere il team nel DB con nome specificato
    """
    return db.query(TeamModel).filter(TeamModel.name == name).first()

def get_team_by_id(db: Session, team_id: int) -> Optional[TeamModel]:
    return db.query(TeamModel).filter(TeamModel.id == team_id).first()


def get_all_teams(db: Session) -> list[TeamModel]:
    return db.query(TeamModel).all()


def get_other_team_with_name(db: Session, name: str, team_id: int):
    """
    Funzione che verifica se sia presente un ALTRO team (ossia altro id) con stesso nome
    """
    existing_team = db.query(TeamModel).filter(
        TeamModel.name == name,
        TeamModel.id != team_id # Esclude il team corrente
    ).first()
    return existing_team


def update_team(db: Session, team_id: int, team_schema: TeamCreate, workers: list[AgentModel]) -> TeamModel:
    """
    Funzione che aggiorna un team nel DB.
    """
    # 1. Recupera l'agente esistente
    db_team = get_team_by_id(db=db, team_id=team_id)

    # 2. Aggiorna i campi usando model_dump()
    for key, value in team_schema.model_dump(exclude_unset=True, exclude={'worker_ids'}).items():   # escludo i valori di 'worker_ids' dallo schema pydantic TeamCreate
        setattr(db_team, key, value)

    if workers is not None:  # Controlla se è stato passato
        db_team.workers = workers

    # 3. Commit e refresh
    db.commit()
    db.refresh(db_team)

    return db_team


def delete_team(db: Session, team_model: TeamModel):
    """
    Elimina un team dal DB.
    """
    db.delete(team_model)
    db.commit()