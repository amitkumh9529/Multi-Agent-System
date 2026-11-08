import os
from .local_storage import LocalStorageProvider

if os.getenv("STORAGE_TYPE") == "local":
    storage_provider = LocalStorageProvider()
else:
    storage_provider = LocalStorageProvider()   # per adesso gestisco solo caso in locale