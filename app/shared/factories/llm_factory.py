from langchain_core.language_models.chat_models import BaseChatModel
from app.shared.security.credential_manager import credential_manager

class LLMFactory:
    """
    Factory centralizzata per istanziare modelli LLM da differenti provider.
    Supporta:
      - Groq (Cloud Free - Llama 3.3 70B, Llama 3.1 8B)
      - Google Gemini (Cloud Free - Gemini 1.5/2.0 Flash)
      - Ollama (Local)
      - Azure OpenAI & AWS Bedrock (Enterprise)
    """

    @staticmethod
    def get_llm_model(
            provider: str,
            model_name: str,
            temperature: float = 0.0,
            max_tokens: int = None,
            callbacks: list = None
    ) -> BaseChatModel:
        """
        Factory che restituisce l'istanza LangChain corretta in base al provider.
        """
        provider_clean = (provider or "").lower().strip()

        # --- CASO 1: GROQ CLOUD (Free Tier - Alta Velocità, No GPU Locale) ---
        if provider_clean == "groq":
            from langchain_groq import ChatGroq
            creds = credential_manager.get_groq_credentials()
            if not creds["api_key"]:
                raise ValueError("GROQ_API_KEY mancante. Ottienine una gratis su https://console.groq.com")

            return ChatGroq(
                model=model_name or "qwen/qwen3.8-27b",
                groq_api_key=creds["api_key"],
                temperature=temperature,
                max_tokens=max_tokens,
                callbacks=callbacks
            )

        # --- CASO 2: GOOGLE GEMINI (Free Tier via Google AI Studio) ---
        elif provider_clean in ["google", "gemini"]:
            from langchain_google_genai import ChatGoogleGenerativeAI
            creds = credential_manager.get_gemini_credentials()
            if not creds["api_key"]:
                raise ValueError("GEMINI_API_KEY mancante. Ottienine una gratis su https://aistudio.google.com")

            return ChatGoogleGenerativeAI(
                model=model_name or "gemini-3.8-flash",
                google_api_key=creds["api_key"],
                temperature=temperature,
                max_output_tokens=max_tokens,
                callbacks=callbacks
            )

        # --- CASO 3: OLLAMA (Local) ---
        elif provider_clean in ["local", "ollama"]:
            from langchain_ollama import ChatOllama
            creds = credential_manager.get_ollama_credentials()
            return ChatOllama(
                model=model_name or "llama3.2:3b",
                temperature=temperature,
                base_url=creds.get("ollama_base_url", "http://localhost:11434"),
                callbacks=callbacks
            )

        # --- CASO 4: AZURE OPENAI ---
        elif provider_clean == "azure":
            from langchain_openai import AzureChatOpenAI
            creds = credential_manager.get_azure_credentials()
            if not creds["api_key"]:
                raise ValueError("Azure API Key mancante")

            return AzureChatOpenAI(
                azure_deployment=model_name,
                api_version=creds["api_version"],
                azure_endpoint=creds["endpoint"],
                api_key=creds["api_key"],
                temperature=temperature,
                max_tokens=max_tokens,
                callbacks=callbacks
            )

        # --- CASO 5: AWS BEDROCK CONVERSE ---
        elif provider_clean == "aws-converse":
            from langchain_aws import ChatBedrockConverse
            creds = credential_manager.get_aws_credentials()
            return ChatBedrockConverse(
                model_id=model_name,
                client=None,
                region_name=creds["region_name"],
                aws_access_key_id=creds["aws_access_key_id"],
                aws_secret_access_key=creds["aws_secret_access_key"],
                temperature=temperature,
                max_tokens=max_tokens,
                callbacks=callbacks
            )

        # --- CASO 6: AWS BEDROCK STANDARD ---
        elif provider_clean == "aws":
            from langchain_aws import ChatBedrock
            from botocore.config import Config
            creds = credential_manager.get_aws_credentials()
            return ChatBedrock(
                model_id=model_name,
                client=None,
                region_name=creds["region_name"],
                aws_access_key_id=creds["aws_access_key_id"],
                aws_secret_access_key=creds["aws_secret_access_key"],
                model_kwargs={
                    "temperature": temperature,
                    "max_tokens": 32000
                },
                config=Config(
                    read_timeout=600,
                    connect_timeout=10,
                    retries={'max_attempts': 3, 'mode': 'standard'}
                ),
                callbacks=callbacks
            )

        else:
            raise ValueError(f"Provider '{provider}' non supportato. Usa 'groq', 'gemini', 'ollama', 'azure' o 'aws'.")
