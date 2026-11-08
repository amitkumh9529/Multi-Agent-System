from sqlalchemy.orm import Session
from app.shared.persistence.models import LLMModel, PromptModel, AgentModel, ToolModel
from app.shared.schemas.agent_schemas import AgentType


def seed_llm_models(db: Session):
    """Popola il DB con i modelli di default (Groq, Gemini, Ollama, ecc.) se non esistono."""

    if db.query(LLMModel).first():
        return

    print("🌱 Seeding dei modelli LLM iniziali...")

    initial_models = [
        # Modelli 100% Free Cloud
        LLMModel(
            name="Groq Qwen 27B (Free/Fast)",
            api_model_name="qwen/qwen3.8-27b",
            provider="groq",
        ),
        LLMModel(
            name="Groq GPT-OSS 120B (Powerful/Free)",
            api_model_name="openai/gpt-oss-120b",
            provider="groq",
        ),
        LLMModel(
            name="Groq GPT-OSS 20B (Compact/Fast)",
            api_model_name="openai/gpt-oss-20b",
            provider="groq",
        ),
        LLMModel(
            name="Google Gemini 3.8 Flash (Free)",
            api_model_name="gemini-3.8-flash",
            provider="gemini",
        ),
        LLMModel(
            name="Ollama Llama 3.2 3B (Local CPU)",
            api_model_name="llama3.2:3b",
            provider="local",
        ),
    ]

    db.add_all(initial_models)
    db.commit()


def seed_prompts(db: Session):
    """Popola il DB con prompt di default se non esistono."""

    if db.query(PromptModel).first():
        return

    print("🌱 Seeding dei prompt iniziali...")

    initial_prompts = [
        PromptModel(
            name="chapter_writer_prompt",
            description="Prompt per generare un capitolo ebook relativo ad un argomento",
            system_prompt="Sei un assistente esperto nella generazione di contenuti per ebook. "
                          "Il tuo unico compito è prendere un titolo di un capitolo fornito dall'utente e generare il capitolo relativo all'argomento, per un ebook. "
                          "Il capitolo generato deve essere esaustivo sull'argomento. Rispondi SOLO con il paragrafo generato."
        ),
        PromptModel(
            name="index_generator_prompt",
            description="Prompt per generare un elenco di capitoli",
            system_prompt="Sei un assistente esperto nella strutturazione di contenuti. "
                          "Il tuo unico compito è prendere un argomento fornito dall'utente e restituire un elenco puntato di capitoli per un ebook su quell'argomento. "
                          "Rispondi SOLO con l'elenco dei capitoli, nient'altro."
        ),
        PromptModel(
            name="ebook_supervisor_prompt",
            description="Prompt per gestire la creazione di un ebook",
            system_prompt="Sei un agente supervisore per la scrittura di ebook. "
                          "Il tuo compito è coordinare il processo di scrittura. "
                          "Procedi in questo modo: scrivi prima tutti i capitoli e poi generali ad uno ad uno tramite tools. Ricordati di fornire il contesto della richiesta dell'utente al tool. "
                          "Una volta ottenuti tutti i capitoli completi, il tuo compito finale è presentare l'intero ebook in formato markdown senza sintetizzare nulla. "
                          "Scrivi solo il contenuto dell'ebook."
        )
    ]
    db.add_all(initial_prompts)
    db.commit()


def seed_agents(db: Session):
    """Popola il DB con agenti starter preconfigurati."""

    if db.query(AgentModel).first():
        return

    first_model = db.query(LLMModel).first()
    model_id = first_model.id if first_model else 1

    initial_agents = [
        AgentModel(
            name="chapter_writer_agent",
            description="Agente in grado di scrivere un intero capitolo a partire da un titolo",
            temperature=0,
            agent_type=AgentType.WORKER,
            prompt_id=1,
            llm_model_id=model_id
        ),
        AgentModel(
            name="index_generator_agent",
            description="Agente in grado di redigere un indice di un ebook su un argomento",
            temperature=0,
            agent_type=AgentType.WORKER,
            prompt_id=2,
            llm_model_id=model_id
        ),
        AgentModel(
            name="ebook_supervisor",
            description="Supervisore nella scrittura di un ebook",
            temperature=0,
            agent_type=AgentType.SUPERVISOR,
            prompt_id=3,
            llm_model_id=model_id
        )
    ]
    db.add_all(initial_agents)
    db.commit()


def seed_tools(db: Session):
    """Popola il catalogo dei tool disponibili."""

    available_tools = [
        {
            "name": "web_search",
            "display_name": "Ricerca Web (DuckDuckGo / Tavily)",
            "description": "Permette all'agente di cercare informazioni in tempo reale su internet."
        }
    ]

    for tool_data in available_tools:
        exists = db.query(ToolModel).filter(ToolModel.name == tool_data["name"]).first()
        if not exists:
            new_tool = ToolModel(**tool_data)
            db.add(new_tool)

    db.commit()
    print("🌱 Seeding dei tool...")
