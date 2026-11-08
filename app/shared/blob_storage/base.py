from abc import ABC, abstractmethod
from fastapi import UploadFile
import uuid

class BaseStorageProvider(ABC):
    """
    Interfaccia astratta per lo blob_storage.
    Tutte le implementazioni (Locale, S3, Azure Blob) devono seguire questo schema.
    """

    @abstractmethod
    def create_kb_folder(self, kb_id: uuid.UUID):
        """Crea il contenitore (cartella o bucket prefix)"""
        pass

    @abstractmethod
    def delete_kb_folder(self, kb_id: uuid.UUID):
        """Elimina il contenitore e tutto il contenuto"""
        pass

    @abstractmethod
    def save_file(self, kb_id: uuid.UUID, file: UploadFile) -> str:
        """
        Salva il file e ritorna il path (o URL) dove è stato salvato.
        """
        pass

    @abstractmethod
    def delete_file(self, file_path: str):
        """Elimina un singolo file"""
        pass