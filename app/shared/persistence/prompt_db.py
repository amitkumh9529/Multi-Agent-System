from sqlalchemy.orm import Session

from typing import Optional
from app.shared.persistence.models import PromptModel
from app.shared.schemas.prompt_schemas import PromptCreate


def create_prompt(db: Session, prompt_schema: PromptCreate) -> PromptModel:
    """
    Salva un nuovo prompt nel DB.
    """

    db_prompt = PromptModel(**prompt_schema.model_dump())

    db.add(db_prompt)
    db.commit()
    db.refresh(db_prompt)

    return db_prompt


def get_prompt_by_id(db: Session, prompt_id: int) -> Optional[PromptModel]:
    return db.query(PromptModel).filter(PromptModel.id == prompt_id).first()

def get_prompt_by_name(db: Session, prompt_name: str) -> Optional[PromptModel]:
    return db.query(PromptModel).filter(PromptModel.name == prompt_name).first()


def get_all_prompts(db: Session) -> list[PromptModel]:
    return db.query(PromptModel).all()


def get_other_prompt_with_name(db: Session, prompt_name: str, prompt_id: int) -> Optional[PromptModel]:
    """
        Funzione che verifica se sia presente un ALTRO (altro id) prompt con stesso nome
    """

    already_existing_name = db.query(PromptModel).filter(
        PromptModel.id != prompt_id,
        PromptModel.name == prompt_name
    ).first()
    return already_existing_name


def update_prompt(db: Session, prompt_id: int, prompt_schema: PromptCreate) -> Optional[PromptModel]:
    """
    Aggiorna nel DB il prompt con id specificato con i nuovi dati
    """
    db_prompt = db.query(PromptModel).filter(PromptModel.id == prompt_id).first()

    # 2. Aggiorna i campi usando model_dump()
    for key, value in prompt_schema.model_dump(exclude_unset=True).items():
        setattr(db_prompt, key, value)

    # 3. Commit e refresh
    db.commit()
    db.refresh(db_prompt)

    return db_prompt


def delete_prompt(db: Session, db_prompt: PromptModel) -> None:
    db.delete(db_prompt)
    db.commit()
    return

def is_prompt_used_by_agents(db: Session, prompt_id: int) -> bool:
    prompt = get_prompt_by_id(db=db, prompt_id=prompt_id)
    return True if len(prompt.agents) > 0 else False