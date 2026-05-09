from fastapi import FastAPI
from apps.api_gateway.middleware.cors import add_cors
from apps.api_gateway.middleware.rate_limit import rate_limit_middleware
from apps.api_gateway.middleware.logging import log_requests
from apps.api_gateway.routes.health import router as health_router
from apps.api_gateway.routes.chat import router as chat_router
from apps.api_gateway.routes.agents import router as agents_router
from apps.api_gateway.routes.auth import router as auth_router
from shared.constants.app import APP_NAME

app = FastAPI(title=APP_NAME)

add_cors(app)
app.middleware("http")(rate_limit_middleware)
app.middleware("http")(log_requests)

app.include_router(health_router)
app.include_router(chat_router)
app.include_router(agents_router)
app.include_router(auth_router)

@app.get("/")
async def root():
    return {"message": "KrishiMind-AI API Gateway is running"}
