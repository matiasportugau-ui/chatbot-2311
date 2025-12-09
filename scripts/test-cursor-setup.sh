#!/bin/bash

# Cursor Configuration Testing Script
# Runs automated tests and provides manual testing checklist

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo -e "${CYAN}═══════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}  Cursor Configuration Testing${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════${NC}"
echo -e "Project Root: ${PROJECT_ROOT}\n"

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    echo -e "${RED}Error: Node.js is not installed${NC}"
    echo "Please install Node.js 18+ to run automated tests"
    exit 1
fi

# Check Node.js version
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo -e "${YELLOW}Warning: Node.js version is less than 18${NC}"
    echo "Some features may not work correctly"
fi

# Create reports directory
REPORTS_DIR="$PROJECT_ROOT/cursor-test-reports"
mkdir -p "$REPORTS_DIR"

# Test results
TEST_RESULTS="$REPORTS_DIR/test-results-$(date +%Y%m%d-%H%M%S).json"
PASSED=0
FAILED=0
WARNINGS=0

# Function to run a test
run_test() {
    local test_name="$1"
    local test_command="$2"
    local test_type="$3" # "automated" or "manual"
    
    echo -e "\n${BLUE}Running: ${test_name}${NC}"
    echo -e "${BLUE}Type: ${test_type}${NC}"
    
    if [ "$test_type" = "automated" ]; then
        if eval "$test_command"; then
            echo -e "${GREEN}✓ ${test_name} passed${NC}"
            PASSED=$((PASSED + 1))
            echo "{\"test\": \"$test_name\", \"status\": \"passed\", \"type\": \"$test_type\", \"timestamp\": \"$(date -Iseconds)\"}" >> "$TEST_RESULTS"
        else
            echo -e "${RED}✗ ${test_name} failed${NC}"
            FAILED=$((FAILED + 1))
            echo "{\"test\": \"$test_name\", \"status\": \"failed\", \"type\": \"$test_type\", \"timestamp\": \"$(date -Iseconds)\"}" >> "$TEST_RESULTS"
        fi
    else
        echo -e "${YELLOW}⚠ ${test_name} requires manual execution${NC}"
        WARNINGS=$((WARNINGS + 1))
        echo "{\"test\": \"$test_name\", \"status\": \"pending\", \"type\": \"$test_type\", \"timestamp\": \"$(date -Iseconds)\"}" >> "$TEST_RESULTS"
    fi
}

# Initialize test results file
echo "[" > "$TEST_RESULTS"

# Phase 1: Automated Verification
echo -e "\n${CYAN}═══════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}Phase 1: Automated Verification${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════${NC}"

# Test 1: Verify Cursor Configuration Files
run_test "Verify Cursor Configuration Files" \
    "node scripts/verify-cursor-config.js" \
    "automated"

# Test 2: Analyze Code Patterns
run_test "Analyze Code Patterns" \
    "node scripts/analyze-code-patterns.js" \
    "automated"

# Phase 2: Manual Testing Checklist
echo -e "\n${CYAN}═══════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}Phase 2: Manual Testing Checklist${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════${NC}"

echo -e "\n${YELLOW}The following tests require manual execution in Cursor:${NC}\n"

# Manual Test 1: Open Project in Cursor
echo -e "${BLUE}Manual Test 1: Open Project in Cursor${NC}"
echo "  Instructions:"
echo "    1. Open Cursor application"
echo "    2. File → Open Folder"
echo "    3. Select: $PROJECT_ROOT"
echo "    4. Verify Cursor loaded configuration"
run_test "Open Project in Cursor" "true" "manual"

# Manual Test 2: Test Agent
echo -e "\n${BLUE}Manual Test 2: Test Cursor Agent${NC}"
echo "  Instructions:"
echo "    1. Press Cmd/Ctrl + L to open chat"
echo "    2. Ask: 'How does the conversation flow work?'"
echo "    3. Verify response references ia_conversacional_integrada.py"
echo "  Prompts available in: cursor-test-prompts.md"
run_test "Test Cursor Agent" "true" "manual"

# Manual Test 3: Test @Docs
echo -e "\n${BLUE}Manual Test 3: Test @Docs Integration${NC}"
echo "  Instructions:"
echo "    1. In Cursor chat, type: @Docs Next.js How do I create an API route?"
echo "    2. Try: @Docs FastAPI How do I create an async endpoint?"
echo "    3. Verify documentation is relevant and accurate"
run_test "Test @Docs Integration" "true" "manual"

# Manual Test 4: Test Inline Edit
echo -e "\n${BLUE}Manual Test 4: Test Inline Edit${NC}"
echo "  Instructions:"
echo "    1. Open src/app/api/health/route.ts"
echo "    2. Select the handler function"
echo "    3. Press Cmd/Ctrl + K"
echo "    4. Type: 'Add rate limiting to this endpoint using withRateLimit'"
echo "    5. Review generated code"
run_test "Test Inline Edit" "true" "manual"

# Manual Test 5: Review Documentation
echo -e "\n${BLUE}Manual Test 5: Review Documentation${NC}"
echo "  Instructions:"
echo "    1. Open and read CURSOR_SETUP.md"
echo "    2. Check CURSOR_TESTING_GUIDE.md"
echo "    3. Verify documentation is complete and helpful"
run_test "Review Documentation" "true" "manual"

# Manual Test 6: Optional MCP Setup
echo -e "\n${BLUE}Manual Test 6: Optional MCP Setup${NC}"
echo "  Instructions:"
echo "    1. Read CURSOR_MCP_SETUP.md"
echo "    2. Follow setup instructions if desired"
echo "    3. Test MCP integration"
run_test "Optional MCP Setup" "true" "manual"

# Close test results JSON array
echo "]" >> "$TEST_RESULTS"

# Phase 3: Summary
echo -e "\n${CYAN}═══════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}Phase 3: Test Summary${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════${NC}"

echo -e "\n${BLUE}Results:${NC}"
echo -e "  ${GREEN}✓ Passed (Automated):${NC} $PASSED"
echo -e "  ${RED}✗ Failed (Automated):${NC} $FAILED"
echo -e "  ${YELLOW}⚠ Manual Tests:${NC} $WARNINGS"
echo -e "\nTest results saved to: $TEST_RESULTS"

# Generate summary report
SUMMARY_REPORT="$REPORTS_DIR/summary-$(date +%Y%m%d-%H%M%S).md"
cat > "$SUMMARY_REPORT" << EOF
# Cursor Configuration Test Summary

**Date:** December 1, 2025
**Project:** $PROJECT_ROOT

## Results

- **Passed (Automated):** $PASSED
- **Failed (Automated):** $FAILED
- **Manual Tests:** $WARNINGS

## Automated Tests

1. ✓ Verify Cursor Configuration Files
2. ✓ Analyze Code Patterns

## Manual Tests

1. ⚠ Open Project in Cursor
2. ⚠ Test Cursor Agent
3. ⚠ Test @Docs Integration
4. ⚠ Test Inline Edit
5. ⚠ Review Documentation
6. ⚠ Optional MCP Setup

## Next Steps

1. Complete manual tests in Cursor
2. Review test results: $TEST_RESULTS
3. Check verification reports in project root
4. Review code pattern analysis report

## Documentation

- CURSOR_SETUP.md - Setup guide
- CURSOR_TESTING_GUIDE.md - Testing guide
- cursor-test-prompts.md - Test prompts
- CURSOR_MCP_SETUP.md - MCP setup (optional)
EOF

echo -e "\nSummary report saved to: $SUMMARY_REPORT"

# Final status
if [ $FAILED -eq 0 ]; then
    echo -e "\n${GREEN}All automated tests passed!${NC}"
    echo -e "${YELLOW}Please complete manual tests in Cursor.${NC}"
    exit 0
else
    echo -e "\n${RED}Some automated tests failed!${NC}"
    echo -e "Please review the errors above and fix them."
    exit 1
fi

