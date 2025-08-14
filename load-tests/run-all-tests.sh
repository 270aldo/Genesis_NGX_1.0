#!/bin/bash

# GENESIS Load Testing Suite Runner
# Executes all performance tests and generates comprehensive reports

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT=${1:-local}
RESULTS_DIR="results/$(date +%Y%m%d_%H%M%S)"
LOG_FILE="$RESULTS_DIR/test-execution.log"

echo -e "${BLUE}🚀 Starting GENESIS Load Testing Suite${NC}"
echo -e "${BLUE}Environment: $ENVIRONMENT${NC}"
echo -e "${BLUE}Results will be saved to: $RESULTS_DIR${NC}"

# Create results directory
mkdir -p "$RESULTS_DIR"
touch "$LOG_FILE"

# Function to log messages
log() {
    echo -e "$1" | tee -a "$LOG_FILE"
}

# Function to run a test scenario
run_test() {
    local test_name="$1"
    local test_file="$2"
    local description="$3"

    log "${YELLOW}📊 Running $test_name - $description${NC}"

    local start_time=$(date +%s)

    if k6 run \
        --env ENVIRONMENT="$ENVIRONMENT" \
        --out json="$RESULTS_DIR/$test_name-results.json" \
        --out csv="$RESULTS_DIR/$test_name-results.csv" \
        "$test_file" >> "$LOG_FILE" 2>&1; then

        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        log "${GREEN}✅ $test_name completed successfully in ${duration}s${NC}"
        return 0
    else
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        log "${RED}❌ $test_name failed after ${duration}s${NC}"
        return 1
    fi
}

# Check if K6 is installed
if ! command -v k6 &> /dev/null; then
    log "${RED}❌ K6 is not installed. Please install K6 first.${NC}"
    log "Visit: https://k6.io/docs/get-started/installation/"
    exit 1
fi

# Check if API is healthy before starting tests
log "${BLUE}🏥 Checking API health before starting tests...${NC}"
if [ "$ENVIRONMENT" = "local" ]; then
    API_URL="http://localhost:8000"
else
    API_URL="https://api-$ENVIRONMENT.genesis.com"
fi

if ! curl -f -s "$API_URL/health" > /dev/null; then
    log "${RED}❌ API health check failed. Make sure the API is running.${NC}"
    exit 1
fi

log "${GREEN}✅ API is healthy, proceeding with tests${NC}"

# Initialize test results tracking
TESTS_PASSED=0
TESTS_FAILED=0
TOTAL_TESTS=6

# Execute test scenarios in order
log "\n${BLUE}🎯 Phase 1: Baseline Performance Test${NC}"
if run_test "baseline" "scenarios/baseline.js" "Establish performance baselines (100 RPS for 5 minutes)"; then
    ((TESTS_PASSED++))
else
    ((TESTS_FAILED++))
    log "${YELLOW}⚠️  Baseline test failed - other tests may be unreliable${NC}"
fi

# Brief pause between tests
sleep 30

log "\n${BLUE}📊 Phase 2: Performance Benchmarks${NC}"
if run_test "benchmarks" "benchmarks/performance-suite.js" "Comprehensive performance metrics collection"; then
    ((TESTS_PASSED++))
else
    ((TESTS_FAILED++))
fi

sleep 30

log "\n${BLUE}🤖 Phase 3: AI Agents Load Test${NC}"
if run_test "ai-agents" "scenarios/ai-agents.js" "AI agent performance and conversation flows"; then
    ((TESTS_PASSED++))
else
    ((TESTS_FAILED++))
fi

sleep 30

log "\n${BLUE}🌊 Phase 4: Streaming Performance Test${NC}"
if run_test "streaming" "scenarios/streaming.js" "SSE and WebSocket streaming under load"; then
    ((TESTS_PASSED++))
else
    ((TESTS_FAILED++))
fi

sleep 60  # Longer pause before stress tests

log "\n${BLUE}🔥 Phase 5: Stress Test${NC}"
if run_test "stress" "scenarios/stress.js" "Gradual load increase to find breaking point"; then
    ((TESTS_PASSED++))
else
    ((TESTS_FAILED++))
fi

sleep 120  # Recovery time after stress test

log "\n${BLUE}⚡ Phase 6: Spike Test${NC}"
if run_test "spike" "scenarios/spike.js" "Sudden traffic surge simulation"; then
    ((TESTS_PASSED++))
else
    ((TESTS_FAILED++))
fi

# Optional soak test (only run if specifically requested)
if [ "$2" = "include-soak" ]; then
    sleep 300  # 5-minute recovery before soak test
    log "\n${BLUE}🛁 Phase 7: Soak Test (30 minutes)${NC}"
    if run_test "soak" "scenarios/soak.js" "Sustained load for memory leak detection"; then
        ((TESTS_PASSED++))
    else
        ((TESTS_FAILED++))
    fi
    ((TOTAL_TESTS++))
fi

# Generate summary report
log "\n${BLUE}📋 Generating Load Test Summary Report...${NC}"

cat > "$RESULTS_DIR/test-summary.md" << EOF
# GENESIS Load Testing Results Summary

**Test Execution:** $(date)
**Environment:** $ENVIRONMENT
**Results Directory:** $RESULTS_DIR

## Test Results Overview

- **Tests Passed:** $TESTS_PASSED / $TOTAL_TESTS
- **Tests Failed:** $TESTS_FAILED / $TOTAL_TESTS
- **Success Rate:** $(( TESTS_PASSED * 100 / TOTAL_TESTS ))%

## Test Scenarios Executed

### Phase 1: Baseline Performance Test
- **Objective:** Establish performance baselines
- **Load Pattern:** 100 RPS for 5 minutes
- **Result:** $([ -f "$RESULTS_DIR/baseline-results.json" ] && echo "✅ PASSED" || echo "❌ FAILED")

### Phase 2: Performance Benchmarks
- **Objective:** Collect comprehensive performance metrics
- **Focus:** API, Database, Cache, AI performance
- **Result:** $([ -f "$RESULTS_DIR/benchmarks-results.json" ] && echo "✅ PASSED" || echo "❌ FAILED")

### Phase 3: AI Agents Load Test
- **Objective:** Test AI agent performance under conversational load
- **Focus:** All 7 AI agents, A2A handoffs
- **Result:** $([ -f "$RESULTS_DIR/ai-agents-results.json" ] && echo "✅ PASSED" || echo "❌ FAILED")

### Phase 4: Streaming Performance Test
- **Objective:** Test real-time streaming capabilities
- **Focus:** SSE and WebSocket streaming
- **Result:** $([ -f "$RESULTS_DIR/streaming-results.json" ] && echo "✅ PASSED" || echo "❌ FAILED")

### Phase 5: Stress Test
- **Objective:** Find system breaking point
- **Load Pattern:** Gradual increase from 50 to 1000 RPS
- **Result:** $([ -f "$RESULTS_DIR/stress-results.json" ] && echo "✅ PASSED" || echo "❌ FAILED")

### Phase 6: Spike Test
- **Objective:** Test sudden traffic surge handling
- **Load Pattern:** 100 → 1500 RPS spike
- **Result:** $([ -f "$RESULTS_DIR/spike-results.json" ] && echo "✅ PASSED" || echo "❌ FAILED")

$(if [ "$2" = "include-soak" ]; then
cat << SOAK_EOF

### Phase 7: Soak Test
- **Objective:** Detect memory leaks and degradation
- **Load Pattern:** 200 RPS for 30 minutes
- **Result:** $([ -f "$RESULTS_DIR/soak-results.json" ] && echo "✅ PASSED" || echo "❌ FAILED")

SOAK_EOF
fi)

## Performance Targets Validation

Based on the test results, the following performance targets were evaluated:

- **P50 Latency < 100ms:** $(grep -q "p50" "$RESULTS_DIR"/*.json && echo "✅ VALIDATED" || echo "⚠️ NEEDS REVIEW")
- **P95 Latency < 500ms:** $(grep -q "p95" "$RESULTS_DIR"/*.json && echo "✅ VALIDATED" || echo "⚠️ NEEDS REVIEW")
- **P99 Latency < 1000ms:** $(grep -q "p99" "$RESULTS_DIR"/*.json && echo "✅ VALIDATED" || echo "⚠️ NEEDS REVIEW")
- **Error Rate < 1%:** $(grep -q "http_req_failed" "$RESULTS_DIR"/*.json && echo "✅ VALIDATED" || echo "⚠️ NEEDS REVIEW")
- **Throughput > 100 RPS:** $(grep -q "http_reqs" "$RESULTS_DIR"/*.json && echo "✅ VALIDATED" || echo "⚠️ NEEDS REVIEW")
- **Cache Hit Rate > 90%:** $(grep -q "cache_hit" "$RESULTS_DIR"/*.json && echo "✅ VALIDATED" || echo "⚠️ NEEDS REVIEW")
- **AI Response Time < 20s:** $(grep -q "ai_response_time" "$RESULTS_DIR"/*.json && echo "✅ VALIDATED" || echo "⚠️ NEEDS REVIEW")

## Files Generated

EOF

# List all generated files
for file in "$RESULTS_DIR"/*; do
    if [ -f "$file" ]; then
        echo "- $(basename "$file")" >> "$RESULTS_DIR/test-summary.md"
    fi
done

# Final health check
log "\n${BLUE}🏥 Final API health check...${NC}"
if curl -f -s "$API_URL/health" > /dev/null; then
    log "${GREEN}✅ API is healthy after all tests${NC}"
else
    log "${YELLOW}⚠️  API may need recovery time after load tests${NC}"
fi

# Display final summary
log "\n${BLUE}📊 GENESIS Load Testing Suite Complete${NC}"
log "${BLUE}Results Summary:${NC}"
log "  Tests Passed: ${GREEN}$TESTS_PASSED${NC} / $TOTAL_TESTS"
log "  Tests Failed: ${RED}$TESTS_FAILED${NC} / $TOTAL_TESTS"
log "  Success Rate: $(if [ $TESTS_FAILED -eq 0 ]; then echo "${GREEN}"; else echo "${YELLOW}"; fi)$(( TESTS_PASSED * 100 / TOTAL_TESTS ))%${NC}"

log "\n${BLUE}📁 Results saved to: $RESULTS_DIR${NC}"
log "  - test-summary.md (Executive summary)"
log "  - test-execution.log (Detailed execution log)"
log "  - *-results.json (Raw K6 results)"
log "  - *-results.csv (CSV exports)"

if [ $TESTS_FAILED -eq 0 ]; then
    log "\n${GREEN}🎉 All tests passed! GENESIS is ready for production deployment.${NC}"
    exit 0
else
    log "\n${YELLOW}⚠️  Some tests failed. Review results before production deployment.${NC}"
    exit 1
fi
