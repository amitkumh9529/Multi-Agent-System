import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from dotenv import load_dotenv

# Carica .env se presente
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()

raw_url = os.getenv("DATABASE_URL", "postgresql+psycopg://myuser:mypassword@localhost:54320/mydatabase")

# Normalizza per psycopg 3
if raw_url.startswith("postgresql://") and not raw_url.startswith("postgresql+psycopg://"):
    DATABASE_URL = raw_url.replace("postgresql://", "postgresql+psycopg://", 1)
elif raw_url.startswith("postgres://") and not raw_url.startswith("postgres+psycopg://"):
    DATABASE_URL = raw_url.replace("postgres://", "postgresql+psycopg://", 1)
else:
    DATABASE_URL = raw_url

engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=10,
    pool_timeout=30,
    pool_pre_ping=True,
    connect_args={
        'connect_timeout': 5
    }
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

def create_db_and_tables():
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"⚠️ Errore creazione tabelle database: {e}")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
