#!/bin/bash

# Prepare handoff documentation when switching tasks or ending session

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get current agent ID
if [ -f ".current-agent-id" ]; then
    AGENT_ID=$(cat .current-agent-id)
else
    echo -e "${YELLOW}No current agent ID found.${NC}"
    echo "Run ./scripts/init-agent.sh <purpose> first."
    exit 1
fi

AGENT_DIR=".claude-agents/active/${AGENT_ID}"
HANDOFF_FILE="${AGENT_DIR}/handoff.md"

if [ ! -f "$HANDOFF_FILE" ]; then
    echo -e "${YELLOW}Handoff file not found for ${AGENT_ID}${NC}"
    exit 1
fi

echo -e "${BLUE}Preparing handoff for ${AGENT_ID}...${NC}"
echo

# Get current timestamp
CURRENT_TIME=$(date '+%Y-%m-%d %H:%M:%S')

# Update handoff timestamp
sed -i.bak "s/\*\*Handoff Date\*\*: \[TIMESTAMP\]/\*\*Handoff Date\*\*: ${CURRENT_TIME}/g" "$HANDOFF_FILE"

# Open editor for handoff notes
echo -e "${YELLOW}Opening handoff notes for editing...${NC}"
echo "Please document:"
echo "  - What you completed"
echo "  - What remains to be done"
echo "  - Any important decisions or gotchas"
echo "  - Test results"
echo "  - Recommendations for the next agent"
echo

# Use the default editor, or nano if not set
EDITOR=${EDITOR:-nano}
$EDITOR "$HANDOFF_FILE"

# Update status to show handoff prepared
sed -i.bak "s/\*\*Status\*\*:.*/\*\*Status\*\*: Handoff Prepared/g" "${AGENT_DIR}/status.md"
sed -i.bak "s/\*\*Last Updated\*\*:.*/\*\*Last Updated\*\*: ${CURRENT_TIME}/g" "${AGENT_DIR}/status.md"

# Add note to coordination board
echo -e "\n### ${CURRENT_TIME} - ${AGENT_ID} - Handoff Prepared" >> .claude-agents/active/shared/coordination.md
echo "Agent ${AGENT_ID} has prepared handoff documentation. See ${AGENT_DIR}/handoff.md" >> .claude-agents/active/shared/coordination.md

# Release any file locks
echo -e "${BLUE}Checking for file locks to release...${NC}"
if [ -f ".claude-agents/active/shared/conflicts.md" ]; then
    # Automatically release file locks for this agent
    AGENT_NAME=$(basename "$AGENT_DIR")
    LOCK_COUNT=$(grep -c "\[$AGENT_NAME\]" ".claude-agents/active/shared/conflicts.md" 2>/dev/null || echo "0")
    
    if [[ $LOCK_COUNT -gt 0 ]]; then
        # Remove locks from this agent (using temp file to avoid in-place editing)
        grep -v "\[$AGENT_NAME\]" ".claude-agents/active/shared/conflicts.md" > ".claude-agents/active/shared/conflicts.md.tmp" || true
        mv ".claude-agents/active/shared/conflicts.md.tmp" ".claude-agents/active/shared/conflicts.md"
        echo -e "${GREEN}✓ Released $LOCK_COUNT file lock(s)${NC}"
    else
        echo "No file locks found for this agent"
    fi
else
    echo "No conflict tracking file found"
fi

# Offer to archive the session
echo
echo -e "${GREEN}✓ Handoff documentation prepared!${NC}"
echo
read -p "Archive this agent session? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Create archive directory with timestamp
    ARCHIVE_DIR=".claude-agents/completed/${AGENT_ID}-${CURRENT_TIME//[: ]/-}"
    mkdir -p "$ARCHIVE_DIR"
    
    # Move agent files to archive
    mv "${AGENT_DIR}"/* "$ARCHIVE_DIR/"
    rmdir "${AGENT_DIR}"
    
    # Remove current agent ID
    rm -f .current-agent-id
    
    echo -e "${GREEN}✓ Agent session archived to: ${ARCHIVE_DIR}${NC}"
else
    echo "Session remains active. Remember to:"
    echo "  - Update status.md if you continue working"
    echo "  - Run this script again when truly done"
fi

echo
echo "Handoff location: ${HANDOFF_FILE}"
echo "Next agent should read this before starting work!"

# Clean up backup files
rm -f "${AGENT_DIR}"/*.bak