#!/bin/bash
# GENESIS Beta Validation CI/CD Integration Script
# This script is designed to run in CI/CD pipelines (GitHub Actions, etc.)

set -e  # Exit on error

# Configuration
PYTHON_VERSION="3.11"
REPORTS_DIR="reports"
ARTIFACTS_DIR="artifacts"

# Function to print with timestamp
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Function to print section header
section() {
    echo ""
    echo "========================================"
    echo "$1"
    echo "========================================"
    echo ""
}

# Initialize
section "GENESIS Beta Validation - CI/CD Run"

# Create directories
mkdir -p "$REPORTS_DIR"
mkdir -p "$ARTIFACTS_DIR"

# System information
log "System Information:"
log "- OS: $(uname -s)"
log "- Python: $(python3 --version)"
log "- Current Dir: $(pwd)"

# Install dependencies if needed
if [[ -f "pyproject.toml" ]]; then
    if command -v poetry &> /dev/null; then
        section "Installing Dependencies with Poetry"
        poetry install --with dev
        PYTHON_CMD="poetry run python"
    else
        log "Poetry not found, using pip"
        PYTHON_CMD="python3"
        
        if [[ -f "requirements.txt" ]]; then
            section "Installing Dependencies with pip"
            pip install -r requirements.txt
        fi
    fi
else
    PYTHON_CMD="python3"
fi

# Run different test suites based on CI stage
STAGE="${CI_STAGE:-full}"

case $STAGE in
    quick)
        section "Running Quick Validation Tests"
        $PYTHON_CMD -m tests.beta_validation.run_beta_validation \
            --quick \
            --output-dir "$REPORTS_DIR"
        ;;
    
    critical)
        section "Running Critical Scenarios Only"
        # Run specific critical categories
        for category in user_frustration multi_agent; do
            log "Testing category: $category"
            $PYTHON_CMD -m tests.beta_validation.run_beta_validation \
                --category "$category" \
                --output-dir "$REPORTS_DIR"
        done
        ;;
    
    performance)
        section "Running Performance Tests"
        $PYTHON_CMD -m tests.beta_validation.run_beta_validation \
            --category stress_tests \
            --output-dir "$REPORTS_DIR"
        ;;
    
    full|*)
        section "Running Full Beta Validation Suite"
        $PYTHON_CMD -m tests.beta_validation.run_beta_validation \
            --parallel \
            --report \
            --output-dir "$REPORTS_DIR"
        ;;
esac

# Capture exit code
EXIT_CODE=$?

# Process results
section "Processing Results"

# Find latest reports
LATEST_JSON=$(ls -t "$REPORTS_DIR"/beta_validation_results_*.json 2>/dev/null | head -1)
LATEST_SUMMARY=$(ls -t "$REPORTS_DIR"/beta_validation_summary_*.txt 2>/dev/null | head -1)

if [[ -n "$LATEST_JSON" ]]; then
    # Extract key metrics using Python
    $PYTHON_CMD << EOF
import json
import sys

with open("$LATEST_JSON", 'r') as f:
    data = json.load(f)

summary = data.get('summary', {})
print(f"Total Scenarios: {summary.get('total_scenarios', 0)}")
print(f"Passed: {summary.get('passed', 0)}")
print(f"Failed: {summary.get('failed', 0)}")
print(f"Pass Rate: {summary.get('pass_rate', 0):.1f}%")

# Set GitHub Actions outputs if available
if 'GITHUB_OUTPUT' in os.environ:
    with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
        f.write(f"pass_rate={summary.get('pass_rate', 0):.1f}\n")
        f.write(f"total_scenarios={summary.get('total_scenarios', 0)}\n")
        f.write(f"passed={summary.get('passed', 0)}\n")
        f.write(f"failed={summary.get('failed', 0)}\n")
        f.write(f"has_critical_issues={'true' if data.get('critical_issues') else 'false'}\n")

# Check for critical issues
if data.get('critical_issues'):
    print("\n⚠️  CRITICAL ISSUES DETECTED!")
    for issue in data['critical_issues'][:5]:
        print(f"- {issue['category']}/{issue['scenario']}")
    sys.exit(2)
elif summary.get('pass_rate', 0) < 90:
    print("\n⚠️  Pass rate below 90% threshold")
    sys.exit(1)
else:
    print("\n✅ All tests passed!")
    sys.exit(0)
EOF
    
    # Capture Python exit code
    PYTHON_EXIT=$?
    
    # Override exit code if needed
    if [[ $PYTHON_EXIT -ne 0 ]]; then
        EXIT_CODE=$PYTHON_EXIT
    fi
fi

# Copy reports to artifacts
if [[ -n "$LATEST_JSON" ]]; then
    cp "$LATEST_JSON" "$ARTIFACTS_DIR/"
fi

if [[ -n "$LATEST_SUMMARY" ]]; then
    cp "$LATEST_SUMMARY" "$ARTIFACTS_DIR/"
    
    # Show summary in CI log
    section "Test Summary"
    cat "$LATEST_SUMMARY" | head -50
fi

# Generate badge data (for README badges)
if [[ -n "$LATEST_JSON" ]]; then
    $PYTHON_CMD << EOF
import json

with open("$LATEST_JSON", 'r') as f:
    data = json.load(f)

pass_rate = data.get('summary', {}).get('pass_rate', 0)

# Determine color
if pass_rate >= 90:
    color = "brightgreen"
elif pass_rate >= 70:
    color = "yellow"
else:
    color = "red"

# Create badge JSON
badge = {
    "schemaVersion": 1,
    "label": "Beta Validation",
    "message": f"{pass_rate:.1f}%",
    "color": color
}

with open("$ARTIFACTS_DIR/badge.json", 'w') as f:
    json.dump(badge, f)
EOF
fi

# Exit with appropriate code
if [[ $EXIT_CODE -eq 0 ]]; then
    log "✅ Beta validation passed!"
elif [[ $EXIT_CODE -eq 1 ]]; then
    log "⚠️  Beta validation completed with warnings"
elif [[ $EXIT_CODE -eq 2 ]]; then
    log "❌ Beta validation failed - Critical issues found!"
else
    log "❌ Beta validation failed with error code: $EXIT_CODE"
fi

exit $EXIT_CODE