# 🌱 KrishiMind-AI

> **AI-Powered Agricultural Intelligence Platform**
> A modular, multi-agent backend that diagnoses farm issues, predicts outcomes, optimises decisions, and learns continuously — built for smallholders in India and Africa as well as industrial farms in the US and EU.

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Agent Taxonomy](#agent-taxonomy)
- [Request Lifecycle](#request-lifecycle)
- [RAG Pipeline](#rag-pipeline)
- [Memory System](#memory-system)
- [LLM Routing Strategy](#llm-routing-strategy)
- [API Reference](#api-reference)
- [Frontend](#frontend)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [Docker Setup](#docker-setup)
- [Development Guide](#development-guide)
- [Testing](#testing)
- [Observability & Logging](#observability--logging)
- [Roadmap](#roadmap)

---

## Overview

KrishiMind-AI is a production-grade, agentic AI platform designed to bring cutting-edge agricultural intelligence directly to farmers. The system combines a **conversational AI chatbot** with a **fleet of specialised AI agents** — each responsible for a distinct farming domain — orchestrated through a **LangGraph-based workflow** and surfaced via a **React web frontend**.

### Core Principles

| Principle | Why It Matters |
|---|---|
| **Agent isolation (SRP)** | Each AI agent works independently and is individually testable |
| **Tool-first design** | Agents are callable as tools, fully MCP-compatible |
| **Multi-LLM support** | Avoids vendor lock-in via LiteLLM routing |
| **Offline-tolerant** | Batch + async workflows survive connectivity gaps |
| **Explainability** | Farmers must trust and understand every output |
| **Evaluation-driven** | Every agent is measurable via DeepEval and RAGAS |

---

## Key Features

### 🌿 Crop & Farm Intelligence
- **AI Crop Disease Detection** — vision-powered diagnosis from farm photos with confidence scores, severity ratings, and treatment protocols including dosage and organic alternatives
- **Image Analysis** — multi-angle plant image understanding using GPT-4o vision
- **Fertilizer Optimisation** — multi-factor agronomic reasoning for exact NPK recommendations
- **Soil Health Analysis** — pH, NPK, and organic matter inference with remediation guidance
- **Crop Planning** — season-aware crop selection and rotation advice
- **Weed & Harvest Intelligence** — detection, control, and optimal harvest timing

### 🌤️ Weather & Risk
- **Hyper-local Weather Risk Assessment** — integrates OpenWeatherMap data with LLM analysis for farm-specific advisories on drought, frost, flood, and pest-favorable conditions
- **Optimal Spray Windows** — wind, temperature, and humidity-based scheduling
- **Climate Risk Scoring** — probability models for cyclone, flood, and cold wave events

### 💰 Market Intelligence
- **Price Forecasting** — commodity price trends and optimal selling windows via AgMarket API
- **Market Advisory** — logistics, transport, and storage optimisation

### 🐄 Livestock Management
- **Health Assessment** — symptom-based disease and injury detection
- **Feed Optimisation** — cost-efficient nutrition planning
- **Welfare Alerts** — heat stress, behavior, and breeding cycle monitoring

### 📚 Knowledge & Education
- **RAG-Powered Knowledge Base** — answers grounded in FAO manuals, ICAR guidelines, PlantVillage disease datasets, and government advisories
- **Advisory Chat Agent** — conversational farming expert with memory across sessions
- **Scheme Awareness** — references PM-KISAN, PMFBY, KCC, eNAM and other government programmes

### 🔐 Platform Infrastructure
- JWT authentication with farmer role-based access
- Per-IP sliding-window rate limiting (stricter on `/chat`)
- Structured JSON logging with correlation IDs, farmer context, and slow-request detection
- OpenTelemetry-ready observability
- Full Docker Compose setup for one-command local development

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    React Frontend (Vite)                 │
│  Dashboard · Chat · Crop · Soil · Weather · Market ·    │
│  Livestock · Knowledge Base                              │
└───────────────────────┬─────────────────────────────────┘
                        │ HTTPS / REST
┌───────────────────────▼─────────────────────────────────┐
│              FastAPI  API Gateway  (:8000)               │
│  Middleware: Logging · Rate Limit · CORS · Auth          │
│  Routes: /auth  /chat  /agents  /health                  │
└───┬──────────────────────────────────────────────────────┘
    │
┌───▼──────────────────────────────────────────────────────┐
│            Chatbot Orchestrator (LangGraph)               │
│                                                           │
│  Intent Classifier ──► Agent Dispatcher                  │
│       │                      │                            │
│       │              ┌───────┴────────┐                  │
│       │         Parallel Agent Calls  │                  │
│       │    ┌──────┬──────┬──────┬─────┴──┐              │
│       │  Image Disease Soil  Weather Market               │
│       │  Agent Agent  Agent  Agent  Agent                │
│       │    └──────┴──────┴──────┴────────┘              │
│       │              │                                    │
│       └──► Aggregator + Explainer ◄── RAG Pipeline       │
│                      │                                    │
│              Structured Response                          │
└───────────────────────────────────────────────────────────┘
    │
┌───▼──────────────────────────────────────────────────────┐
│              Data & Storage Layer                         │
│  PostgreSQL · Redis · Qdrant (Vector DB) · MinIO         │
└──────────────────────────────────────────────────────────┘
```

### LangGraph Conversation Graph

```
User Input
    ↓
Intent Router Agent
    ↓
┌──────────────┬──────────────┬──────────────┐
│ Image Agent  │ Weather Agent│  Soil Agent  │  (parallel)
└──────────────┴──────────────┴──────────────┘
    ↓
Disease / Fertilizer / Risk Agents  (parallel)
    ↓
Aggregation & Explanation Agent
    ↓
Final Structured Response + Memory Update
```

---

## Technology Stack

| Layer | Technology |
|---|---|
| **API** | FastAPI 0.111 + Uvicorn |
| **Orchestration** | LangGraph (stateful, parallel, conditional) |
| **Agents** | LangChain + custom service modules |
| **LLM Routing** | LiteLLM (OpenAI, Anthropic, Groq, Ollama) |
| **Vision** | GPT-4o (image analysis, disease detection) |
| **CV Models** | YOLOv8, EfficientNet (roadmap) |
| **Vector DB** | Qdrant v1.9.2 |
| **Relational DB** | PostgreSQL 16 + SQLAlchemy async |
| **Cache / Memory** | Redis 7 (short-term conversation memory) |
| **Object Storage** | MinIO (farm images, S3-compatible) |
| **Embeddings** | OpenAI text-embedding-3-small (1536-dim) |
| **Auth** | JWT (python-jose) + pbkdf2_sha256 passwords |
| **Frontend** | React 18 + Vite + Tailwind CSS + Zustand |
| **Async HTTP** | httpx + aiohttp |
| **Observability** | OpenTelemetry + Prometheus + JSON structured logs |
| **Evaluation** | DeepEval + RAGAS |
| **Protocol** | MCP (Model Context Protocol) |
| **Containerisation** | Docker Compose |

---

## Project Structure

```
krishimind-ai/
│
├── apps/
│   ├── api_gateway/                    # FastAPI entry point
│   │   ├── main.py                     # App factory, middleware wiring
│   │   ├── middleware/
│   │   │   ├── logging.py              # Advanced structured logging middleware
│   │   │   └── rate_limit.py           # Sliding-window IP rate limiter
│   │   └── routes/
│   │       ├── auth.py                 # /auth (register, login, me, logout)
│   │       ├── chat.py                 # /chat (main conversation endpoint)
│   │       ├── agents.py               # /agents (direct agent invocation)
│   │       └── health.py               # /health, /health/ready
│   │
│   ├── chatbot_orchestrator/           # LangGraph multi-agent orchestrator
│   │   ├── main.py                     # ChatbotOrchestrator class
│   │   ├── router/
│   │   │   └── intent_classifier.py    # LLM intent detection + agent routing
│   │   ├── memory/
│   │   │   ├── redis_store.py          # Short-term Redis conversation memory
│   │   │   ├── vector_memory.py        # Semantic long-term memory (Qdrant)
│   │   │   └── farm_profile_store.py   # Persistent farmer profile (PostgreSQL)
│   │   └── synthesis/
│   │       ├── aggregator.py           # Merges multi-agent results
│   │       └── explainer.py            # Farmer-friendly LLM explanation
│   │
│   └── web_frontend/                   # React SPA
│       └── src/
│           ├── App.jsx                 # Router + protected routes
│           ├── pages/                  # Dashboard, Chat, CropAnalysis, ...
│           ├── components/             # Sidebar, Topbar, Layout
│           ├── store/
│           │   └── authStore.js        # Zustand auth state
│           └── services/
│               └── api.js              # Axios client + interceptors
│
├── agents/
│   ├── crop/
│   │   ├── image_analysis/service.py   # Vision LLM crop image analysis
│   │   ├── disease_detection/service.py# Disease/pest diagnosis (vision + text)
│   │   ├── soil_agent/service.py       # Soil health inference
│   │   ├── fertilizer_agent/service.py # NPK and fertilizer optimisation
│   │   ├── weather_agent/service.py    # OpenWeatherMap + LLM risk advisory
│   │   └── crop_planning_agent/        # Crop selection and rotation planning
│   └── market/
│       └── price_forecast_agent/       # Commodity price analysis
│
├── rag/
│   └── pipelines/
│       └── rag_pipeline.py             # Qdrant retrieval + LLM generation
│
├── shared/
│   ├── auth/
│   │   └── jwt.py                      # Token creation, verification, FastAPI deps
│   ├── llm/
│   │   └── client.py                   # LiteLLM unified client + model tier map
│   ├── schemas/
│   │   └── chat.py                     # Pydantic request/response models
│   ├── constants/
│   │   └── app.py                      # Intent constants, app metadata
│   └── utils/
│       └── logging.py                  # JSONFormatter + get_logger + log_agent_call
│
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env.example
└── README.md
```

---

## Agent Taxonomy

Every agent is an isolated Python module exposing a single async `service` function. Each can also run as an **MCP server endpoint**, making it callable as a tool from any MCP-compatible orchestrator.

### 🌱 Crop & Farm Agents

| Agent | Responsibility | LLM Tier |
|---|---|---|
| Image Analysis Agent | Multi-angle crop image understanding | `vision` (GPT-4o) |
| Disease Detection Agent | Crop disease & pest identification | `reasoning` (GPT-4o) |
| Fertilizer Agent | NPK quantity/type optimisation | `reasoning` (GPT-4o) |
| Soil Agent | pH, NPK, organic matter inference | `cheap` (GPT-4o-mini) |
| Weather Agent | Hyper-local risk forecasting | `cheap` (GPT-4o-mini) |
| Crop Planning Agent | Crop selection & rotation | `cheap` (GPT-4o-mini) |
| Weed Agent | Weed detection & control | `cheap` |
| Harvest Agent | Optimal harvest timing | `cheap` |
| Post-Harvest Agent | Storage & quality advice | `cheap` |
| Progress Monitoring Agent | Temporal crop growth tracking | `vision` |

### 🐄 Livestock Agents

| Agent | Responsibility |
|---|---|
| Livestock Health Agent | Disease & injury detection |
| Feed Optimisation Agent | Cost-efficient nutrition |
| Breeding Agent | Genetic & cycle planning |
| Welfare Agent | Stress, heat, behavior alerts |

### 📦 Market, Risk & Sustainability Agents

| Agent | Responsibility |
|---|---|
| Market Advisor Agent | Price prediction & selling windows |
| Logistics Agent | Transport & storage optimisation |
| Risk Assessment Agent | Climate, pest, flood probability |
| Insurance Agent | Claim readiness & risk scoring |
| Sustainability Agent | Carbon, water, biodiversity metrics |
| Compliance Agent | Regional regulatory checks |

### 🎓 Knowledge & Community Agents

| Agent | Responsibility |
|---|---|
| Education Agent | RAG-based learning |
| Community Insight Agent | Peer insights & trends |
| Advisory Chat Agent | Conversational farming expert |

---

## Request Lifecycle

A complete `/chat` request flows through the following steps:

```
1. Client sends POST /chat
   { message, images[], crop, season, farm_context, conversation_id }

2. API Gateway Middleware
   ├── Logging middleware assigns X-Request-ID correlation ID
   ├── Rate limit check (20 req/min for /chat, 60 req/min otherwise)
   └── JWT auth validates Bearer token → extracts farmer_id + role

3. ChatbotOrchestrator.handle_message()
   ├── Load conversation history from Redis
   ├── Load farm profile from PostgreSQL
   ├── Retrieve semantic memories from Qdrant vector store

4. Intent Classifier (LLM, fast tier)
   Input: message + image flag + conversation history
   Output: {
     intent: "crop_disease",
     confidence: 0.92,
     agents_to_call: ["image_analysis", "disease_detection", "rag_knowledge_agent"],
     extracted_entities: { crop, location, urgency }
   }

5. Parallel Agent Dispatch (asyncio.gather)
   ├── image_analysis.service.analyze_images()
   ├── disease_detection.service.detect_disease()
   └── rag_pipeline.rag_answer()

6. Aggregator
   Merges AgentResult objects → deduplicated recommendations, ranked warnings,
   key data points, average confidence score

7. LLM Synthesis (cheap tier, 200-300 words)
   Generates farmer-friendly explanation with:
   - Direct answer to the query
   - Most important action first
   - 3-5 specific steps with timing
   - Confidence level stated naturally
   - Warnings integrated naturally

8. Memory Update
   ├── Save turn to Redis (short-term)
   └── Embed and store in Qdrant (long-term semantic recall)

9. Response
   {
     response: "...",
     intent: "crop_disease",
     agents_used: [...],
     recommendations: [...],
     warnings: [...],
     confidence: 0.87,
     processing_time_ms: 3240
   }
```

---

## RAG Pipeline

The RAG (Retrieval-Augmented Generation) system grounds all knowledge answers in curated agricultural content rather than relying solely on LLM parametric knowledge.

### Knowledge Sources
- FAO manuals and crop production guides
- ICAR (Indian Council of Agricultural Research) publications
- USDA and EU agricultural documentation
- PlantVillage crop disease datasets
- Government advisories (PM-KISAN, PMFBY, eNAM, KCC)
- Validated agent outputs from production interactions

### RAG Flow

```
Farmer Query
    ↓
Embed query (OpenAI text-embedding-3-small, 1536-dim)
    ↓
Qdrant ANN Search (collection: krishimind_knowledge_base)
    ↓
Score Threshold Filter (score > 0.65)
    ↓
Top-K Chunk Assembly with source citations
    ↓
LLM Answer Generation (cheap tier, temperature=0.3)
    ↓
Response with citation confidence scores
```

### Fallback Behaviour
When Qdrant is unavailable, the pipeline gracefully falls back to pure LLM generation. If that also fails, the system returns the Kisan Call Centre number (1800-180-1551) and directs the farmer to their local Krishi Vigyan Kendra.

---

## Memory System

KrishiMind-AI uses four complementary memory stores:

| Memory Type | Store | Contents | Lifetime |
|---|---|---|---|
| **Short-term** | Redis | Last N conversation turns per session | TTL-based (hours) |
| **Long-term Semantic** | Qdrant | Embedded conversation summaries | Persistent |
| **Farm Profile** | PostgreSQL | Crops, farm size, location, preferences | Persistent |
| **Image History** | MinIO | Uploaded crop/livestock images | Persistent |

The orchestrator loads all four stores at the start of each request and writes back after generating a response, ensuring continuity of advice across sessions without the farmer needing to repeat context.

---

## LLM Routing Strategy

All LLM calls are unified through `shared/llm/client.py` using LiteLLM. Model assignment is tuned so the cheapest model that can adequately handle each task is used by default:

| Alias | Default Model | Used By |
|---|---|---|
| `cheap` | `openai/gpt-4o-mini` | Intent classifier, RAG synthesis, market, soil, weather, crop planning |
| `fast` | `openai/gpt-4o-mini` | High-throughput or latency-sensitive calls |
| `reasoning` | `openai/gpt-4o` | Disease detection, fertilizer optimisation (multi-step agronomic reasoning) |
| `vision` | `openai/gpt-4o` | Image analysis (requires multimodal capability) |
| `local` | Configurable (Ollama) | Offline/edge deployments |

Override any alias via environment variables (`DEFAULT_LLM`, `REASONING_LLM`, `VISION_LLM`, `FAST_LLM`). The client includes automatic fallback to `cheap` if the primary model call fails, so the system degrades gracefully rather than erroring.

---

## API Reference

The full interactive API documentation is available at `http://localhost:8000/docs` (Swagger UI) and `http://localhost:8000/redoc` when the server is running.

### Authentication

```
POST /auth/register
POST /auth/login          → { access_token, token_type }
GET  /auth/me             → { farmer_id, name, role, ... }
PUT  /auth/me             → update profile
POST /auth/logout
```

All protected endpoints require `Authorization: Bearer <token>`.

### Chat

```
POST /chat
Content-Type: application/json

{
  "message": "My tomato leaves are turning yellow with brown spots",
  "images": ["<base64-encoded-jpeg>"],
  "crop": "tomato",
  "season": "kharif",
  "conversation_id": "uuid-optional",
  "farm_context": {
    "location": "Nashik, Maharashtra",
    "farm_size": 2.5
  }
}
```

Response:
```json
{
  "response": "Based on the image and symptoms described...",
  "intent": "crop_disease",
  "agents_used": ["image_analysis", "disease_detection", "rag_knowledge_agent"],
  "recommendations": ["Apply Mancozeb @ 2.5g/litre..."],
  "warnings": ["Withhold harvest for 7 days after application"],
  "confidence": 0.87,
  "processing_time_ms": 3241
}
```

```
GET  /chat/history/{session_id}?limit=20
DELETE /chat/history/{session_id}
```

### Agents (Direct Invocation)

```
GET  /agents              → list available agents and their status
POST /agents/analyze-image
POST /agents/disease-detect
POST /agents/soil-analyze
POST /agents/weather-risk
POST /agents/fertilizer-optimize
POST /agents/crop-plan
POST /agents/market-intel
```

### Health

```
GET /health               → liveness probe
GET /health/ready         → readiness probe (checks downstream dependencies)
```

---

## Frontend

The React SPA is built with Vite, Tailwind CSS, and Zustand for state management.

### Pages

| Route | Page | Description |
|---|---|---|
| `/dashboard` | Farm Dashboard | Overview widgets, quick stats, recent alerts |
| `/chat` | AI Assistant | Full conversational chat with image upload and agent badges |
| `/crop` | Crop Analysis | Disease detection with drag-and-drop image upload |
| `/soil` | Soil & Fertilizer | Soil health form and fertilizer plan generator |
| `/weather` | Weather Risk | Real-time risk dashboard for the farmer's location |
| `/market` | Market Intelligence | Price trends, sell timing, commodity charts |
| `/livestock` | Livestock Health | Symptom checker and health monitoring |
| `/learn` | Knowledge Base | RAG-powered search over agricultural knowledge |
| `/settings` | Settings | Account management and farm profile |

### Frontend Stack

- **React 18** with React Router v6
- **Tailwind CSS** with a custom agricultural colour palette (`leaf`, `earth`, `soil`, `sky`)
- **Zustand** for auth state (persisted to localStorage)
- **Axios** with request/response interceptors for auth token injection and 401 handling
- **Recharts** for price trend visualisations
- **react-markdown** for rendering structured LLM responses
- **react-dropzone** for multi-image farm photo uploads
- **lucide-react** for icons

### Auth Flow

1. Farmer registers or logs in → receives JWT access token
2. Token stored in Zustand store (persisted via localStorage)
3. Axios request interceptor injects `Authorization: Bearer <token>` on every API call
4. 401 response interceptor clears auth state and redirects to `/login`

---

## Getting Started

### Prerequisites

- Docker & Docker Compose (recommended)
- Python 3.11+ (for local development without Docker)
- Node.js 20+ (for frontend development)
- An OpenAI API key (minimum requirement; Anthropic and Groq are optional)

### Quickstart with Docker

```bash
# 1. Clone the repository
git clone https://github.com/your-org/krishimind-ai.git
cd krishimind-ai

# 2. Configure environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY at minimum

# 3. Start all services
docker compose up -d

# 4. Verify everything is running
docker compose ps
curl http://localhost:8000/health
```

Services started:
- API Backend: `http://localhost:8000`
- React Frontend: `http://localhost:5173`
- PostgreSQL: `localhost:5432`
- Redis: `localhost:6379`
- Qdrant: `http://localhost:6333`
- MinIO Console: `http://localhost:9001`

### Local Development (without Docker)

```bash
# Backend
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env              # add API keys

# Start infrastructure only
docker compose up -d postgres redis qdrant minio

# Run the API
uvicorn apps.api_gateway.main:app --reload --port 8000

# Frontend (separate terminal)
cd apps/web_frontend
npm install
npm run dev
```

### Demo Login

```
Email:    demo@krishimind.ai
Password: demo1234
```

---

## Environment Variables

Copy `.env.example` to `.env` and fill in the values:

```bash
# ── App ──────────────────────────────────────────────
APP_ENV=dev                          # dev | staging | production
APP_NAME=KrishiMind-AI
APP_VERSION=0.1.0
SECRET_KEY=change-me-to-64-char-random-string
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# ── API Gateway ───────────────────────────────────────
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# ── LLM via LiteLLM ──────────────────────────────────
OPENAI_API_KEY=sk-...              # Required
ANTHROPIC_API_KEY=sk-ant-...       # Optional (for Claude reasoning)
GROQ_API_KEY=gsk_...               # Optional (for fast inference)
DEFAULT_LLM=openai/gpt-4o-mini
VISION_LLM=openai/gpt-4o
REASONING_LLM=openai/gpt-4o        # or anthropic/claude-3-5-sonnet

# ── Databases ─────────────────────────────────────────
DATABASE_URL=postgresql+asyncpg://krishimind:password@localhost:5432/krishimind_db
REDIS_URL=redis://localhost:6379/0
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=                    # Leave empty for local Qdrant
QDRANT_COLLECTION=krishimind_kb

# ── Object Storage ────────────────────────────────────
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=krishimind-images
MINIO_SECURE=false

# ── External APIs ─────────────────────────────────────
OPENWEATHER_API_KEY=your-key       # openweathermap.org
AGMARKET_API_KEY=your-key          # Market price data

# ── MCP ───────────────────────────────────────────────
MCP_TOKEN_SECRET=mcp-secret-token

# ── Observability ─────────────────────────────────────
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318
LOG_LEVEL=INFO
```

---

## Docker Setup

The `docker-compose.yml` defines six services on a shared `krishimind` bridge network:

| Service | Image | Port | Purpose |
|---|---|---|---|
| `postgres` | postgres:16-alpine | 5432 | Relational data, farm profiles |
| `redis` | redis:7-alpine | 6379 | Session cache, conversation memory |
| `qdrant` | qdrant/qdrant:v1.9.2 | 6333 / 6334 | Vector search (REST / gRPC) |
| `minio` | minio/minio | 9000 / 9001 | Image storage / web console |
| `api` | ./Dockerfile | 8000 | FastAPI backend with hot reload |
| `frontend` | node:20-alpine | 5173 | React Vite dev server |

All services have health checks. The `api` service waits for `postgres`, `redis`, and `qdrant` to pass their health checks before starting.

```bash
# Start everything
docker compose up -d

# View logs
docker compose logs -f api

# Restart just the backend after code changes
docker compose restart api

# Stop all services
docker compose down

# Full teardown including volumes
docker compose down -v
```

---

## Development Guide

### Adding a New Agent

1. Create `agents/<domain>/<agent_name>/service.py` with an async service function:

```python
async def my_new_agent(
    param1: str,
    param2: Optional[Dict] = None,
) -> Dict[str, Any]:
    """Returns a structured dict compatible with AgentResult."""
    ...
```

2. Register the agent in `apps/chatbot_orchestrator/main.py` under `_dispatch_agents()`.

3. Map the intent to the new agent in `apps/chatbot_orchestrator/router/intent_classifier.py` under `INTENT_TO_AGENTS`.

4. Add a direct API route in `apps/api_gateway/routes/agents.py` if you want HTTP-level access.

5. Assign a model tier in `shared/llm/client.py` under `AGENT_MODEL`.

### Intent Classification

The system recognises the following primary intents, each routing to one or more agents:

| Intent Constant | Agents Called |
|---|---|
| `crop_disease` | image_analysis, disease_detection, rag_knowledge_agent |
| `soil_health` | soil_agent, rag_knowledge_agent |
| `fertilizer` | fertilizer_agent, soil_agent |
| `weather_risk` | weather_agent |
| `crop_planning` | crop_planning_agent, weather_agent |
| `market_price` | market_agent |
| `livestock_health` | rag_knowledge_agent |
| `education` | rag_knowledge_agent |
| `general_chat` | rag_knowledge_agent |

If the LLM classifier fails (network error, parse error), a keyword fallback classifier activates automatically.

### Logging

All log output is structured JSON (using `shared/utils/logging.py`). The advanced gateway middleware (`apps/api_gateway/middleware/logging.py`) emits three events per request:

- `request_started` — method, path, client IP, farmer_id, role, query params
- `request_finished` — status code, duration_ms, response_bytes, slow_request flag
- `slow_request_detected` — separate warning event when latency exceeds the per-route threshold

Correlation IDs (`X-Request-ID`) are propagated through a `ContextVar` so any downstream log call (agent, RAG, LLM client) can include the same trace ID.

---

## Testing

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run a specific module
pytest tests/agents/test_disease_detection.py

# Run with async support
pytest --asyncio-mode=auto
```

Tests use `httpx.AsyncClient` as the ASGI test client, with mocked LLM responses to avoid API costs in CI.

---

## Observability & Logging

### Structured Logs

Every log line is a JSON object with at minimum:

```json
{
  "timestamp": "2026-05-12T08:30:00.123Z",
  "level": "INFO",
  "logger": "apps.api_gateway.middleware.logging",
  "event": "request_finished",
  "request_id": "a1b2c3d4-...",
  "method": "POST",
  "path": "/chat",
  "route_family": "chat",
  "status_code": 200,
  "duration_ms": 3241.87,
  "slow_request": false,
  "response_bytes": 1842,
  "farmer_id": "farmer-uuid",
  "role": "farmer"
}
```

### Slow Request Thresholds

| Route Family | Threshold |
|---|---|
| `agent` | 8,000 ms |
| `chat` | 6,000 ms |
| `auth` | 500 ms |
| `health` | 200 ms |
| `other` | 2,000 ms |

### Metrics

Prometheus metrics are exposed via `prometheus-client`. The OTEL exporter is configured via `OTEL_EXPORTER_OTLP_ENDPOINT` for integration with Grafana, Jaeger, or any OTLP-compatible backend.

---

## Roadmap

### Phase 1 — Foundation ✅
- FastAPI setup, LiteLLM integration, Redis memory, 3 core agents (Image, Disease, Weather)

### Phase 2 — Core Intelligence ✅
- Soil + Fertilizer agents, Crop Planning, LangGraph orchestration, parallel agent execution

### Phase 3 — RAG + Education ✅
- Knowledge ingestion, RAG pipeline, Qdrant integration, Education agent

### Phase 4 — Market, Risk & Livestock (In Progress)
- Price forecasting with ML models
- Livestock CV models (YOLOv8)
- Risk scoring (flood, drought, frost probability)
- Insurance readiness assistant

### Phase 5 — Production Hardening
- Response streaming (Server-Sent Events)
- Multilingual support (Hindi, Marathi, Tamil, Swahili)
- Offline sync and batch workflows
- RAGAS evaluation pipeline for continuous RAG quality measurement
- DeepEval agent benchmark suite
- Mobile app (React Native)

---

## Contributing

1. Fork the repository and create a feature branch: `git checkout -b feat/my-feature`
2. Follow the existing module structure — one agent = one `service.py`
3. Write tests for new agent logic
4. Ensure `LOG_LEVEL=DEBUG` does not leak any PII or API keys
5. Open a pull request with a description of the agent's responsibilities, the LLM tier chosen, and why

---

## License

© KrishiMind-AI. All rights reserved. See `LICENSE` for details.

---

*Built with ❤️ for farmers — from smallholders in rural India to large-scale operations worldwide.*
