#!/bin/bash
# NGX Agents - Comprehensive Cleanup Script
# This script safely removes obsolete files, duplicates, and outdated documentation
# Created: $(date +%Y-%m-%d)

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# Change to project root
cd "$PROJECT_ROOT"

echo -e "${GREEN}NGX Agents - Cleanup Script${NC}"
echo "Project root: $PROJECT_ROOT"
echo "----------------------------------------"

# Create archive directory with timestamp
ARCHIVE_DIR="archive/cleanup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$ARCHIVE_DIR"
echo -e "${YELLOW}Archive directory created: $ARCHIVE_DIR${NC}"

# Function to safely remove files
safe_remove() {
    local file="$1"
    if [ -f "$file" ]; then
        echo "  Removing: $file"
        rm -f "$file"
    fi
}

# Function to archive then remove
archive_and_remove() {
    local file="$1"
    if [ -f "$file" ]; then
        echo "  Archiving: $file"
        cp "$file" "$ARCHIVE_DIR/" 2>/dev/null || true
        rm -f "$file"
    fi
}

# 1. Archive important files before deletion
echo -e "\n${YELLOW}Step 1: Archiving important files...${NC}"

# Archive session documentation
for file in CONTEXTO_SESION_*.md SESION_*.md PROJECT_STATUS_*.md RESUMEN_*.md; do
    [ -f "$file" ] && archive_and_remove "$file"
done

# Archive memory bank sessions
mkdir -p "$ARCHIVE_DIR/memory-bank"
for file in memory-bank/session_*.md; do
    [ -f "$file" ] && cp "$file" "$ARCHIVE_DIR/memory-bank/" 2>/dev/null || true
done

# Archive planning documents
mkdir -p "$ARCHIVE_DIR/docs"
for file in docs/plan_*.md docs/todos.md; do
    [ -f "$file" ] && cp "$file" "$ARCHIVE_DIR/docs/" 2>/dev/null || true
done

# 2. Remove server log files
echo -e "\n${YELLOW}Step 2: Removing server log files...${NC}"
for logfile in server*.log cache_monitoring.log *.log; do
    safe_remove "$logfile"
done

# 3. Remove Python cache directories
echo -e "\n${YELLOW}Step 3: Removing Python cache directories...${NC}"
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type f -name "*.pyo" -delete 2>/dev/null || true

# 4. Remove backup files
echo -e "\n${YELLOW}Step 4: Removing backup files...${NC}"
find . -type f -name "*.bak" -exec rm -f {} + 2>/dev/null || true
find . -type f -name "*.new" -exec rm -f {} + 2>/dev/null || true

# 5. Remove old backup directories
echo -e "\n${YELLOW}Step 5: Removing old backup directories...${NC}"
for dir in backup_pyproject_*; do
    if [ -d "$dir" ]; then
        echo "  Removing directory: $dir"
        rm -rf "$dir"
    fi
done

# 6. Remove specific obsolete files
echo -e "\n${YELLOW}Step 6: Removing specific obsolete files...${NC}"
safe_remove "quick_health_report.txt"
safe_remove "update_results.txt"
safe_remove "QUICK_FIX_NEXT_ERROR.md"
safe_remove "BACKEND_VERIFICATION_STATUS.md"
safe_remove "AGENT_COMMUNICATION_ANALYSIS.md"

# 7. Clean frontend build artifacts (optional)
echo -e "\n${YELLOW}Step 7: Cleaning frontend build artifacts...${NC}"
if [ -d "frontend/.next" ]; then
    echo "  Removing .next build directory..."
    rm -rf frontend/.next
fi

# 8. Remove test result files
echo -e "\n${YELLOW}Step 8: Removing old test results...${NC}"
find . -name "pytest_cache" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name ".coverage" -type f -delete 2>/dev/null || true
find . -name "htmlcov" -type d -exec rm -rf {} + 2>/dev/null || true

# 9. Clean up memory bank old sessions
echo -e "\n${YELLOW}Step 9: Cleaning memory bank old sessions...${NC}"
for file in memory-bank/session_*.md; do
    if [ -f "$file" ]; then
        echo "  Removing: $file"
        rm -f "$file"
    fi
done

# 10. Update .gitignore if needed
echo -e "\n${YELLOW}Step 10: Checking .gitignore...${NC}"
if [ ! -f .gitignore ]; then
    echo "Creating .gitignore file..."
    cat > .gitignore << 'EOF'
# Logs
*.log
logs/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Python
__pycache__/
*.py[cod]
*$py.class
*.pyc
.pytest_cache/
.coverage
htmlcov/
*.egg-info/
dist/
build/

# Environments
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Backups
*.bak
*.new
backup_*/
archive_*/

# Next.js
frontend/.next/
frontend/out/
frontend/node_modules/

# Misc
.env.local
.env.*.local
EOF
    echo ".gitignore created"
else
    echo ".gitignore already exists"
fi

# Summary
echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}Cleanup Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "Archived files location: ${YELLOW}$ARCHIVE_DIR${NC}"

# Count cleaned items
LOG_COUNT=$(find "$ARCHIVE_DIR" -name "*.log" 2>/dev/null | wc -l)
MD_COUNT=$(find "$ARCHIVE_DIR" -name "*.md" 2>/dev/null | wc -l)

echo -e "\nCleaned up:"
echo -e "  - Log files: ${YELLOW}$LOG_COUNT${NC}"
echo -e "  - Documentation files: ${YELLOW}$MD_COUNT${NC}"
echo -e "  - Python cache directories"
echo -e "  - Backup files (*.bak, *.new)"
echo -e "  - Old backup directories"

echo -e "\n${YELLOW}Note: Important files have been archived before deletion.${NC}"
echo -e "${YELLOW}You can find them in: $ARCHIVE_DIR${NC}"

# Optional: Ask to remove archive after review
echo -e "\n${YELLOW}Would you like to review the archive before permanently deleting it? (y/n)${NC}"
read -r response
if [[ "$response" =~ ^[Nn]$ ]]; then
    echo "Archive kept at: $ARCHIVE_DIR"
else
    echo -e "${GREEN}Archive preserved for review.${NC}"
    echo "To permanently delete the archive later, run:"
    echo "  rm -rf $ARCHIVE_DIR"
fi

echo -e "\n${GREEN}Cleanup script completed successfully!${NC}"