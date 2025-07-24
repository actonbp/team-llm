#!/bin/bash

# View the status of all active agents

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}           ACTIVE AGENT STATUS REPORT                   ${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo

# Check if any agents are active
if [ ! -d ".claude-agents/active" ] || [ -z "$(ls -A .claude-agents/active 2>/dev/null | grep -v shared)" ]; then
    echo -e "${YELLOW}No active agents found.${NC}"
    echo "Run ./scripts/init-agent.sh <purpose> to create one."
    exit 0
fi

# Current agent (if set)
if [ -f ".current-agent-id" ]; then
    CURRENT_AGENT=$(cat .current-agent-id)
    echo -e "${GREEN}You are: ${CURRENT_AGENT}${NC}"
    echo
fi

# Iterate through active agents
for agent_dir in .claude-agents/active/*/; do
    # Skip the shared directory
    if [[ "$agent_dir" == *"shared"* ]]; then
        continue
    fi
    
    # Skip if not a directory
    if [ ! -d "$agent_dir" ]; then
        continue
    fi
    
    agent_name=$(basename "$agent_dir")
    status_file="${agent_dir}status.md"
    
    if [ -f "$status_file" ]; then
        echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo -e "${CYAN}Agent: ${agent_name}${NC}"
        echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        
        # Extract key information from status.md
        last_updated=$(grep -A1 "Last Updated" "$status_file" | tail -1 | sed 's/.*: //')
        current_task=$(grep -A1 "Current Task" "$status_file" | tail -1 | sed 's/.*: //')
        status=$(grep -A1 "Status\*\*:" "$status_file" | tail -1 | sed 's/.*: //')
        eta=$(grep -A1 "ETA" "$status_file" | tail -1 | sed 's/.*: //')
        branch=$(grep -A1 "Branch" "$status_file" | tail -1 | sed 's/.*: //')
        
        # Color code status
        case "$status" in
            *"Progress"*)
                status_color="${GREEN}"
                ;;
            *"Blocked"*)
                status_color="${RED}"
                ;;
            *"Complete"*)
                status_color="${BLUE}"
                ;;
            *)
                status_color="${YELLOW}"
                ;;
        esac
        
        echo "Last Updated: $last_updated"
        echo "Current Task: $current_task"
        echo -e "Status: ${status_color}$status${NC}"
        echo "ETA: $eta"
        echo "Branch: $branch"
        
        # Show locked files
        echo
        echo "Locked Files:"
        # Extract files between "Files Being Modified" and "Status"
        awk '/Files Being Modified/,/\*\*Status\*\*/' "$status_file" | grep -E "^- " | head -n -1 || echo "  None"
        
        echo
    fi
done

# Show coordination board summary
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}           COORDINATION BOARD SUMMARY                   ${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"

if [ -f ".claude-agents/active/shared/coordination.md" ]; then
    # Count open discussions
    open_discussions=$(grep -c "Status\*\*: \[Open" .claude-agents/active/shared/coordination.md 2>/dev/null || echo "0")
    echo "Open Discussions: $open_discussions"
    
    # Show recent announcements
    echo
    echo "Recent Activity:"
    tail -n 20 .claude-agents/active/shared/coordination.md | grep -E "^### \[" | tail -n 3 || echo "  No recent activity"
fi

# Show file conflicts
echo
echo -e "${YELLOW}═══════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}           FILE LOCK SUMMARY                            ${NC}"  
echo -e "${YELLOW}═══════════════════════════════════════════════════════${NC}"

if [ -f ".claude-agents/active/shared/conflicts.md" ]; then
    # Extract currently locked files (skip header row)
    locked_files=$(awk '/Currently Locked Files/,/Lock History/' .claude-agents/active/shared/conflicts.md | grep -E "^\|" | grep -v "File Path" | grep -v "^|--" | wc -l)
    
    if [ "$locked_files" -gt 0 ]; then
        echo -e "${RED}⚠️  $locked_files files currently locked${NC}"
        echo
        awk '/Currently Locked Files/,/Lock History/' .claude-agents/active/shared/conflicts.md | grep -E "^\|" | grep -v "File Path" | grep -v "^|--" | head -n 5
    else
        echo -e "${GREEN}✓ No file conflicts${NC}"
    fi
fi

echo
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
echo
echo "Commands:"
echo "  View full agent details:  cat .claude-agents/active/AGENT-ID/status.md"
echo "  View coordination board:  cat .claude-agents/active/shared/coordination.md"
echo "  View file locks:          cat .claude-agents/active/shared/conflicts.md"