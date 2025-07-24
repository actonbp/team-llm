# Team-LLM Testing Plan

## Current State Analysis

### ✅ What's Complete
1. **Backend Infrastructure (100%)**
   - All database models (Experiment, Session, Participant, Message, Ethics)
   - Full CRUD APIs (Experiments, Sessions, Participants)
   - WebSocket real-time communication
   - AI agent integration framework
   - Comprehensive test suite

2. **Frontend (70%)**
   - Experiment management UI
   - Session monitoring dashboard
   - WebSocket integration
   - Missing: Participant management UI

3. **AI Agents**
   - Base framework complete
   - OpenAI and Anthropic agent classes exist
   - BUT: Require actual API keys to function

### 🚧 What's Missing for Testing

1. **Environment Setup**
   - No `.env` file configured
   - No database created/migrated
   - No API keys for AI providers

2. **Mock AI Agents**
   - Need mock agents for testing without API keys
   - Simulate AI behavior locally

3. **Running Services**
   - Backend server not running
   - Frontend dev server not running
   - Database not initialized

## Minimal Testing Path

### Option 1: Mock AI Simulation (Recommended for Quick Testing)
```bash
# 1. Set up environment
cd backend
cp .env.example .env  # Create if doesn't exist
# Edit .env with minimal config

# 2. Initialize database
python -m alembic init alembic
python -m alembic revision --autogenerate -m "Initial migration"
python -m alembic upgrade head

# 3. Create mock AI agent
# Implement MockAgent class

# 4. Run backend
uvicorn app.main:app --reload

# 5. Test with curl/API
# Create experiment, session, join with AI agents
```

### Option 2: Full Stack Testing
```bash
# 1. Backend setup (as above)
# 2. Frontend setup
cd frontend
npm install
npm run dev

# 3. Access UI at http://localhost:5173
# 4. Create experiment via UI
# 5. Start session and monitor
```

### Option 3: All-AI Simulation Script
```python
# Create a Python script that:
# 1. Creates an experiment
# 2. Creates a session
# 3. Spawns multiple AI agents
# 4. Has them chat until task completion
# 5. Logs the conversation
```

## Test Scenarios

### 1. Basic Connectivity Test
- Create experiment via API
- Create session
- Connect via WebSocket
- Send messages

### 2. Multi-Agent Chat
- 3-4 AI agents
- Simple collaborative task
- Test message flow and responses

### 3. Task Completion Flow
- AI agents work toward goal
- One triggers task-complete
- Session ends properly

### 4. Ethics & Consent
- Test consent flow
- Data withdrawal
- Ethics logging

## Next Steps Priority

1. **Create `.env` file** with minimal config
2. **Initialize SQLite database** (no PostgreSQL needed for testing)
3. **Implement MockAgent** for local testing
4. **Create simple test experiment YAML**
5. **Write all-AI simulation script**
6. **Run end-to-end test**

## Example Test Experiment YAML

```yaml
experimentName: "AI Team Test"
description: "Simple ranking task for AI agents"
version: 1
roles:
  - name: "Alice"
    type: "AI"
    model: "mock"
    persona: "You are helpful and analytical"
    knowledge:
      Restaurant A: 
        food_quality: "excellent"
        price: "expensive"
  - name: "Bob"
    type: "AI"
    model: "mock"
    persona: "You are practical and budget-conscious"
    knowledge:
      Restaurant B:
        food_quality: "good"
        price: "affordable"
  - name: "Charlie"
    type: "AI"
    model: "mock"
    persona: "You are a food enthusiast"
    knowledge:
      Restaurant C:
        food_quality: "authentic"
        atmosphere: "cozy"
scenario:
  type: "ranking"
  duration: 300
  task: "Rank the three restaurants from best to worst"
  completionTrigger:
    type: "keyword"
    value: "task-complete"
conditions:
  - id: "test"
    name: "Test Condition"
    description: "Basic test setup"
```

## Questions to Address

1. Do we want to test with real AI APIs or mock agents first?
2. Should we use SQLite for testing or set up PostgreSQL?
3. Do we need the frontend for initial testing or just API/WebSocket?
4. What's the simplest collaborative task for testing?