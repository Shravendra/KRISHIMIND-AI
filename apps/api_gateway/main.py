from __future__ import annotations

import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from apps.api_gateway.routes.health import router as health_router
from apps.api_gateway.routes.chat import router as chat_router
from apps.api_gateway.routes.agents import router as agents_router
from apps.api_gateway.routes.auth import router as auth_router

from apps.api_gateway.middleware.logging import logging_middleware
from apps.api_gateway.middleware.rate_limit import RateLimitMiddleware

from shared.constants.app import APP_NAME, APP_VERSION
from contextlib import asynccontextmanager
from apps.db.init_db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):

    await init_db()

    yield

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="AI-powered agricultural intelligence platform API",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


# CORS
origins = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:5173,http://localhost:3000"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins + ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Function middleware
app.middleware("http")(logging_middleware)

# Class middleware
app.add_middleware(RateLimitMiddleware)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):

    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "type": type(exc).__name__,
        },
    )


app.include_router(health_router)
app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(agents_router)


@app.get("/", tags=["root"])
async def root():

    return {
        "service": APP_NAME,
        "version": APP_VERSION,
        "status": "running",
    }