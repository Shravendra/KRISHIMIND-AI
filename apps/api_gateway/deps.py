from apps.chatbot_orchestrator.main import ChatbotOrchestrator

_orchestrator = ChatbotOrchestrator()

def get_orchestrator() -> ChatbotOrchestrator:
    return _orchestrator
