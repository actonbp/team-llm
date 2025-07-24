"""
Test configuration and fixtures
"""
import asyncio
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator, Generator
from app.db.database import Base
from app.main import app
from fastapi.testclient import TestClient


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def async_engine():
    """Create an async database engine for testing"""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        future=True
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    await engine.dispose()


@pytest_asyncio.fixture
async def async_session(async_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create an async database session for testing"""
    async_session_maker = async_sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async with async_session_maker() as session:
        yield session


@pytest.fixture
def client(async_session) -> TestClient:
    """Create a test client"""
    from app.db.database import get_db
    
    async def override_get_db():
        yield async_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def sample_experiment_yaml():
    """Sample experiment YAML configuration"""
    return """
experimentName: "Trust Building Exercise"
description: "A collaborative problem-solving task to study trust dynamics"
version: 1
roles:
  - name: "Human Participant"
    type: "human"
    instructions: "Work with your partner to solve the puzzle"
  - name: "AI Assistant"
    type: "AI"
    model: "gpt-4"
    persona: "You are a helpful and collaborative partner"
    knowledge:
      domain: "general problem solving"
    strategy: "Be supportive and encouraging"
scenario:
  type: "puzzle"
  duration: 600
  completionTrigger:
    type: "manual"
    value: "task-complete"
conditions:
  - id: "baseline"
    name: "Baseline Condition"
    description: "Standard AI behavior"
    variables:
      ai_responsiveness: "normal"
  - id: "high-trust"
    name: "High Trust Condition"
    description: "AI demonstrates high trustworthiness"
    variables:
      ai_responsiveness: "high"
      ai_transparency: true
"""


@pytest.fixture
def sample_experiment_data():
    """Sample experiment data for testing"""
    return {
        "name": "Test Experiment",
        "description": "Test experiment description",
        "version": 1,
        "config": {
            "experimentName": "Test Experiment",
            "description": "Test experiment description",
            "version": 1,
            "roles": [
                {
                    "name": "Human Participant",
                    "type": "human",
                    "instructions": "Test instructions"
                }
            ],
            "scenario": {
                "type": "test",
                "duration": 300
            },
            "conditions": [
                {
                    "id": "test-condition",
                    "name": "Test Condition",
                    "description": "Test condition description"
                }
            ]
        }
    }


@pytest.fixture
def auth_headers():
    """Authorization headers for protected endpoints"""
    return {"Authorization": "Bearer test-token"}