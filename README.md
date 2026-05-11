# KRISHIMIND-AI (runnable starter)

This is a production-oriented starter backend for an AI-powered agricultural intelligence platform.

## Included
- FastAPI API gateway
- Conversational orchestrator
- Rule-based intent routing
- Memory store with Redis fallback
- Simple RAG pipeline
- Crop image analysis agent
- MCP-style tool registry
- Retry/fallback/orchestration utilities

## Important note
Your original tree uses hyphenated Python service folders such as `api-gateway` and `chatbot-orchestrator`.
Python imports are cleaner and safer with snake_case folders, so this runnable starter uses:
- `api_gateway`
- `chatbot_orchestrator`
- `web_frontend`
- `mobile_app`

## Run locally
```bash
python -m venv .venv
# activate venv
pip install -r requirements.txt
uvicorn apps.api_gateway.main:app --reload --port 8000
```

## Sample chat request
```bash
curl -X POST http://127.0.0.1:8000/chat   -H "Content-Type: application/json"   -d '{
    "message": "My tomato leaves have yellow spots",
    "farmer_id": "f001",
    "crop": "tomato",
    "location": {"lat": 28.6, "lon": 77.2},
    "images": [{"url": "leaf_1.jpg"}]
  }'
```
