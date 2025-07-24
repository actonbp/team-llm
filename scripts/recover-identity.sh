#!/bin/bash

# Script to help agents recover their identity after context reset/auto-compaction

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}        AGENT IDENTITY RECOVERY TOOL                    ${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo

# Check current branch
CURRENT_BRANCH=$(git branch --show-current)
echo -e "${YELLOW}Current Git Branch:${NC} $CURRENT_BRANCH"

# Extract possible agent ID from branch
if [[ $CURRENT_BRANCH =~ agent-([0-9]+) ]]; then
    BRANCH_AGENT_ID="agent-${BASH_REMATCH[1]}"
    echo -e "${GREEN}✓ Found agent ID in branch:${NC} $BRANCH_AGENT_ID"
else
    echo -e "${RED}✗ No agent ID found in branch name${NC}"
fi

echo
echo -e "${YELLOW}Recent Commits with Agent IDs:${NC}"
git log --oneline -20 | grep "\[agent-" | head -10 || echo "  No recent agent commits found"

echo
echo -e "${YELLOW}Active Agents and Their Work:${NC}"
for agent_dir in .claude-agents/active/agent-*/; do
    if [[ -d "$agent_dir" ]]; then
        agent_name=$(basename "$agent_dir")
        echo
        echo -e "${BLUE}══ $agent_name ══${NC}"
        
        if [[ -f "$agent_dir/status.md" ]]; then
            # Extract key information
            last_updated=$(grep -E "^\*\*Last Updated\*\*:" "$agent_dir/status.md" | cut -d: -f2- | xargs)
            current_task=$(grep -E "^\*\*Current Task\*\*:" "$agent_dir/status.md" | cut -d: -f2- | xargs)
            status=$(grep -E "^\*\*Status\*\*:" "$agent_dir/status.md" | grep -v "Last" | cut -d: -f2- | xargs)
            branch=$(grep -E "^\*\*Branch\*\*:" "$agent_dir/status.md" | cut -d: -f2- | xargs)
            
            echo "  Last Updated: $last_updated"
            echo "  Current Task: $current_task"
            echo "  Status: $status"
            echo "  Branch: $branch"
            
            # Check if this matches current branch
            if [[ "$branch" == *"$CURRENT_BRANCH"* ]] || [[ "$CURRENT_BRANCH" == *"$agent_name"* ]]; then
                echo -e "  ${GREEN}★ LIKELY MATCH - Branch matches current!${NC}"
            fi
        fi
    fi
done

echo
echo -e "${YELLOW}Files Modified in Current Branch:${NC}"
git diff --name-only main..HEAD | head -20

echo
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}        IDENTITY DETERMINATION                          ${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"

# Try to determine identity
LIKELY_AGENT=""
if [[ -n "$BRANCH_AGENT_ID" ]]; then
    # Check if agent directory exists with pattern matching
    for dir in .claude-agents/active/$BRANCH_AGENT_ID*; do
        if [[ -d "$dir" ]]; then
            LIKELY_AGENT=$(basename "$dir")
            break
        fi
    done
fi

if [[ -n "$LIKELY_AGENT" ]]; then
    echo
    echo -e "${GREEN}✓ MOST LIKELY IDENTITY: $LIKELY_AGENT${NC}"
    echo
    echo "To continue as this agent:"
    echo "1. Read your status: cat .claude-agents/active/$LIKELY_AGENT/status.md"
    echo "2. Read your log: cat .claude-agents/active/$LIKELY_AGENT/log.md"
    echo "3. Check your plan: cat .claude-agents/active/$LIKELY_AGENT/plan.md"
    echo "4. Update your status and continue working"
    echo
    echo -e "${YELLOW}DO NOT run init-agent.sh - you already exist!${NC}"
else
    echo
    echo -e "${YELLOW}⚠ Could not determine a likely agent identity${NC}"
    echo
    echo "Please:"
    echo "1. Review the agent list above"
    echo "2. Look for work that seems familiar"
    echo "3. Check which files you were modifying"
    echo "4. If you find your identity, continue that agent's work"
    echo "5. Only create a new agent if you're certain you're new"
fi

echo
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"