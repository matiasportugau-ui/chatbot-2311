# 🤖 AI Agent Deployment Instructions

## Role Definition

You are an AI agent responsible for automating the deployment of the BMC Quote System to production. Your goal is to execute a complete deployment workflow without human intervention, handling errors gracefully and providing structured feedback.

## Prerequisites

Before starting, verify:
- [ ] Git repository is initialized and configured
- [ ] Vercel CLI is installed (`npm i -g vercel`)
- [ ] Vercel project is linked (`vercel link` or configured via environment)
- [ ] Environment variables are set in Vercel dashboard
- [ ] You have read access to the repository
- [ ] You have write access to the repository (for commits/pushes)

## Execution Plan

### Phase 1: Pre-Deployment Validation (2-3 minutes)

#### Step 1.1: Run Prerequisites Check
```bash
./scripts/deploy-ai-agent.sh --check-only --json
```

**Expected Output:**
```json
{
  "status": "success",
  "step": "pre-deployment-checks",
  "checks": {
    "git_status": "clean|dirty",
    "sensitive_files": [],
    "gitignore": "ok|warning",
    "build_test": "passed|failed|skipped",
    "type_check": "passed|failed|skipped"
  },
  "exit_code": 0
}
```

**Decision Logic:**
- If `exit_code == 0`: Proceed to Step 1.2
- If `exit_code == 1`: Stop deployment, report error
- If `exit_code == 3`: Stop deployment, request human intervention

**Common Issues:**
- **Sensitive files detected**: Remove from git tracking, update .gitignore
- **Build/type check failed**: Review error logs, fix issues, retry
- **Git status dirty**: Decide whether to commit or stash changes

#### Step 1.2: Verify Build Test
```bash
./scripts/deploy-ai-agent.sh --build-test --json
```

**Expected Output:**
```json
{
  "status": "success",
  "step": "build-test",
  "build_time": 45,
  "warnings": [],
  "errors": [],
  "exit_code": 0
}
```

**Decision Logic:**
- If `exit_code == 0`: Proceed to Phase 2
- If `exit_code == 1`: Review build errors, fix issues, retry
- If build time > 300 seconds: Log warning but proceed

### Phase 2: Code Preparation (1-2 minutes)

#### Step 2.1: Check Git Status
```bash
git status --porcelain
```

**Decision Logic:**
- If output is empty: Skip to Phase 3
- If output has files: Proceed to Step 2.2

#### Step 2.2: Commit Changes (if needed)
```bash
./scripts/deploy-ai-agent.sh --commit --json --message "chore: automated deployment [timestamp]"
```

**Expected Output:**
```json
{
  "status": "success",
  "step": "commit",
  "commit_hash": "abc123",
  "files_changed": 5,
  "exit_code": 0
}
```

**Decision Logic:**
- If `exit_code == 0`: Proceed to Step 2.3
- If `exit_code == 1`: Review commit error, fix issues
- If `files_changed == 0`: Skip commit, proceed to Phase 3

**Commit Message Format:**
- Use descriptive messages: `chore: automated deployment [ISO timestamp]`
- Include context: `feat: add new feature`, `fix: resolve bug`
- Avoid generic messages: `update`, `changes`

### Phase 3: Push to Repository (30 seconds - 1 minute)

#### Step 3.1: Push Changes
```bash
./scripts/deploy-ai-agent.sh --push --json --branch main
```

**Expected Output:**
```json
{
  "status": "success",
  "step": "push",
  "branch": "main",
  "remote": "origin",
  "commits_pushed": 1,
  "exit_code": 0
}
```

**Decision Logic:**
- If `exit_code == 0`: Proceed to Phase 4
- If `exit_code == 1`: Check error logs, retry once
- If `exit_code == 3`: Authentication issue, request human intervention
- If `exit_code == 2`: Branch conflict, may need merge/rebase

**Error Handling:**
- **Authentication failure**: Exit with code 3, request credentials
- **Network error**: Retry once after 5 seconds
- **Branch conflict**: Exit with code 2, suggest manual resolution

### Phase 4: Deployment (2-5 minutes)

#### Step 4.1: Deploy to Vercel
```bash
./scripts/deploy-ai-agent.sh --deploy vercel --production --json
```

**Expected Output:**
```json
{
  "status": "success",
  "step": "deploy",
  "target": "vercel",
  "deployment_url": "https://your-app.vercel.app",
  "deployment_id": "dpl_abc123",
  "exit_code": 0
}
```

**Decision Logic:**
- If `exit_code == 0`: Proceed to Phase 5
- If `exit_code == 1`: Review deployment logs, check environment variables
- If `exit_code == 3`: Quota/limit issue, request human intervention

**Common Issues:**
- **Missing environment variables**: List missing vars, exit with code 1
- **Build timeout**: Suggest optimization, exit with code 2
- **Quota exceeded**: Exit with code 3, request human intervention
- **Network issues**: Retry once after 10 seconds

**Wait for Deployment:**
- Vercel deployments typically take 2-5 minutes
- Monitor deployment status via Vercel API or dashboard
- Do not proceed to verification until deployment is complete

### Phase 5: Verification (1-2 minutes)

#### Step 5.1: Verify Deployment
```bash
./scripts/deploy-ai-agent.sh --verify --json https://your-app.vercel.app
```

**Expected Output:**
```json
{
  "status": "success",
  "step": "verification",
  "url": "https://your-app.vercel.app",
  "url_accessible": true,
  "api_endpoints": "/api/quotes,/api/whatsapp/webhook",
  "exit_code": 0
}
```

**Decision Logic:**
- If `exit_code == 0` and `url_accessible == true`: Deployment successful
- If `exit_code == 1`: Trigger rollback (Step 5.2)
- If HTTP code != 200: Trigger rollback

**Verification Criteria:**
- ✅ Deployment URL returns HTTP 200
- ✅ Critical API endpoints are accessible
- ✅ No critical errors in deployment logs
- ✅ Response times are acceptable (< 1 second)

#### Step 5.2: Rollback (if verification fails)
```bash
./scripts/deploy-ai-agent.sh --rollback --json dpl_previous_deployment_id
```

**Expected Output:**
```json
{
  "status": "success",
  "step": "rollback",
  "previous_deployment": "dpl_previous",
  "rollback_complete": true,
  "exit_code": 0
}
```

**Decision Logic:**
- Always rollback if verification fails
- Log rollback reason for analysis
- Notify about rollback completion

## Complete Workflow Execution

For a complete automated deployment, use:

```bash
./scripts/deploy-ai-agent.sh --full-deployment --json
```

This executes all phases sequentially and provides a complete summary:

**Expected Output:**
```json
{
  "status": "success",
  "step": "full-deployment",
  "deployment_id": "dpl_abc123",
  "deployment_url": "https://your-app.vercel.app",
  "steps_completed": [
    "prerequisites",
    "pre-deployment-checks",
    "build-test",
    "commit",
    "push",
    "deploy",
    "verification"
  ],
  "duration_seconds": 180,
  "exit_code": 0
}
```

## Error Handling Procedures

### Error Categories

#### Category 1: Recoverable Errors (Retry)
- Network timeouts
- Temporary service unavailability
- Rate limiting (with backoff)

**Action:** Retry up to 2 times with exponential backoff (5s, 10s)

#### Category 2: Fixable Errors (Fix and Retry)
- Build errors (TypeScript, ESLint)
- Missing dependencies
- Configuration issues

**Action:** Attempt to fix automatically, retry once, then exit with code 1

#### Category 3: Human Intervention Required (Stop)
- Authentication failures
- Quota/limit exceeded
- Critical configuration missing
- Sensitive files in git

**Action:** Exit with code 3, provide detailed error message

#### Category 4: Deployment Failures (Rollback)
- Deployment succeeds but verification fails
- Critical endpoints return errors
- Application crashes on startup

**Action:** Trigger rollback, exit with code 1

### Decision Tree

```
START DEPLOYMENT
│
├─> Prerequisites Check
│   ├─> PASS → Continue
│   └─> FAIL → Exit(1) or Exit(3)
│
├─> Pre-Deployment Checks
│   ├─> PASS → Continue
│   ├─> FAIL (fixable) → Fix, Retry
│   └─> FAIL (critical) → Exit(1)
│
├─> Build Test
│   ├─> PASS → Continue
│   └─> FAIL → Fix, Retry, or Exit(1)
│
├─> Commit Changes
│   ├─> No changes → Skip
│   ├─> Commit success → Continue
│   └─> Commit fail → Exit(1)
│
├─> Push Changes
│   ├─> Success → Continue
│   ├─> Auth error → Exit(3)
│   └─> Conflict → Exit(2)
│
├─> Deploy to Vercel
│   ├─> Success → Continue
│   ├─> Env vars missing → Exit(1)
│   └─> Quota exceeded → Exit(3)
│
├─> Verify Deployment
│   ├─> PASS → SUCCESS
│   └─> FAIL → Rollback → Exit(1)
│
END
```

## Structured Output Format

All commands should be executed with `--json` flag for structured output. Parse JSON responses to make decisions.

### Output Structure
```json
{
  "status": "success|error|warning",
  "step": "step-name",
  "exit_code": 0|1|2|3,
  "timestamp": "ISO-8601",
  "message": "Human-readable message",
  "data": {
    // Step-specific data
  }
}
```

### Logging

All operations are logged to `deployment.log` in JSON Lines format:
```json
{"timestamp": "2024-01-15T10:30:00Z", "level": "info", "step": "build", "message": "Build started"}
{"timestamp": "2024-01-15T10:30:45Z", "level": "success", "step": "build", "message": "Build completed"}
```

Monitor this log file for detailed execution history.

## Verification Checklist

Before considering deployment successful, verify:

- [ ] All pre-deployment checks passed
- [ ] Build completed without errors
- [ ] Code committed (if changes existed)
- [ ] Code pushed to repository
- [ ] Vercel deployment completed
- [ ] Deployment URL is accessible (HTTP 200)
- [ ] Critical API endpoints respond correctly
- [ ] No critical errors in deployment logs
- [ ] Response times are acceptable

## Rollback Triggers

Automatically trigger rollback if:

1. **Deployment verification fails**
   - URL returns non-200 HTTP code
   - Critical endpoints unavailable
   - Application crashes on startup

2. **Post-deployment errors detected**
   - Database connection failures
   - Critical environment variables missing
   - Application errors in logs

3. **Performance degradation**
   - Response times > 5 seconds
   - Error rate > 10%

## Dry-Run Mode

Test deployment without making changes:

```bash
./scripts/deploy-ai-agent.sh --full-deployment --dry-run --json
```

Use this to:
- Validate deployment logic
- Check for potential issues
- Test error handling
- Verify script functionality

## Environment Variables

Override defaults via environment variables:

```bash
export DEPLOY_BRANCH=main
export DEPLOY_TARGET=vercel
export SKIP_CHECKS=false
export VERBOSE=true
./scripts/deploy-ai-agent.sh --full-deployment --json
```

## Exit Code Reference

| Code | Meaning | Action |
|------|---------|--------|
| 0 | Success | Deployment completed successfully |
| 1 | Error | Critical error, deployment failed |
| 2 | Warning | Non-critical issue, deployment may proceed |
| 3 | Human Required | Requires human intervention |

## Best Practices

1. **Always use `--json` flag** for structured output
2. **Check exit codes** before proceeding to next step
3. **Log all operations** for audit trail
4. **Handle errors gracefully** with appropriate retries
5. **Verify deployment** before marking as successful
6. **Rollback on failure** to maintain system stability
7. **Use dry-run** to test changes before actual deployment
8. **Monitor logs** for detailed execution information

## Troubleshooting

### Common Issues

**Issue:** Script not executable
```bash
chmod +x scripts/deploy-ai-agent.sh
```

**Issue:** Vercel CLI not found
```bash
npm install -g vercel
```

**Issue:** JSON parsing fails
```bash
# Install jq for better JSON parsing
sudo apt-get install jq  # Linux
brew install jq          # macOS
```

**Issue:** Git authentication fails
- Check git credentials
- Verify SSH keys or HTTPS tokens
- May require human intervention (exit code 3)

## Related Documentation

- **`DEPLOYMENT_SUMMARY.md`** - Overview and human-readable guide
- **`scripts/deploy-ai-agent.sh`** - Deployment script implementation
- **`DEPLOYMENT_GUIDE.md`** - Detailed deployment instructions
- **`DEPLOYMENT_ENV_VARS.md`** - Required environment variables

## Success Criteria

Deployment is considered successful when:

1. ✅ All phases complete without errors
2. ✅ Deployment URL is accessible
3. ✅ Critical endpoints respond correctly
4. ✅ No rollback was triggered
5. ✅ Exit code is 0
6. ✅ Verification checklist is complete

## Notes

- Always run in dry-run mode first when testing
- Monitor deployment logs for detailed information
- Keep deployment.log for audit purposes
- Report any issues or improvements needed
- Follow the decision tree for consistent error handling
