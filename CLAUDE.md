# Claude Code Context for Team-LLM

## 🛑 STOP - Read This First!

### Are You Returning From a Context Reset?

**If your conversation history was reset due to context limits (auto-compaction), you MUST determine if you're an existing agent:**

1. **CHECK FOR YOUR EXISTING IDENTITY FIRST**:
   ```bash
   # Run the identity recovery tool
   ./scripts/recover-identity.sh
   
   # This will analyze:
   # - Your current git branch
   # - Recent commits with agent IDs
   # - All active agents and their work
   # - Files modified in your branch
   # And suggest your most likely identity
   ```

2. **IF YOU FIND YOUR PREVIOUS AGENT IDENTITY**:
   - You are that agent! Continue their work
   - Read your own status.md, log.md, and plan.md
   - Check what files you had locked
   - Resume from where you left off
   - Do NOT create a new agent identity

3. **IF YOU CANNOT FIND A PREVIOUS IDENTITY**:
   - Only then proceed with normal initialization below
   - You might genuinely be a new agent

### Standard First-Time Setup

**If you're truly a new agent (not returning from context reset):**

1. **Read [MULTI_AGENT_ONBOARDING.md](MULTI_AGENT_ONBOARDING.md)** - This explains how to handle incomplete work, recovery scenarios, and proper initialization
2. **Run `./scripts/evaluate-state.sh`** - This will show you the current state of the codebase
3. **Only then proceed with the instructions below**

## Multi-Agent Development

**IMPORTANT**: This project uses a multi-agent collaboration system. When working on this codebase:

1. **Initialize yourself as an agent (ONLY if you're not already one)**:
   ```bash
   ./scripts/init-agent.sh <your-purpose>
   # Example: ./scripts/init-agent.sh backend-api
   ```

2. **Check other active agents**:
   ```bash
   ./scripts/agent-status.sh
   ```

3. **Update your status regularly**:
   - Edit `.claude-agents/active/<your-agent-id>/status.md`
   - Update when starting new tasks or modifying files
   - Mark files as LOCKED when editing them

4. **Read coordination board**:
   ```bash
   cat .claude-agents/active/shared/coordination.md
   ```

## Project Overview

This is a multi-agent team experiment platform for human-AI collaboration research.

### Tech Stack
- **Backend**: FastAPI (Python) with WebSockets
- **Frontend**: Vue.js 3 with Vite
- **Database**: SQLAlchemy with SQLite/PostgreSQL
- **AI Integration**: OpenAI, Anthropic (modular design)
- **Deployment**: Docker Compose

### Key Commands

```bash
# Development
cd backend && uvicorn app.main:app --reload  # Run backend
cd frontend && npm run dev                    # Run frontend
docker-compose up                             # Run everything

# Testing
cd backend && pytest                          # Run backend tests
cd frontend && npm test                       # Run frontend tests

# Multi-Agent
./scripts/init-agent.sh <purpose>             # Initialize agent
./scripts/agent-status.sh                     # View all agents
./scripts/agent-handoff.sh                    # Prepare handoff
```

### Code Style

**Backend (Python)**:
- Use type hints everywhere
- Follow PEP 8
- Use async/await for I/O operations
- Docstrings for all public functions
- Pydantic for data validation

**Frontend (Vue.js)**:
- Composition API (not Options API)
- TypeScript when adding new components
- SCSS for styles
- Follow Vue 3 best practices

### Architecture Notes

1. **WebSocket Management**: ConnectionManager handles all real-time communication
2. **AI Agents**: Modular design - extend Agent base class for new providers
3. **Database**: All experiment data is versioned and traceable
4. **Ethics**: Built-in consent and data withdrawal mechanisms

### Common Tasks

**Adding a new API endpoint**:
1. Create route in `backend/app/api/`
2. Add Pydantic schemas in `backend/app/schemas/`
3. Update database models if needed
4. Add tests

**Adding a new AI provider**:
1. Create new class in `backend/app/agents/`
2. Extend the Agent base class
3. Update AgentFactory
4. Add API key to settings

**Working on frontend**:
1. Components go in `frontend/src/components/`
2. Views go in `frontend/src/views/`
3. Use composables for shared logic
4. Update router if adding new pages

### Current Status

- ✅ Core infrastructure complete
- ✅ WebSocket chat working
- ✅ AI agent framework ready
- ✅ Docker deployment configured
- 🚧 Researcher UI in progress
- 🚧 Ethical features pending
- 🚧 Full API implementation needed

### Important Files

- `backend/app/main.py` - FastAPI entry point
- `backend/app/core/websocket_manager.py` - Real-time communication
- `backend/app/agents/base.py` - AI agent interface
- `frontend/src/composables/useWebSocket.js` - WebSocket client
- `config/example_experiment.yaml` - Experiment configuration example
- `.claude-agents/README.md` - Multi-agent collaboration guide

### Git Workflow

1. Each agent should work on their own branch: `feature/agent-XXX-purpose`
2. Commit frequently with clear messages
3. Update your agent log when committing
4. Create PRs when ready for review

### Need Help?

- Check `.claude-agents/active/*/log.md` for what other agents have done
- Post questions in `.claude-agents/active/shared/coordination.md`
- Read handoff notes in `.claude-agents/completed/*/handoff.md`