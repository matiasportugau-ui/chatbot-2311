# CRM Dashboard - Quick Start Guide

**Last Updated:** 2025-12-16
**Status:** Phase 5 Complete, Infrastructure Ready
**Cost to Date:** ~$0.35 USD (~78k tokens)

---

## 📋 What Was Just Created

### 1. Project Memory ([CLAUDE.md](CLAUDE.md))
Complete project context including:
- ✅ All completed phases (1-5)
- ✅ Architecture overview
- ✅ File structure
- ✅ API patterns
- ✅ Development workflow
- ✅ Known issues
- ✅ Next phases plan

**Use this when:** Starting a new session or onboarding team members

---

### 2. Development Report ([DEVELOPMENT_REPORT.md](DEVELOPMENT_REPORT.md))
Comprehensive production-ready assessment with:
- ✅ Executive summary
- ✅ Production readiness checklist
- ✅ Manual testing guide (step-by-step)
- ✅ API testing with cURL commands
- ✅ Automated development plan (Phases 6-8)
- ✅ Token & cost analysis
- ✅ Risk assessment (Green/Yellow/Red)
- ✅ Scorecard: **88/100** overall

**Use this when:** Planning deployments, reporting progress, or estimating costs

---

### 3. Slash Commands (`.claude/commands/`)

**Available commands:**
- `/dev-report` - Generate development report
- `/manual-test` - Run testing checklist
- `/autoplan` - Create automated phase plan
- `/cost-estimate` - Calculate token/cost estimates

**How to use:**
```bash
# In Claude Code chat
/dev-report

# Or just say:
"Generate dev report"
"Run manual tests"
"Create automated plan for phase 6"
"Estimate cost for next phase"
```

---

## 🚀 How to Start Development

### Option 1: Continue Phase 6 (CRM API)
```bash
# 1. Start dev server
npm run dev

# 2. Say to Claude:
"Continue with Phase 6 in autopilot mode"

# Or more specific:
"Implement quote API endpoints for Phase 6"
```

**What you'll get:**
- Quote CRUD API routes
- React Query hooks
- Real MongoDB connection
- Quote creation UI
- Google Sheets sync

**Estimated:** 20k tokens | $0.25 USD | 2-3 hours

---

### Option 2: Manual Testing First
```bash
# 1. Run tests
npm run dev

# 2. Say to Claude:
"/manual-test"

# Or:
"Run manual testing checklist"
```

**What you'll test:**
- ✅ Authentication (login/logout)
- ✅ RBAC (all 4 roles)
- ✅ Responsive design
- ✅ Kanban drag & drop
- ✅ API endpoints

---

### Option 3: Review & Plan
```bash
# Say to Claude:
"/dev-report"

# Then:
"/autoplan phase 6"
```

**What you'll get:**
- Current status report
- Detailed Phase 6 plan with milestones
- Cost estimates (economical/balanced/exhaustive)
- Validation criteria
- Risk assessment

---

## 📊 Cost & Token Management

### Current Session
```
Used: 79,259 tokens (39.6%)
Remaining: 120,741 tokens (60.4%)
Cost: ~$0.35 USD
```

### Project Total (Phases 1-5)
```
Total tokens: ~78,000
Total cost: ~$0.35 USD
Files created: 43 files
Lines of code: ~4,300
```

### Budget for Phases 6-8
```
Phase 6 (CRM API): 20k tokens | $0.25 USD
Phase 7 (Analytics): 15k tokens | $0.18 USD
Phase 8 (Testing): 12k tokens | $0.15 USD
Total remaining: ~47k tokens | $0.58 USD
```

**Total project cost estimate:** ~$0.87 USD for all 8 phases

---

## 🧪 Manual Testing (Quick Version)

### Test 1: Login
```bash
1. Go to http://localhost:3000/crm
2. Login: admin@example.com / admin123
3. ✅ Should see dashboard with Kanban board
```

### Test 2: Drag & Drop
```bash
1. Drag "Q-2024-001" from Pending to Sent
2. ✅ Card moves, stats update
```

### Test 3: Responsive
```bash
1. Open DevTools (F12)
2. Toggle device toolbar (Ctrl+Shift+M)
3. Try iPhone, iPad, Desktop
4. ✅ All layouts work correctly
```

### Test 4: API
```bash
# List users
curl http://localhost:3000/api/users

# Create user (requires auth)
curl -X POST http://localhost:3000/api/users \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "test123",
    "name": "Test User",
    "role": "sales"
  }'
```

---

## 📁 File Structure Reference

```
chatbot-2311/
├── CLAUDE.md                    # Project memory (read this first!)
├── DEVELOPMENT_REPORT.md        # Full development report
├── CRM_BUILD_PROGRESS.md        # Phase-by-phase progress
├── CRM_ARCHITECTURE.md          # Technical architecture
├── QUICK_START.md               # This file
├── .claude/
│   └── commands/                # Slash commands
│       ├── dev-report.md
│       ├── manual-test.md
│       ├── autoplan.md
│       └── cost-estimate.md
├── src/
│   ├── app/
│   │   ├── (auth)/login/        # Login page
│   │   ├── (dashboard)/crm/     # CRM dashboard
│   │   └── api/                 # API routes
│   ├── components/
│   │   ├── ui/                  # Shadcn components
│   │   ├── layout/              # Header, Sidebar
│   │   ├── features/kanban/     # Kanban board
│   │   └── providers/           # React Query, Session
│   ├── lib/
│   │   ├── auth/                # Auth service, RBAC
│   │   └── crm/                 # CRM service layer
│   ├── hooks/                   # React Query hooks
│   ├── stores/                  # Zustand stores
│   └── types/                   # TypeScript types
└── package.json
```

---

## 🎯 Recommended Next Steps

### Immediate (Today)
1. ✅ Review [DEVELOPMENT_REPORT.md](DEVELOPMENT_REPORT.md)
2. ✅ Run manual tests (see above)
3. ✅ Review Phase 6 plan

### This Week
1. ⏳ Implement Phase 6 (CRM API)
   - Quote CRUD endpoints
   - Real MongoDB connection
   - Quote creation UI
   - Google Sheets sync

2. ⏳ Manual testing after each milestone

### Next Week
1. ⏳ Phase 7: Analytics Dashboard
2. ⏳ Phase 8: Testing & Polish
3. ⏳ Production deployment

---

## 💡 Pro Tips

### For Cost Optimization
```bash
# Use "economical" mode for simple tasks
"Create a simple API endpoint (economical mode)"

# Use "balanced" for normal development (recommended)
"Implement Phase 6 (balanced mode)"

# Use "exhaustive" only when needed
"Implement Phase 6 with comprehensive error handling (exhaustive mode)"
```

### For Better Results
```bash
# Be specific
❌ "Add features"
✅ "Add quote creation form with customer dropdown and product selection"

# Reference existing patterns
❌ "Create API"
✅ "Create quote API following the user API pattern in src/app/api/users/"

# Request validation
❌ "Build feature"
✅ "Build feature with validation criteria: must work on mobile, must have error handling"
```

### For Autopilot Mode
```bash
# Enable autopilot
"Continue in autopilot mode"

# Set clear boundaries
"Continue Phase 6 in autopilot, but ask before modifying authentication"

# Review checkpoints
"Complete Phase 6 milestone 1, then pause for review"
```

---

## 🔧 Troubleshooting

### Issue: MongoDB connection fails
```bash
# Check MongoDB is running
mongod --version

# Check .env.local
cat .env.local | grep MONGODB_URI

# Should be:
MONGODB_URI=mongodb://localhost:27017/bmc-cotizaciones
```

### Issue: Session not persisting
```bash
# Check NEXTAUTH_SECRET is set
cat .env.local | grep NEXTAUTH_SECRET

# Generate if missing:
openssl rand -base64 32
```

### Issue: Build errors
```bash
# Clear Next.js cache
rm -rf .next
npm run dev
```

---

## 📞 Support & Resources

### Documentation
- **Architecture:** [CRM_ARCHITECTURE.md](CRM_ARCHITECTURE.md)
- **Progress:** [CRM_BUILD_PROGRESS.md](CRM_BUILD_PROGRESS.md)
- **Report:** [DEVELOPMENT_REPORT.md](DEVELOPMENT_REPORT.md)

### Slash Commands
- `/dev-report` - Development status
- `/manual-test` - Testing checklist
- `/autoplan` - Next phase plan
- `/cost-estimate` - Budget calculator

### Ask Claude
```
"Show me the API pattern for quotes"
"How do I test authentication?"
"What's the cost estimate for Phase 6?"
"Generate development report"
```

---

## ✅ Success Criteria

**You know you're ready to continue when:**
- ✅ Can login successfully
- ✅ Can drag quotes in Kanban
- ✅ Responsive design works
- ✅ Understand the cost model
- ✅ Have a plan for Phase 6

---

**Ready to continue?** Just say:
- "Continue with Phase 6"
- "Run manual tests first"
- "Show me the automated plan"

**Cost so far:** $0.35 USD (~78k tokens)
**Budget remaining:** $0.52 USD (~122k tokens)
**Estimated to complete:** $0.87 USD total

🚀 **Let's build!**
