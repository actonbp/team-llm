# Multi-Agent Collaboration System

This directory facilitates coordination between multiple Claude Code agents working on the same codebase simultaneously.

## ⚠️ CRITICAL WARNING: Agent Identity ⚠️

**The `.current-agent-id` file is SHARED and UNRELIABLE for determining your identity!**

- This file shows whoever LAST ran init-agent.sh, NOT necessarily you
- DO NOT rely on it to know who you are
- Instead, verify your identity by:
  1. Checking your conversation history and assigned work
  2. Looking at your git branch name
  3. Finding YOUR directory in `.claude-agents/active/`
  4. Reading your own status.md file

**If you get confused about your identity, STOP and verify before continuing!**

## Quick Start

1. **Initialize as an agent**: Run `./scripts/init-agent.sh` from the project root
2. **Check active agents**: Run `./scripts/agent-status.sh` to see who's working on what
3. **Start working**: Update your status file regularly as you work
4. **Handoff tasks**: Use `./scripts/agent-handoff.sh` when switching tasks

## Directory Structure

```
.claude-agents/
├── active/                 # Currently active agent sessions
│   ├── agent-{ID}/        # Your agent workspace
│   │   ├── status.md      # Current task and files (UPDATE FREQUENTLY)
│   │   ├── log.md         # Detailed activity log
│   │   ├── plan.md        # Your approach and next steps
│   │   └── handoff.md     # Notes for the next agent
│   └── shared/
│       ├── coordination.md # Cross-agent planning
│       └── conflicts.md    # Track file conflicts
├── completed/             # Archived sessions (auto-moved after 24h inactive)
└── templates/             # Templates for consistency
```

## Agent Protocol

### 1. Starting Work
```bash
# Initialize your agent workspace
./scripts/init-agent.sh [purpose]
# Example: ./scripts/init-agent.sh backend-api
# This creates: agent-001-backend-api/

# WARNING: This updates .current-agent-id globally!
# Other agents may see YOUR ID in that file
# Always verify your identity through other means
```

### 2. Before Starting Any Task
- Read all `active/*/status.md` files
- Check `shared/conflicts.md` for file locks
- Update your `status.md` with intended work

### 3. Status Updates (CRITICAL)
Update your `status.md` every time you:
- Start a new subtask
- Begin editing new files
- Complete a component
- Encounter blockers

Format:
```markdown
# Agent Status: agent-001-backend-api
**Last Updated**: 2024-07-24 14:30:00
**Current Task**: Implementing user authentication endpoints
**Branch**: feature/agent-001-auth
**Files Being Modified**:
- backend/app/api/auth.py (LOCKED)
- backend/app/models/user.py (LOCKED)
**Status**: In Progress
**ETA**: 30 minutes
```

### 4. Coordination
Before making architectural decisions:
1. Check if another agent is working on related components
2. Use `shared/coordination.md` to propose changes
3. Wait for acknowledgment from affected agents

### 5. Handoff Process
When switching tasks or ending session:
1. Run `./scripts/agent-handoff.sh`
2. Document in `handoff.md`:
   - What was completed
   - What remains
   - Any gotchas or decisions made
   - Test results
   - Next recommended steps

## Best Practices

### DO:
- ✅ Update status.md at least every 30 minutes
- ✅ Use descriptive agent IDs (agent-001-frontend, not just agent-001)
- ✅ Check other agents' work before starting
- ✅ Communicate blockers immediately in shared/coordination.md
- ✅ Work on separate git branches
- ✅ Pull latest changes frequently

### DON'T:
- ❌ Modify files another agent has locked
- ❌ Make breaking changes without coordination
- ❌ Leave sessions active when not working
- ❌ Assume other agents know what you're doing

## Git Workflow

### Option 1: Branch per Agent (Recommended)
```bash
git checkout -b feature/agent-001-auth
# Work on your branch
git push origin feature/agent-001-auth
```

### Option 2: Git Worktrees (Advanced)
```bash
# Create a separate worktree for your agent
git worktree add ../team-llm-agent-001 feature/agent-001-auth
cd ../team-llm-agent-001
./scripts/init-agent.sh auth
```

## Handling Conflicts

If two agents need the same file:
1. Check who has it locked in their status.md
2. Coordinate in shared/coordination.md
3. Options:
   - Wait for the other agent
   - Split the work differently
   - Pair on the task (update both status files)

## Example Workflows

### Parallel Development
- Agent-001: Working on backend API endpoints
- Agent-002: Building frontend components
- Agent-003: Writing tests
- Agent-004: Updating documentation

### Sequential Handoff
1. Agent-001: Designs database schema → handoff.md
2. Agent-002: Implements models based on schema → handoff.md
3. Agent-003: Builds API endpoints → handoff.md
4. Agent-004: Creates frontend integration

### Pair Programming
- Both agents update status.md with same files
- Use shared/coordination.md for decisions
- Alternate who makes commits
- Document thought process in respective log.md

## Troubleshooting

**Q: I'm confused about which agent I am**
A: DO NOT trust .current-agent-id! Check:
   1. Your conversation history - what work were you assigned?
   2. Your git branch: `git branch --show-current`
   3. Find your directory: `ls -la .claude-agents/active/`
   4. Read your status.md to confirm your work

**Q: I accidentally started working on another agent's tasks**
A: Stop immediately! 
   1. Save your work: `git diff > wrong-work.patch`
   2. Reset changes: `git checkout -- .`
   3. Document in coordination.md
   4. Return to your assigned work

**Q: Another agent has locked the files I need**
A: Check their ETA in status.md, coordinate in shared/coordination.md

**Q: I don't see other agents' updates**
A: Git pull and check you're reading active/ directory

**Q: How do I know what other agents have done?**
A: Read their log.md files and check git log for their branches

**Q: Can I work on multiple tasks?**
A: Yes, but update status.md to list all active tasks and files

## Scripts Reference

- `init-agent.sh [purpose]` - Initialize agent workspace
- `agent-status.sh` - View all active agents and their tasks
- `agent-handoff.sh` - Prepare handoff documentation
- `agent-cleanup.sh` - Archive inactive sessions
- `agent-conflicts.sh` - Check for file conflicts

Remember: **Communication is key!** When in doubt, over-communicate in your status.md and shared/coordination.md files.