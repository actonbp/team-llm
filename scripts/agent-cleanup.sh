#!/bin/bash

# Archive inactive agent sessions older than specified time
# Usage: ./scripts/agent-cleanup.sh [hours]
# Default: Archives sessions inactive for more than 24 hours

set -e

# Default to 24 hours if not specified
INACTIVE_HOURS=${1:-24}

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
AGENTS_DIR="$PROJECT_ROOT/.claude-agents"
ACTIVE_DIR="$AGENTS_DIR/active"
COMPLETED_DIR="$AGENTS_DIR/completed"

echo "🧹 Agent Cleanup Utility"
echo "========================"
echo "Archiving agents inactive for more than $INACTIVE_HOURS hours..."
echo

# Ensure completed directory exists
mkdir -p "$COMPLETED_DIR"

# Counter for archived agents
ARCHIVED_COUNT=0

# Function to check if agent is inactive
is_inactive() {
    local agent_dir="$1"
    local status_file="$agent_dir/status.md"
    
    if [[ ! -f "$status_file" ]]; then
        return 0  # No status file = inactive
    fi
    
    # Get last modified time of status file
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        LAST_MODIFIED=$(stat -f %m "$status_file")
    else
        # Linux
        LAST_MODIFIED=$(stat -c %Y "$status_file")
    fi
    
    CURRENT_TIME=$(date +%s)
    HOURS_INACTIVE=$(( ($CURRENT_TIME - $LAST_MODIFIED) / 3600 ))
    
    if [[ $HOURS_INACTIVE -gt $INACTIVE_HOURS ]]; then
        echo -e "${YELLOW}  Agent $(basename "$agent_dir") inactive for $HOURS_INACTIVE hours${NC}"
        return 0
    else
        return 1
    fi
}

# Process each agent directory
for agent_dir in "$ACTIVE_DIR"/agent-*/; do
    if [[ -d "$agent_dir" ]]; then
        agent_name=$(basename "$agent_dir")
        
        if is_inactive "$agent_dir"; then
            echo -e "${YELLOW}  Archiving $agent_name...${NC}"
            
            # Create timestamp for archive
            ARCHIVE_TIME=$(date "+%Y%m%d_%H%M%S")
            ARCHIVE_NAME="${agent_name}_${ARCHIVE_TIME}"
            
            # Move to completed directory
            mv "$agent_dir" "$COMPLETED_DIR/$ARCHIVE_NAME"
            
            # Release any file locks
            if [[ -f "$ACTIVE_DIR/shared/conflicts.md" ]]; then
                # Remove locks from this agent
                # Using a temp file to avoid in-place editing issues
                grep -v "| \[$agent_name\]" "$ACTIVE_DIR/shared/conflicts.md" > "$ACTIVE_DIR/shared/conflicts.md.tmp" || true
                mv "$ACTIVE_DIR/shared/conflicts.md.tmp" "$ACTIVE_DIR/shared/conflicts.md"
            fi
            
            ((ARCHIVED_COUNT++))
            echo -e "${GREEN}  ✓ Archived to completed/$ARCHIVE_NAME${NC}"
        fi
    fi
done

# Summary
echo
if [[ $ARCHIVED_COUNT -eq 0 ]]; then
    echo -e "${GREEN}✓ No inactive agents to archive${NC}"
else
    echo -e "${GREEN}✓ Archived $ARCHIVED_COUNT inactive agent(s)${NC}"
fi

# Optional: Clean up very old archives (older than 30 days)
if [[ "$2" == "--clean-old" ]]; then
    echo
    echo "Cleaning archives older than 30 days..."
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS - find doesn't support -mtime with fractions
        find "$COMPLETED_DIR" -type d -name "agent-*" -mtime +30 -exec rm -rf {} \; 2>/dev/null || true
    else
        # Linux
        find "$COMPLETED_DIR" -type d -name "agent-*" -mtime +30 -exec rm -rf {} \; 2>/dev/null || true
    fi
    
    echo -e "${GREEN}✓ Old archives cleaned${NC}"
fi

echo
echo "Tip: Run with --clean-old to also remove archives older than 30 days"
echo "     Example: ./scripts/agent-cleanup.sh 24 --clean-old"