import json
from typing import Optional
from app.shared.persistence.models import ChatThreadModel
import uuid
import re

import asyncio
from typing import AsyncGenerator
from sqlalchemy.orm import Session

# I tuoi import
from app.shared.factories.checkpointer_factory import CheckpointFactory
from app.shared.persistence import team_db, thread_db, message_db
from app.shared.persistence.models.message_model import MessageType
from app.shared.schemas.thread_schemas import ChatThreadCreate

from app.execution_plane.runtime.graph_factory import GraphFactory


def clean_langchain_id(dirty_id: str) -> uuid.UUID:
    """Helper per pulire ID sporchi di LangChain"""
    if not dirty_id: return uuid.uuid4()
    match = re.search(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', str(dirty_id))
    return uuid.UUID(match.group(0)) if match else uuid.uuid4()



class ThreadService:

    @staticmethod
    async def chat_stream_workflow(
            db: Session,
            team_id: int,
            thread_id: str,
            user_message: str
    ) -> AsyncGenerator[str, None]:
        """
        Gestisce tutto il flusso: Preparazione -> Streaming -> Salvataggio
        """

        # 1. PREPARAZIONE
        try:
            # Funzione sincrona: prima di continuare serve sapere se i dati scelti siano validi
            await asyncio.to_thread(    # Uso to_thread così l'esecuzione sincrona non blocca l'intero sistema, ma viene gestita in thread a parte: è sincrona solo per chi fa richiesta
                ThreadService._prepare_conversation_sync,
                db, team_id, thread_id, user_message
            )
        except ValueError as e:
            # Convertiamo errori di business in messaggi per lo stream o errori HTTP
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
            return

        # 2. SETUP GRAFO e TRACKER
        from app.shared.utils.token_tracker import TokenUsageTracker
        usage_tracker = TokenUsageTracker()

        async with CheckpointFactory.get_checkpointer() as checkpointer:
            try:
                graph = await asyncio.to_thread(
                    GraphFactory.build_team_graph,
                    db, team_id, checkpointer,
                    callbacks=[usage_tracker]
                )
            except Exception as e:
                yield f"data: Error: {str(e)}\n\n"
                return

            config = {"configurable": {"thread_id": thread_id}}
            inputs = {"messages": [("user", user_message)]}
            final_message = None    # Variabile "buffer" per ricordare l'ultimo messaggio IA valido visto

            # 3. STREAMING  (asincrono)
            try:
                async for event in graph.astream(inputs, config=config, stream_mode="values"):
                    if "messages" in event:
                        last_msg = event["messages"][-1]

                        # Logica di business per filtrare cosa mandare al frontend
                        payload = ThreadService._format_sse_payload(last_msg)
                        if payload:
                            print(f"Payload: {payload}")
                            yield f"data: {json.dumps(payload)}\n\n"
                            await asyncio.sleep(0.01)

                        # Salviamo riferimento per DB
                        if last_msg.type == "ai" and not last_msg.tool_calls:
                            final_message = last_msg

                # 4. STREAMING UTILIZZO TOKEN
                if usage_tracker.total_tokens > 0:
                    usage_payload = {
                        "type": "usage",
                        "total_tokens": usage_tracker.total_tokens,
                        "prompt_tokens": usage_tracker.prompt_tokens,
                        "completion_tokens": usage_tracker.completion_tokens
                    }
                    yield f"data: {json.dumps(usage_payload)}\n\n"

            except asyncio.CancelledError:
                # Opzionale: Loggare che l'utente ha chiuso la connessione
                print(f"--- Utente disconnesso dal thread {thread_id} ---")
                # Rilanciamo l'errore o lo gestiamo, ma il 'finally' partirà comunque.
                raise

            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)})}\n\n"

            # 5. SALVATAGGIO MESSAGGIO FINALE (sincrono)
            finally:
                if final_message:
                    await asyncio.to_thread(ThreadService._save_ai_message_sync, db, thread_id, final_message)


    @staticmethod
    def _format_sse_payload(msg):
        """Helper per pulire la logica di formattazione JSON"""
        payload = {"type": msg.type, "content": msg.content}
        if msg.type == "ai" and msg.tool_calls:
            payload["tool_calls"] = msg.tool_calls
        if msg.type == "tool":
            payload["name"] = msg.name
            payload["tool_call_id"] = msg.tool_call_id
        return payload



    @staticmethod
    def _prepare_conversation_sync(db: Session, team_id: int, thread_id: str, message: str):
        """Verifica team, crea thread e salva messaggio utente."""
        # 1. Check Team
        db_team = team_db.get_team_by_id(db=db, team_id=team_id)
        if not db_team:
            raise ValueError(f"Team {team_id} non trovato.")

        # 2. Upsert Thread
        db_thread = thread_db.get_thread(db=db, thread_id=thread_id)
        if not db_thread:
            thread_db.create_thread(
                db=db,
                thread_data=ChatThreadCreate(thread_id=thread_id, title=f"Chat {thread_id[:8]}")
            )
        else:
            thread_db.update_thread(db=db, old_thread=db_thread)

        # 3. Save User Message
        message_db.add_message(
            db=db,
            thread_id=thread_id,
            content=message,
            msg_type=MessageType.HUMAN
        )


    @staticmethod
    def _save_ai_message_sync(db: Session, thread_id: str, ai_msg):
        """Salva il messaggio finale dell'AI."""
        content = ai_msg.content
        if isinstance(content, list):
            content = "".join(str(item) for item in content)

        lang_id = getattr(ai_msg, 'id', None)
        clean_id = clean_langchain_id(lang_id)

        message_db.add_message(
            db=db,
            id=clean_id,
            thread_id=thread_id,
            content=str(content),
            msg_type=MessageType.AI,
        )

    @staticmethod
    def get_thread(db: Session, thread_id: str) -> Optional[ChatThreadModel]:
        """
        Logica di business per ottenere i dati di un thread
        """
        thread = thread_db.get_thread(db=db, thread_id=thread_id)
        if thread is None:
            raise ValueError(f"Thread con id='{thread_id}' non trovato")
        return thread


    @staticmethod
    def get_threads_list(db: Session) -> list[ChatThreadModel]:
        """
        Logica di business per ottenere la lista di tutte le chat
        """
        threads = thread_db.get_all_threads(db=db)
        return threads


    @staticmethod
    def delete_thread(db: Session, thread_id: str):
        """
        Logica di business per eliminare una chat
        """
        db_thread = thread_db.get_thread(db=db, thread_id=thread_id)
        if db_thread is None:
            raise ValueError(f"Thread con id='{thread_id}' non trovato")
        thread_db.delete_thread(db=db, db_thread=db_thread)
        return None