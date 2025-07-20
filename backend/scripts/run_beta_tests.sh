#!/bin/bash
# GENESIS Beta Validation Test Automation Script
# This script automates the beta validation testing process

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
REPORTS_DIR="${PROJECT_ROOT}/reports"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Print header
echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}GENESIS Beta Validation Test Suite${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""

# Function to print status
print_status() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

# Function to print success
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

# Function to print error
print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Function to print warning
print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Parse command line arguments
CATEGORY=""
QUICK=false
PARALLEL=false
VERBOSE=false
REPORT=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --category)
            CATEGORY="$2"
            shift 2
            ;;
        --quick)
            QUICK=true
            shift
            ;;
        --parallel)
            PARALLEL=true
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --report)
            REPORT=true
            shift
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --category CATEGORY  Run specific test category"
            echo "  --quick             Run quick validation subset"
            echo "  --parallel          Run tests in parallel"
            echo "  --verbose           Enable verbose output"
            echo "  --report            Generate HTML report"
            echo "  --help              Show this help message"
            echo ""
            echo "Categories:"
            echo "  - user_frustration"
            echo "  - edge_cases"
            echo "  - multi_agent"
            echo "  - ecosystem_integration"
            echo "  - stress_tests"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Change to project root
cd "$PROJECT_ROOT"

# Check Python environment
print_status "Checking Python environment..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
print_success "Python $PYTHON_VERSION detected"

# Check if virtual environment is activated
if [[ -z "$VIRTUAL_ENV" ]]; then
    print_warning "Virtual environment not activated"
    
    # Try to activate Poetry environment
    if command -v poetry &> /dev/null; then
        print_status "Activating Poetry environment..."
        eval "$(poetry env info --path)/bin/activate"
    else
        print_warning "Poetry not found, continuing without virtual environment"
    fi
fi

# Create reports directory
mkdir -p "$REPORTS_DIR"
print_success "Reports directory ready: $REPORTS_DIR"

# Build command
CMD="python -m tests.beta_validation.run_beta_validation"
CMD="$CMD --output-dir $REPORTS_DIR"

if [[ -n "$CATEGORY" ]]; then
    CMD="$CMD --category $CATEGORY"
    print_status "Running category: $CATEGORY"
elif [[ "$QUICK" == true ]]; then
    CMD="$CMD --quick"
    print_status "Running quick validation subset"
else
    print_status "Running all test categories"
fi

if [[ "$PARALLEL" == true ]]; then
    CMD="$CMD --parallel"
    print_status "Running tests in parallel mode"
fi

if [[ "$VERBOSE" == true ]]; then
    CMD="$CMD --verbose"
fi

if [[ "$REPORT" == true ]]; then
    CMD="$CMD --report"
fi

# Run tests
print_status "Starting beta validation tests..."
echo ""

# Execute command and capture exit code
set +e  # Don't exit on error
$CMD
EXIT_CODE=$?
set -e

echo ""

# Analyze results
if [[ $EXIT_CODE -eq 0 ]]; then
    print_success "All tests passed! System is ready for BETA launch."
    
    # Show latest report location
    LATEST_REPORT=$(ls -t "$REPORTS_DIR"/beta_validation_summary_*.txt 2>/dev/null | head -1)
    if [[ -n "$LATEST_REPORT" ]]; then
        echo ""
        print_status "Summary report: $LATEST_REPORT"
        echo ""
        
        # Show key metrics
        echo -e "${BLUE}Key Metrics:${NC}"
        grep -E "Overall Pass Rate:|Total Scenarios:|Passed:|Failed:" "$LATEST_REPORT" | head -4
    fi
    
elif [[ $EXIT_CODE -eq 1 ]]; then
    print_warning "Tests completed but pass rate is below 90%"
    print_warning "Review and fix failing scenarios before BETA launch"
    
elif [[ $EXIT_CODE -eq 2 ]]; then
    print_error "CRITICAL ISSUES FOUND!"
    print_error "BETA launch must be BLOCKED until these are fixed"
    
    # Show critical issues from latest report
    LATEST_REPORT=$(ls -t "$REPORTS_DIR"/beta_validation_summary_*.txt 2>/dev/null | head -1)
    if [[ -n "$LATEST_REPORT" ]]; then
        echo ""
        echo -e "${RED}Critical Issues:${NC}"
        sed -n '/CRITICAL ISSUES/,/^$/p' "$LATEST_REPORT" | head -20
    fi
    
else
    print_error "Fatal error occurred during testing (exit code: $EXIT_CODE)"
fi

# Show report locations
echo ""
echo -e "${BLUE}Reports saved to: $REPORTS_DIR${NC}"
echo ""

# Offer to open report
if [[ $EXIT_CODE -ne 0 ]] && [[ -n "$LATEST_REPORT" ]]; then
    read -p "Would you like to view the detailed report? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        less "$LATEST_REPORT"
    fi
fi

exit $EXIT_CODE