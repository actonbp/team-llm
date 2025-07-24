# Multi-Agent System Onboarding Guide

## For Humans Starting Claude Code

### Quick Start Checklist
1. Open terminal in project directory
2. Check existing agent status first:
   ```bash
   ./scripts/agent-status.sh
   ```
3. Start Claude Code
4. The agent will read this guide and initialize itself

### What Claude Code Agent Will Do
1. Read README.md and discover multi-agent system
2. Initialize itself as an agent using `./scripts/init-agent.sh`
3. Check for incomplete work from previous agents
4. Review coordination board and file locks
5. Begin work or complete unfinished tasks

### Recovery Scenarios

#### Scenario 1: Previous Agent Left Mid-Task
**Symptoms**: 
- Files marked as "LOCKED" in conflicts.md
- Agent status shows "In Progress" but timestamp is old
- No recent commits on agent's branch

**Recovery Steps**:
1. Check the agent's last log entries
2. Review their plan.md and handoff.md (even if incomplete)
3. Assess code state with git diff
4. Either continue their work or properly close it out

#### Scenario 2: Computer Shutdown / Agent Termination
**Symptoms**:
- No proper handoff documentation
- Agent workspace exists but no recent updates
- Uncommitted changes in working directory

**Recovery Protocol**:
```bash
# 1. Check for uncommitted work
git status
git diff

# 2. Check agent's last known state
cat .claude-agents/active/agent-*/status.md

# 3. Review their logs for context
cat .claude-agents/active/agent-*/log.md | tail -50

# 4. Decide whether to:
#    a) Continue as same agent (if < 4 hours)
#    b) Create new agent and inherit work
#    c) Commit WIP and start fresh
```

#### Scenario 3: Multiple Interrupted Agents
**Symptoms**:
- Multiple agent directories in active/
- Several branches with incomplete work
- Conflicting approaches in different branches

**Triage Protocol**:
1. Run evaluation script (see below)
2. Prioritize based on completion percentage
3. Merge compatible work
4. Document abandoned approaches

### State Evaluation Tools

Create `./scripts/evaluate-state.sh`:
```bash
#!/bin/bash
# Comprehensive state evaluation for incoming agents

echo "=== CODEBASE STATE EVALUATION ==="
echo

# 1. Check all active agents
echo "Active Agents:"
for agent_dir in .claude-agents/active/*/; do
    if [[ -d "$agent_dir" && "$agent_dir" != *"shared"* ]]; then
        agent_name=$(basename "$agent_dir")
        last_update=$(grep "Last Updated" "$agent_dir/status.md" | cut -d: -f2-)
        status=$(grep "Status" "$agent_dir/status.md" | grep -v "Last" | cut -d: -f2-)
        echo "  - $agent_name: $status (Last: $last_update)"
    fi
done

# 2. Check for uncommitted changes
echo
echo "Repository State:"
echo "  Current branch: $(git branch --show-current)"
echo "  Uncommitted files: $(git status --porcelain | wc -l)"
echo "  Stashed changes: $(git stash list | wc -l)"

# 3. Check for locked files
echo
echo "Locked Files:"
locked_count=$(grep -c "LOCKED" .claude-agents/active/shared/conflicts.md 2>/dev/null || echo "0")
echo "  Total locked: $locked_count"

# 4. Recent activity
echo
echo "Recent Coordination Activity:"
tail -5 .claude-agents/active/shared/coordination.md | grep -E "^### " || echo "  No recent activity"

# 5. Health checks
echo
echo "System Health:"
echo "  ✓ Scripts executable: $(test -x scripts/init-agent.sh && echo "Yes" || echo "No")"
echo "  ✓ Docker running: $(docker ps &>/dev/null && echo "Yes" || echo "No")"
echo "  ✓ Backend reachable: $(curl -s http://localhost:8000/health &>/dev/null && echo "Yes" || echo "No")"
echo "  ✓ Frontend reachable: $(curl -s http://localhost:8080 &>/dev/null && echo "Yes" || echo "No")"
```

### Agent Self-Initialization Protocol

For agents reading this documentation, follow these steps:

1. **Read Core Documentation**:
   ```bash
   # Order of reading:
   # 1. README.md - Project overview
   # 2. CLAUDE.md - Your specific context
   # 3. This file - Onboarding procedures
   # 4. .claude-agents/README.md - Collaboration details
   ```

2. **Evaluate Current State**:
   ```bash
   ./scripts/evaluate-state.sh  # Run state evaluation
   ./scripts/agent-status.sh     # Check other agents
   ```

3. **Decision Tree**:
   ```
   Are there active agents with recent updates (< 2 hours)?
   ├─ YES → Read their status, coordinate if needed
   └─ NO → Are there abandoned tasks?
       ├─ YES → Review and decide to continue or clean up
       └─ NO → Initialize fresh agent for your task
   ```

4. **Initialize Based on Findings**:
   ```bash
   # Case 1: Fresh start
   ./scripts/init-agent.sh <your-purpose>
   
   # Case 2: Continuing abandoned work
   ./scripts/init-agent.sh continue-<previous-agent-purpose>
   # Then document in your log.md that you're continuing previous work
   
   # Case 3: Cleanup needed first
   ./scripts/init-agent.sh cleanup-and-<your-purpose>
   # First clean up, then proceed with main task
   ```

### Best Practices for Resilience

1. **Frequent State Persistence**:
   - Commit work-in-progress at natural breakpoints
   - Update status.md every 15-30 minutes
   - Use descriptive commit messages: "WIP: [agent-id] implementing X, next: Y"

2. **Defensive Coordination**:
   - Always assume you might be interrupted
   - Document decisions immediately in log.md
   - Leave breadcrumbs in code comments: `// AGENT-001: Chose approach X because Y`

3. **Graceful Degradation**:
   - Design changes to be partially functional
   - Avoid large refactors that break everything mid-way
   - Use feature flags when possible

4. **Recovery-Friendly Practices**:
   - Keep changes focused and atomic
   - Write tests as you go (they document intent)
   - Update documentation alongside code

### Common Recovery Patterns

#### Pattern 1: The "Half-Implemented Feature"
```bash
# Previous agent started a new API endpoint but didn't finish
# You find:
# - New route defined but not working
# - Database model partially created
# - No tests

# Recovery:
# 1. Read their plan.md to understand intent
# 2. Check if database migrations were run
# 3. Complete implementation or roll back cleanly
```

#### Pattern 2: The "Broken Build"
```bash
# Previous agent's changes broke tests/build
# Recovery:
# 1. Check their last few commits
# 2. Run tests to identify failures
# 3. Either fix forward or revert problematic commits
# 4. Document in coordination.md
```

#### Pattern 3: The "Conflicting Approaches"
```bash
# Multiple agents tried different solutions
# Recovery:
# 1. Evaluate each approach's completeness
# 2. Choose most promising or combine compatible parts
# 3. Document decision and abandoned approaches
# 4. Clean up unused code/branches
```

### Communication Templates

#### Taking Over Incomplete Work
```markdown
### [TIMESTAMP] - [YOUR-AGENT-ID] - Continuing [PREVIOUS-AGENT-ID]'s Work
**Status**: In Progress
**Found**: [Previous agent]'s work on [feature] was incomplete due to [interruption/shutdown]
**Assessment**: 
- Completed: [what was done]
- Remaining: [what needs to be done]
- Approach: [continuing their approach / pivoting because X]
**ETA**: [time estimate]
```

#### Cleaning Up Abandoned Work
```markdown
### [TIMESTAMP] - [YOUR-AGENT-ID] - Cleanup of Abandoned Tasks
**Status**: In Progress
**Found Multiple Incomplete Tasks**:
1. [agent-001]: [task] - 60% complete, last update [date]
2. [agent-002]: [task] - 30% complete, last update [date]
**Decision**: 
- Salvaging: [what can be used]
- Discarding: [what will be removed]
- Rationale: [why these decisions]
```

### Emergency Procedures

#### If Everything Seems Broken
1. Don't panic - document what you find
2. Check if there's a known-good branch:
   ```bash
   git branch -r | grep stable
   git log --oneline -10  # Look for last known good commit
   ```
3. Consider starting a recovery agent:
   ```bash
   ./scripts/init-agent.sh emergency-recovery
   ```
4. Document everything in coordination.md
5. Focus on getting to a stable state before new features

#### If You're About to Be Interrupted
1. Commit current work immediately:
   ```bash
   git add -A
   git commit -m "WIP: [agent-id] emergency commit - [what you were doing]"
   ```
2. Update status.md with current state
3. Add quick note to handoff.md:
   ```markdown
   ## Emergency Handoff - [TIMESTAMP]
   Was working on: [current task]
   Next step was: [immediate next action]
   Watch out for: [any gotchas]
   ```

### Success Metrics

An agent successfully handles interruption recovery when:
- ✓ No work is lost
- ✓ No duplicate effort occurs
- ✓ Transitions are smooth
- ✓ Code remains stable
- ✓ Documentation stays current
- ✓ Team momentum continues

Remember: The goal is resilient, continuous progress regardless of interruptions!