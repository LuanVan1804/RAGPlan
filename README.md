# Travel Plan Chatbot

Travel-only chatbot built with LangGraph + LangServe (backend) and React (frontend).  
It validates user requests, retrieves travel context from RAG, and returns either:
1. a travel plan, or
2. travel recommendations.

Non-travel questions are rejected.

## 1. Project flow

The graph flow is:
1. User sends input
2. Chatbot validates if the request is travel-related
3. Chatbot retrieves context from RAG and combines it with LLM reasoning
4. Chatbot returns plan/recommendation only for travel topics

## 2. Prerequisites

- Python 3.10+
- Node.js 18+
- OpenAI API key
- LangSmith API key (recommended for tracing/management)

## 3. Setup backend

From project root (`RAGPlan`):

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file in project root:

```env
OPENAI_API_KEY=sk-...
LANGSMITH_API_KEY=lsv2_...
LANGSMITH_PROJECT=travel-chatbot
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
```

Notes:
- `LANGSMITH_PROJECT` controls where traces are grouped in LangSmith.
- The app loads `.env` automatically from `app/config.py`.

## 4. Run backend

```bash
python main.py
```

Backend URLs:
- API root: `http://localhost:8000`
- Swagger docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

Main endpoints:
- `POST /travel-planner/invoke`
- `POST /travel-planner/stream`
- `POST /travel-planner/batch`
- `GET /health`

## 5. Manage and monitor in LangSmith

1. Open `https://smith.langchain.com`
2. Select/create the project named by `LANGSMITH_PROJECT`
3. Run chatbot requests from UI or API
4. Inspect traces for each run:
   - validation result (travel/non-travel)
   - RAG retrieval behavior
   - final synthesis output
5. Use traces to debug failures and prompt quality

Operational tips:
- Use a separate project name per environment (example: `travel-chatbot-dev`, `travel-chatbot-prod`)
- Keep `LANGSMITH_API_KEY` in local `.env` only

## 6. Run frontend

In a new terminal:

```bash
cd frontend
npm install
npm run dev
```

Open:
- `http://localhost:5173`

The frontend sends requests to backend at `http://localhost:8000`.

## 7. Use the chatbot

Example travel prompts:
- `Plan a 5-day trip to Tokyo with $2500 budget`
- `Recommend places to visit in Bali for couples`
- `Suggest a budget itinerary in Paris for 3 days`

Expected behavior:
- Travel requests: chatbot returns plan/recommendation
- Non-travel requests: chatbot replies that it only supports travel topics

## 8. Quick API test

```bash
curl -X POST http://localhost:8000/travel-planner/invoke ^
  -H "Content-Type: application/json" ^
  -d "{\"input\":{\"message\":\"Plan a 4-day trip to Tokyo with $2000\"}}"
```

## 9. Project structure

```text
RAGPlan/
├── app/
│   ├── config.py       # env and LangSmith settings
│   ├── graph.py        # LangGraph workflow
│   ├── rag.py          # RAG retrieval logic/documents
│   ├── tool.py         # parser, weather, cost tools
│   └── server.py       # FastAPI + LangServe app
├── frontend/           # React client
├── main.py             # backend entrypoint
├── requirements.txt
└── langgraph.json
```
