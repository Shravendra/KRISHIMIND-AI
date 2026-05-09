from fastapi import APIRouter, Depends
from shared.schemas.chat import ChatRequest, ChatResponse
from apps.api_gateway.deps import get_orchestrator
from apps.chatbot_orchestrator.main import ChatbotOrchestrator

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    orchestrator: ChatbotOrchestrator = Depends(get_orchestrator),
):
    return await orchestrator.handle_message(request)
