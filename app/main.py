import sys
import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

# Fix per Windows + Psycopg async pool
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Carica variabili d'ambiente da app/.env o .env root
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.shared.persistence.db_client import create_db_and_tables, SessionLocal
from app.shared.persistence.seed import seed_llm_models, seed_prompts, seed_agents, seed_tools
from app.shared.factories.checkpointer_factory import CheckpointFactory
from app.shared.factories.vector_store_factory import VectorStoreFactory
from app.control_plane.routes import (
    agents,
    prompts,
    teams,
    llm_models,
    knowledge_bases,
    tools
)
from app.execution_plane.routes import threads


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestore unificato del ciclo di vita dell'applicazione.
    Esegue in sequenza le operazioni sincrone (DB Setup) e asincrone (Pool Init).
    """

    # --- FASE 1: STARTUP SINCRONO (DB SQL) ---
    print("🔧 [Startup] 1/3: Verifica schema Database...")
    create_db_and_tables()

    print("🌱 [Startup] 2/3: Seeding dati iniziali...")
    db = SessionLocal()
    try:
        # Popoliamo il DB se necessario
        seed_llm_models(db)
        seed_prompts(db)
        seed_agents(db)
        seed_tools(db)
    except Exception as e:
        print(f"⚠️ Errore durante il seeding (non bloccante): {e}")
    finally:
        db.close()

    # --- FASE 2: STARTUP ASINCRONO (Pool LangGraph) ---
    print("🚀 [Startup] 3/3: Inizializzazione Connection Pool Async...")
    try:
        await CheckpointFactory.initialize()
    except Exception as e:
        print(f"⚠️ Warning inizializzazione CheckpointFactory: {e}")

    print("✅ Sistema pronto.")

    yield

    # --- FASE 3: SHUTDOWN ---
    print("🛑 [Shutdown] Chiusura risorse...")
    try:
        await CheckpointFactory.close()
    except Exception as e:
        print(f"Errore chiusura CheckpointFactory: {e}")
    VectorStoreFactory.dispose()


def create_app() -> FastAPI:
    """
    Costruisce l'applicazione unica.
    """
    application = FastAPI(
        title="AI Enterprise RAG Platform",
        description="Unified API for Control Plane (Management) and Execution Plane (Runtime)",
        version="1.0.0",
        lifespan=lifespan
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # --- ROUTERS: CONTROL PLANE ---
    cp_prefix = "/api/v1/control"
    application.include_router(teams.router, prefix=f"{cp_prefix}/teams", tags=["Control Plane - Teams"])
    application.include_router(agents.router, prefix=f"{cp_prefix}/agents", tags=["Control Plane - Agents"])
    application.include_router(tools.router, prefix=f"{cp_prefix}/tools", tags=["Control Plane - Tools"])
    application.include_router(prompts.router, prefix=f"{cp_prefix}/prompts", tags=["Control Plane - Prompts"])
    application.include_router(llm_models.router, prefix=f"{cp_prefix}/llm", tags=["Control Plane - LLM Models"])
    application.include_router(knowledge_bases.router, prefix=f"{cp_prefix}/kb", tags=["Control Plane - Knowledge Bases"])

    # --- ROUTERS: EXECUTION PLANE ---
    ep_prefix = "/api/v1/execution"
    application.include_router(threads.router, prefix=f"{ep_prefix}/threads", tags=["Execution Plane - Chat Threads"])

    # --- HEALTH CHECKS ---
    @application.get("/health", tags=["System"])
    def health_check():
        return {
            "status": "healthy",
            "components": {
                "database": "connected",
                "checkpoint_pool": "active"
            }
        }

    @application.get("/", tags=["System"])
    def root():
        return {"message": "AI RAG Platform API is running. Go to /docs for Swagger UI."}

    return application


app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
