# MAS Platform

I built **MAS Platform** as a thesis project to explore how people can create and use AI agents without having to assemble every part of an agent system by hand. The project brings together a visual workspace, a FastAPI backend, and a PostgreSQL-backed runtime for configuring agents, organizing them into teams, and chatting with them.

The platform combines **multi-agent orchestration** with **retrieval-augmented generation (RAG)**. I designed it around two connected areas: a **control plane** for configuring reusable AI components and an **execution plane** for running conversations with agents and teams.

## What it can do

- **Configure agents** with a language model, instructions, tools, and knowledge bases.
- **Create teams** that use a supervisor-and-worker pattern to coordinate specialized agents.
- **Manage prompts** and reuse them across agent configurations.
- **Connect language models** through Groq, Google Gemini, Ollama, Azure OpenAI, and AWS Bedrock integrations.
- **Create knowledge bases** and upload PDF, TXT, and Markdown documents for retrieval.
- **Chat with agents and teams** using streamed responses and persistent conversation threads.
- **Use web search** with Tavily when configured, or the DuckDuckGo fallback.
- **Choose embedding providers** including Google Gemini, Hugging Face, Azure OpenAI, and AWS Bedrock.

Provider availability depends on the credentials and deployments configured for your environment. The repository includes an example environment file with the options used by the project.

## Screenshots

### Home and agent workspace

![MAS Platform home dashboard](images/docsMasPlatform_welcome.png)

### Chat with retrieval

![Chat interface with RAG](images/chat_rag.png)

![Agent response](images/team_answer.png)

### Agent teams

![Team of collaborating agents](images/TeamOfAgents.png)

## How the project is organized

MAS Platform is split into three main parts:

| Component | Purpose | Technologies |
| --- | --- | --- |
| **Frontend** | Web interface for teams, agents, prompts, knowledge bases, and chat | React, TypeScript, Vite |
| **Backend** | REST API, configuration management, document ingestion, and agent execution | Python, FastAPI, LangChain, LangGraph |
| **Database** | Application data, vector search, and persisted conversation state | PostgreSQL, pgvector |

The backend exposes a **control plane** at `/api/v1/control` for managing teams, agents, tools, prompts, language models, and knowledge bases. The **execution plane** at `/api/v1/execution` handles chat threads and messages.

For RAG, uploaded documents are ingested into a knowledge base, embedded, and retrieved to provide relevant context during a conversation. For team conversations, a supervisor can coordinate work across configured worker agents.

## Run with Docker Compose

### Requirements

- [Git](https://git-scm.com/)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) or Docker Engine with the Compose plugin
- An API key for at least one cloud model provider if you want to use a cloud-hosted model. Ollama can be used for local model inference.

### 1. Get the project

```bash
git clone https://github.com/r-gab01/MAS_Platform.git
cd MAS_Platform
```

### 2. Configure the backend

Create the backend environment file from the example:

```bash
cp app/example.env app/.env
```

On Windows PowerShell, use:

```powershell
Copy-Item app/example.env app/.env
```

Open `app/.env` and add the credentials for the providers you plan to use. For example, set `GROQ_API_KEY` or `GEMINI_API_KEY`. A `TAVILY_API_KEY` is optional; when it is not set, web search uses DuckDuckGo.

The example file is configured for a PostgreSQL database reached from the host. When running the backend **inside Docker Compose**, set both `DATABASE_URL` and `POSTGRES_URI` in `app/.env` to the Compose database address:

```dotenv
DATABASE_URL=postgresql://myuser:mypassword@vectordb:5432/mydatabase
POSTGRES_URI=postgresql://myuser:mypassword@vectordb:5432/mydatabase
```

These credentials match the local database settings in `docker-compose.yaml`. Change them consistently in both files if you choose different database credentials. Do not commit real API keys or passwords.

### 3. Start the services

Start the database first:

```bash
docker compose up -d vectordb
```

Wait until the database reports that it is ready to accept connections. You can follow its startup output with `docker compose logs -f vectordb`; press `Ctrl+C` to stop following the logs without stopping the database. Then build and start the application services:

```bash
docker compose up --build -d app frontend
```

The first build may take a few minutes. The services are available at:

| Service | Address |
| --- | --- |
| Frontend | [http://localhost:3000](http://localhost:3000) |
| Backend API | [http://localhost:8000](http://localhost:8000) |
| Interactive API docs | [http://localhost:8000/docs](http://localhost:8000/docs) |
| API health check | [http://localhost:8000/health](http://localhost:8000/health) |

To follow service logs:

```bash
docker compose logs -f
```

To stop the services:

```bash
docker compose down
```

To stop the services and remove the local database volume as well:

```bash
docker compose down --volumes
```

**Note:** Removing the volume deletes the database data stored by this local Compose setup.

## Run the services locally

The repository includes PowerShell launch scripts for Windows. For a local backend process, the PostgreSQL service still needs to be running. You can start only the database with Docker:

```bash
docker compose up -d vectordb
```

For this setup, keep the host database address in `app/.env` pointed at `localhost:54320`, as in `app/example.env`.

### Backend

Requires Python 3.12 or later. From the repository root, create a virtual environment and install the backend dependencies:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r app\requirements.txt
```

Start the backend:

```powershell
.\start_backend.ps1
```

The API will be available at `http://localhost:8000`.

### Frontend

Requires Node.js 18 or later. In a separate terminal:

```powershell
cd frontend
npm install
npm run dev
```

The frontend will be available at `http://localhost:3000`. Its Vite development server proxies API requests to `http://localhost:8000` by default.

## Configuration reference

The main settings in `app/example.env` are:

| Variable | Purpose |
| --- | --- |
| `GROQ_API_KEY` | Credentials for Groq language models |
| `GEMINI_API_KEY` | Credentials for Google Gemini models and embeddings |
| `OLLAMA_BASE_URL` | URL of an Ollama server; the example defaults to `http://localhost:11434` |
| `DATABASE_URL` | SQLAlchemy connection string for application data |
| `POSTGRES_URI` | PostgreSQL connection string used by the conversation checkpoint store |
| `EMBEDDING_PROVIDER` | Embedding provider selection; the example uses `gemini` |
| `TAVILY_API_KEY` | Optional Tavily web-search credentials |
| `STORAGE_TYPE` | Document storage mode; the example uses local storage |
| `LOCAL_STORAGE_PATH` | Local directory used for uploaded documents |

Additional provider credentials are read from environment variables when using Azure OpenAI or AWS Bedrock. See [`app/example.env`](app/example.env) and [`credential_manager.py`](app/shared/security/credential_manager.py) for the variables currently supported by the implementation.

## API documentation

The FastAPI application provides interactive Swagger documentation at `/docs` when the backend is running. For the project’s endpoint and data-model reference, see [`app/API_DOCUMENTATION.md`](app/API_DOCUMENTATION.md).

Common API paths include:

| Area | Base path |
| --- | --- |
| Teams, agents, prompts, tools, models, and knowledge bases | `/api/v1/control` |
| Chat threads and messages | `/api/v1/execution/threads` |
| Health check | `/health` |

## Run the tests

From the repository root, install the backend dependencies and run the test suite:

```bash
python -m pip install -r app/requirements.txt
python -m pytest
```

The current tests cover provider credential validation and the web-search fallback.

## Repository layout

```text
MAS_Platform/
├── app/
│   ├── control_plane/       # Configuration and management API
│   ├── execution_plane/     # Chat and agent execution
│   ├── shared/              # Persistence, providers, tools, and shared schemas
│   ├── example.env          # Example backend configuration
│   └── main.py              # FastAPI application entry point
├── db/                      # PostgreSQL initialization
├── frontend/
│   └── src/                 # React application
├── images/                  # README screenshots
├── tests/                   # Backend tests
├── docker-compose.yaml
├── start_backend.ps1
└── start_frontend.ps1
```

## Project notes

This project is an evolving thesis implementation. Model availability, external provider APIs, and local configuration can affect runtime behavior. If you find an issue or have an idea for improvement, feel free to open an issue or submit a pull request.
