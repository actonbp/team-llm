#!/bin/bash

# Comprehensive state evaluation for incoming agents
# This script helps new agents understand the current state of the codebase

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}           CODEBASE STATE EVALUATION                    ${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo

# 1. Check all active agents
echo -e "${CYAN}Active Agents:${NC}"
agent_count=0
for agent_dir in .claude-agents/active/*/; do
    if [[ -d "$agent_dir" && "$agent_dir" != *"shared"* ]]; then
        agent_name=$(basename "$agent_dir")
        if [[ -f "$agent_dir/status.md" ]]; then
            last_update=$(grep "Last Updated" "$agent_dir/status.md" 2>/dev/null | head -1 | sed 's/.*: //')
            status=$(grep -E "^\*\*Status\*\*:" "$agent_dir/status.md" 2>/dev/null | head -1 | sed 's/.*: //')
            current_task=$(grep "Current Task" "$agent_dir/status.md" 2>/dev/null | head -1 | sed 's/.*: //')
            
            # Calculate time since last update
            if [[ ! -z "$last_update" ]]; then
                # This is simplified - in production you'd calculate actual time difference
                echo -e "  ${YELLOW}$agent_name${NC}"
                echo "    Status: $status"
                echo "    Task: $current_task"
                echo "    Last Update: $last_update"
            fi
            ((agent_count++))
        fi
    fi
done

if [[ $agent_count -eq 0 ]]; then
    echo -e "  ${GREEN}No active agents found${NC}"
fi

# 2. Check for uncommitted changes
echo
echo -e "${CYAN}Repository State:${NC}"
current_branch=$(git branch --show-current 2>/dev/null || echo "unknown")
uncommitted_count=$(git status --porcelain 2>/dev/null | wc -l | tr -d ' ')
stash_count=$(git stash list 2>/dev/null | wc -l | tr -d ' ')
unpushed_count=$(git log origin/$current_branch..$current_branch --oneline 2>/dev/null | wc -l | tr -d ' ')

echo "  Current branch: $current_branch"
echo -e "  Uncommitted files: ${uncommitted_count:-0} $([ ${uncommitted_count:-0} -gt 0 ] && echo -e "${RED}(needs attention)${NC}")"
echo "  Stashed changes: ${stash_count:-0}"
echo "  Unpushed commits: ${unpushed_count:-0}"

# Show uncommitted files if any
if [[ ${uncommitted_count:-0} -gt 0 ]]; then
    echo -e "  ${YELLOW}Modified files:${NC}"
    git status --porcelain | head -5 | sed 's/^/    /'
    if [[ $uncommitted_count -gt 5 ]]; then
        echo "    ... and $((uncommitted_count - 5)) more"
    fi
fi

# 3. Check for locked files
echo
echo -e "${CYAN}File Lock Status:${NC}"
if [[ -f ".claude-agents/active/shared/conflicts.md" ]]; then
    # Count locked files more accurately
    locked_files=$(awk '/Currently Locked Files/,/Lock History/' .claude-agents/active/shared/conflicts.md | grep -E "^\|" | grep -v "File Path" | grep -v "^|--" | grep -v "^$")
    locked_count=$(echo "$locked_files" | grep -c "." 2>/dev/null || echo "0")
    
    if [[ $locked_count -gt 0 ]]; then
        echo -e "  ${RED}⚠️  $locked_count files currently locked:${NC}"
        echo "$locked_files" | head -3 | sed 's/^/    /'
        if [[ $locked_count -gt 3 ]]; then
            echo "    ... and $((locked_count - 3)) more"
        fi
    else
        echo -e "  ${GREEN}✓ No files currently locked${NC}"
    fi
else
    echo "  No conflict tracking file found"
fi

# 4. Recent activity
echo
echo -e "${CYAN}Recent Coordination Activity:${NC}"
if [[ -f ".claude-agents/active/shared/coordination.md" ]]; then
    recent_activity=$(tail -20 .claude-agents/active/shared/coordination.md | grep -E "^### " | tail -3)
    if [[ ! -z "$recent_activity" ]]; then
        echo "$recent_activity" | sed 's/^/  /'
    else
        echo "  No recent activity recorded"
    fi
else
    echo "  No coordination board found"
fi

# 5. Check for abandoned work (agents not updated in >2 hours)
echo
echo -e "${CYAN}Potentially Abandoned Work:${NC}"
abandoned_count=0
for agent_dir in .claude-agents/active/*/; do
    if [[ -d "$agent_dir" && "$agent_dir" != *"shared"* ]]; then
        agent_name=$(basename "$agent_dir")
        if [[ -f "$agent_dir/status.md" ]]; then
            # In a real implementation, we'd check actual timestamps
            # For now, we'll flag any agent with old-looking timestamps
            status=$(grep -E "^\*\*Status\*\*:" "$agent_dir/status.md" 2>/dev/null | head -1)
            if [[ "$status" == *"In Progress"* ]]; then
                echo -e "  ${YELLOW}⚠️  $agent_name may need attention${NC}"
                ((abandoned_count++))
            fi
        fi
    fi
done

if [[ $abandoned_count -eq 0 ]]; then
    echo -e "  ${GREEN}✓ No obviously abandoned work${NC}"
fi

# 6. System health checks
echo
echo -e "${CYAN}System Health:${NC}"

# Check if scripts are executable
scripts_ok=true
for script in init-agent.sh agent-status.sh agent-handoff.sh; do
    if [[ ! -x "scripts/$script" ]]; then
        scripts_ok=false
        break
    fi
done
echo -e "  Scripts executable: $([ "$scripts_ok" = true ] && echo -e "${GREEN}✓ Yes${NC}" || echo -e "${RED}✗ No${NC}")"

# Check Docker
docker_running=$(docker ps &>/dev/null && echo "true" || echo "false")
echo -e "  Docker running: $([ "$docker_running" = "true" ] && echo -e "${GREEN}✓ Yes${NC}" || echo -e "${YELLOW}○ No${NC}")"

# Check services (with timeout to avoid hanging)
backend_ok=$(timeout 2 curl -s http://localhost:8000/health &>/dev/null && echo "true" || echo "false")
frontend_ok=$(timeout 2 curl -s http://localhost:8080 &>/dev/null && echo "true" || echo "false")

echo -e "  Backend reachable: $([ "$backend_ok" = "true" ] && echo -e "${GREEN}✓ Yes${NC}" || echo -e "${YELLOW}○ No${NC}")"
echo -e "  Frontend reachable: $([ "$frontend_ok" = "true" ] && echo -e "${GREEN}✓ Yes${NC}" || echo -e "${YELLOW}○ No${NC}")"

# 7. Branch analysis
echo
echo -e "${CYAN}Branch Analysis:${NC}"
# List feature branches
feature_branches=$(git branch -r | grep -E "feature/agent-" | wc -l | tr -d ' ')
echo "  Agent feature branches: $feature_branches"

# Check for merge conflicts
if git merge-tree $(git merge-base HEAD origin/main) HEAD origin/main | grep -q "<<<<<<< "; then
    echo -e "  ${RED}⚠️  Potential merge conflicts with main${NC}"
else
    echo -e "  ${GREEN}✓ No merge conflicts with main${NC}"
fi

# 8. Quick recommendations
echo
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}           RECOMMENDATIONS                              ${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"

if [[ ${uncommitted_count:-0} -gt 0 ]]; then
    echo -e "${YELLOW}•${NC} Found uncommitted changes - review with 'git status' and 'git diff'"
fi

if [[ $abandoned_count -gt 0 ]]; then
    echo -e "${YELLOW}•${NC} Check potentially abandoned agents before starting new work"
fi

if [[ $agent_count -eq 0 ]]; then
    echo -e "${GREEN}•${NC} No active agents - safe to initialize fresh: ./scripts/init-agent.sh <purpose>"
else
    echo -e "${BLUE}•${NC} Active agents found - check their status before starting"
fi

if [[ $locked_count -gt 0 ]]; then
    echo -e "${RED}•${NC} Some files are locked - coordinate before modifying them"
fi

echo
echo "Run './scripts/agent-status.sh' for detailed agent information"
echo "Run './scripts/init-agent.sh <purpose>' to start working"