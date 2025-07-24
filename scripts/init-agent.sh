#!/bin/bash

# Initialize a new agent workspace for multi-agent collaboration

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get the purpose/task from command line argument
PURPOSE=$1

if [ -z "$PURPOSE" ]; then
    echo -e "${YELLOW}Usage: $0 <purpose>${NC}"
    echo "Example: $0 backend-api"
    echo "Example: $0 frontend-ui"
    echo "Example: $0 testing"
    exit 1
fi

# Generate agent ID
TIMESTAMP=$(date +%Y%m%d%H%M%S)
RANDOM_ID=$(printf "%03d" $((RANDOM % 1000)))
AGENT_ID="agent-${RANDOM_ID}-${PURPOSE}"
AGENT_DIR=".claude-agents/active/${AGENT_ID}"

echo -e "${BLUE}Initializing agent workspace...${NC}"
echo "Agent ID: ${AGENT_ID}"

# Create agent directory
mkdir -p "${AGENT_DIR}"

# Copy templates
cp .claude-agents/templates/status.md "${AGENT_DIR}/"
cp .claude-agents/templates/log.md "${AGENT_DIR}/"
cp .claude-agents/templates/plan.md "${AGENT_DIR}/"
cp .claude-agents/templates/handoff.md "${AGENT_DIR}/"

# Get current timestamp
CURRENT_TIME=$(date '+%Y-%m-%d %H:%M:%S')

# Initialize status.md
sed -i.bak "s/\[AGENT-ID\]/${AGENT_ID}/g" "${AGENT_DIR}/status.md"
sed -i.bak "s/\[TIMESTAMP\]/${CURRENT_TIME}/g" "${AGENT_DIR}/status.md"
sed -i.bak "s/\[What you're working on\]/Initializing workspace for ${PURPOSE}/g" "${AGENT_DIR}/status.md"
sed -i.bak "s/\[Your git branch\]/feature\/${AGENT_ID}/g" "${AGENT_DIR}/status.md"
sed -i.bak "s/\[file1.py\] (LOCKED)/# No files locked yet/g" "${AGENT_DIR}/status.md"
sed -i.bak "s/- \[file2.js\] (LOCKED)//g" "${AGENT_DIR}/status.md"
sed -i.bak "s/\[Not Started | In Progress | Blocked | Testing | Complete\]/Not Started/g" "${AGENT_DIR}/status.md"
sed -i.bak "s/\[Estimated time to completion\]/TBD/g" "${AGENT_DIR}/status.md"
sed -i.bak "s/\[Brief description of what you're implementing\]/Setting up workspace for ${PURPOSE}/g" "${AGENT_DIR}/status.md"
sed -i.bak "s/\[Any issues preventing progress\]/None/g" "${AGENT_DIR}/status.md"
sed -i.bak "s/\[Anything other agents should know\]/New agent initialized for ${PURPOSE}/g" "${AGENT_DIR}/status.md"

# Initialize log.md
sed -i.bak "s/\[AGENT-ID\]/${AGENT_ID}/g" "${AGENT_DIR}/log.md"
sed -i.bak "s/\[TIMESTAMP\]/${CURRENT_TIME}/g" "${AGENT_DIR}/log.md"
sed -i.bak "s/\[What this agent is working on\]/${PURPOSE}/g" "${AGENT_DIR}/log.md"
sed -i.bak "s/\[branch-name\]/feature\/${AGENT_ID}/g" "${AGENT_DIR}/log.md"

# Initialize plan.md
sed -i.bak "s/\[AGENT-ID\]/${AGENT_ID}/g" "${AGENT_DIR}/plan.md"
sed -i.bak "s/\[High-level goal of this agent's work\]/${PURPOSE}/g" "${AGENT_DIR}/plan.md"

# Initialize handoff.md
sed -i.bak "s/\[AGENT-ID\]/${AGENT_ID}/g" "${AGENT_DIR}/handoff.md"
sed -i.bak "s/\[TIMESTAMP\]/${CURRENT_TIME}/g" "${AGENT_DIR}/handoff.md"

# Clean up backup files
rm -f "${AGENT_DIR}"/*.bak

# Create git branch (optional - uncomment if you want automatic branch creation)
# echo -e "${BLUE}Creating git branch: feature/${AGENT_ID}${NC}"
# git checkout -b "feature/${AGENT_ID}"

# Add entry to coordination board
echo -e "\n### ${CURRENT_TIME} - ${AGENT_ID}\nNew agent initialized for: ${PURPOSE}" >> .claude-agents/active/shared/coordination.md

echo -e "${GREEN}✓ Agent workspace initialized successfully!${NC}"
echo
echo "Next steps:"
echo "1. Read other active agents' status files:"
echo "   ls -la .claude-agents/active/*/status.md"
echo
echo "2. Update your plan:"
echo "   \$EDITOR ${AGENT_DIR}/plan.md"
echo
echo "3. Start working and update your status:"
echo "   \$EDITOR ${AGENT_DIR}/status.md"
echo
echo "Your workspace: ${AGENT_DIR}/"
echo
echo -e "${YELLOW}Remember to update your status.md regularly!${NC}"

# Store agent ID for current session
echo "${AGENT_ID}" > .current-agent-id

echo
echo -e "${YELLOW}⚠️  IMPORTANT WARNING ⚠️${NC}"
echo "The .current-agent-id file has been updated to show YOUR agent ID."
echo "However, this file is GLOBAL and will change when other agents initialize."
echo "DO NOT rely on this file to remember who you are!"
echo "Your TRUE identity is: ${AGENT_ID}"
echo "Your workspace is: ${AGENT_DIR}/"