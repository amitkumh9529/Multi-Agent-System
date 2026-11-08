# AI Enterprise RAG Platform - Documentazione API

**Versione:** 1.0.0

**Descrizione:** Piattaforma aziendale di intelligenza artificiale basata su architettura RAG (Retrieval-Augmented Generation) con sistema multi-agente per l'orchestrazione di team di AI.

---

## Indice

1. [Overview Architetturale](#overview-architetturale)
2. [Control Plane - Teams](#control-plane---teams)
3. [Control Plane - Agents](#control-plane---agents)
4. [Control Plane - Tools](#control-plane---tools)
5. [Control Plane - Prompts](#control-plane---prompts)
6. [Control Plane - LLM Models](#control-plane---llm-models)
7. [Control Plane - Knowledge Bases](#control-plane---knowledge-bases)
8. [Execution Plane - Chat Threads](#execution-plane---chat-threads)
9. [System](#system)
10. [Appendice - Schemi Dati](#appendice---schemi-dati)

---

## Overview Architetturale

### Introduzione

La **AI Enterprise RAG Platform** è una piattaforma avanzata per la gestione e l'esecuzione di sistemi multi-agente basati su intelligenza artificiale. La piattaforma implementa il pattern **Retrieval-Augmented Generation (RAG)** combinato con un'architettura **supervisor-worker** per orchestrare team di agenti AI in grado di collaborare per risolvere task complessi.

### Architettura a Due Livelli

La piattaforma è organizzata secondo un'architettura a due livelli principali:

#### 1. Control Plane (Piano di Controllo)

Il **Control Plane** rappresenta il livello di configurazione e gestione della piattaforma. Attraverso questo piano, gli amministratori e gli sviluppatori possono:

- **Configurare Teams**: Creare e gestire team di agenti con una struttura gerarchica supervisor-worker
- **Gestire Agents**: Definire agenti AI con specifici LLM, prompt, tool e knowledge bases
- **Amministrare Prompts**: Creare e versionare system prompt per guidare il comportamento degli agenti
- **Selezionare LLM Models**: Utilizzare diversi modelli di linguaggio da vari provider (OpenAI, Azure, Anthropic, ecc.)
- **Configurare Tools**: Abilitare capacità specifiche agli agenti (ricerca web, calcoli, API calls, ecc.)
- **Costruire Knowledge Bases**: Creare repository di documenti per il RAG, con upload e indicizzazione automatica

#### 2. Execution Plane (Piano di Esecuzione)

Il **Execution Plane** rappresenta il livello runtime dove avviene l'interazione effettiva con gli agenti. Include:

- **Chat Threads**: Gestione di conversazioni persistenti con stato
- **Streaming Responses**: Risposte in tempo reale dagli agenti
- **Message History**: Storico completo delle conversazioni
- **Context Management**: Mantenimento del contesto conversazionale

### Pattern Architetturali

#### Multi-Agent System con Supervisor-Worker

La piattaforma implementa un pattern di orchestrazione multi-agente dove:

- **Supervisor Agent**: Coordina il team, analizza le richieste dell'utente, delega compiti ai worker e sintetizza le risposte
- **Worker Agents**: Agenti specializzati che eseguono task specifici utilizzando i loro tool e knowledge bases

Questa architettura permette di:
- Decomporre problemi complessi in sottotask gestibili
- Specializzare agenti su domini specifici
- Migliorare la qualità delle risposte attraverso la collaborazione
- Scalare orizzontalmente aggiungendo nuovi worker

#### Retrieval-Augmented Generation (RAG)

Il sistema RAG integrato permette agli agenti di:
1. **Ingestione**: Caricare documenti (PDF, TXT, MD) in knowledge bases
2. **Indicizzazione**: Convertire i documenti in embeddings vettoriali
3. **Retrieval**: Recuperare informazioni rilevanti al momento dell'inferenza
4. **Generazione**: Generare risposte contestualizzate basate sui documenti recuperati

### Flusso Dati

```
1. Configurazione (Control Plane):
   User → Create Team → Configure Supervisor + Workers
        → Assign Prompts, LLMs, Tools, KBs to each Agent
        → Upload Documents to Knowledge Bases

2. Esecuzione (Execution Plane):
   User → Send Message to Thread
        → Supervisor analyzes request
        → Delegates to specialized Workers
        → Workers retrieve from KBs (RAG)
        → Workers use Tools
        → Supervisor synthesizes final response
        → Stream response to User
```

### Caratteristiche Principali

1. **Modularità**: Ogni componente (agent, prompt, tool, KB) è indipendente e riutilizzabile
2. **Flessibilità**: Supporto per multiple LLM providers e configurazioni
3. **Scalabilità**: Architettura distribuita pronta per deployment enterprise
4. **Persistenza**: Tutti i dati e le conversazioni sono persistiti
5. **Streaming**: Risposte in tempo reale per migliore UX
6. **RAG Nativo**: Knowledge bases integrate per risposte basate su dati proprietari

---

## Control Plane - Teams

I team rappresentano gruppi di agenti organizzati secondo un pattern supervisor-worker. Un team è composto da un agente supervisor che coordina uno o più worker agents.

### GET `/api/v1/control/teams`

Restituisce la lista di tutti i teams creati nel sistema.

**Descrizione:** Endpoint per ottenere l'elenco completo dei team configurati.

**Parametri:** Nessuno

**Response 200 - Success**

Content-Type: `application/json`

Schema:
```json
[
  {
    "id": "integer",
    "name": "string (1-255 caratteri)",
    "description": "string | null"
  }
]
```

**Esempio Response:**
```json
[
  {
    "id": 1,
    "name": "Customer Support Team",
    "description": "Team specializzato nel supporto clienti"
  }
]
```

---

### POST `/api/v1/control/teams`

Crea un nuovo team nel sistema.

**Descrizione:** Endpoint per creare un team specificando il supervisor e i worker agents.

**Request Body**

Content-Type: `application/json`

Schema: `TeamCreate`

```json
{
  "name": "string (required, 1-255 caratteri)",
  "description": "string | null",
  "supervisor_id": "integer (required, > 0)",
  "worker_ids": ["array di integer"]
}
```

**Campi:**
- `name` (required): Nome identificativo del team
- `description` (optional): Descrizione del team e del suo scopo
- `supervisor_id` (required): ID dell'agente che fungerà da supervisor
- `worker_ids` (optional): Array di ID degli agenti worker del team

**Response 201 - Created**

Content-Type: `application/json`

Schema: `TeamRead`

**Response 422 - Validation Error**

Errori di validazione dei dati in input.

**Esempio Request:**
```json
{
  "name": "Data Analysis Team",
  "description": "Team per analisi dati e reportistica",
  "supervisor_id": 1,
  "worker_ids": [2, 3, 4]
}
```

---

### GET `/api/v1/control/teams/{team_id}`

Restituisce il team con id specificato inclusi i dettagli completi del supervisor e dei workers.

**Descrizione:** Endpoint per ottenere informazioni dettagliate su un team specifico.

**Parametri Path:**
- `team_id` (required): integer - ID del team

**Response 200 - Success**

Content-Type: `application/json`

Schema: `TeamReadFull`

```json
{
  "id": "integer",
  "name": "string",
  "description": "string | null",
  "supervisor": {
    "id": "integer",
    "name": "string",
    "description": "string",
    "prompt_id": "integer | null",
    "llm_model_id": "integer",
    "temperature": "number (0-1)",
    "agent_type": "supervisor"
  },
  "workers": [
    {
      "id": "integer",
      "name": "string",
      "description": "string",
      "prompt_id": "integer | null",
      "llm_model_id": "integer",
      "temperature": "number (0-1)",
      "agent_type": "worker"
    }
  ]
}
```

**Response 422 - Validation Error**

---

### PUT `/api/v1/control/teams/team_id}`

Aggiorna un team nel sistema.

**Descrizione:** Endpoint per modificare la configurazione di un team esistente.

**Parametri Query:**
- `team_id` (required): integer - ID del team da aggiornare

**Request Body**

Content-Type: `application/json`

Schema: `TeamCreate`

**Response 200 - Success**

Content-Type: `application/json`

Schema: `TeamRead`

**Response 422 - Validation Error**

---

### DELETE `/api/v1/control/teams/{team_id}`

Cancella il team con id specificato dal sistema.

**Descrizione:** Endpoint per eliminare definitivamente un team.

**Parametri Path:**
- `team_id` (required): integer - ID del team da eliminare

**Response 204 - No Content**

Team eliminato con successo.

**Response 422 - Validation Error**

---

## Control Plane - Agents

Gli agenti sono l'unità fondamentale della piattaforma. Ogni agente è configurato con un modello LLM, un prompt opzionale, tools e knowledge bases.

### GET `/api/v1/control/agents`

Restituisce la lista di tutti gli agenti creati nel sistema.

**Descrizione:** Endpoint per ottenere l'elenco di tutti gli agenti configurati.

**Parametri:** Nessuno

**Response 200 - Success**

Content-Type: `application/json`

Schema:
```json
[
  {
    "id": "integer",
    "name": "string (1-255 caratteri)",
    "description": "string",
    "prompt_id": "integer | null",
    "llm_model_id": "integer",
    "temperature": "number (0-1, default: 0)",
    "agent_type": "supervisor | worker"
  }
]
```

---

### POST `/api/v1/control/agents`

Crea un nuovo agente nel sistema.

**Descrizione:** Endpoint per creare un agente specificando modello LLM, prompt, tools e knowledge bases.

**Request Body**

Content-Type: `application/json`

Schema: `AgentCreate`

```json
{
  "name": "string (required, 1-255 caratteri)",
  "description": "string (required)",
  "prompt_id": "integer | null (> 0)",
  "llm_model_id": "integer (required, > 0)",
  "temperature": "number (0-1, default: 0)",
  "agent_type": "supervisor | worker (default: worker)",
  "tool_ids": ["array di integer"],
  "kb_ids": ["array di uuid | null"]
}
```

**Campi:**
- `name` (required): Nome identificativo dell'agente
- `description` (required): Descrizione del ruolo e delle capacità dell'agente
- `prompt_id` (optional): ID del prompt da utilizzare come system prompt
- `llm_model_id` (required): ID del modello LLM da utilizzare
- `temperature` (optional): Temperatura per il modello (0 = deterministico, 1 = creativo)
- `agent_type` (optional): Tipo di agente (supervisor o worker)
- `tool_ids` (optional): Array di ID dei tool da assegnare all'agente
- `kb_ids` (optional): Array di UUID delle knowledge bases da assegnare

**Response 201 - Created**

Content-Type: `application/json`

Schema: `AgentRead`

**Response 422 - Validation Error**

**Esempio Request:**
```json
{
  "name": "Research Assistant",
  "description": "Agente specializzato nella ricerca e analisi di informazioni",
  "prompt_id": 5,
  "llm_model_id": 1,
  "temperature": 0.3,
  "agent_type": "worker",
  "tool_ids": [1, 3, 5],
  "kb_ids": ["550e8400-e29b-41d4-a716-446655440000"]
}
```

---

### GET `/api/v1/control/agents/{agent_id}`

Restituisce l'agente con id specificato con tutti i dettagli completi.

**Descrizione:** Endpoint per ottenere informazioni dettagliate su un agente specifico, inclusi prompt, LLM model, tools e knowledge bases associate.

**Parametri Path:**
- `agent_id` (required): integer - ID dell'agente

**Response 200 - Success**

Content-Type: `application/json`

Schema: `AgentReadFull`

```json
{
  "id": "integer",
  "name": "string",
  "description": "string",
  "llm_model_id": "integer",
  "temperature": "number",
  "agent_type": "supervisor | worker",
  "prompt": {
    "id": "integer",
    "name": "string",
    "description": "string | null",
    "system_prompt": "string"
  } | null,
  "llm_model": {
    "id": "integer",
    "name": "string",
    "api_model_name": "string",
    "provider": "string"
  },
  "tools": [
    {
      "id": "integer",
      "name": "string",
      "display_name": "string",
      "description": "string | null"
    }
  ],
  "knowledge_bases": [
    {
      "id": "uuid",
      "name": "string",
      "description": "string | null"
    }
  ]
}
```

**Response 422 - Validation Error**

---

### PUT `/api/v1/control/agents/{agent_id}`

Aggiorna l'agente nel sistema con i nuovi valori.

**Descrizione:** Endpoint per modificare la configurazione di un agente esistente.

**Parametri Path:**
- `agent_id` (required): integer - ID dell'agente da aggiornare

**Request Body**

Content-Type: `application/json`

Schema: `AgentCreate`

**Response 200 - Success**

Content-Type: `application/json`

Schema: `AgentReadFull`

**Response 422 - Validation Error**

---

### DELETE `/api/v1/control/agents/{agent_id}`

Cancella l'agente con id specificato dal sistema.

**Descrizione:** Endpoint per eliminare definitivamente un agente.

**Parametri Path:**
- `agent_id` (required): integer - ID dell'agente da eliminare

**Response 204 - No Content**

Agente eliminato con successo.

**Response 422 - Validation Error**

---

## Control Plane - Tools

I tools sono capacità specifiche che possono essere assegnate agli agenti per estendere le loro funzionalità (es. ricerca web, calcoli, chiamate API).

### GET `/api/v1/control/tools/tools`

Restituisce la lista di tutti i tool disponibili nel sistema.

**Descrizione:** Endpoint per ottenere l'elenco di tutti i tools che possono essere assegnati agli agenti.

**Parametri:** Nessuno

**Response 200 - Success**

Content-Type: `application/json`

Schema:
```json
[
  {
    "id": "integer",
    "name": "string",
    "display_name": "string",
    "description": "string | null"
  }
]
```

**Esempio Response:**
```json
[
  {
    "id": 1,
    "name": "web_search",
    "display_name": "Web Search",
    "description": "Ricerca informazioni sul web tramite motori di ricerca"
  },
  {
    "id": 2,
    "name": "calculator",
    "display_name": "Calculator",
    "description": "Esegue calcoli matematici complessi"
  }
]
```

---

## Control Plane - Prompts

I prompt sono system prompt utilizzati per guidare il comportamento e le risposte degli agenti.

### GET `/api/v1/control/prompts`

Restituisce la lista di tutti i prompt creati.

**Descrizione:** Endpoint per ottenere l'elenco di tutti i system prompt configurati.

**Parametri:** Nessuno

**Response 200 - Success**

Content-Type: `application/json`

Schema:
```json
[
  {
    "id": "integer",
    "name": "string (1-255 caratteri)",
    "description": "string | null",
    "system_prompt": "string"
  }
]
```

---

### POST `/api/v1/control/prompts`

Crea un nuovo prompt nel sistema.

**Descrizione:** Endpoint per creare un nuovo system prompt.

**Request Body**

Content-Type: `application/json`

Schema: `PromptCreate`

```json
{
  "name": "string (required, 1-255 caratteri)",
  "description": "string | null",
  "system_prompt": "string (required)"
}
```

**Campi:**
- `name` (required): Nome identificativo del prompt
- `description` (optional): Descrizione dello scopo del prompt
- `system_prompt` (required): Contenuto effettivo del system prompt

**Response 201 - Created**

Content-Type: `application/json`

Schema: `PromptRead`

**Response 422 - Validation Error**

**Esempio Request:**
```json
{
  "name": "Customer Support Specialist",
  "description": "Prompt per agente di supporto clienti",
  "system_prompt": "Sei un assistente specializzato nel supporto clienti. Rispondi sempre in modo professionale, empatico e orientato alla soluzione. Mantieni un tono cordiale e comprensivo."
}
```

---

### GET `/api/v1/control/prompts/{prompt_id}`

Restituisce il prompt con id specificato.

**Descrizione:** Endpoint per ottenere i dettagli di un prompt specifico.

**Parametri Path:**
- `prompt_id` (required): integer - ID del prompt

**Response 200 - Success**

Content-Type: `application/json`

Schema: `PromptRead`

**Response 422 - Validation Error**

---

### PUT `/api/v1/control/prompts/{prompt_id}`

Aggiorna un prompt esistente.

**Descrizione:** Endpoint per modificare il contenuto di un prompt.

**Parametri Path:**
- `prompt_id` (required): integer - ID del prompt da aggiornare

**Request Body**

Content-Type: `application/json`

Schema: `PromptCreate`

**Response 200 - Success**

Content-Type: `application/json`

Schema: `PromptRead`

**Response 422 - Validation Error**

---

### DELETE `/api/v1/control/prompts/{prompt_id}`

Elimina un prompt dal sistema.

**Descrizione:** Endpoint per eliminare definitivamente un prompt.

**Parametri Path:**
- `prompt_id` (required): integer - ID del prompt da eliminare

**Response 204 - No Content**

Prompt eliminato con successo.

**Response 422 - Validation Error**

---

## Control Plane - LLM Models

Gli LLM Models rappresentano i modelli di linguaggio disponibili da diversi provider (OpenAI, Azure, Anthropic, ecc.).

### GET `/api/v1/control/llm`

Restituisce la lista di tutti gli LLM Models configurati.

**Descrizione:** Endpoint per ottenere l'elenco di tutti i modelli di linguaggio disponibili nel sistema.

**Parametri:** Nessuno

**Response 200 - Success**

Content-Type: `application/json`

Schema:
```json
[
  {
    "id": "integer",
    "name": "string (1-255 caratteri)",
    "api_model_name": "string (1-255 caratteri)",
    "provider": "string (1-255 caratteri)"
  }
]
```

**Esempio Response:**
```json
[
  {
    "id": 1,
    "name": "GPT-4 Turbo",
    "api_model_name": "gpt-4-turbo-preview",
    "provider": "openai"
  },
  {
    "id": 2,
    "name": "Claude 3 Sonnet",
    "api_model_name": "claude-3-sonnet-20240229",
    "provider": "anthropic"
  }
]
```

---

### GET `/api/v1/control/llm/{llm_model_id}`

Restituisce il modello LLM specificato.

**Descrizione:** Endpoint per ottenere i dettagli di un modello LLM specifico.

**Parametri Path:**
- `llm_model_id` (required): integer - ID del modello LLM

**Response 200 - Success**

Content-Type: `application/json`

Schema: `LLMModelRead`

```json
{
  "id": "integer",
  "name": "string",
  "api_model_name": "string",
  "provider": "string"
}
```

**Response 422 - Validation Error**

---

## Control Plane - Knowledge Bases

Le Knowledge Bases sono repository di documenti utilizzati per il Retrieval-Augmented Generation (RAG). Permettono agli agenti di accedere a informazioni proprietarie.

### GET `/api/v1/control/kb`

Restituisce la lista di tutte le Knowledge Bases nel sistema.

**Descrizione:** Endpoint per ottenere l'elenco di tutte le knowledge bases configurate.

**Parametri:** Nessuno

**Response 200 - Success**

Content-Type: `application/json`

Schema:
```json
[
  {
    "id": "uuid",
    "name": "string (3-50 caratteri)",
    "description": "string | null"
  }
]
```

---

### POST `/api/v1/control/kb`

Crea una nuova knowledge base nel sistema.

**Descrizione:** Endpoint per creare una nuova knowledge base vuota.

**Request Body**

Content-Type: `application/json`

Schema: `KnowledgeBaseCreate`

```json
{
  "name": "string (required, 3-50 caratteri)",
  "description": "string | null"
}
```

**Campi:**
- `name` (required): Nome identificativo della knowledge base (3-50 caratteri)
- `description` (optional): Descrizione del contenuto e dello scopo della KB

**Response 201 - Created**

Content-Type: `application/json`

Schema: `KnowledgeBaseRead`

**Response 422 - Validation Error**

**Esempio Request:**
```json
{
  "name": "Product Documentation",
  "description": "Documentazione completa dei prodotti aziendali"
}
```

---

### GET `/api/v1/control/kb/{kb_id}`

Restituisce la knowledge base specificata con tutti i documenti associati.

**Descrizione:** Endpoint per ottenere i dettagli completi di una knowledge base, inclusa la lista di documenti.

**Parametri Path:**
- `kb_id` (required): uuid - ID della knowledge base

**Response 200 - Success**

Content-Type: `application/json`

Schema: `KnowledgeBaseReadFull`

```json
{
  "id": "uuid",
  "name": "string",
  "description": "string | null",
  "created_at": "datetime",
  "updated_at": "datetime",
  "documents": [
    {
      "id": "uuid",
      "filename": "string",
      "file_type": "string",
      "file_size": "integer",
      "status": "pending | processing | completed | failed"
    }
  ]
}
```

**Response 422 - Validation Error**

---

### PUT `/api/v1/control/kb/{kb_id}`

Applica un aggiornamento alla knowledge base selezionata.

**Descrizione:** Endpoint per modificare i metadati di una knowledge base.

**Parametri Path:**
- `kb_id` (required): uuid - ID della knowledge base da aggiornare

**Request Body**

Content-Type: `application/json`

Schema: `KnowledgeBaseCreate`

**Response 200 - Success**

Content-Type: `application/json`

Schema: `KnowledgeBaseReadFull`

**Response 422 - Validation Error**

---

### DELETE `/api/v1/control/kb/{kb_id}`

Rimuove la knowledge base selezionata dal sistema.

**Descrizione:** Endpoint per eliminare definitivamente una knowledge base, inclusi tutti i file locali e i vettori nel database.

**Parametri Path:**
- `kb_id` (required): uuid - ID della knowledge base da eliminare

**Response 204 - No Content**

Knowledge base eliminata con successo.

**Response 422 - Validation Error**

---

### POST `/api/v1/control/kb/{kb_id}/documents`

Carica un documento nella Knowledge Base specificata.

**Descrizione:** Endpoint per caricare file (PDF, TXT, MD) in una knowledge base. Il file viene processato, indicizzato e convertito in embeddings per il retrieval.

**Parametri Path:**
- `kb_id` (required): uuid - ID della knowledge base

**Request Body**

Content-Type: `multipart/form-data`

Schema:
```
file: binary (required)
```

**Campi:**
- `file` (required): File binario da caricare (PDF, TXT, MD)

**Response 201 - Created**

Content-Type: `application/json`

Schema: `DocumentReadFull`

```json
{
  "id": "uuid",
  "filename": "string",
  "file_type": "string",
  "file_size": "integer",
  "status": "pending | processing | completed | failed",
  "knowledge_base": {
    "id": "uuid",
    "name": "string",
    "description": "string | null"
  }
}
```

**Response 422 - Validation Error**

**Note:**
- I file supportati sono: PDF, TXT, MD
- Il processamento è asincrono: lo status iniziale è "pending"
- Monitorare il campo `status` per verificare il completamento dell'indicizzazione

---

### DELETE `/api/v1/control/kb/{kb_id}/documents/{doc_id}`

Elimina definitivamente un documento e il file associato dal sistema.

**Descrizione:** Endpoint per rimuovere un documento da una knowledge base, inclusi i file locali e i vettori indicizzati.

**Parametri Path:**
- `kb_id` (required): uuid - ID della knowledge base
- `doc_id` (required): uuid - ID del documento da eliminare

**Response 204 - No Content**

Documento eliminato con successo.

**Response 422 - Validation Error**

---

## Execution Plane - Chat Threads

I Chat Threads rappresentano conversazioni persistenti con i team di agenti. Ogni thread mantiene lo stato e lo storico dei messaggi.

### POST `/api/v1/execution/threads/{thread_id}/chat`

Endpoint per inviare un messaggio a un team e ricevere una risposta in streaming.

**Descrizione:** Endpoint principale di chat che delega la logica al ThreadService. Supporta risposte in streaming per una migliore user experience.

**Parametri Path:**
- `thread_id` (required): string - ID univoco del thread (generato dal client)

**Request Body**

Content-Type: `application/json`

Schema: `ChatRequest`

```json
{
  "message": "string (required)",
  "team_id": "integer (required)"
}
```

**Campi:**
- `message` (required): Il messaggio dell'utente
- `team_id` (required): L'ID del team che deve rispondere

**Response 200 - Success**

Content-Type: `application/json` (streaming)

La risposta viene trasmessa in streaming man mano che gli agenti elaborano la richiesta.

**Response 422 - Validation Error**

**Esempio Request:**
```json
{
  "message": "Analizza i dati di vendita del Q4 2023 e fornisci insights sui trend",
  "team_id": 1
}
```

**Note:**
- Il `thread_id` è generato dal client (tipicamente un UUID)
- Se il thread non esiste, viene creato automaticamente
- Le risposte sono in streaming per ridurre la latenza percepita
- Il supervisor coordina i worker e sintetizza la risposta finale

---

### GET `/api/v1/execution/threads`

Ottiene la lista di tutte le chat avviate dall'utente.

**Descrizione:** Endpoint per recuperare l'elenco di tutti i thread di conversazione.

**Parametri:** Nessuno

**Response 200 - Success**

Content-Type: `application/json`

Schema:
```json
[
  {
    "thread_id": "string",
    "title": "string | null",
    "created_at": "datetime",
    "updated_at": "datetime"
  }
]
```

**Esempio Response:**
```json
[
  {
    "thread_id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Analisi vendite Q4",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:45:00Z"
  }
]
```

---

### GET `/api/v1/execution/threads/{thread_id}/messages`

Ottiene lo storico dei messaggi per una specifica chat.

**Descrizione:** Endpoint per recuperare tutti i messaggi di un thread. Da chiamare al caricamento della pagina per visualizzare la conversazione.

**Parametri Path:**
- `thread_id` (required): string - ID del thread

**Response 200 - Success**

Content-Type: `application/json`

Schema:
```json
[
  {
    "id": "uuid",
    "type": "human | ai",
    "content": "string",
    "created_at": "datetime"
  }
]
```

**Esempio Response:**
```json
[
  {
    "id": "450e8400-e29b-41d4-a716-446655440001",
    "type": "human",
    "content": "Ciao, ho bisogno di aiuto",
    "created_at": "2024-01-15T10:30:00Z"
  },
  {
    "id": "450e8400-e29b-41d4-a716-446655440002",
    "type": "ai",
    "content": "Ciao! Sono qui per aiutarti. Come posso esserti utile?",
    "created_at": "2024-01-15T10:30:15Z"
  }
]
```

**Response 422 - Validation Error**

---

### DELETE `/api/v1/execution/threads/{thread_id}`

Cancella il thread con id specificato dal sistema.

**Descrizione:** Endpoint per eliminare definitivamente un thread e tutti i messaggi associati.

**Parametri Path:**
- `thread_id` (required): string - ID del thread da eliminare

**Response 204 - No Content**

Thread eliminato con successo.

**Response 422 - Validation Error**

---

## System

Endpoints di sistema per health check e diagnostica.

### GET `/health`

Health check endpoint.

**Descrizione:** Endpoint per verificare lo stato di salute del servizio.

**Parametri:** Nessuno

**Response 200 - Success**

Content-Type: `application/json`

Servizio operativo.

---

### GET `/`

Root endpoint.

**Descrizione:** Endpoint radice dell'API.

**Parametri:** Nessuno

**Response 200 - Success**

Content-Type: `application/json`

---

## Appendice - Schemi Dati

### AgentCreate

Schema per la creazione di un nuovo agente.

**Campi:**
- `name` (string, required): Nome dell'agente (1-255 caratteri)
- `description` (string, required): Descrizione del team
- `prompt_id` (integer | null, optional): ID del prompt da associare (> 0)
- `llm_model_id` (integer, required): ID del modello LLM da associare (> 0)
- `temperature` (number, optional): Temperatura del modello LLM (0-1, default: 0)
- `agent_type` (AgentType, optional): Tipo di agente (default: "worker")
- `tool_ids` (array[integer], optional): Array di ID dei tool
- `kb_ids` (array[uuid] | null, optional): Array di UUID delle knowledge bases

---

### AgentRead

Schema per la lettura di un agente (versione base).

**Campi:**
- `id` (integer, required): ID univoco dell'agente
- `name` (string, required): Nome dell'agente (1-255 caratteri)
- `description` (string, required): Descrizione del team
- `prompt_id` (integer | null): ID del prompt associato (> 0)
- `llm_model_id` (integer, required): ID del modello LLM (> 0)
- `temperature` (number): Temperatura del modello (0-1, default: 0)
- `agent_type` (AgentType): Tipo di agente (default: "worker")

---

### AgentReadFull

Schema per la lettura completa di un agente con tutte le relazioni.

**Campi:**
- `id` (integer, required): ID univoco dell'agente
- `name` (string, required): Nome dell'agente (1-255 caratteri)
- `description` (string, required): Descrizione del team
- `llm_model_id` (integer, required): ID del modello LLM (> 0)
- `temperature` (number): Temperatura del modello (0-1, default: 0)
- `agent_type` (AgentType): Tipo di agente (default: "worker")
- `prompt` (PromptRead | null, required): Oggetto prompt completo
- `llm_model` (LLMModelRead, required): Oggetto LLM model completo
- `tools` (array[ToolRead], required): Array di tool assegnati
- `knowledge_bases` (array[KnowledgeBaseRead], required): Array di KB assegnate

---

### AgentType

Enum per il tipo di agente.

**Valori:**
- `supervisor`: Agente supervisor che coordina i worker
- `worker`: Agente worker specializzato

---

### TeamCreate

Schema per la creazione di un nuovo team.

**Campi:**
- `name` (string, required): Nome del team (1-255 caratteri)
- `description` (string | null, optional): Descrizione del team
- `supervisor_id` (integer, required): ID dell'agente supervisor (> 0)
- `worker_ids` (array[integer], optional): Lista degli ID dei worker

---

### TeamRead

Schema per la lettura di un team (versione base).

**Campi:**
- `id` (integer, required): ID univoco del team
- `name` (string, required): Nome del team (1-255 caratteri)
- `description` (string | null): Descrizione del team

---

### TeamReadFull

Schema per la lettura completa di un team con tutti gli agenti.

**Campi:**
- `id` (integer, required): ID univoco del team
- `name` (string, required): Nome del team (1-255 caratteri)
- `description` (string | null): Descrizione del team
- `supervisor` (AgentRead, required): Oggetto supervisor completo
- `workers` (array[AgentRead], required): Array di worker agents

---

### ToolRead

Schema per la lettura di un tool.

**Campi:**
- `id` (integer, required): ID univoco del tool
- `name` (string, required): Nome tecnico del tool
- `display_name` (string, required): Nome visualizzato
- `description` (string | null): Descrizione del tool

---

### PromptCreate

Schema per la creazione di un nuovo prompt.

**Campi:**
- `name` (string, required): Nome del prompt (1-255 caratteri)
- `description` (string | null, optional): Descrizione del prompt
- `system_prompt` (string, required): Contenuto del system prompt

---

### PromptRead

Schema per la lettura di un prompt.

**Campi:**
- `id` (integer, required): ID univoco del prompt
- `name` (string, required): Nome del prompt (1-255 caratteri)
- `description` (string | null): Descrizione del prompt
- `system_prompt` (string, required): Contenuto del system prompt

---

### LLMModelRead

Schema per la lettura di un modello LLM.

**Campi:**
- `id` (integer, required): ID univoco del modello
- `name` (string, required): Nome del modello LLM (1-255 caratteri)
- `api_model_name` (string, required): Nome del deployment/modello API (1-255 caratteri)
- `provider` (string, required): Nome del provider (1-255 caratteri)

**Esempi di provider:**
- `openai`: OpenAI (GPT-3.5, GPT-4, ecc.)
- `anthropic`: Anthropic (Claude)
- `azure`: Azure OpenAI Service
- `google`: Google (PaLM, Gemini)

---

### KnowledgeBaseCreate

Schema per la creazione di una knowledge base.

**Campi:**
- `name` (string, required): Nome della KB (3-50 caratteri)
- `description` (string | null, optional): Descrizione della KB

---

### KnowledgeBaseRead

Schema per la lettura di una knowledge base (versione base).

**Campi:**
- `id` (uuid, required): ID univoco della KB
- `name` (string, required): Nome della KB (3-50 caratteri)
- `description` (string | null): Descrizione della KB

---

### KnowledgeBaseReadFull

Schema per la lettura completa di una knowledge base con documenti.

**Campi:**
- `id` (uuid, required): ID univoco della KB
- `name` (string, required): Nome della KB (3-50 caratteri)
- `description` (string | null): Descrizione della KB
- `created_at` (datetime, required): Data di creazione
- `updated_at` (datetime, required): Data ultimo aggiornamento
- `documents` (array[DocumentRead], optional): Array di documenti (default: [])

---

### DocumentRead

Schema per la lettura di un documento.

**Campi:**
- `id` (uuid, required): ID univoco del documento
- `filename` (string, required): Nome del file
- `file_type` (string, required): Tipo MIME del file
- `file_size` (integer, required): Dimensione in bytes
- `status` (ProcessingStatus, required): Stato del processamento

---

### DocumentReadFull

Schema per la lettura completa di un documento con relazione alla KB.

**Campi:**
- `id` (uuid, required): ID univoco del documento
- `filename` (string, required): Nome del file
- `file_type` (string, required): Tipo MIME del file
- `file_size` (integer, required): Dimensione in bytes
- `status` (ProcessingStatus, required): Stato del processamento
- `knowledge_base` (KnowledgeBaseRead | null, required): KB di appartenenza

---

### ProcessingStatus

Enum per lo stato di processamento di un documento.

**Valori:**
- `pending`: Documento caricato, in attesa di processamento
- `processing`: Documento in fase di indicizzazione
- `completed`: Documento processato e indicizzato con successo
- `failed`: Errore durante il processamento

---

### ChatRequest

Schema per una richiesta di chat.

**Campi:**
- `message` (string, required): Il messaggio dell'utente
- `team_id` (integer, required): L'ID del team che deve rispondere

---

### ChatThreadRead

Schema per la lettura di un thread di chat.

**Campi:**
- `thread_id` (string, required): UUID generato dal client
- `title` (string | null): Titolo della conversazione
- `created_at` (datetime, required): Data di creazione
- `updated_at` (datetime, required): Data ultimo aggiornamento

---

### ChatMessageRead

Schema per la lettura di un messaggio di chat.

**Campi:**
- `id` (uuid, required): ID univoco del messaggio
- `type` (MessageType, required): Tipo messaggio ('human' o 'ai')
- `content` (string, required): Contenuto del messaggio
- `created_at` (datetime, required): Data di creazione

---

### MessageType

Enum per il tipo di messaggio.

**Valori:**
- `human`: Messaggio inviato dall'utente
- `ai`: Messaggio generato dall'AI

---

### HTTPValidationError

Schema per errori di validazione.

**Campi:**
- `detail` (array[ValidationError]): Array di errori di validazione

---

### ValidationError

Schema per un singolo errore di validazione.

**Campi:**
- `loc` (array[string | integer], required): Posizione dell'errore
- `msg` (string, required): Messaggio di errore
- `type` (string, required): Tipo di errore

---

## Conclusione

Questa documentazione fornisce una panoramica completa dell'**AI Enterprise RAG Platform**. La piattaforma offre un'architettura modulare e scalabile per la gestione di sistemi multi-agente con capacità RAG avanzate.

Per ulteriori informazioni sull'implementazione, consultare il codice sorgente o contattare il team di sviluppo.

**Versione documento:** 1.0.0  
**Ultima revisione:** 2026-01-13

