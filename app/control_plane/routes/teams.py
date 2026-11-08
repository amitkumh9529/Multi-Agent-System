from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.shared.schemas.team_schemas import TeamCreate, TeamRead, TeamBase, TeamReadFull
from app.shared.persistence.db_client import get_db
from app.control_plane.services import team_service

router = APIRouter()

@router.post("", response_model=TeamRead, status_code=status.HTTP_201_CREATED)
def create_team(
        team_data: TeamCreate,
        db: Session = Depends(get_db)
):
    """
    Crea un nuovo team nel sistema
    """

    try:
        created_team = team_service.create_team(db=db, team_data=team_data)
        return created_team

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=list[TeamRead])
def read_all_teams(db: Session = Depends(get_db)):
    """
    Restituisce la lista di teams creati
    """
    try:
        return team_service.get_all_teams(db=db)

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{team_id}", response_model=TeamReadFull)
def read_team(team_id: int,
               db: Session = Depends(get_db)
               ):
    """
    Restituisce il team con id specificato
    """
    try:
        return team_service.get_team(db=db, team_id=team_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{team_id}", response_model=TeamRead)
def update_team(team_data: TeamCreate,
                 team_id: int,
                 db: Session = Depends(get_db)
                 ):
    """
    Aggiorna un team nel sistema
    """
    try:
        updated_team = team_service.update_team(db=db, team_id=team_id, team_data=team_data)

        return updated_team

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_team(team_id: int,
                 db: Session = Depends(get_db)):
    """
    Cancella il team con id specificato dal sistema
    """
    try:
        team_service.delete_team(db=db, team_id=team_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
