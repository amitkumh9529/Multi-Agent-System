# Usiamo PostgreSQL per la memoria (checkpointing). Il checkpointing permette di
# avere persistenza dei dati e riprendere conversazioni interrotte.
# Tramite questa factory abbiamo un gestore centralizzato per il pool di connessioni.
# Il pool permette di non aprire una nuova connessione al DB ad ogni messaggio.

import sys
import os
from pathlib import Path
from contextlib import asynccontextmanager
import asyncio

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from psycopg_pool import AsyncConnectionPool
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from dotenv import load_dotenv

# Carica app/.env o .env
env_file = Path(__file__).resolve().parent.parent.parent / ".env"
if env_file.exists():
    load_dotenv(dotenv_path=env_file)
else:
    load_dotenv()


class CheckpointFactory:
    """
    Singleton Factory per gestire il pool di connessioni e il checkpointer di LangGraph.
    """
    _pool: AsyncConnectionPool = None

    @staticmethod
    def _get_database_url():
        url = os.getenv("POSTGRES_URI") or os.getenv("DATABASE_URL")
        if not url:
            raise ValueError("POSTGRES_URI o DATABASE_URL non impostato")
        # AsyncConnectionPool usa psycopg direttamente, quindi rimuove eventuali dialetti SQLAlchemy (+psycopg)
        if "+psycopg" in url:
            url = url.replace("+psycopg", "")
        return url

    @classmethod
    async def initialize(cls):
        """Inizializza il pool globale. Da chiamare allo startup dell'app."""
        if cls._pool is None:
            print("🔌 CheckpointFactory: Apertura Connection Pool...")

            # 1. Creazione Pool (closed)
            cls._pool = AsyncConnectionPool(
                conninfo=cls._get_database_url(),
                max_size=20,
                open=False,
                kwargs={"autocommit": True}
            )

            # 2. Apertura asincrona esplicita
            await cls._pool.open()
            await cls._pool.wait()
            print("✅ CheckpointFactory: Pool Aperto e pronto.")

    @classmethod
    async def close(cls):
        """Chiude il pool. Da chiamare allo shutdown dell'app."""
        if cls._pool:
            print("🔌 CheckpointFactory: Chiusura Pool...")
            await cls._pool.close()
            cls._pool = None

    @classmethod
    @asynccontextmanager
    async def get_checkpointer(cls):
        """
        Context manager che restituisce un AsyncPostgresSaver usando il pool condiviso.
        """
        if cls._pool is None:
            await cls.initialize()

        checkpointer = AsyncPostgresSaver(cls._pool)

        # Assicura che le tabelle esistano (idempotente)
        await checkpointer.setup()

        try:
            yield checkpointer
        finally:
            pass
