#!/bin/bash

# AI Agent Deployment Script
# Non-interactive deployment script with structured JSON output
# Usage: ./scripts/deploy-ai-agent.sh [OPTIONS]

set -euo pipefail

# Color codes for output (when not in JSON mode)
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LOG_FILE="${PROJECT_ROOT}/deployment.log"
JSON_OUTPUT=false
DRY_RUN=false
VERBOSE=false
SKIP_CHECKS=false

# Deployment configuration
DEPLOY_BRANCH="${DEPLOY_BRANCH:-main}"
DEPLOY_TARGET="${DEPLOY_TARGET:-vercel}"
DEPLOY_COMMIT_MSG="${DEPLOY_COMMIT_MSG:-chore: automated deployment}"

# Exit codes
EXIT_SUCCESS=0
EXIT_ERROR=1
EXIT_WARNING=2
EXIT_HUMAN_REQUIRED=3

# Initialize JSON output structure
declare -A JSON_RESULT
JSON_RESULT["status"]=""
JSON_RESULT["step"]=""
JSON_RESULT["exit_code"]=$EXIT_SUCCESS
JSON_RESULT["timestamp"]="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

# Functions

log_json() {
    local level=$1
    shift
    local message="$*"
    echo "{\"timestamp\":\"$(date -u +"%Y-%m-%dT%H:%M:%SZ")\",\"level\":\"$level\",\"step\":\"${JSON_RESULT[step]}\",\"message\":\"$message\"}" >> "$LOG_FILE"
}

log_info() {
    if [ "$JSON_OUTPUT" = true ]; then
        log_json "info" "$@"
    else
        echo -e "${GREEN}ℹ${NC} $*"
    fi
}

log_error() {
    if [ "$JSON_OUTPUT" = true ]; then
        log_json "error" "$@"
    else
        echo -e "${RED}✗${NC} $*" >&2
    fi
}

log_warning() {
    if [ "$JSON_OUTPUT" = true ]; then
        log_json "warning" "$@"
    else
        echo -e "${YELLOW}⚠${NC} $*"
    fi
}

log_success() {
    if [ "$JSON_OUTPUT" = true ]; then
        log_json "success" "$@"
    else
        echo -e "${GREEN}✓${NC} $*"
    fi
}

output_json() {
    if [ "$JSON_OUTPUT" = true ]; then
        echo "$1"
    fi
}

output_json_result() {
    if [ "$JSON_OUTPUT" = true ]; then
        # Build JSON output manually
        local json="{"
        local first=true
        
        for key in "${!JSON_RESULT[@]}"; do
            if [ "$first" = false ]; then
                json+=","
            fi
            first=false
            json+="\"$key\":"
            
            # Check if value is already JSON (array/object) or needs quoting
            local value="${JSON_RESULT[$key]}"
            if [[ "$value" =~ ^\[.*\]$ ]] || [[ "$value" =~ ^\{.*\}$ ]]; then
                json+="$value"
            else
                # Escape quotes and wrap in quotes
                value="${value//\"/\\\"}"
                json+="\"$value\""
            fi
        done
        
        json+="}"
        echo "$json"
    fi
}

exit_with_code() {
    local code=$1
    shift
    JSON_RESULT["exit_code"]=$code
    JSON_RESULT["status"]="error"
    JSON_RESULT["message"]="$*"
    
    if [ "$JSON_OUTPUT" = true ]; then
        output_json_result
    fi
    
    exit $code
}

exit_success() {
    JSON_RESULT["status"]="success"
    JSON_RESULT["exit_code"]=$EXIT_SUCCESS
    
    if [ "$JSON_OUTPUT" = true ]; then
        output_json_result
    fi
    
    exit $EXIT_SUCCESS
}

# Check prerequisites
check_prerequisites() {
    JSON_RESULT["step"]="prerequisites"
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        exit_with_code $EXIT_ERROR "Node.js is not installed"
    fi
    
    # Check npm
    if ! command -v npm &> /dev/null; then
        exit_with_code $EXIT_ERROR "npm is not installed"
    fi
    
    # Check git
    if ! command -v git &> /dev/null; then
        exit_with_code $EXIT_ERROR "git is not installed"
    fi
    
    # Check Vercel CLI (if deploying to Vercel)
    if [ "$DEPLOY_TARGET" = "vercel" ]; then
        if ! command -v vercel &> /dev/null; then
            exit_with_code $EXIT_ERROR "Vercel CLI is not installed. Install with: npm i -g vercel"
        fi
    fi
    
    # Check jq for JSON parsing (optional but recommended)
    if ! command -v jq &> /dev/null; then
        log_warning "jq is not installed. JSON output may be limited."
    fi
    
    log_success "Prerequisites check passed"
}

# Pre-deployment checks
pre_deployment_checks() {
    JSON_RESULT["step"]="pre-deployment-checks"
    local checks_passed=true
    declare -A checks
    
    cd "$PROJECT_ROOT"
    
    # Check git status
    if git diff --quiet && git diff --cached --quiet; then
        checks["git_status"]="clean"
        log_info "Git working tree is clean"
    else
        checks["git_status"]="dirty"
        log_info "Git working tree has uncommitted changes"
    fi
    
    # Check for sensitive files
    local sensitive_files=()
    if git ls-files --error-unmatch .env.production &>/dev/null; then
        sensitive_files+=(".env.production")
        checks_passed=false
        log_error ".env.production is tracked in git!"
    fi
    
    if git ls-files --error-unmatch credentials.json &>/dev/null; then
        sensitive_files+=("credentials.json")
        checks_passed=false
        log_error "credentials.json is tracked in git!"
    fi
    
    checks["sensitive_files"]="${sensitive_files[*]}"
    
    if [ ${#sensitive_files[@]} -gt 0 ]; then
        exit_with_code $EXIT_ERROR "Sensitive files detected in git. Remove them before deploying."
    fi
    
    # Check .gitignore
    if grep -q "^\.env\.production$" .gitignore 2>/dev/null || grep -q "^\.env\.\*$" .gitignore 2>/dev/null; then
        checks["gitignore"]="ok"
        log_success ".gitignore properly configured"
    else
        checks["gitignore"]="warning"
        log_warning ".env.production may not be ignored"
    fi
    
    # Test build (if not skipping checks)
    if [ "$SKIP_CHECKS" = false ]; then
        log_info "Running build test..."
        if npm run build > /tmp/build.log 2>&1; then
            checks["build_test"]="passed"
            log_success "Build test passed"
        else
            checks["build_test"]="failed"
            checks_passed=false
            log_error "Build test failed. Check /tmp/build.log for details."
        fi
        
        # Type check
        log_info "Running TypeScript check..."
        if npm run type-check > /tmp/typecheck.log 2>&1; then
            checks["type_check"]="passed"
            log_success "TypeScript check passed"
        else
            checks["type_check"]="failed"
            checks_passed=false
            log_error "TypeScript check failed. Check /tmp/typecheck.log for details."
        fi
    else
        checks["build_test"]="skipped"
        checks["type_check"]="skipped"
        log_warning "Checks skipped (--skip-checks flag)"
    fi
    
    # Convert checks associative array to JSON
    local checks_json="{"
    local first_check=true
    for key in "${!checks[@]}"; do
        if [ "$first_check" = false ]; then
            checks_json+=","
        fi
        first_check=false
        checks_json+="\"$key\":\"${checks[$key]}\""
    done
    checks_json+="}"
    JSON_RESULT["checks"]="$checks_json"
    
    if [ "$checks_passed" = false ]; then
        exit_with_code $EXIT_ERROR "Pre-deployment checks failed"
    fi
    
    log_success "All pre-deployment checks passed"
}

# Build test
build_test() {
    JSON_RESULT["step"]="build-test"
    local start_time=$(date +%s)
    
    cd "$PROJECT_ROOT"
    
    log_info "Running build..."
    
    if [ "$DRY_RUN" = true ]; then
        log_info "[DRY RUN] Would run: npm run build"
        JSON_RESULT["build_time"]=0
        JSON_RESULT["status"]="success"
        return
    fi
    
    if npm run build > /tmp/build.log 2>&1; then
        local end_time=$(date +%s)
        local build_time=$((end_time - start_time))
        JSON_RESULT["build_time"]=$build_time
        JSON_RESULT["warnings"]="[]"
        JSON_RESULT["errors"]="[]"
        log_success "Build completed in ${build_time}s"
    else
        local errors=$(grep -i "error" /tmp/build.log | head -5 || echo "[]")
        JSON_RESULT["errors"]="$errors"
        exit_with_code $EXIT_ERROR "Build failed. Check /tmp/build.log for details."
    fi
}

# Commit changes
commit_changes() {
    JSON_RESULT["step"]="commit"
    
    cd "$PROJECT_ROOT"
    
    # Check if there are changes to commit
    if git diff --quiet && git diff --cached --quiet; then
        log_info "No changes to commit"
        JSON_RESULT["commit_hash"]=""
        JSON_RESULT["files_changed"]=0
        return
    fi
    
    local files_changed=$(git diff --name-only | wc -l)
    JSON_RESULT["files_changed"]=$files_changed
    
    if [ "$DRY_RUN" = true ]; then
        log_info "[DRY RUN] Would commit $files_changed files"
        JSON_RESULT["commit_hash"]="dry-run"
        return
    fi
    
    log_info "Staging $files_changed files..."
    git add .
    
    log_info "Committing changes..."
    if git commit -m "$DEPLOY_COMMIT_MSG" > /tmp/commit.log 2>&1; then
        local commit_hash=$(git rev-parse --short HEAD)
        JSON_RESULT["commit_hash"]=$commit_hash
        log_success "Committed changes: $commit_hash"
    else
        exit_with_code $EXIT_ERROR "Commit failed. Check /tmp/commit.log for details."
    fi
}

# Push to repository
push_changes() {
    JSON_RESULT["step"]="push"
    
    cd "$PROJECT_ROOT"
    
    # Check if branch exists
    if ! git show-ref --verify --quiet refs/heads/"$DEPLOY_BRANCH"; then
        exit_with_code $EXIT_ERROR "Branch $DEPLOY_BRANCH does not exist"
    fi
    
    # Check if there are commits to push
    local commits_ahead=$(git rev-list --count origin/"$DEPLOY_BRANCH"..HEAD 2>/dev/null || echo "0")
    
    if [ "$commits_ahead" -eq 0 ]; then
        log_info "No commits to push"
        JSON_RESULT["commits_pushed"]=0
        return
    fi
    
    JSON_RESULT["branch"]="$DEPLOY_BRANCH"
    JSON_RESULT["remote"]="origin"
    JSON_RESULT["commits_pushed"]=$commits_ahead
    
    if [ "$DRY_RUN" = true ]; then
        log_info "[DRY RUN] Would push $commits_ahead commits to $DEPLOY_BRANCH"
        return
    fi
    
    log_info "Pushing $commits_ahead commits to $DEPLOY_BRANCH..."
    
    if git push origin "$DEPLOY_BRANCH" > /tmp/push.log 2>&1; then
        log_success "Pushed to $DEPLOY_BRANCH"
    else
        # Check for authentication errors
        if grep -qi "authentication\|permission\|denied" /tmp/push.log; then
            exit_with_code $EXIT_HUMAN_REQUIRED "Git authentication failed. Check credentials."
        fi
        
        # Check for conflicts
        if grep -qi "conflict\|rejected" /tmp/push.log; then
            exit_with_code $EXIT_WARNING "Push rejected. May need merge/rebase."
        fi
        
        exit_with_code $EXIT_ERROR "Push failed. Check /tmp/push.log for details."
    fi
}

# Deploy to Vercel
deploy_vercel() {
    JSON_RESULT["step"]="deploy"
    JSON_RESULT["target"]="vercel"
    
    cd "$PROJECT_ROOT"
    
    if [ "$DRY_RUN" = true ]; then
        log_info "[DRY RUN] Would deploy to Vercel"
        JSON_RESULT["deployment_url"]="dry-run"
        JSON_RESULT["deployment_id"]="dry-run"
        return
    fi
    
    log_info "Deploying to Vercel..."
    
    # Deploy to production
    local deploy_output=$(vercel --prod --yes 2>&1)
    local deploy_exit=$?
    
    if [ $deploy_exit -ne 0 ]; then
        # Check for common errors
        if echo "$deploy_output" | grep -qi "environment.*variable"; then
            exit_with_code $EXIT_ERROR "Missing environment variables. Check Vercel dashboard."
        fi
        
        if echo "$deploy_output" | grep -qi "quota\|limit"; then
            exit_with_code $EXIT_HUMAN_REQUIRED "Vercel quota exceeded. Requires human intervention."
        fi
        
        exit_with_code $EXIT_ERROR "Vercel deployment failed: $deploy_output"
    fi
    
    # Extract deployment URL and ID from output
    local deployment_url=$(echo "$deploy_output" | grep -oP 'https://[^\s]+\.vercel\.app' | head -1 || echo "")
    local deployment_id=$(echo "$deploy_output" | grep -oP 'dpl_[a-zA-Z0-9]+' | head -1 || echo "")
    
    JSON_RESULT["deployment_url"]="$deployment_url"
    JSON_RESULT["deployment_id"]="$deployment_id"
    
    log_success "Deployed to Vercel: $deployment_url"
}

# Verify deployment
verify_deployment() {
    JSON_RESULT["step"]="verification"
    local url="${1:-}"
    
    if [ -z "$url" ]; then
        # Try to get URL from previous deployment
        url="${JSON_RESULT[deployment_url]:-}"
    fi
    
    if [ -z "$url" ]; then
        exit_with_code $EXIT_ERROR "No deployment URL provided for verification"
    fi
    
    JSON_RESULT["url"]="$url"
    
    log_info "Verifying deployment at $url..."
    
    # Check if URL is accessible
    local http_code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "$url" || echo "000")
    
    if [ "$http_code" = "200" ]; then
        JSON_RESULT["url_accessible"]=true
        log_success "Deployment URL is accessible"
    else
        JSON_RESULT["url_accessible"]=false
        exit_with_code $EXIT_ERROR "Deployment URL returned HTTP $http_code"
    fi
    
    # Check API endpoints (if known)
    local api_endpoints=("/api/quotes" "/api/whatsapp/webhook")
    local accessible_endpoints=()
    
    for endpoint in "${api_endpoints[@]}"; do
        local endpoint_url="${url}${endpoint}"
        local endpoint_code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 "$endpoint_url" || echo "000")
        
        if [ "$endpoint_code" = "200" ] || [ "$endpoint_code" = "405" ] || [ "$endpoint_code" = "404" ]; then
            accessible_endpoints+=("$endpoint")
        fi
    done
    
    JSON_RESULT["api_endpoints"]="$(IFS=','; echo "${accessible_endpoints[*]}")"
    
    log_success "Verification completed"
}

# Rollback deployment
rollback_deployment() {
    JSON_RESULT["step"]="rollback"
    local deployment_id="${1:-}"
    
    if [ -z "$deployment_id" ]; then
        exit_with_code $EXIT_ERROR "Deployment ID required for rollback"
    fi
    
    JSON_RESULT["previous_deployment"]="$deployment_id"
    
    if [ "$DRY_RUN" = true ]; then
        log_info "[DRY RUN] Would rollback to $deployment_id"
        JSON_RESULT["rollback_complete"]=true
        return
    fi
    
    log_info "Rolling back to deployment $deployment_id..."
    
    # Vercel rollback
    if vercel rollback "$deployment_id" --yes > /tmp/rollback.log 2>&1; then
        JSON_RESULT["rollback_complete"]=true
        log_success "Rollback completed"
    else
        exit_with_code $EXIT_ERROR "Rollback failed. Check /tmp/rollback.log for details."
    fi
}

# Full deployment workflow
full_deployment() {
    local start_time=$(date +%s)
    JSON_RESULT["step"]="full-deployment"
    
    log_info "Starting full deployment workflow..."
    
    # Step 1: Prerequisites
    check_prerequisites
    
    # Step 2: Pre-deployment checks
    if [ "$SKIP_CHECKS" = false ]; then
        pre_deployment_checks
    fi
    
    # Step 3: Build test
    build_test
    
    # Step 4: Commit (if needed)
    commit_changes
    
    # Step 5: Push
    push_changes
    
    # Step 6: Deploy
    case "$DEPLOY_TARGET" in
        "vercel")
            deploy_vercel
            ;;
        *)
            exit_with_code $EXIT_ERROR "Unsupported deployment target: $DEPLOY_TARGET"
            ;;
    esac
    
    # Step 7: Verify
    verify_deployment "${JSON_RESULT[deployment_url]}"
    
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    JSON_RESULT["duration_seconds"]=$duration
    JSON_RESULT["steps_completed"]="[\"prerequisites\",\"pre-deployment-checks\",\"build-test\",\"commit\",\"push\",\"deploy\",\"verification\"]"
    
    log_success "Full deployment completed in ${duration}s"
}

# Parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --json)
                JSON_OUTPUT=true
                shift
                ;;
            --dry-run)
                DRY_RUN=true
                shift
                ;;
            --verbose)
                VERBOSE=true
                shift
                ;;
            --skip-checks)
                SKIP_CHECKS=true
                shift
                ;;
            --check-only)
                JSON_OUTPUT=true
                check_prerequisites
                pre_deployment_checks
                exit_success
                ;;
            --build-test)
                JSON_OUTPUT=true
                check_prerequisites
                build_test
                exit_success
                ;;
            --commit)
                JSON_OUTPUT=true
                commit_changes
                exit_success
                ;;
            --push)
                JSON_OUTPUT=true
                push_changes
                exit_success
                ;;
            --deploy)
                JSON_OUTPUT=true
                shift
                local target="${1:-vercel}"
                DEPLOY_TARGET="$target"
                case "$target" in
                    vercel)
                        deploy_vercel
                        ;;
                    *)
                        exit_with_code $EXIT_ERROR "Unsupported target: $target"
                        ;;
                esac
                exit_success
                ;;
            --verify)
                JSON_OUTPUT=true
                shift
                local url="${1:-}"
                verify_deployment "$url"
                exit_success
                ;;
            --rollback)
                JSON_OUTPUT=true
                shift
                local deployment_id="${1:-}"
                rollback_deployment "$deployment_id"
                exit_success
                ;;
            --full-deployment)
                JSON_OUTPUT=true
                full_deployment
                exit_success
                ;;
            --branch)
                shift
                DEPLOY_BRANCH="${1:-main}"
                shift
                ;;
            --message)
                shift
                DEPLOY_COMMIT_MSG="${1:-chore: automated deployment}"
                shift
                ;;
            --target)
                shift
                DEPLOY_TARGET="${1:-vercel}"
                shift
                ;;
            --production)
                # Flag for production deployment (already default)
                shift
                ;;
            -h|--help)
                cat << EOF
AI Agent Deployment Script

Usage: $0 [OPTIONS]

Options:
  --json              Output results in JSON format
  --dry-run           Simulate deployment without making changes
  --verbose           Enable verbose logging
  --skip-checks       Skip pre-deployment checks
  --check-only        Run pre-deployment checks only
  --build-test        Run build test only
  --commit            Commit changes only
  --push              Push changes only
  --deploy TARGET     Deploy to specified target (vercel)
  --verify URL        Verify deployment at URL
  --rollback ID       Rollback to deployment ID
  --full-deployment   Execute complete deployment workflow
  --branch BRANCH     Specify branch (default: main)
  --message MSG       Commit message (default: "chore: automated deployment")
  --target TARGET     Deployment target (default: vercel)
  --production        Deploy to production (default)

Environment Variables:
  DEPLOY_BRANCH       Branch to deploy (default: main)
  DEPLOY_TARGET       Deployment target (default: vercel)
  DEPLOY_COMMIT_MSG   Commit message

Exit Codes:
  0  Success
  1  Error
  2  Warning
  3  Human intervention required

Examples:
  $0 --full-deployment --json
  $0 --check-only --json
  $0 --deploy vercel --production --json
EOF
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                exit_with_code $EXIT_ERROR "Unknown option: $1"
                ;;
        esac
    done
}

# Main execution
main() {
    # Initialize log file
    touch "$LOG_FILE"
    log_json "info" "Deployment script started"
    
    # Parse arguments
    parse_args "$@"
    
    # If no specific action was requested, show help
    if [ $# -eq 0 ]; then
        parse_args --help
    fi
}

# Run main function
main "$@"
