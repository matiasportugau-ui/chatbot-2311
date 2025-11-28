# Comprehensive Merge Plan

## Executive Summary

**Source Branch**: `backup-development-2025-11-28`  
**Target Branch**: `new-branch` (main/default)  
**Merge Date**: TBD  
**Estimated Duration**: 4-6 hours  
**Risk Level**: Medium (with proper preparation)

This plan provides a comprehensive, step-by-step guide for safely merging the development branch into main, including pre-merge preparation, execution steps, testing procedures, and rollback strategies.

---

## 1. Pre-Merge Preparation

### 1.1 Pre-Merge Checklist

#### Code Quality

- [ ] Review all critical issues identified in `DETAILED_BRANCH_COMPARISON.md`
- [ ] Fix critical bugs before merge:
  - [ ] Fix revenue calculation error in `/api/trends` (line 232-234)
  - [ ] Implement `/api/context/import` endpoint (currently empty)
  - [ ] Fix Excel export functionality
- [ ] Code review completed for all new endpoints
- [ ] No blocking linter errors
- [ ] All TODO/FIXME comments addressed or documented

#### Security

- [ ] Authentication/authorization strategy defined
- [ ] Rate limiting plan documented
- [ ] Input validation reviewed
- [ ] Security audit completed

#### Database

- [ ] Database migration scripts prepared
- [ ] Index creation scripts ready
- [ ] Backup strategy confirmed
- [ ] Rollback scripts prepared

#### Testing

- [ ] Test plan created
- [ ] Test environment prepared
- [ ] Test data ready
- [ ] Integration test scenarios defined

#### Documentation

- [ ] API documentation updated
- [ ] Migration guide reviewed
- [ ] Changelog prepared
- [ ] Team notified of upcoming merge

### 1.2 Critical Fixes Required Before Merge

#### Priority 1: Critical Bugs

**1. Fix Revenue Calculation in Trends API**

```typescript
// File: src/app/api/trends/route.ts
// Line 232-234 - INCORRECT
const averageRevenuePerQuote =
  currentValue > 0 && quotesCount > 0
    ? (currentValue / quotesCount).toFixed(2) // WRONG: divides revenue by quotes
    : '0'

// FIXED VERSION:
const averageRevenuePerQuote =
  quotesCount > 0
    ? (currentValue / quotesCount).toFixed(2) // Revenue / quotes = avg per quote
    : '0'
```

**2. Implement Context Import Endpoint**

```typescript
// File: src/app/api/context/import/route.ts
// Currently empty - needs full implementation

export const dynamic = 'force-dynamic'
import { getSharedContextService } from '@/lib/shared-context-service'
import { NextRequest, NextResponse } from 'next/server'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { sessionId, userPhone, context } = body

    if (!sessionId || !userPhone || !context) {
      return NextResponse.json(
        { error: 'sessionId, userPhone, and context are required' },
        { status: 400 }
      )
    }

    const service = getSharedContextService()
    const success = await service.saveContext(sessionId, {
      ...context,
      user_phone: userPhone,
      session_id: sessionId,
    })

    if (!success) {
      return NextResponse.json(
        { error: 'Failed to import context' },
        { status: 500 }
      )
    }

    return NextResponse.json({
      success: true,
      message: 'Context imported successfully',
    })
  } catch (error: any) {
    console.error('Context Import API Error:', error)
    return NextResponse.json(
      {
        success: false,
        error: error.message || 'Internal server error',
      },
      { status: 500 }
    )
  }
}
```

**3. Fix Excel Export**

```typescript
// File: src/app/api/export/route.ts
// Add actual Excel support

import * as XLSX from 'xlsx'

// In the export function:
case 'EXCEL':
  const worksheet = XLSX.utils.json_to_sheet(data)
  const workbook = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(workbook, worksheet, 'Data')
  const excelBuffer = XLSX.write(workbook, { type: 'buffer' })
  exportData = excelBuffer
  contentType = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
  break
```

#### Priority 2: Security Hardening

**1. Add Basic Authentication Middleware**

```typescript
// File: src/lib/auth.ts (NEW FILE)
import { NextRequest, NextResponse } from 'next/server'

export function requireAuth(handler: Function) {
  return async (request: NextRequest) => {
    const token = request.headers.get('Authorization')

    if (!token) {
      return NextResponse.json(
        { error: 'Unauthorized - Missing token' },
        { status: 401 }
      )
    }

    // Validate token (implement your auth logic)
    const isValid = await validateToken(token)
    if (!isValid) {
      return NextResponse.json(
        { error: 'Unauthorized - Invalid token' },
        { status: 401 }
      )
    }

    return handler(request)
  }
}

export function requireAdmin(handler: Function) {
  return async (request: NextRequest) => {
    const token = request.headers.get('Authorization')
    const isAdmin = await checkAdminRole(token)

    if (!isAdmin) {
      return NextResponse.json(
        { error: 'Forbidden - Admin access required' },
        { status: 403 }
      )
    }

    return handler(request)
  }
}
```

**2. Add Rate Limiting**

```typescript
// File: src/lib/rate-limit.ts (NEW FILE)
import { NextRequest } from 'next/server'

const rateLimitMap = new Map<string, { count: number; resetTime: number }>()

export function rateLimit(
  request: NextRequest,
  maxRequests: number = 100,
  windowMs: number = 15 * 60 * 1000
): { allowed: boolean; remaining: number } {
  const ip =
    request.headers.get('x-forwarded-for') ||
    request.headers.get('x-real-ip') ||
    'unknown'

  const now = Date.now()
  const record = rateLimitMap.get(ip)

  if (!record || now > record.resetTime) {
    rateLimitMap.set(ip, {
      count: 1,
      resetTime: now + windowMs,
    })
    return { allowed: true, remaining: maxRequests - 1 }
  }

  if (record.count >= maxRequests) {
    return { allowed: false, remaining: 0 }
  }

  record.count++
  return { allowed: true, remaining: maxRequests - record.count }
}
```

#### Priority 3: Database Indexes

**Create Index Script**

```javascript
// File: scripts/create-indexes.js
const { MongoClient } = require('mongodb')

async function createIndexes() {
  const client = new MongoClient(process.env.MONGODB_URI)
  await client.connect()
  const db = client.db()

  // Conversations indexes
  await db.collection('conversations').createIndex({ timestamp: -1 })
  await db.collection('conversations').createIndex({ user_phone: 1 })
  await db.collection('conversations').createIndex({ session_id: 1 })

  // Quotes indexes
  await db.collection('quotes').createIndex({ timestamp: -1 })
  await db.collection('quotes').createIndex({ estado: 1 })
  await db.collection('quotes').createIndex({ cliente: 1 })

  // Context indexes
  await db.collection('context').createIndex({ session_id: 1, user_phone: 1 })
  await db.collection('context').createIndex({ last_updated: -1 })

  // Sessions indexes
  await db.collection('sessions').createIndex({ session_id: 1 })
  await db.collection('sessions').createIndex({ user_phone: 1 })
  await db.collection('sessions').createIndex({ last_activity: -1 })

  // Search indexes (text search)
  await db.collection('conversations').createIndex({
    'messages.content': 'text',
    user_phone: 'text',
    intent: 'text',
  })

  await db.collection('quotes').createIndex({
    cliente: 'text',
    consulta: 'text',
    direccion: 'text',
  })

  console.log('✅ All indexes created successfully')
  await client.close()
}

createIndexes().catch(console.error)
```

---

## 2. Merge Execution Plan

### 2.1 Pre-Merge Steps (Day Before)

**Step 1: Create Backup**

```bash
# 1. Backup current main branch
git checkout new-branch
git pull origin new-branch
git tag backup-pre-merge-$(date +%Y%m%d)

# 2. Backup database
python3 scripts/recover_conversations.py
# Or via API
curl http://localhost:3000/api/recovery?action=backup

# 3. Backup environment variables
cp .env .env.backup.$(date +%Y%m%d)
```

**Step 2: Prepare Merge Branch**

```bash
# 1. Create merge branch from main
git checkout new-branch
git pull origin new-branch
git checkout -b merge/backup-development-2025-11-28

# 2. Merge development branch
git merge backup-development-2025-11-28 --no-commit --no-ff

# 3. Review conflicts (if any)
git status
```

**Step 3: Apply Critical Fixes**

```bash
# Apply fixes from Priority 1 section
# Fix revenue calculation
# Implement context import
# Fix Excel export
```

**Step 4: Run Pre-Merge Tests**

```bash
# 1. Linting
npm run lint
# or
npm run lint:fix

# 2. Type checking
npm run type-check
# or
tsc --noEmit

# 3. Build test
npm run build

# 4. Unit tests (if available)
npm test
```

### 2.2 Merge Day Execution

#### Phase 1: Final Preparation (30 minutes)

**Step 1: Final Code Review**

```bash
# Review all changes one more time
git diff new-branch..merge/backup-development-2025-11-28

# Review file list
git diff --name-status new-branch..merge/backup-development-2025-11-28
```

**Step 2: Notify Team**

- Send notification to team about merge window
- Set status to "maintenance mode" if needed
- Prepare rollback plan communication

**Step 3: Environment Preparation**

```bash
# 1. Ensure clean working directory
git status

# 2. Ensure all dependencies installed
npm install
pip install -r requirements.txt

# 3. Verify environment variables
cat .env | grep -E "MONGODB_URI|OPENAI_API_KEY"
```

#### Phase 2: Database Migration (15 minutes)

**Step 1: Create Indexes**

```bash
# Run index creation script
node scripts/create-indexes.js
# Or
python3 scripts/create_indexes.py
```

**Step 2: Verify Database**

```bash
# Test MongoDB connection
curl http://localhost:3000/api/health

# Verify indexes created
mongosh $MONGODB_URI --eval "db.conversations.getIndexes()"
```

#### Phase 3: Code Merge (30 minutes)

**Step 1: Complete Merge**

```bash
# 1. Final merge commit
git checkout merge/backup-development-2025-11-28
git commit -m "Merge backup-development-2025-11-28 into new-branch

- Added 12 new API endpoints
- Enhanced MongoDB integration
- Unified launcher system
- Data recovery system
- Context management improvements

See DETAILED_BRANCH_COMPARISON.md for full details"

# 2. Push merge branch
git push origin merge/backup-development-2025-11-28
```

**Step 2: Create Pull Request (if using PR workflow)**

- Create PR from `merge/backup-development-2025-11-28` to `new-branch`
- Add reviewers
- Link to `DETAILED_BRANCH_COMPARISON.md`
- Add merge checklist

**Step 3: Merge to Main**

```bash
# Option A: Direct merge (if approved)
git checkout new-branch
git merge merge/backup-development-2025-11-28
git push origin new-branch

# Option B: Squash merge (cleaner history)
git checkout new-branch
git merge --squash merge/backup-development-2025-11-28
git commit -m "Merge: backup-development-2025-11-28 - Major feature update"
git push origin new-branch
```

#### Phase 4: Post-Merge Verification (45 minutes)

**Step 1: Build Verification**

```bash
# 1. Clean build
rm -rf .next node_modules/.cache
npm run build

# 2. Verify no build errors
echo $? # Should be 0
```

**Step 2: API Testing**

```bash
# Test health endpoint
curl http://localhost:3000/api/health | jq

# Test new endpoints
curl http://localhost:3000/api/analytics/quotes | jq
curl http://localhost:3000/api/trends?type=quotes | jq
curl http://localhost:3000/api/mongodb/validate | jq
```

**Step 3: Integration Testing**

```bash
# Test unified launcher
python3 unified_launcher.py --mode chat

# Test recovery system
python3 scripts/recover_conversations.py --no-backup

# Test context management
curl -X POST http://localhost:3000/api/context/shared \
  -H "Content-Type: application/json" \
  -d '{"action": "create_session", "userPhone": "+1234567890"}'
```

**Step 4: Smoke Tests**

- [ ] Health check returns all services ready
- [ ] Analytics endpoint returns data
- [ ] Search endpoint works
- [ ] Export/import endpoints functional
- [ ] Context endpoints operational
- [ ] Recovery system accessible

---

## 3. Testing Procedures

### 3.1 Unit Tests (To Be Created)

**Priority Test Cases**:

```typescript
// tests/api/analytics/quotes.test.ts
describe('Analytics Quotes API', () => {
  it('should return quote statistics', async () => {
    const response = await fetch('/api/analytics/quotes')
    expect(response.status).toBe(200)
    const data = await response.json()
    expect(data.success).toBe(true)
    expect(data.data).toHaveProperty('totalQuotes')
  })

  it('should handle date filtering', async () => {
    const dateFrom = new Date('2025-01-01').toISOString()
    const response = await fetch(`/api/analytics/quotes?dateFrom=${dateFrom}`)
    expect(response.status).toBe(200)
  })

  it('should handle errors gracefully', async () => {
    // Mock MongoDB error
    // Verify error response
  })
})
```

### 3.2 Integration Tests

**Test Scenarios**:

1. **Full Quote Workflow**

   - Create conversation
   - Generate quote
   - View analytics
   - Export data

2. **Context Management**

   - Create session
   - Add messages
   - Export context
   - Import context

3. **Recovery System**
   - Create backup
   - Restore data
   - Verify integrity

### 3.3 Performance Tests

```bash
# Load test new endpoints
ab -n 1000 -c 10 http://localhost:3000/api/analytics/quotes
ab -n 1000 -c 10 http://localhost:3000/api/search
```

### 3.4 Security Tests

- [ ] Test authentication on protected endpoints
- [ ] Test rate limiting
- [ ] Test input validation
- [ ] Test SQL/NoSQL injection prevention
- [ ] Test file upload limits

---

## 4. Rollback Plan

### 4.1 Rollback Triggers

**Immediate Rollback Required If**:

- Critical system failure
- Data corruption detected
- Security breach identified
- Performance degradation > 50%
- Multiple endpoints failing

### 4.2 Rollback Procedure

**Step 1: Immediate Actions**

```bash
# 1. Revert merge commit
git checkout new-branch
git revert -m 1 HEAD
git push origin new-branch

# 2. Or reset to previous tag
git reset --hard backup-pre-merge-YYYYMMDD
git push origin new-branch --force
```

**Step 2: Database Rollback**

```bash
# Restore from backup
python3 scripts/recover_conversations.py --restore backups/backup_YYYYMMDD_HHMMSS.json

# Or via API
curl -X POST http://localhost:3000/api/recovery \
  -H "Content-Type: application/json" \
  -d '{"action": "restore", "source": "backup", "data": [...]}'
```

**Step 3: Environment Rollback**

```bash
# Restore environment variables
cp .env.backup.YYYYMMDD .env

# Restart services
pm2 restart all
# or
systemctl restart chatbot
```

**Step 4: Verification**

```bash
# Verify system operational
curl http://localhost:3000/api/health

# Verify data integrity
python3 scripts/verify_data_integrity.py
```

### 4.3 Rollback Communication

1. Notify team immediately
2. Document rollback reason
3. Create incident report
4. Schedule post-mortem

---

## 5. Post-Merge Tasks

### 5.1 Immediate (Day 1)

- [ ] Monitor error logs
- [ ] Monitor performance metrics
- [ ] Verify all endpoints operational
- [ ] Check database performance
- [ ] Review user feedback

### 5.2 Short-term (Week 1)

- [ ] Implement authentication (if not done pre-merge)
- [ ] Add rate limiting to all endpoints
- [ ] Create comprehensive test suite
- [ ] Update API documentation
- [ ] Monitor for security issues

### 5.3 Medium-term (Month 1)

- [ ] Optimize database queries
- [ ] Implement caching strategy
- [ ] Add monitoring and alerting
- [ ] Performance tuning
- [ ] User training on new features

---

## 6. Risk Mitigation

### 6.1 Identified Risks

| Risk                             | Probability | Impact   | Mitigation                        |
| -------------------------------- | ----------- | -------- | --------------------------------- |
| Database performance degradation | Medium      | High     | Create indexes before merge       |
| API endpoint failures            | Low         | High     | Comprehensive testing             |
| Security vulnerabilities         | Medium      | Critical | Implement auth before merge       |
| Data loss                        | Low         | Critical | Multiple backups                  |
| Breaking changes                 | Low         | Medium   | Backward compatibility maintained |

### 6.2 Mitigation Strategies

**Database Performance**:

- Create all indexes before merge
- Monitor query performance
- Have rollback scripts ready

**API Failures**:

- Comprehensive testing before merge
- Gradual rollout option
- Feature flags for new endpoints

**Security**:

- Implement basic auth before merge
- Security review completed
- Rate limiting in place

**Data Loss**:

- Multiple backup points
- Verified restore procedures
- Data validation scripts

---

## 7. Timeline

### 7.1 Pre-Merge (2-3 days)

- **Day 1**: Code review, fix critical bugs
- **Day 2**: Security hardening, create indexes
- **Day 3**: Testing, final preparation

### 7.2 Merge Day (4-6 hours)

- **Hour 1**: Final preparation, backups
- **Hour 2**: Database migration
- **Hour 3**: Code merge
- **Hour 4**: Testing and verification
- **Hours 5-6**: Monitoring, adjustments

### 7.3 Post-Merge (1 week)

- **Day 1**: Intensive monitoring
- **Days 2-3**: Bug fixes, optimizations
- **Days 4-7**: Documentation, training

---

## 8. Success Criteria

### 8.1 Technical Success

- [ ] All endpoints operational
- [ ] No critical errors in logs
- [ ] Performance within acceptable range
- [ ] Database queries optimized
- [ ] Security measures in place

### 8.2 Business Success

- [ ] New features accessible
- [ ] User feedback positive
- [ ] No service disruption
- [ ] Documentation updated
- [ ] Team trained on new features

---

## 9. Communication Plan

### 9.1 Pre-Merge Communication

**Stakeholders to Notify**:

- Development team
- QA team
- DevOps team
- Product management
- Support team

**Communication Channels**:

- Team Slack/Teams channel
- Email notification
- Status page update (if applicable)

### 9.2 During Merge

- Real-time updates in team channel
- Status page updates
- Error alerts to on-call engineer

### 9.3 Post-Merge

- Success notification
- Feature announcement
- Documentation links
- Training schedule

---

## 10. Checklist Summary

### Pre-Merge Checklist

- [ ] All critical bugs fixed
- [ ] Security measures implemented
- [ ] Database indexes created
- [ ] Tests passing
- [ ] Documentation updated
- [ ] Backups created
- [ ] Team notified

### Merge Day Checklist

- [ ] Final code review
- [ ] Database migration completed
- [ ] Merge executed
- [ ] Build successful
- [ ] All tests passing
- [ ] Smoke tests passed
- [ ] Monitoring active

### Post-Merge Checklist

- [ ] System stable
- [ ] Performance acceptable
- [ ] No critical errors
- [ ] Documentation updated
- [ ] Team trained
- [ ] Success metrics met

---

## 11. Emergency Contacts

**On-Call Engineer**: [To be filled]  
**Database Admin**: [To be filled]  
**DevOps Lead**: [To be filled]  
**Security Team**: [To be filled]

---

## 12. Appendices

### Appendix A: File Change Summary

See `BRANCH_DIFF_ANALYSIS_REPORT.md` for complete file change list.

### Appendix B: API Endpoint Reference

**New Endpoints**:

- `/api/analytics/quotes` - Quote analytics
- `/api/trends` - Trend analysis
- `/api/export` - Data export
- `/api/import` - Data import
- `/api/search` - Full-text search
- `/api/settings` - Settings management
- `/api/notifications` - Notifications CRUD
- `/api/recovery` - Data recovery
- `/api/mongodb/validate` - MongoDB validation
- `/api/context/export` - Context export
- `/api/context/import` - Context import
- `/api/context/shared` - Shared context

### Appendix C: Database Schema Changes

**New Collections**:

- `settings` - User and system settings
- `notifications` - System notifications
- `search_history` - Search query history

**Indexes Required**:

- See section 1.2 Priority 3 for complete index list

---

## Conclusion

This merge plan provides a comprehensive roadmap for safely integrating the development branch into main. Follow the steps sequentially, complete all checklists, and maintain clear communication throughout the process.

**Remember**: It's better to delay a merge than to merge broken code. If any critical issues are found during preparation, address them before proceeding.

**Estimated Total Time**: 4-6 hours for merge execution + 2-3 days preparation

**Risk Level**: Medium (with proper preparation and execution)

---

**Plan Created**: November 28, 2025  
**Last Updated**: November 28, 2025  
**Status**: Ready for Execution
