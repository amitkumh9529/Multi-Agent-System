from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.shared.persistence.db_client import get_db
from app.shared.persistence.models import LLMModel
from app.shared.schemas.llm_model_schemas import LLMModelRead

router = APIRouter()

@router.get("",response_model=list[LLMModelRead])
def read_all_llm_models(db: Session = Depends(get_db)):
    """
    Restituisce la lista degli LLM Models
    """
    try:
        llm_models = db.query(LLMModel).all()
        return llm_models
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/{llm_model_id}",response_model=LLMModelRead)
def read_llm_model(
        llm_model_id: int,
        db: Session = Depends(get_db)
):
    """
    Restituisce il prompt specificato
    """
    try:
        llm_model = db.query(LLMModel).filter(LLMModel.id == llm_model_id).first()
        return llm_model
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

