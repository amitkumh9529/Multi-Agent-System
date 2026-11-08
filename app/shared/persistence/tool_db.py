
from sqlalchemy.orm import Session
from app.shared.persistence.models import ToolModel


def filter_tools(db: Session, tool_list: list) -> list:
    """
    Filtra la lista di tool in ingresso restituendo la lista di tool realmente esistenti nel db
    """
    return db.query(ToolModel).filter(ToolModel.id.in_(tool_list)).all()


def get_tools(db: Session) -> list:
    """
    Query per ottenere la lista di tool dal db
    """
    return db.query(ToolModel).all()