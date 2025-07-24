"""
Main FastAPI application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.api import experiments, sessions, participants, websocket
from app.core.config import settings
from app.db.database import create_db_and_tables

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown"""
    # Startup
    logger.info("Starting up Team-LLM platform...")
    await create_db_and_tables()
    yield
    # Shutdown
    logger.info("Shutting down Team-LLM platform...")


# Create FastAPI app
app = FastAPI(
    title="Team-LLM Platform",
    description="Multi-Agent Team Experiment Platform for Human-AI Collaboration Research",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(experiments.router, prefix="/api/experiments", tags=["experiments"])
app.include_router(sessions.router, prefix="/api/sessions", tags=["sessions"])
app.include_router(participants.router, prefix="/api/participants", tags=["participants"])
app.include_router(websocket.router, prefix="/ws", tags=["websocket"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Team-LLM Platform",
        "version": "1.0.0",
        "docs": "/docs",
        "researcher_ui": "http://localhost:8080",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "team-llm-backend"}