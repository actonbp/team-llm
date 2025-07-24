#!/bin/bash

# Check for file conflicts between agents
# Usage: ./scripts/agent-conflicts.sh [--resolve]

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
AGENTS_DIR="$PROJECT_ROOT/.claude-agents"
CONFLICTS_FILE="$AGENTS_DIR/active/shared/conflicts.md"
RESOLVE_MODE=false

# Check for --resolve flag
if [[ "$1" == "--resolve" ]]; then
    RESOLVE_MODE=true
fi

echo -e "${CYAN}🔍 Agent Conflict Checker${NC}"
echo "=========================="
echo

# Function to check if file is actually locked in git
is_file_modified() {
    local file_path="$1"
    # Check if file exists and has uncommitted changes
    if [[ -f "$PROJECT_ROOT/$file_path" ]]; then
        git -C "$PROJECT_ROOT" diff --quiet "$file_path" 2>/dev/null
        return $?
    fi
    return 1
}

# Function to get current agent from most recent status file
get_active_agent() {
    local latest_agent=""
    local latest_time=0
    
    for status_file in "$AGENTS_DIR"/active/agent-*/status.md; do
        if [[ -f "$status_file" ]]; then
            if [[ "$OSTYPE" == "darwin"* ]]; then
                mod_time=$(stat -f %m "$status_file")
            else
                mod_time=$(stat -c %Y "$status_file")
            fi
            
            if [[ $mod_time -gt $latest_time ]]; then
                latest_time=$mod_time
                latest_agent=$(basename "$(dirname "$status_file")")
            fi
        fi
    done
    
    echo "$latest_agent"
}

# Check if conflicts file exists
if [[ ! -f "$CONFLICTS_FILE" ]]; then
    echo -e "${GREEN}✓ No conflicts file found - no conflicts!${NC}"
    exit 0
fi

# Extract locked files from conflicts.md
echo -e "${CYAN}Currently Locked Files:${NC}"
echo

# Parse the conflicts file for locked files
LOCKED_FILES=$(awk '/Currently Locked Files/,/Lock History/' "$CONFLICTS_FILE" | 
    grep -E "^\|" | 
    grep -v "File Path" | 
    grep -v "^|--" | 
    grep -v "Example:")

if [[ -z "$LOCKED_FILES" ]]; then
    echo -e "${GREEN}✓ No files currently locked${NC}"
else
    # Process each locked file
    while IFS='|' read -r _ file_path agent since eta purpose _; do
        # Skip empty lines
        if [[ -z "$file_path" ]] || [[ "$file_path" =~ ^[[:space:]]*$ ]]; then
            continue
        fi
        
        # Clean up the values
        file_path=$(echo "$file_path" | xargs)
        agent=$(echo "$agent" | xargs | tr -d '[]')
        eta=$(echo "$eta" | xargs | tr -d '[]')
        purpose=$(echo "$purpose" | xargs | tr -d '[]')
        
        # Skip example entries
        if [[ "$file_path" == "Example:"* ]]; then
            continue
        fi
        
        echo -e "${YELLOW}📄 $file_path${NC}"
        echo "   Locked by: $agent"
        echo "   ETA: $eta"
        echo "   Purpose: $purpose"
        
        # Check if file is actually being modified
        if is_file_modified "$file_path"; then
            echo -e "   Status: ${YELLOW}⚠️  Has uncommitted changes${NC}"
        else
            echo -e "   Status: ${GREEN}✓ No uncommitted changes${NC}"
            if [[ "$RESOLVE_MODE" == true ]]; then
                echo -e "   ${CYAN}→ Removing stale lock${NC}"
                STALE_LOCKS+=("$file_path")
            fi
        fi
        echo
    done <<< "$LOCKED_FILES"
fi

# Check for potential conflicts (files modified by multiple agents)
echo -e "${CYAN}Checking for Potential Conflicts:${NC}"
echo

CONFLICT_COUNT=0

# Get all modified files
MODIFIED_FILES=$(git -C "$PROJECT_ROOT" diff --name-only 2>/dev/null || true)

if [[ -z "$MODIFIED_FILES" ]]; then
    echo -e "${GREEN}✓ No modified files found${NC}"
else
    # Check each modified file
    for file in $MODIFIED_FILES; do
        # Check how many agents have this file in their status
        AGENTS_MODIFYING=""
        
        for status_file in "$AGENTS_DIR"/active/agent-*/status.md; do
            if [[ -f "$status_file" ]] && grep -q "$file" "$status_file" 2>/dev/null; then
                agent_name=$(basename "$(dirname "$status_file")")
                AGENTS_MODIFYING="$AGENTS_MODIFYING $agent_name"
            fi
        done
        
        # Count agents
        agent_count=$(echo "$AGENTS_MODIFYING" | wc -w)
        
        if [[ $agent_count -gt 1 ]]; then
            echo -e "${RED}⚠️  CONFLICT: $file${NC}"
            echo "   Modified by multiple agents:$AGENTS_MODIFYING"
            ((CONFLICT_COUNT++))
        fi
    done
fi

if [[ $CONFLICT_COUNT -eq 0 ]]; then
    echo -e "${GREEN}✓ No conflicts detected${NC}"
fi

# Resolve mode actions
if [[ "$RESOLVE_MODE" == true ]] && [[ ${#STALE_LOCKS[@]} -gt 0 ]]; then
    echo
    echo -e "${CYAN}Resolving Stale Locks:${NC}"
    
    # Create backup
    cp "$CONFLICTS_FILE" "$CONFLICTS_FILE.backup"
    
    # Remove stale locks
    for stale_file in "${STALE_LOCKS[@]}"; do
        echo "  Removing lock for: $stale_file"
        # Use grep to remove the line containing the file
        grep -v "$stale_file" "$CONFLICTS_FILE" > "$CONFLICTS_FILE.tmp" || true
        mv "$CONFLICTS_FILE.tmp" "$CONFLICTS_FILE"
    done
    
    echo -e "${GREEN}✓ Removed ${#STALE_LOCKS[@]} stale lock(s)${NC}"
    echo "  Backup saved to: conflicts.md.backup"
fi

# Summary and recommendations
echo
echo -e "${CYAN}Summary:${NC}"

# Count total locks
TOTAL_LOCKS=$(echo "$LOCKED_FILES" | grep -c "." || echo "0")
echo "  Total locked files: $TOTAL_LOCKS"
echo "  Conflicts found: $CONFLICT_COUNT"

if [[ "$RESOLVE_MODE" == false ]] && [[ ${#STALE_LOCKS[@]} -gt 0 ]]; then
    echo
    echo -e "${YELLOW}Tip: Run with --resolve to automatically remove stale locks${NC}"
    echo "     ./scripts/agent-conflicts.sh --resolve"
fi

# Get current agent
CURRENT_AGENT=$(get_active_agent)
if [[ -n "$CURRENT_AGENT" ]]; then
    echo
    echo -e "Current agent: ${CYAN}$CURRENT_AGENT${NC}"
fi