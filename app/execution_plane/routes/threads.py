# API: /api/v1/chat/{team_id} (POST per avviare/continuare la chat)
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.execution_plane.services.thread_service import ThreadService
from app.shared.persistence import message_db
from app.shared.persistence.db_client import get_db
from app.shared.schemas.message_schemas import ChatMessageRead
from app.shared.schemas.thread_schemas import ChatThreadRead

router = APIRouter()

# Schema di input semplice mandato dal frontend per chattare
class ChatRequest(BaseModel):
    message: str = Field(..., description="Il messaggio dell'utente")
    team_id: int = Field(..., description="L'ID del team che deve rispondere")




@router.post("/{thread_id}/chat")
async def chat_with_thread(
        thread_id: str,
        payload: ChatRequest,
        db: Session = Depends(get_db)
):
    """
        Endpoint Chat Stream.
        Delega tutta la logica al ThreadService.
    """

    stream_generator = ThreadService.chat_stream_workflow(
        db=db,
        team_id=payload.team_id,
        thread_id=thread_id,
        user_message=payload.message
    )

    return StreamingResponse(stream_generator, media_type="text/event-stream")



@router.get("", response_model=list[ChatThreadRead])
def read_all_threads(db: Session = Depends(get_db)):
    """
    Ottiene la lista di tutte le chat avviate dall'utente
    """

    try:
        return ThreadService.get_threads_list(db=db)

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/{thread_id}/messages", response_model=list[ChatMessageRead])
def get_messages(
        thread_id: str,
        db: Session = Depends(get_db),
):
    """
    Ottiene lo storico dei messaggi per una specifica chat.
    Da chiamare al caricamento della pagina.
    """
    try:
        messages = message_db.get_thread_history(
            db=db,
            thread_id=thread_id
        )
        return messages

    except ValueError:
        raise HTTPException(status_code=400, detail="Thread ID non valido")


@router.delete("/{thread_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_thread(thread_id: str,
                 db: Session = Depends(get_db)):
    """
    Cancella il thread con id specificato dal sistema
    """
    try:
        ThreadService.delete_thread(db=db, thread_id=thread_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))