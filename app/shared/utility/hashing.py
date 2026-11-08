import hashlib

def calculate_file_hash(file_file) -> str:
    """
    Calcola l'hash SHA-256 del contenuto di un file (UploadFile).
    """
    sha256_hash = hashlib.sha256()

    # Assicuriamoci di essere all'inizio del file
    file_file.seek(0)

    # Leggiamo a blocchi di 4KB per efficienza
    for byte_block in iter(lambda: file_file.read(4096), b""):
        sha256_hash.update(byte_block)

    # Resettiamo il cursore all'inizio per permettere il salvataggio successivo!
    file_file.seek(0)

    return sha256_hash.hexdigest()