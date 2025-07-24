# Team-LLM Quick Start Guide

## 🧪 Testing Phase Notice

The Team-LLM platform is currently in **testing phase** with the goal of running all-AI agent simulations. This guide will help you get a minimal test environment running quickly.

## Prerequisites

- Python 3.8+
- Node.js 16+ (only if testing frontend)
- Git

## Fastest Path: All-AI Simulation

### 1. Clone and Setup (2 minutes)

```bash
# Clone repository
git clone https://github.com/actonbp/team-llm.git
cd team-llm

# Set up backend
cd backend
cp .env.example .env
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Initialize Database (1 minute)

```bash
# Still in backend directory
python -c "from app.db.database import Base, engine; import asyncio; asyncio.run(Base.metadata.create_all(engine))"
```

### 3. Start Backend Server

```bash
uvicorn app.main:app --reload
```

Keep this terminal open. The server is now running at http://localhost:8000

### 4. Run AI Simulation (New Terminal)

```bash
cd team-llm/backend
source venv/bin/activate  # Windows: venv\Scripts\activate
python scripts/run_ai_simulation.py
```

You should see:
- ✅ Experiment created
- ✅ Session created with access code
- ✅ AI agents joining and chatting
- 🤖 Live conversation between AI agents
- ✅ Task completion

## What's Happening?

The simulation:
1. Creates an experiment with 3 mock AI agents
2. Each agent has unique knowledge about a restaurant
3. They collaborate to rank the restaurants
4. One eventually says "task-complete" to end the session

## Testing Other Features

### API Documentation
Visit http://localhost:8000/docs for interactive API documentation

### Manual API Testing

```bash
# Create experiment
curl -X POST http://localhost:8000/api/experiments/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Test", "description": "Test experiment", "version": 1, "config": {}}'

# List experiments
curl http://localhost:8000/api/experiments/
```

### WebSocket Testing
Use the API docs to create a session, then connect via WebSocket:
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/session/SESSION_ID?participant_id=PARTICIPANT_ID');
```

## Mock vs Real AI Agents

Currently using **mock agents** that:
- Simulate realistic AI behavior
- Don't require API keys
- Add occasional typos for realism
- Respond based on their configured knowledge

To use real AI agents:
1. Add API keys to `.env`
2. Change `model: "mock"` to `model: "openai/gpt-4"` or `model: "anthropic/claude-3"`

## Troubleshooting

### "Module not found" errors
```bash
pip install -r requirements.txt --upgrade
```

### Database errors
```bash
rm team_llm.db  # Delete existing database
# Re-run initialization
```

### Port already in use
```bash
# Kill existing process or use different port
uvicorn app.main:app --reload --port 8001
```

## Next Steps

1. **Modify the test scenario**: Edit `backend/scripts/run_ai_simulation.py`
2. **Create custom experiments**: Use the `/api/experiments/import` endpoint
3. **Add more AI agents**: Extend the roles in your experiment config
4. **Test the frontend**: Run `npm install && npm run dev` in the frontend directory

## Current Limitations

- Frontend is 70% complete (missing participant management UI)
- No authentication implemented yet
- Mock agents have simple behavior patterns
- WebSocket reconnection not implemented

## Questions?

- Check API docs: http://localhost:8000/docs
- Review code: Backend is fully functional
- Experiment with different scenarios in the simulation script