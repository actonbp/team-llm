# Merge Plan for Team-LLM Main Branch

## Current State Analysis

### Original Vision vs. Implementation

**Original Vision:**
- Multi-agent experiment platform
- Support ANY mix of humans and AI (not just 3 AI + 1 human)
- Configurable tasks (not hardcoded restaurant scenario)
- Real-time WebSocket communication
- Easy deployment for researchers
- Multiple experimental conditions

**What Was Built:**
1. **Backend (agent-950)**: ✅ Complete infrastructure with APIs, WebSocket, mock agents
2. **Frontend (agent-830)**: 🚧 70% complete - functional dashboard, missing participant UI
3. **AI Conversation (agent-799)**: ✅ Natural conversation logic implemented
4. **Testing (agent-427)**: ✅ Comprehensive test suite created

### Critical Issues Fixed
- ✅ SQLAlchemy 2.0 compatibility (metadata → extra_data)
- ✅ Database models now work properly

## Merge Strategy

### Phase 1: Core Fixes (Already Done on Main)
- ✅ SQLAlchemy v2.0 fix
- ✅ Rename metadata column to extra_data

### Phase 2: Essential Features to Merge

1. **From agent-799 (AI Conversation)**:
   - `scripts/run_ai_simulation.py` - Main AI simulation script
   - `scripts/restaurant_task_config.py` - Task configuration
   - Natural conversation logic implementation

2. **From agent-427 (Testing)**:
   - Test scripts for validation
   - `backend/scripts/test_ai_simulation_minimal.py`
   - Documentation improvements

3. **From agent-950 (Backend)**:
   - Mock agent implementation
   - WebSocket improvements
   - API completeness

4. **From agent-830 (Frontend)**:
   - Dashboard components
   - Session monitoring UI
   - WebSocket integration

### Phase 3: Configuration System (Missing!)

**Gap Analysis**: The original vision required configurable experiments, but current implementation has hardcoded restaurant task.

**Needed:**
```yaml
# config/experiments/restaurant_ranking.yaml
experiment:
  name: "Restaurant Location Ranking"
  task_type: "ranking"
  participants:
    min: 1
    max: 6
    allow_ai: true
    allow_human: true
  
  agents:
    - name: "Alex"
      model: "gpt-4"
      persona: "analytical"
      knowledge: {...}
```

### Phase 4: Multi-Human Support (Missing!)

Current system only supports single human + AI agents. Need to add:
- Waiting room for multiple humans
- Session management for mixed teams
- Proper turn-taking for multiple humans

## Recommended Approach

1. **Immediate**: Test AI simulation with current fixes
2. **Next**: Cherry-pick essential features from each branch
3. **Then**: Add configuration system
4. **Finally**: Implement multi-human support

## Commands to Execute

```bash
# Test current state
cd backend && python scripts/run_ai_simulation.py

# Cherry-pick essential features
git cherry-pick <specific commits>

# Or selective merge
git checkout feature/agent-799-ai-conversation-implementation -- scripts/
```

## Success Criteria

- [ ] AI agents can have natural conversations
- [ ] Backend starts without errors
- [ ] Frontend shows experiment dashboard
- [ ] Tests pass
- [ ] Configuration system allows new experiments
- [ ] Multiple humans can join same session