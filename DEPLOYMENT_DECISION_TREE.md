# 🌳 Deployment Decision Tree & Error Handling

## Overview

This document defines the decision logic and error handling procedures for automated AI agent deployments. It provides structured guidance for handling various scenarios during the deployment process.

## Decision Tree Structure

```
┌─────────────────────────────────────────────────────────────┐
│                    START DEPLOYMENT                         │
└───────────────────────────┬───────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│          PHASE 1: PREREQUISITES CHECK                       │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Check: Node.js, npm, git, Vercel CLI installed      │  │
│  └───────────────────┬──────────────────────────────────┘  │
│                      │                                      │
│         ┌────────────┴────────────┐                         │
│         │                        │                          │
│    ┌────▼────┐            ┌─────▼─────┐                   │
│    │  PASS   │            │   FAIL     │                   │
│    └────┬────┘            └─────┬─────┘                   │
│         │                       │                          │
│         │                  ┌─────▼─────┐                   │
│         │                  │ Exit(1)   │                   │
│         │                  │ Report    │                   │
│         │                  └───────────┘                   │
└─────────┼───────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────┐
│      PHASE 2: PRE-DEPLOYMENT CHECKS                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Check: Git status, sensitive files, build, typecheck │  │
│  └───────────────────┬──────────────────────────────────┘  │
│                      │                                      │
│    ┌─────────────────┼─────────────────┐                   │
│    │                 │                 │                   │
│ ┌──▼──┐        ┌─────▼─────┐    ┌─────▼─────┐            │
│ │PASS │        │  WARNING   │    │   FAIL    │            │
│ └──┬──┘        └─────┬─────┘    └─────┬─────┘            │
│    │                 │                 │                   │
│    │            ┌────▼─────┐    ┌─────▼─────┐            │
│    │            │ Continue  │    │  Fixable? │            │
│    │            │ with log  │    └─────┬─────┘            │
│    │            └──────────┘          │                  │
│    │                            ┌──────┴──────┐           │
│    │                            │              │           │
│    │                      ┌─────▼─────┐  ┌───▼────┐      │
│    │                      │    YES     │  │   NO   │      │
│    │                      └─────┬─────┘  └───┬────┘      │
│    │                            │            │            │
│    │                      ┌─────▼─────┐  ┌──▼─────┐      │
│    │                      │ Fix & Retry│  │Exit(1) │      │
│    │                      └────────────┘  └────────┘      │
└────┼───────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────────┐
│          PHASE 3: BUILD TEST                                │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Run: npm run build, npm run type-check               │  │
│  └───────────────────┬──────────────────────────────────┘  │
│                      │                                      │
│         ┌────────────┴────────────┐                         │
│         │                        │                          │
│    ┌────▼────┐            ┌─────▼─────┐                   │
│    │  PASS   │            │   FAIL     │                   │
│    └────┬────┘            └─────┬─────┘                   │
│         │                       │                          │
│         │                  ┌─────▼─────┐                   │
│         │                  │ Error Type │                   │
│         │                  └─────┬─────┘                   │
│         │                        │                          │
│         │          ┌─────────────┼─────────────┐            │
│         │          │             │             │            │
│         │    ┌─────▼─────┐ ┌────▼────┐ ┌─────▼─────┐      │
│         │    │ TypeScript │ │ Build   │ │ Dependency│      │
│         │    │   Error    │ │ Error   │ │  Missing  │      │
│         │    └─────┬─────┘ └────┬────┘ └─────┬─────┘      │
│         │          │            │            │             │
│         │          │      ┌─────▼─────┐      │            │
│         │          │      │ Fix & Retry│      │            │
│         │          │      └────────────┘      │            │
│         │          │            │            │            │
│         │          │      ┌─────▼─────┐      │            │
│         │          │      │ Max Retries│      │            │
│         │          │      └─────┬─────┘      │            │
│         │          │            │             │            │
│         │          │      ┌─────▼─────┐      │            │
│         │          │      │ Exit(1)   │      │            │
│         │          │      └───────────┘      │            │
└─────────┼───────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────┐
│          PHASE 4: GIT OPERATIONS                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Check: git status, commit changes, push to remote   │  │
│  └───────────────────┬──────────────────────────────────┘  │
│                      │                                      │
│              ┌───────▼────────┐                            │
│              │  Git Status    │                            │
│              └───────┬────────┘                            │
│                      │                                     │
│         ┌────────────┴────────────┐                        │
│         │                        │                         │
│    ┌────▼────┐            ┌─────▼─────┐                  │
│    │  CLEAN  │            │   DIRTY    │                  │
│    └────┬────┘            └─────┬─────┘                  │
│         │                       │                         │
│         │                  ┌────▼─────┐                   │
│         │                  │  Commit   │                   │
│         │                  └────┬─────┘                   │
│         │                       │                         │
│         │                  ┌────▼─────┐                   │
│         │                  │  Success?│                   │
│         │                  └────┬─────┘                   │
│         │                       │                         │
│         │          ┌────────────┴────────────┐            │
│         │          │                        │             │
│         │    ┌─────▼─────┐          ┌──────▼─────┐       │
│         │    │    YES     │          │     NO     │       │
│         │    └─────┬─────┘          └──────┬─────┘       │
│         │          │                        │             │
│         │          │                  ┌─────▼─────┐       │
│         │          │                  │ Exit(1)   │       │
│         │          │                  └───────────┘       │
│         │          │                                      │
│         │          ▼                                      │
│         │    ┌─────────────────┐                          │
│         │    │   Push Changes  │                          │
│         │    └────────┬────────┘                          │
│         │             │                                   │
│         │      ┌───────▼────────┐                         │
│         │      │  Push Result    │                         │
│         │      └───────┬────────┘                         │
│         │              │                                  │
│         │   ┌──────────┼──────────┐                       │
│         │   │          │          │                       │
│         │ ┌─▼──┐   ┌───▼───┐  ┌──▼────┐                 │
│         │ │ OK │   │ Auth  │  │Conflict│                 │
│         │ └─┬──┘   └───┬───┘  └───┬────┘                 │
│         │   │          │          │                       │
│         │   │    ┌─────▼─────┐   │                       │
│         │   │    │ Exit(3)   │   │                       │
│         │   │    └───────────┘   │                       │
│         │   │                    │                       │
│         │   │              ┌─────▼─────┐                │
│         │   │              │ Exit(2)   │                │
│         │   │              └───────────┘                │
└─────────┼───────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────┐
│          PHASE 5: DEPLOYMENT                                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Deploy: vercel --prod                                │  │
│  └───────────────────┬──────────────────────────────────┘  │
│                      │                                      │
│         ┌────────────┴────────────┐                         │
│         │                        │                          │
│    ┌────▼────┐            ┌─────▼─────┐                   │
│    │ SUCCESS │            │   FAIL     │                   │
│    └────┬────┘            └─────┬─────┘                   │
│         │                       │                          │
│         │                  ┌─────▼─────┐                   │
│         │                  │ Error Type │                   │
│         │                  └─────┬─────┘                   │
│         │                        │                          │
│         │    ┌───────────────────┼───────────────────┐      │
│         │    │                   │                   │      │
│         │ ┌──▼───┐         ┌─────▼─────┐      ┌─────▼─────┐│
│         │ │ Env  │         │  Timeout  │      │  Quota    ││
│         │ │ Vars │         │           │      │  Exceeded ││
│         │ └──┬───┘         └─────┬─────┘      └─────┬─────┘│
│         │    │                  │                   │      │
│         │    │            ┌─────▼─────┐      ┌─────▼─────┐ │
│         │    │            │ Retry(1)  │      │ Exit(3)   │ │
│         │    │            └───────────┘      └───────────┘ │
│         │    │                                            │
│         │ ┌──▼─────┐                                      │
│         │ │Exit(1) │                                      │
│         │ └────────┘                                      │
└─────────┼───────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────┐
│          PHASE 6: VERIFICATION                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ Verify: URL accessible, endpoints respond             │  │
│  └───────────────────┬──────────────────────────────────┘  │
│                      │                                      │
│         ┌────────────┴────────────┐                         │
│         │                        │                          │
│    ┌────▼────┐            ┌─────▼─────┐                   │
│    │  PASS   │            │   FAIL     │                   │
│    └────┬────┘            └─────┬─────┘                   │
│         │                       │                          │
│         │                  ┌─────▼─────┐                   │
│         │                  │ ROLLBACK  │                   │
│         │                  └─────┬─────┘                   │
│         │                       │                          │
│         │                  ┌─────▼─────┐                   │
│         │                  │ Exit(1)   │                   │
│         │                  └───────────┘                   │
│         │                                                  │
│         ▼                                                  │
│    ┌──────────┐                                            │
│    │ SUCCESS  │                                            │
│    │ Exit(0)  │                                            │
│    └──────────┘                                            │
└─────────────────────────────────────────────────────────────┘
```

## Error Classification

### Category 1: Recoverable Errors (Retry with Backoff)

**Characteristics:**
- Temporary network issues
- Service unavailability
- Rate limiting
- Timeout errors

**Handling:**
1. Retry up to 2 times
2. Exponential backoff: 5s, 10s
3. Log each retry attempt
4. If all retries fail → escalate to Category 2

**Examples:**
- Network timeout during git push
- Vercel API rate limit
- Temporary DNS resolution failure

### Category 2: Fixable Errors (Auto-Fix and Retry)

**Characteristics:**
- Build errors (syntax, type errors)
- Missing dependencies
- Configuration issues
- Git conflicts (simple merge)

**Handling:**
1. Attempt automatic fix
2. Retry operation once
3. If fix fails → exit with code 1
4. Log fix attempt and result

**Examples:**
- TypeScript compilation errors
- Missing npm packages
- ESLint errors
- Simple git merge conflicts

**Auto-Fix Strategies:**
- **TypeScript errors**: Report specific errors, suggest fixes
- **Missing dependencies**: Run `npm install`
- **ESLint errors**: Report violations, suggest fixes
- **Git conflicts**: Attempt simple merge, if complex → exit(2)

### Category 3: Human Intervention Required (Stop)

**Characteristics:**
- Authentication failures
- Quota/limit exceeded
- Critical configuration missing
- Sensitive files in git
- Complex merge conflicts
- Vercel Root Directory misconfiguration

**Handling:**
1. Stop deployment immediately
2. Exit with code 3
3. Provide detailed error message
4. Suggest resolution steps
5. Log for human review

**Examples:**
- Git authentication failure
- Vercel quota exceeded
- Missing critical environment variables
- `.env.production` tracked in git
- Complex branch conflicts requiring manual resolution
- **Vercel Root Directory error:** "The specified Root Directory does not exist"
  - **Resolution:** Go to Vercel Dashboard → Settings → General → Clear Root Directory field

### Category 4: Deployment Failures (Rollback)

**Characteristics:**
- Deployment succeeds but verification fails
- Critical endpoints return errors
- Application crashes on startup
- Performance degradation

**Handling:**
1. Trigger automatic rollback
2. Rollback to previous deployment
3. Exit with code 1
4. Log rollback reason
5. Notify about failure

**Examples:**
- Deployment URL returns HTTP 500
- Database connection fails
- Critical API endpoints unavailable
- Application errors in logs

## Decision Logic Tables

### Pre-Deployment Checks

| Check | Pass | Warning | Fail | Action |
|-------|------|---------|------|--------|
| Git status clean | ✅ | - | ❌ | Continue / Commit changes |
| Sensitive files | ✅ | - | ❌ | Exit(1), remove files |
| .gitignore config | ✅ | ⚠️ | ❌ | Continue / Log warning |
| Build test | ✅ | - | ❌ | Fix errors, retry, or Exit(1) |
| Type check | ✅ | - | ❌ | Fix errors, retry, or Exit(1) |

### Git Operations

| Operation | Success | Auth Error | Conflict | Network Error | Action |
|-----------|---------|------------|----------|---------------|--------|
| Commit | ✅ | - | - | - | Continue |
| Commit | ❌ | - | - | - | Exit(1) |
| Push | ✅ | - | - | - | Continue |
| Push | ❌ | 🔐 | - | - | Exit(3) |
| Push | ❌ | - | ⚠️ | - | Exit(2) |
| Push | ❌ | - | - | 🌐 | Retry(1), then Exit(1) |

### Deployment

| Result | Env Vars | Timeout | Quota | Network | Action |
|--------|----------|---------|-------|---------|--------|
| Success | ✅ | ✅ | ✅ | ✅ | Continue |
| Fail | ❌ | ✅ | ✅ | ✅ | Exit(1) |
| Fail | ✅ | ❌ | ✅ | ✅ | Retry(1), then Exit(2) |
| Fail | ✅ | ✅ | ❌ | ✅ | Exit(3) |
| Fail | ✅ | ✅ | ✅ | ❌ | Retry(1), then Exit(1) |

### Verification

| Check | HTTP 200 | Endpoints OK | Errors | Action |
|-------|----------|-------------|--------|--------|
| Pass | ✅ | ✅ | ✅ | Success, Exit(0) |
| Fail | ❌ | ✅ | ✅ | Rollback, Exit(1) |
| Fail | ✅ | ❌ | ✅ | Rollback, Exit(1) |
| Fail | ✅ | ✅ | ❌ | Rollback, Exit(1) |

## Retry Logic

### Retry Strategy

**Maximum Retries:** 2 attempts per operation

**Backoff Strategy:** Exponential
- First retry: 5 seconds
- Second retry: 10 seconds

**Retry Conditions:**
- Network timeouts
- Temporary service unavailability
- Rate limiting (with backoff)
- Transient errors

**No Retry Conditions:**
- Authentication failures → Exit(3)
- Configuration errors → Exit(1)
- Build errors → Fix and retry once
- Quota exceeded → Exit(3)

### Retry Flow

```
Operation Attempt
│
├─> Success → Continue
│
├─> Recoverable Error
│   ├─> Retry Count < 2?
│   │   ├─> YES → Wait (backoff) → Retry
│   │   └─> NO → Escalate to Category 2
│   │
│   └─> After Max Retries → Exit(1)
│
└─> Non-Recoverable Error
    ├─> Category 2 → Fix & Retry Once
    ├─> Category 3 → Exit(3)
    └─> Category 4 → Rollback & Exit(1)
```

## Rollback Triggers

### Automatic Rollback Conditions

1. **Verification Failure**
   - Deployment URL returns non-200 HTTP code
   - Critical endpoints unavailable
   - Application crashes on startup

2. **Post-Deployment Errors**
   - Database connection failures
   - Critical environment variables missing
   - Application errors in logs

3. **Performance Issues**
   - Response times > 5 seconds
   - Error rate > 10%
   - High memory/CPU usage

### Rollback Procedure

```
Verification Fails
│
├─> Identify Previous Deployment
│   └─> Get deployment ID from Vercel API
│
├─> Execute Rollback
│   └─> vercel rollback <deployment-id>
│
├─> Verify Rollback
│   └─> Check previous deployment is active
│
└─> Report Result
    ├─> Success → Log, Exit(1)
    └─> Fail → Exit(1), Alert
```

## Exit Code Decision Matrix

| Scenario | Exit Code | Meaning | Next Action |
|----------|-----------|---------|-------------|
| All checks pass | 0 | Success | Complete |
| Build/Type errors | 1 | Error | Fix and retry |
| Git conflicts | 2 | Warning | Manual resolution |
| Auth/Quota issues | 3 | Human Required | Stop, wait |
| Verification fails | 1 | Error | Rollback |
| Rollback fails | 1 | Error | Alert human |

## Error Message Format

### Standard Error Format

```json
{
  "status": "error",
  "step": "step-name",
  "exit_code": 1,
  "error_type": "Category1|Category2|Category3|Category4",
  "message": "Human-readable error message",
  "details": {
    "operation": "operation-name",
    "error": "Specific error details",
    "suggestion": "Suggested fix or action"
  },
  "retry_count": 0,
  "can_retry": true|false,
  "requires_human": true|false
}
```

### Error Message Examples

**Category 1 (Recoverable):**
```json
{
  "status": "error",
  "step": "push",
  "exit_code": 1,
  "error_type": "Category1",
  "message": "Network timeout during git push",
  "details": {
    "operation": "git push",
    "error": "Connection timed out after 30 seconds",
    "suggestion": "Retrying with exponential backoff"
  },
  "retry_count": 1,
  "can_retry": true,
  "requires_human": false
}
```

**Category 3 (Human Required):**
```json
{
  "status": "error",
  "step": "deploy",
  "exit_code": 3,
  "error_type": "Category3",
  "message": "Vercel quota exceeded",
  "details": {
    "operation": "vercel deploy",
    "error": "Deployment quota limit reached",
    "suggestion": "Contact Vercel support or upgrade plan"
  },
  "retry_count": 0,
  "can_retry": false,
  "requires_human": true
}
```

## Best Practices

1. **Always check exit codes** before proceeding
2. **Log all decisions** for audit trail
3. **Provide clear error messages** with suggestions
4. **Retry intelligently** with backoff
5. **Rollback on verification failure** to maintain stability
6. **Escalate appropriately** when human intervention needed
7. **Monitor deployment logs** for patterns
8. **Update decision tree** based on learnings

## Related Documentation

- **`DEPLOYMENT_AI_AGENT_PROMPT.md`** - AI agent execution instructions
- **`DEPLOYMENT_SUMMARY.md`** - Deployment overview
- **`scripts/deploy-ai-agent.sh`** - Implementation
