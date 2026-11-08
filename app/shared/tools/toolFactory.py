import uuid
from langchain_core.tools import tool
from app.shared.factories.vector_store_factory import VectorStoreFactory
from app.shared.security.credential_manager import credential_manager


def create_tool(tool_type: str):
    """
    Funzione per la creazione di tool:
      - web_search: Usa Tavily se la chiave è configurata, altrimenti fallback automatico su DuckDuckGo (100% Free).
    """
    if tool_type == "web_search":
        tavily_key = credential_manager.get_tavily_api_key()
        if tavily_key:
            from langchain_community.tools.tavily_search import TavilySearchResults
            return TavilySearchResults(
                max_results=5,
                tavily_api_key=tavily_key
            )
        else:
            from langchain_community.tools.ddg_search.tool import DuckDuckGoSearchRun
            return DuckDuckGoSearchRun(
                name="web_search",
                description="Permette di cercare informazioni aggiornate su internet tramite DuckDuckGo."
            )

    else:
        raise ValueError(f"Tool '{tool_type}' non supportato dalla factory.")


def create_rag_tool(kb_id: uuid.UUID, knowledge_descr: str):
    """
    Wrapper che permette di catturare le informazioni della Knowledge Base in un tool in modo che rimanga il riferimento alle variabili
    e l'agente possa usare la KB corretta.
    """
    vector_store = VectorStoreFactory.get_vector_store(kb_id=str(kb_id))

    @tool(response_format="content_and_artifact", description=knowledge_descr)
    def retrieve_context(query: str):
        """Retrieve informazioni per migliorare la qualità della risposta"""

        retrieved_docs = vector_store.similarity_search(query, k=2)
        serialized = "\n\n".join(
            (f"Source: {doc.metadata}\nContent: {doc.page_content}")
            for doc in retrieved_docs
        )
        return serialized, retrieved_docs
    return retrieve_context


def create_send_email_tool(credentials):

    @tool
    def send_email_tool(recipient: str, subject: str, body: str) -> str:
        """
        Utilizza questo tool per inviare una email a un destinatario specifico.
        """
        print(f"\n[MOCK EMAIL SYSTEM] -------------------------")
        print(f"TO: {recipient}")
        print(f"SUBJECT: {subject}")
        print(f"BODY:\n{body}")
        print(f"-----------------------------------------------\n")

        with open("email_logs.txt", "a") as f:
            f.write(f"TO: {recipient} | SUB: {subject} | STATUS: SENT\n")

        return f"Email inviata con successo a {recipient} (Modalità Simulazione)."
    return send_email_tool
