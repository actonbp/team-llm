# Team-LLM: Multi-Agent Team Experiment Platform

A flexible, researcher-friendly platform for conducting experiments with teams composed of humans and AI agents. Built with experimental rigor, ethical integrity, and operational simplicity at its core.

## 🤖 For Claude Code Users - Start Here!

This project uses a **multi-agent collaboration system**. If you're using Claude Code:

1. **First Time?** Read [MULTI_AGENT_ONBOARDING.md](MULTI_AGENT_ONBOARDING.md)
2. **Check Current State**: 
   ```bash
   ./scripts/evaluate-state.sh    # See what's happening
   ./scripts/agent-status.sh      # View active agents
   ```
3. **Start Working**:
   ```bash
   ./scripts/init-agent.sh <your-purpose>
   # Example: ./scripts/init-agent.sh backend-api
   ```

## Overview

This platform enables researchers to:
- Run experiments with any combination of human and AI participants
- Configure complex experimental conditions without coding
- Ensure ethical compliance with built-in consent and data withdrawal mechanisms
- Deploy experiments easily with Docker containerization

## Architecture

### Backend (FastAPI + Python)
- Real-time WebSocket communication
- Modular AI agent framework supporting multiple LLM providers
- Structured database with comprehensive experiment tracking
- RESTful API for experiment management

### Frontend (Vue.js)
- Researcher Command Center for experiment design and monitoring
- Participant interface with ethical safeguards
- Real-time chat with WebSocket support
- Responsive, accessible design

### Key Features
- **Flexible Team Configurations**: Support for all-human, mixed human-AI, or all-AI teams
- **Experimental Rigor**: Version-controlled experiments with complete reproducibility
- **Ethical Design**: Multi-stage consent process, debriefing, and data withdrawal
- **Easy Deployment**: One-command Docker deployment for non-technical researchers

## Project Structure

```
team-llm/
├── backend/          # FastAPI application
│   ├── app/          # Main application code
│   ├── models/       # Database models
│   ├── agents/       # AI agent implementations
│   ├── api/          # API endpoints
│   └── core/         # Core functionality
├── frontend/         # Vue.js application
│   ├── src/          # Source code
│   ├── public/       # Static assets
│   └── dist/         # Build output
├── database/         # Database schemas and migrations
├── config/           # Experiment configuration files
├── docker/           # Docker configuration
├── docs/             # Documentation
└── tests/            # Test suites
```

## 🧪 Current Status: Testing Phase

**The platform is in active testing phase.** Core functionality is complete:
- ✅ Backend APIs (100% complete)
- ✅ WebSocket real-time communication
- ✅ AI agent integration framework
- ✅ Database models and ethics tracking
- 🚧 Frontend UI (70% complete)

**Ready for Testing:** All-AI agent simulations can be run locally without requiring actual LLM API keys using our mock agent system.

## Quick Start (Testing Mode)

### Option 1: All-AI Simulation (Recommended for Testing)

```bash
# 1. Set up backend environment
cd backend
cp .env.example .env  # Uses SQLite by default, no setup needed
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. Initialize database
python -m alembic init alembic
python -m alembic revision --autogenerate -m "Initial migration"
python -m alembic upgrade head

# 3. Start backend server
uvicorn app.main:app --reload

# 4. Run all-AI simulation (in another terminal)
cd backend
python scripts/run_ai_simulation.py

# Access API documentation: http://localhost:8000/docs
```

### Option 2: Full Stack Testing (Requires Frontend)

```bash
# Start backend (as above)

# In another terminal, start frontend
cd frontend
npm install
npm run dev

# Access the application
# Researcher Dashboard: http://localhost:5173
# API Documentation: http://localhost:8000/docs
```

## Development Setup

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Configuration

Experiments are configured using YAML files in the `config/` directory. Example:

```yaml
experimentName: "AI Teammate Detection Study"
scenario:
  instructions: "Your team must rank three potential restaurant locations..."
  completionTrigger:
    type: "keyword"
    value: "task-complete"
roles:
  - name: "Participant"
    type: "HUMAN"
  - name: "Assistant"
    type: "AI"
    model: "openai/gpt-4"
    persona: "You are a helpful, analytical teammate..."
```

## Development with Claude Code (Multi-Agent Architecture)

This project supports collaborative development using multiple Claude Code agents working simultaneously. If you're using Claude Code, we recommend leveraging our multi-agent coordination system.

### Multi-Agent Setup

```bash
# Initialize as an agent
./scripts/init-agent.sh <purpose>
# Example: ./scripts/init-agent.sh backend-api

# Check active agents
./scripts/agent-status.sh

# Prepare handoff when switching tasks
./scripts/agent-handoff.sh
```

### Coordination System

The `.claude-agents/` directory facilitates communication between multiple agents:
- **Active agents** track their work in `active/agent-{ID}/`
- **Shared coordination** happens in `active/shared/`
- **File locking** prevents conflicts
- **Handoff notes** enable smooth task transitions

See [.claude-agents/README.md](.claude-agents/README.md) for detailed multi-agent collaboration guidelines.

### Best Practices for Multi-Agent Development

1. **Initialize your agent workspace** before starting any work
2. **Check other agents' status** to avoid conflicts
3. **Update your status regularly** (at least every 30 minutes)
4. **Lock files** you're actively modifying
5. **Use separate git branches** per agent
6. **Document decisions** in coordination.md
7. **Prepare handoff notes** when switching tasks

### Example Multi-Agent Workflows

**Parallel Development:**
- Agent-001: Implements backend endpoints
- Agent-002: Builds frontend components  
- Agent-003: Writes tests
- Agent-004: Updates documentation

**Sequential Handoff:**
- Agent-001: Designs schema → Agent-002: Implements models → Agent-003: Creates API

## Contributing

Please read [CONTRIBUTING.md](docs/CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

Built upon insights from the original AI Team App and extensive research into human-AI collaboration.