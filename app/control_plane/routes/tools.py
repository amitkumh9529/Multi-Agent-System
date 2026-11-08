from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.shared.persistence import tool_db
from app.shared.persistence.db_client import get_db
from app.shared.schemas.tool_schemas import ToolRead

router = APIRouter()


@router.get("/tools", response_model=list[ToolRead])
def get_tools(db: Session = Depends(get_db)):
    """
    Restituisce la lista di tool del sistema
    """
    tools = tool_db.get_tools(db)
    return tools