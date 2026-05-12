# RAGPlan - Travel Planning Chatbot

RAGPlan is a travel-focused chatbot with:
1. **Backend**: FastAPI + LangGraph + LangServe (`app/`)
2. **User UI**: React chat client (`user-ui/`)
3. **Admin UI**: React dashboard for knowledge management (`admin-ui/`)

The assistant answers travel requests only (trip plans, recommendations, weather/cost context) and rejects non-travel questions.

## Runtime flow

1. Model analyzes user input and extracts travel fields (`is_travel_related`, `destination`, `days`, `budget`, `people`, request mode).
2. If request is not travel-related, graph returns a rejection response.
3. Graph queries Pinecone RAG by destination; if destination context exists, that context is used.
4. If destination context is missing, graph continues with model internal knowledge.
5. Weather API runs for the extracted destination.
6. Cost calculator runs for the extracted destination/days/people/accommodation type.
7. Synthesis combines parsed input + (optional) Pinecone context + weather + cost into final response.

## 1. Folder structure

```text
RAGPlan/
├── app/
│   ├── server.py               # Main FastAPI app (includes user/admin routers)
│   ├── graph.py                # LangGraph workflow
│   ├── rag.py                  # Pinecone-backed RAG storage and retrieval
│   ├── tool.py                 # Weather/cost/parser helper tools
│   ├── config.py               # .env loading + LangSmith/OpenAI settings
│   ├── admin/                  # Admin APIs: knowledge, monitoring, config
│   └── user/                   # User chat APIs
├── user-ui/                    # End-user chat frontend (Vite + React)
├── admin-ui/                   # Admin frontend for ingestion/listing docs
├── scripts/
│   └── test_user_api.py        # Quick API script for /user/chat/invoke
├── langgraph.json
├── pyproject.toml
├── requirements.txt
└── vector_store.pkl            # Legacy local cache file (not used by Pinecone mode)
```

## 2. Prerequisites

- **Python 3.13+** (based on `pyproject.toml`)
- **Node.js 18+** and npm
- **OPENAI_API_KEY** (required)
- **PINECONE_API_KEY** (required for RAG)
- **LANGSMITH_API_KEY** (optional, for tracing)

## 3. Environment setup

Create `.env` in project root:

```env
OPENAI_API_KEY=sk-...
PINECONE_API_KEY=pcsk_...
PINECONE_INDEX_NAME=ragplan-travel
PINECONE_NAMESPACE=travel-guides
PINECONE_CLOUD=aws
PINECONE_REGION=us-east-1
PINECONE_EMBEDDING_MODEL=text-embedding-3-small
LANGSMITH_API_KEY=lsv2_...                       # optional
LANGSMITH_PROJECT=travel-chatbot                 # optional (default exists)
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
```

`app/config.py` automatically loads `.env` on startup.

## 4. Install dependencies

### Backend (recommended: uv)

```powershell
uv sync
```

### Backend (pip alternative)

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install fastapi langserve langchain-openai pinecone httpx uvicorn
```

### Frontends

```powershell
cd user-ui
npm install
cd ..\admin-ui
npm install
cd ..
```

## 5. Run the project

Open **3 terminals** from repository root.

### Terminal 1: Run backend (port 8000)

If using uv:

```powershell
uv run uvicorn app.server:app --host 0.0.0.0 --port 8000 --reload
```

If using venv/pip:

```powershell
.venv\Scripts\activate
python -m uvicorn app.server:app --host 0.0.0.0 --port 8000 --reload
```

### Terminal 2: Run user UI (port 5173)

```powershell
cd user-ui
npm run dev -- --port 5173
```

Open: `http://localhost:5173`

### Terminal 3: Run admin UI (port 5174)

```powershell
cd admin-ui
npm run dev -- --port 5174
```

Open: `http://localhost:5174`

## 6. URLs and key APIs

### Backend URLs

- API root: `http://localhost:8000/`
- Swagger: `http://localhost:8000/docs`
- Health: `http://localhost:8000/health`

### User chat APIs

- `POST /user/chat/invoke`
- `POST /travel-planner/invoke`
- `POST /travel-planner/stream`
- `POST /travel-planner/batch`

### Admin APIs

- `GET /admin/knowledge/list`
- `POST /admin/knowledge/ingest`
- `POST /admin/knowledge/bulk-ingest`
- `GET /admin/monitoring/status`
- `GET /admin/config`
- `PATCH /admin/config`

## 7. Quick test commands

### Test user endpoint (PowerShell)

```powershell
curl -X POST http://localhost:8000/user/chat/invoke `
  -H "Content-Type: application/json" `
  -d "{\"message\":\"Plan a 4-day trip to Tokyo with $2000 budget\",\"thread_id\":\"demo-thread-1\"}"
```

### Run provided API test script

```powershell
python scripts\test_user_api.py
```

## 8. How to use each UI

### User UI (`http://localhost:5173`)

- Send travel prompts (itinerary/recommendations).
- The UI calls `POST /user/chat/invoke`.

### Admin UI (`http://localhost:5174`)

- View existing knowledge docs.
- Upload `.txt` files to ingest new knowledge (`POST /admin/knowledge/ingest`).
- Destination is derived from filename in current UI implementation.

## 9. Notes and troubleshooting

- Both UIs are hardcoded to call backend at `http://localhost:8000`.
- RAG documents are stored in Pinecone index/namespace configured in `.env`.
- LangSmith tracing is enabled only when `LANGSMITH_API_KEY` is set.
- If ports are already occupied, free them or run with different ports and update frontend API URLs accordingly.
