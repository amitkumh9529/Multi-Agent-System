from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.control_plane.routes import agents, prompts, teams, llm_models, knowledge_bases, tools
from app.execution_plane.routes import threads
from app.shared.persistence.db_client import create_db_and_tables, SessionLocal
from app.shared.persistence.seed import seed_llm_models, seed_prompts, seed_agents, seed_tools


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Context manager per gestire startup e shutdown dell'applicazione.
    Il codice prima di yield viene eseguito all'avvio.
    Il codice dopo yield viene eseguito allo shutdown.
    """
    # 1. Startup: crea le tabelle del database
    print("🔧 Creazione tabelle del database...")
    create_db_and_tables()

    # 2. Esegui il Seeding (popola i dati)
    print("🌱 Verifica e Seeding dei dati...")
    db = SessionLocal()
    try:
        seed_llm_models(db)
        seed_prompts(db)
        seed_agents(db)
        seed_tools(db)
    finally:
        db.close()
    print("✅ Database pronto.")

    yield
    print("👋 Shutdown...")


def create_app() -> FastAPI:
    """
        Factory function che costruisce e restituisce l'istanza FastAPI.
        """
    application = FastAPI(
        title="Control Plane Multi-Agent Orchestrator",
        description="API per la gestione degli agenti con supporto PostgreSQL",
        version="1.0.0",
        lifespan=lifespan
    )

    # Includi i router
    application.include_router(agents.router)
    application.include_router(prompts.router)
    application.include_router(teams.router)
    application.include_router(llm_models.router)
    application.include_router(threads.router)
    application.include_router(knowledge_bases.router)
    application.include_router(tools.router)

    # Endpoint di health check
    @application.get("/", tags=["Health"])
    def read_root():
        """Endpoint per verificare che l'API sia attiva"""
        return {
            "status": "online",
            "message": "Agent Management API is running",
            "docs": "/docs",
            "redoc": "/redoc"
        }


    @application.get("/health", tags=["Health"])
    def health_check():
        """Endpoint di health check per monitoraggio"""
        return {
            "status": "healthy",
            "database": "connected"
        }
    return application

#app = create_app()

