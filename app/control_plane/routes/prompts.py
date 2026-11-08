from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.shared.schemas.prompt_schemas import PromptCreate, PromptRead
from app.control_plane.services import prompt_service
from app.shared.persistence.db_client import get_db

router = APIRouter()

@router.post("", response_model=PromptRead, status_code=status.HTTP_201_CREATED)
def create_prompt(
        prompt_data: PromptCreate,
        db: Session = Depends(get_db),
):
    """
    Crea un nuovo prompt nel sistema.
    """
    try:
        created_prompt = prompt_service.create_prompt(db=db, prompt_data=prompt_data)
        return created_prompt

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=list[PromptRead])
def read_all_prompts(db: Session = Depends(get_db)):
    """
    Restituisce la lista di prompt creati.
    """

    try:
        prompts = prompt_service.get_all_prompts(db=db)
        return prompts

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{prompt_id}", response_model=PromptRead)
def read_prompt(prompt_id: int,
               db: Session = Depends(get_db)
               ):
    """
        Restituisce il prompt con id specificato
    """
    try:
        return prompt_service.get_prompt(db=db, prompt_id=prompt_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{prompt_id}", response_model=PromptRead)
def update_prompt(prompt_data: PromptCreate,
                 prompt_id: int,
                 db: Session = Depends(get_db)
                 ):
    try:
        updated_prompt = prompt_service.update_prompt(db=db, prompt_id=prompt_id, prompt_data=prompt_data)

        return updated_prompt

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{prompt_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_prompt(prompt_id: int,
                 db: Session = Depends(get_db)):
    try:
        prompt_service.delete_prompt(db=db, prompt_id=prompt_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

