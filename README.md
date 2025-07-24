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

## 🚧 Current Status (July 2025)

**Infrastructure: ✅ WORKING** | **AI Conversation: ❌ NOT IMPLEMENTED**

- All backend APIs functional (experiments, sessions, participants)
- WebSocket connections working at `/ws/chat/{session_id}`
- 4 AI agents can join sessions successfully
- **Missing**: Conversation logic - agents connect but don't talk

**Quick Test**: `python scripts/test-ai-agents.py`

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

## Quick Start

```bash
# Clone the repository
git clone https://github.com/actonbp/team-llm.git
cd team-llm

# Start with Docker Compose
docker-compose up

# Access the application
# Researcher Command Center: http://localhost:8080
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