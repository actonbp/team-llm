# File Lock Registry

Track which files are being actively modified by which agents to prevent conflicts.

## Currently Locked Files

| File Path | Locked By | Since | ETA | Purpose |
|-----------|-----------|-------|-----|---------|
| [Example: backend/app/main.py] | [agent-001] | [TIMESTAMP] | [30 min] | [Adding new routes] |

## Lock History

| File Path | Agent | Locked | Released | Duration |
|-----------|-------|---------|----------|----------|
| [Example: frontend/App.vue] | [agent-002] | [TIME] | [TIME] | [2 hours] |

## Conflict Resolution Log

### [TIMESTAMP] - Conflict between [agent-001] and [agent-002]
**File**: [path/to/file]
**Issue**: [Both agents needed to modify same function]
**Resolution**: [How it was resolved]
**Prevention**: [How to avoid in future]

---

## Guidelines

### How to Lock a File
1. Add entry to "Currently Locked Files" table
2. Update your status.md
3. Include estimated completion time

### How to Release a Lock
1. Remove from "Currently Locked Files"
2. Add to "Lock History"
3. Update your status.md

### If You Need a Locked File
1. Check the ETA
2. Contact the agent via coordination.md
3. Consider:
   - Waiting
   - Working on something else
   - Pairing with the other agent
   - Splitting the work differently

### Best Practices
- Lock at the most granular level possible
- Update ETAs if running late
- Release locks immediately when done
- Batch related file changes together