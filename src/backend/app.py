"""Modal App with FastAPI web endpoint for AIUC Evaluation API."""

import modal
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.backend.api import (
    agent_configs,
    attacks,
    batches,
    configs,
    contexts,
    conversations,
    evals,
    grades,
    products,
    prompts,
    risks,
    rubrics,
    playground,
    templates,
)

from src.backend.modal import app, image

fastapi = FastAPI(
    title="AIUC Evaluation API",
    description="Taxonomy-driven adversarial evaluation engine for AI agent safety testing",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

fastapi.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all API routers with /api prefix
fastapi.include_router(agent_configs.router, prefix="/api")
fastapi.include_router(templates.router, prefix="/api")
fastapi.include_router(rubrics.router, prefix="/api")
fastapi.include_router(risks.router, prefix="/api")
fastapi.include_router(attacks.router, prefix="/api")
fastapi.include_router(products.router, prefix="/api")
fastapi.include_router(contexts.router, prefix="/api")
fastapi.include_router(configs.router, prefix="/api")
fastapi.include_router(batches.router, prefix="/api")
fastapi.include_router(evals.router, prefix="/api")
fastapi.include_router(prompts.router, prefix="/api")
fastapi.include_router(conversations.router, prefix="/api")
fastapi.include_router(grades.router, prefix="/api")
fastapi.include_router(playground.router, prefix="/api")


@fastapi.get("/", tags=["Health"])
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "AIUC Evaluation API",
        "version": "0.2.0",
    }


@fastapi.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "database": "connected",
        "service": "AIUC Evaluation API",
    }


@app.function(
    image=image,
    secrets=[modal.Secret.from_name("aiuc-secrets")],
)
@modal.asgi_app()
def web():
    """Deploy FastAPI as Modal web endpoint."""
    return fastapi
