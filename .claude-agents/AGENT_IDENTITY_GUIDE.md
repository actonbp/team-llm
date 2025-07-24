# Agent Identity Guide - CRITICAL READING

## The Identity Confusion Problem

The `.current-agent-id` file is **GLOBAL** and **UNRELIABLE**. It changes every time ANY agent runs `init-agent.sh`, causing confusion about which agent you are.

## How to ALWAYS Know Who You Are

### 1. Remember Your Assignment
- What work were you assigned to do?
- Backend = likely agent-950
- Frontend = likely agent-830
- Testing = likely agent-XXX-tests

### 2. Check Your Git Branch
```bash
git branch --show-current
# Should show: feature/agent-XXX-purpose
# The XXX is YOUR agent ID
```

### 3. Find YOUR Directory
```bash
ls -la .claude-agents/active/agent-*/
# Look for the directory with YOUR work in status.md
```

### 4. Check Your Previous Commits
```bash
git log --oneline --author=agent -5
# Look for commits with YOUR agent ID
```

## Red Flags That You're Confused

🚨 **STOP if you notice:**
- You're suddenly working on completely different technology (backend → frontend)
- Your "status.md" doesn't match work you remember doing
- You're creating files in a domain you weren't assigned
- The .current-agent-id shows a different ID than expected

## What To Do If Confused

1. **STOP IMMEDIATELY** - Don't commit!

2. **Save Any Work**:
   ```bash
   git stash save "Possible wrong-agent work"
   ```

3. **Verify Your Identity** using methods above

4. **Check Coordination Board**:
   ```bash
   grep -B5 -A5 "your-work" .claude-agents/active/shared/coordination.md
   ```

5. **Return to YOUR Work**:
   ```bash
   cd your-correct-directory
   git checkout your-correct-branch
   ```

## Example of Identity Confusion

**What Happened**: Agent-950 (backend) saw `.current-agent-id` showing "agent-830-frontend-dashboard" and started building Vue components instead of working on WebSockets.

**Why It Happened**: Agent-830 had run `init-agent.sh`, updating the global file.

**The Fix**: Always verify identity through multiple sources, never trust just one file.

## Prevention Checklist

Before starting ANY work session:
- [ ] Check your git branch matches your agent ID
- [ ] Verify your agent directory exists
- [ ] Read YOUR status.md to confirm your assignment  
- [ ] Ignore .current-agent-id or treat it skeptically
- [ ] If anything seems wrong, STOP and verify

## Remember

Your identity is determined by:
- ✅ Your assigned work and conversation history
- ✅ Your git branch name
- ✅ Your agent directory in .claude-agents/active/
- ❌ NOT by .current-agent-id (unreliable!)

When in doubt, trace back through your conversation history to find your original assignment.