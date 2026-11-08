import os
from sqlalchemy import create_engine, Engine
from langchain_postgres import PGVector
from app.shared.factories.embedding_factory import EmbeddingFactory


class VectorStoreFactory:
    """
    Factory Singleton per la gestione efficiente delle connessioni PGVector.
    Gestisce un unico SQLAlchemy Engine condiviso per evitare connection leaks.
    """

    _engine: Engine = None

    @staticmethod
    def _get_connection_string() -> str:
        """Normalizza la stringa di connessione per il driver psycopg (v3)."""
        url = os.getenv("DATABASE_URL", "")
        if not url:
            raise ValueError("DATABASE_URL environment variable is not set.")

        # Assicura il prefisso postgresql+psycopg:// per psycopg v3
        if url.startswith("postgresql://") and not url.startswith("postgresql+psycopg://"):
            url = url.replace("postgresql://", "postgresql+psycopg://", 1)
        elif url.startswith("postgres://") and not url.startswith("postgres+psycopg://"):
            url = url.replace("postgres://", "postgresql+psycopg://", 1)

        return url

    @classmethod
    def get_engine(cls) -> Engine:
        """
        Ritorna l'Engine condiviso.
        Se non esiste ancora, lo crea (Lazy Initialization).
        """
        if cls._engine is None:
            print("🔌 VectorStoreFactory: Inizializzazione Database Engine Pool...")
            cls._engine = create_engine(
                cls._get_connection_string(),
                pool_size=10,
                max_overflow=20,
                pool_timeout=30,
                pool_pre_ping=True,
            )
        return cls._engine


    @classmethod
    def get_vector_store(cls, kb_id: str) -> PGVector:
        """
        Restituisce un'istanza di PGVector configurata per una specifica KB.

        :param kb_id: L'ID della Knowledge Base (usato come nome della collection)
        :return: Istanza pronta all'uso di PGVector
        """
        # 1. Otteniamo l'Engine condiviso
        engine = cls.get_engine()

        # 2. Otteniamo il modello di embedding (prioritizza Gemini se presente, altrimenti HuggingFace locale)
        provider = os.getenv("EMBEDDING_PROVIDER")
        if not provider:
            provider = "gemini" if (os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")) else "huggingface"

        embeddings = EmbeddingFactory.get_embedding_model(provider=provider)

        # 3. Restituiamo l'oggetto PGVector collegato al pool esistente
        return PGVector(
            connection=engine,
            embeddings=embeddings,
            collection_name=str(kb_id),
            use_jsonb=True,
        )


    @classmethod
    def dispose(cls):
        """
        Chiude tutte le connessioni del pool.
        Utile per il Graceful Shutdown dell'applicazione.
        """
        if cls._engine:
            print("🔌 VectorStoreFactory: Chiusura Database Engine...")
            cls._engine.dispose()
            cls._engine = None
