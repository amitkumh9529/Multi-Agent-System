from sqlalchemy.orm import Session

from app.shared.persistence import prompt_db
from app.shared.schemas.prompt_schemas import PromptCreate
from app.shared.persistence.models import PromptModel



def create_prompt(db: Session, prompt_data: PromptCreate) -> PromptModel:
    """
    Logica di business per creare un prompt.
    """
    if prompt_db.get_prompt_by_name(db, prompt_data.name):
        raise ValueError(f"Prompt name {prompt_data.name} already exists")

    print(f"Servizio: Creo il prompt '{prompt_data.name}'...")

    db_prompt = prompt_db.create_prompt(db=db, prompt_schema=prompt_data)

    return db_prompt


def get_all_prompts(db: Session) -> list[PromptModel]:
    """
    Logica di business per ottenere la lista di tutti i prompt nel sistema.
    """

    prompts = prompt_db.get_all_prompts(db=db)

    return prompts


def get_prompt(db: Session, prompt_id: int) -> PromptModel:
    db_prompt = prompt_db.get_prompt_by_id(db, prompt_id)
    if not db_prompt:
        raise ValueError(f"Prompt con id='{prompt_id}' non trovato")
    return db_prompt


def update_prompt(db: Session, prompt_id: int, prompt_data: PromptCreate) -> PromptModel:
    """
    Logica di business per aggiornare un prompt.
    """

    # Controllo id prompt esistente
    db_prompt = prompt_db.get_prompt_by_id(db, prompt_id)
    if not db_prompt:
        raise ValueError(f"Prompt con id='{prompt_id}' non trovato")

    # Verifico che il nome non sia già usato da un altro prompt
    if prompt_data.name != db_prompt.name:
        existing_prompt = prompt_db.get_other_prompt_with_name(db, prompt_data.name, prompt_id)
        if existing_prompt:
            raise ValueError(f"Un prompt con nome '{prompt_data.name}' esiste già")

    print(f"Servizio: Agiorno il prompt con id='{prompt_id}' e nome='{prompt_data.name}'...")
    updated_prompt = prompt_db.update_prompt(db=db, prompt_id=prompt_id, prompt_schema=prompt_data)
    return updated_prompt


def delete_prompt(db: Session, prompt_id: int) -> None:
    """
    Logica di business per gestire l'eliminazione di un prompt
    """
    # controllo che il prompt esista
    db_prompt = prompt_db.get_prompt_by_id(db, prompt_id)
    if not db_prompt:
        raise ValueError(f"Prompt con id='{prompt_id}' non trovato")

    # controllo che non sia usato da nessun agente
    agents_with_prompt = prompt_db.is_prompt_used_by_agents(db=db, prompt_id=prompt_id)
    if agents_with_prompt:
        raise ValueError(f"Impossibile eliminare il prompt id={prompt_id}: è assegnato ad un agente")
    prompt_db.delete_prompt(db=db, db_prompt=db_prompt)
    return