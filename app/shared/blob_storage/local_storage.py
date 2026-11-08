import os
import shutil
import uuid
from pathlib import Path
from fastapi import UploadFile
from .base import BaseStorageProvider


class LocalStorageProvider(BaseStorageProvider):
    def __init__(self):
        # Legge il path base dal .env o usa un default
        self.base_path = Path(os.getenv("LOCAL_STORAGE_PATH", "./uploaded_data"))
        self.base_path.mkdir(parents=True, exist_ok=True)  # Crea la root se non esiste

    def _get_kb_path(self, kb_id: uuid.UUID) -> Path:
        return self.base_path / str(kb_id)      # operatore / per i path permette di fare join dei path in modo intelligente per il sistema operativo

    def create_kb_folder(self, kb_id: uuid.UUID):
        kb_path = self._get_kb_path(kb_id)
        kb_path.mkdir(parents=True, exist_ok=True)
        print(f"Creata cartella locale: {kb_path}")

    def delete_kb_folder(self, kb_id: uuid.UUID):
        kb_path = self._get_kb_path(kb_id)
        if kb_path.exists():
            shutil.rmtree(kb_path)  # Rimuove cartella e tutto il contenuto
            print(f"Eliminata cartella locale: {kb_path}")

    def save_file(self, kb_id: uuid.UUID, file: UploadFile) -> str:
        kb_path = self._get_kb_path(kb_id)

        # Assicuriamoci che la cartella esista (safety check)
        if not kb_path.exists():
            self.create_kb_folder(kb_id)

        # Costruiamo il path completo del file
        # Nota: file.filename dovrebbe essere già sanitizzato in produzione
        file_path = kb_path / file.filename

        # Scriviamo il file su disco
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        print(f"💾 File salvato in: {file_path}")
        return str(file_path)  # Ritorniamo il path stringa per il DB

    def delete_file(self, file_path: str):
        path = Path(file_path)
        if path.exists():
            path.unlink()