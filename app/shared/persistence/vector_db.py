from typing import List
from langchain_core.documents import Document
from sqlalchemy import text
from app.shared.factories.vector_store_factory import VectorStoreFactory


def add_documents_to_vector_store(kb_id: str, documents: List[Document]):
    """Salva i documenti (chunks) nel DB vettoriale."""
    # Chiede l'istanza alla Factory (che gestisce il pool sotto il cofano)
    vector_store = VectorStoreFactory.get_vector_store(kb_id)
    vector_store.add_documents(documents)


def delete_collection(kb_id: str):
    """Elimina una intera collezione."""
    vector_store = VectorStoreFactory.get_vector_store(kb_id)
    vector_store.delete_collection()



def delete_documents_from_collection(kb_id: str, filename: str):
    """
    Rimuove i vettori associati a un file specifico usando SQL diretto.
    È molto più affidabile del metodo .delete() di LangChain.
    """
    engine = VectorStoreFactory.get_engine()

    # 1. Definiamo la query SQL paramtrica.

    sql = text("""
               DELETE
               FROM langchain_pg_embedding
               WHERE collection_id = (SELECT uuid
                                      FROM langchain_pg_collection
                                      WHERE name = :kb_id)
                 AND cmetadata ->> 'filename' = :filename
               """)

    # 2. Eseguiamo la transazione
    try:
        with engine.connect() as connection:
            result = connection.execute(sql, {"kb_id": str(kb_id), "filename": str(filename)})
            connection.commit()  # Fondamentale per rendere effettiva la modifica

            # result.rowcount ci dice quanti chunk sono stati cancellati
            if result.rowcount > 0:
                print(f"Eliminati {result.rowcount} chunk vettoriali per filename='{filename}' nella KB='{kb_id}'")
            else:
                print(f"Nessun vettore trovato per filename='{filename}' (potrebbe essere già vuoto).")

    except Exception as e:
        print(f"❌ Errore SQL critico durante cancellazione vettori: {e}")
        raise e