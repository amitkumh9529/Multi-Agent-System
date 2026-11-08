import os
from langchain_core.embeddings import Embeddings
from app.shared.security.credential_manager import credential_manager

class EmbeddingFactory:
    """
    Factory centralizzata per gli Embeddings.
    Supporta:
      - Google Gemini (Cloud Free: models/text-embedding-004) - Nessun uso di GPU o CPU locale!
      - HuggingFace (Local CPU/CUDA: sentence-transformers/all-MiniLM-L6-v2)
      - Azure & AWS (Enterprise)
    """

    @staticmethod
    def get_embedding_model(provider: str = "google") -> Embeddings:
        provider_clean = (provider or "").lower().strip()

        # --- CASO 1: GOOGLE GEMINI EMBEDDINGS (100% Free Cloud, zero GPU/CPU) ---
        if provider_clean in ["google", "gemini"]:
            from langchain_google_genai import GoogleGenerativeAIEmbeddings
            creds = credential_manager.get_gemini_credentials()
            if not creds["api_key"]:
                raise ValueError("GEMINI_API_KEY mancante per Google Embeddings.")

            return GoogleGenerativeAIEmbeddings(
                model="models/text-embedding-004",
                google_api_key=creds["api_key"]
            )

        # --- CASO 2: HUGGINGFACE LOCAL (Leggero su CPU o GPU se presente) ---
        elif provider_clean == "huggingface":
            from langchain_huggingface import HuggingFaceEmbeddings
            import torch
            model_name = "sentence-transformers/all-MiniLM-L6-v2"
            device = "cuda" if torch.cuda.is_available() else "cpu"

            return HuggingFaceEmbeddings(
                model_name=model_name,
                model_kwargs={'device': device}
            )

        # --- CASO 3: AZURE OPENAI ---
        elif provider_clean == "azure":
            from langchain_openai import AzureOpenAIEmbeddings
            creds = credential_manager.get_azure_credentials()
            if not creds["api_key"]:
                raise ValueError("Azure API Key mancante")

            return AzureOpenAIEmbeddings(
                azure_deployment=creds["embedding_deployment"],
                api_version=creds["api_version"],
                azure_endpoint=creds["endpoint"],
                api_key=creds["api_key"]
            )

        # --- CASO 4: AWS BEDROCK ---
        elif provider_clean == "aws":
            from langchain_aws import BedrockEmbeddings
            creds = credential_manager.get_aws_credentials()
            return BedrockEmbeddings(
                model_id=creds["embedding_model_id"],
                client=None,
                region_name=creds["region_name"],
                aws_access_key_id=creds["aws_access_key_id"],
                aws_secret_access_key=creds["aws_secret_access_key"]
            )

        else:
            raise ValueError(f"Provider '{provider}' non supportato per Embeddings.")
