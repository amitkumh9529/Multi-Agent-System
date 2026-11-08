# Configurazione per lettura chiavi da file .env o variabili d'ambiente
import os
from typing import Dict

class CredentialManager:
    """
    Gestisce il recupero sicuro delle credenziali per i vari provider.
    Supporta provider Cloud Free (Groq, Gemini), Local (Ollama, HuggingFace), e Legacy (AWS, Azure).
    """

    def get_groq_credentials(self) -> Dict[str, str]:
        """Recupera credenziali per Groq Cloud (Free Tier)"""
        return {
            "api_key": os.getenv("GROQ_API_KEY")
        }

    def get_gemini_credentials(self) -> Dict[str, str]:
        """Recupera credenziali per Google Gemini (Free Tier)"""
        return {
            "api_key": os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        }

    def get_ollama_credentials(self) -> Dict[str, str]:
        return {
            "ollama_base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        }

    def get_tavily_api_key(self) -> str:
        """Recupera API key per Tavily Search"""
        return os.getenv("TAVILY_API_KEY")

    def get_azure_credentials(self) -> Dict[str, str]:
        """Recupera credenziali per Azure OpenAI"""
        return {
            "api_key": os.getenv("AZURE_OPENAI_API_KEY"),
            "endpoint": os.getenv("AZURE_OPENAI_ENDPOINT"),
            "api_version": os.getenv("AZURE_OPENAI_API_VERSION", "2023-05-15"),
            "embedding_deployment": os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
        }

    def get_aws_credentials(self) -> Dict[str, str]:
        """Recupera credenziali per AWS Bedrock"""
        return {
            "aws_access_key_id": os.getenv("AWS_ACCESS_KEY_ID"),
            "aws_secret_access_key": os.getenv("AWS_SECRET_ACCESS_KEY"),
            "region_name": os.getenv("AWS_REGION", "us-east-1"),
            "embedding_model_id": os.getenv("AWS_EMBEDDING_MODEL_ID")
        }

    def get_huggingface_credentials(self) -> Dict[str, str]:
        return {}

# Istanza singleton
credential_manager = CredentialManager()
