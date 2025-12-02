# 📊 Agent Task Assignment Matrix
## Quick Reference for Daily Work

**Last Updated:** December 2, 2025  
**Project:** BMC Uruguay Deployment

---

## 🎯 Quick Agent Reference

| Agent | Primary Focus | Key Tools | Daily Output |
|-------|--------------|-----------|--------------|
| **Orchestrator** | Coordination & Decisions | GitHub Projects, Slack | Standup notes, decisions log |
| **Infrastructure** | Cloud & DevOps | Vercel, MongoDB Atlas, GitHub Actions | Deployment logs, monitoring |
| **Backend** | Python API & AI | Python, FastAPI, OpenAI | API endpoints, tests |
| **Frontend** | Next.js UI | React, TypeScript, Tailwind | UI components, pages |
| **Integration** | 3rd Party APIs | WhatsApp, Google Sheets, OAuth | Integration tests, webhooks |
| **QA** | Testing & Quality | Cypress, Playwright, Postman | Test results, bug reports |
| **Documentation** | Docs & Knowledge | Markdown, Notion, Diagrams | Documentation updates |

---

## 📅 Phase-by-Phase Task Matrix

### PHASE 0: Onboarding (Day 1)

| Agent | Tasks | Deliverables | Dependencies |
|-------|-------|--------------|--------------|
| **Orchestrator** | • Kickoff meeting<br>• Assign roles<br>• Set up communication<br>• Create project board | • Kickoff deck<br>• Role assignments<br>• Communication channels<br>• Task board | None |
| **Infrastructure** | • Verify Vercel access<br>• Verify MongoDB Atlas access<br>• Verify GitHub Actions access | • Access confirmation | Orchestrator assigns role |
| **Backend** | • Clone repo<br>• Run API locally<br>• Test OpenAI API | • Local API running | Infrastructure provides credentials |
| **Frontend** | • Clone repo<br>• Run Next.js locally<br>• Verify build | • Local UI running | None |
| **Integration** | • Verify WhatsApp API access<br>• Verify Google Cloud access<br>• Verify MercadoLibre access | • Access confirmation | Infrastructure provides credentials |
| **QA** | • Set up test framework<br>• Create test plan template<br>• Set up bug tracking | • Test plan draft<br>• Bug tracker configured | None |
| **Documentation** | • Set up docs platform<br>• Create documentation template<br>• Start architecture diagram | • Doc structure<br>• Template ready | None |

**Phase 0 Gate:** All agents have local environment working ✅

---

### PHASE 1: Foundation (Days 2-4)

#### Day 2 Tasks

| Agent | Morning (9am-1pm) | Afternoon (2pm-6pm) | Blockers? |
|-------|-------------------|---------------------|-----------|
| **Orchestrator** | • Standup<br>• Monitor progress<br>• Review PRs | • Address blockers<br>• Update task board | - |
| **Infrastructure** | 🔥 Create Vercel project<br>🔥 Configure env vars | 🔥 Set up MongoDB Atlas<br>🔥 Configure network access | Need env vars from all agents |
| **Backend** | 🔥 Audit Python dependencies<br>🔥 Update requirements.txt | 🔥 Run unit tests<br>🔥 Fix any failing tests | Need MongoDB credentials |
| **Frontend** | 🔥 Audit npm dependencies<br>🔥 Run `npm run build` | 🔥 Fix TypeScript errors<br>🔥 Fix ESLint warnings | None |
| **Integration** | • Configure Google Service Account<br>• Test Sheets API | • Document setup process | Need service account JSON |
| **QA** | • Write test cases for critical flows | • Set up Cypress/Playwright | Need app running locally |
| **Documentation** | • Document env variables | • Create .env.example | Need env var list from Infrastructure |

#### Day 3 Tasks

| Agent | Morning (9am-1pm) | Afternoon (2pm-6pm) | Blockers? |
|-------|-------------------|---------------------|-----------|
| **Orchestrator** | • Standup<br>• Review Day 2 progress | • Plan Day 4<br>• Update timeline | - |
| **Infrastructure** | 🔥 Create staging environment<br>🔥 Set up GitHub Actions | • Test manual deployment | Need CI/CD workflow file from Backend |
| **Backend** | 🔥 Test IA Conversacional engine<br>🔥 Verify quote calculations | 🔥 Test knowledge base consolidation | None |
| **Frontend** | 🔥 Test all pages render<br>🔥 Verify API routes | 🔥 Test chat interface<br>🔥 Test streaming | Need API endpoints from Backend |
| **Integration** | • Set up WhatsApp webhook (ngrok)<br>• Test local webhook | • Configure MercadoLibre OAuth | Need webhook URL from Infrastructure |
| **QA** | • Continue writing test cases | • Start Cypress tests | Need app deployed to staging |
| **Documentation** | • Create architecture diagram | • Document deployment process | Need architecture details |

#### Day 4 Tasks

| Agent | Morning (9am-1pm) | Afternoon (2pm-6pm) | Blockers? |
|-------|-------------------|---------------------|-----------|
| **Orchestrator** | • Standup<br>• Phase 1 gate review | • Approve Phase 2 start<br>• Update stakeholders | - |
| **Infrastructure** | • Configure domain/SSL (if needed)<br>🔥 Test staging deployment | • Verify deployment succeeded | None |
| **Backend** | 🔥 Create API integration tests<br>🔥 Test MongoDB with prod credentials | • Optimize OpenAI API calls | None |
| **Frontend** | • Optimize bundle size<br>• Test responsive design | • Final build verification | None |
| **Integration** | • Finalize Google Sheets config | • Test all integrations locally | None |
| **QA** | 🔥 Execute smoke tests locally | • Document test results | Need staging URL |
| **Documentation** | • Complete env var documentation<br>• Update architecture diagram | • Review Phase 1 documentation | None |

**Phase 1 Gate:** Local working, staging ready, CI/CD configured ✅

---

### PHASE 2: Staging Deployment (Days 5-6)

#### Day 5 Tasks

| Agent | Morning (9am-1pm) | Afternoon (2pm-6pm) | Blockers? |
|-------|-------------------|---------------------|-----------|
| **Orchestrator** | • Standup<br>• Approve staging deployment | • Monitor deployment status<br>• Address issues | - |
| **Infrastructure** | 🔥 Trigger staging deployment<br>🔥 Verify deployment success | • Configure health checks<br>• Set up monitoring | None |
| **Backend** | 🔥 Test all API endpoints on staging<br>🔥 Test OpenAI integration | 🔥 Test quote generation E2E<br>🔥 Load test (10 req/s) | Need staging URL |
| **Frontend** | 🔥 Verify all pages load on staging<br>🔥 Test chat interface | 🔥 Test dashboard functionality<br>🔥 Run Lighthouse audit | Need staging URL |
| **Integration** | 🔥 Configure WhatsApp webhook to staging<br>🔥 Test WhatsApp sending | 🔥 Test Google Sheets sync<br>🔥 Test MercadoLibre OAuth | Need staging URL |
| **QA** | 🔥 Execute smoke tests on staging | 🔥 Execute integration tests | Need staging URL |
| **Documentation** | • Update deployment runbook | • Document staging learnings | None |

#### Day 6 Tasks

| Agent | Morning (9am-1pm) | Afternoon (2pm-6pm) | Blockers? |
|-------|-------------------|---------------------|-----------|
| **Orchestrator** | • Standup<br>• Review Day 5 issues<br>• Phase 2 gate review | • Approve Phase 3 start | - |
| **Infrastructure** | • Set up Vercel Analytics<br>• Configure MongoDB monitoring | • Verify all monitoring working | None |
| **Backend** | • Fix staging issues<br>• Optimize slow endpoints | • Verify all fixes deployed | Need bug list from QA |
| **Frontend** | • Fix staging UI issues<br>• Verify mobile responsiveness | • Final staging verification | Need bug list from QA |
| **Integration** | • Test Shopify product import<br>• Test N8N workflows | • Document integration issues | None |
| **QA** | 🔥 Execute E2E tests on staging<br>🔥 Document all bugs (GitHub Issues) | 🔥 Verify bug fixes | None |
| **Documentation** | • Document API endpoints (Swagger)<br>• Create troubleshooting guide | • Review documentation | None |

**Phase 2 Gate:** Staging fully functional, integrations working ✅

---

### PHASE 3: Testing & QA (Days 7-8)

#### Day 7 Tasks

| Agent | Morning (9am-1pm) | Afternoon (2pm-6pm) | Blockers? |
|-------|-------------------|---------------------|-----------|
| **Orchestrator** | • Standup<br>• Prioritize QA findings | • Schedule UAT session<br>• Invite stakeholders | - |
| **Backend** | • Fix P1 bugs from QA<br>• Optimize DB queries | • Implement rate limiting<br>• Security review | Need bug list from QA |
| **Frontend** | • Fix P1 bugs from QA<br>• Optimize performance | • Accessibility audit (WCAG 2.1) | Need bug list from QA |
| **Integration** | • Test integration edge cases<br>• Verify error handling | • Create integration health dashboard | None |
| **Infrastructure** | • Review deployment logs<br>• Optimize infra config | • Prepare prod deployment checklist | None |
| **QA** | 🔥 Execute full test suite<br>🔥 Performance testing (50 req/s) | 🔥 Security testing (OWASP)<br>🔥 Create UAT scripts | None |
| **Documentation** | • Complete user documentation | • Complete admin documentation | None |

#### Day 8 Tasks

| Agent | Morning (9am-1pm) | Afternoon (2pm-6pm) | Blockers? |
|-------|-------------------|---------------------|-----------|
| **Orchestrator** | • Standup<br>🔥 Conduct UAT session with stakeholders | • Collect UAT feedback<br>• Phase 3 gate review | Need stakeholder availability |
| **Backend** | • Fix UAT issues (backend) | • Final API security review | Need UAT feedback |
| **Frontend** | • Fix UAT issues (frontend) | • Final UI polish | Need UAT feedback |
| **Integration** | • Document integration troubleshooting | • Verify all integrations healthy | None |
| **Infrastructure** | • Verify rollback procedures<br>• Final prod checklist review | • Prepare for prod deployment | None |
| **QA** | 🔥 Document UAT feedback<br>🔥 Verify all UAT issues resolved | 🔥 Final test pass | Need UAT session results |
| **Documentation** | • Complete developer documentation<br>• Create video tutorial (optional) | • Final documentation review | None |

**Phase 3 Gate:** All tests passing, UAT approved, ready for production ✅

---

### PHASE 4: Production Deployment (Day 9)

| Agent | 9am-11am | 11am-1pm | 2pm-4pm | 4pm-6pm |
|-------|----------|----------|---------|---------|
| **Orchestrator** | • Standup<br>🔥 GO/NO-GO decision | • Monitor all agents | • Monitor deployment | 🔥 Declare success or rollback |
| **Infrastructure** | 🔥 Review prod env vars<br>🔥 Backup MongoDB<br>🔥 Deploy to production | 🔥 Verify deployment success<br>• Active monitoring | • Configure prod alerts | • Update DNS (if needed) |
| **Backend** | 🔥 Monitor API health<br>🔥 Test sample quote | • Monitor OpenAI usage | • Monitor MongoDB performance | • Verify all endpoints healthy |
| **Frontend** | 🔥 Verify pages load<br>🔥 Test chat interface | • Monitor client errors | • Verify analytics working | • Final UI verification |
| **Integration** | 🔥 Update WhatsApp webhook to prod<br>🔥 Test WhatsApp in prod | • Update MercadoLibre OAuth<br>• Test all integrations | • Verify integrations working | • Monitor integration health |
| **QA** | 🔥 Execute smoke tests on prod | 🔥 Monitor for errors | • Execute critical path tests | • Document any issues |
| **Documentation** | • Finalize deployment runbook | • Publish docs to wiki | • Create quick reference guides | • Final docs review |

**Phase 4 Gate:** Production deployed, healthy, zero critical issues ✅

---

### PHASE 5: Monitoring & Handoff (Days 10-11)

#### Day 10 Tasks

| Agent | Morning (9am-1pm) | Afternoon (2pm-6pm) | Notes |
|-------|-------------------|---------------------|-------|
| **Orchestrator** | • Standup<br>• Review production metrics | • Monitor team progress<br>• Update stakeholders | Continue daily standups |
| **Infrastructure** | • Monitor uptime (99.9% target)<br>• Review infra costs | • Set up automated backups<br>• Optimize costs | Production is stable |
| **Backend** | • Monitor API performance<br>• Optimize slow endpoints | • Review OpenAI costs<br>• Document benchmarks | Address any performance issues |
| **Frontend** | • Monitor client performance (Lighthouse)<br>• Fix minor UI issues | • Optimize bundle size | User feedback collection |
| **Integration** | • Monitor integration health<br>• Optimize API calls | • Document integration issues | All integrations stable |
| **QA** | • Monitor production for bugs<br>• Execute daily tests | • Create production monitoring plan | Continue monitoring |
| **Documentation** | • Complete remaining docs<br>• Create onboarding guide | • Review all documentation | Prepare for handoff |

#### Day 11 Tasks

| Agent | Morning (9am-1pm) | Afternoon (2pm-6pm) | Notes |
|-------|-------------------|---------------------|-------|
| **Orchestrator** | • Standup<br>🔥 Conduct team retrospective | • Create project completion report<br>🔥 Handoff to operations | Final day! |
| **Infrastructure** | • Create operations runbook<br>• Train operations team | • Archive deployment artifacts | Handoff to ops |
| **Backend** | • Create API maintenance guide<br>• Document performance benchmarks | • Handoff to backend team | Handoff to dev team |
| **Frontend** | • Document frontend optimization techniques<br>• Handoff to frontend team | • Archive development artifacts | Handoff to dev team |
| **Integration** | • Create integration maintenance guide<br>• Document common issues | • Handoff to integration team | Handoff to ops |
| **QA** | • Create production monitoring test plan<br>• Handoff to QA operations | • Archive test artifacts | Handoff to QA team |
| **Documentation** | • Create maintenance calendar<br>• Final documentation review | 🎉 Project complete! | Docs published |

**Phase 5 Gate:** Production stable 48h, ops trained, docs complete ✅

---

## 🚨 Daily Blockers Tracker

### How to Report Blockers

**In Daily Standup:**
1. State what you're blocked on
2. How long you've been blocked
3. What you need to unblock

**In Slack (#deployment-blockers):**
```
🚫 BLOCKER

Agent: @frontend-agent
Blocked on: API endpoint /api/chat not returning streaming response
Duration: 2 hours
Need: @backend-agent to investigate endpoint
Impact: Cannot complete chat UI testing
Priority: P1 - High
```

### Common Blockers & Solutions

| Blocker | Agent Affected | Solution | Owner |
|---------|----------------|----------|-------|
| Staging URL not working | Frontend, QA, Integration | Check Vercel deployment logs | Infrastructure |
| API returning 500 errors | Frontend, Integration | Check API server logs, verify env vars | Backend |
| MongoDB connection timeout | Backend, Infrastructure | Verify network access settings in Atlas | Infrastructure |
| WhatsApp webhook not receiving | Integration | Verify webhook URL, check Meta Developer Console | Integration |
| Build failing in CI/CD | All | Check GitHub Actions logs, fix syntax errors | Backend/Frontend |
| Tests failing | QA | Check test logs, verify test data | QA + relevant agent |
| Missing credentials | Any | Check .env file, verify secrets in Vercel | Infrastructure |
| Performance issues | Backend, Frontend | Profile code, check database queries | Backend/Frontend |

---

## ✅ Daily Checklist Templates

### For Orchestrator

**Morning Checklist:**
- [ ] Review overnight CI/CD logs
- [ ] Check project board for blockers
- [ ] Review Slack for urgent messages
- [ ] Prepare standup agenda
- [ ] Update phase gate tracker

**Standup Checklist:**
- [ ] Each agent reported (completed/in-progress/blocked)
- [ ] All blockers addressed or escalated
- [ ] New tasks assigned
- [ ] Tomorrow's priorities clear
- [ ] Standup notes posted to Slack

**Evening Checklist:**
- [ ] Review day's PRs and merges
- [ ] Update project status report
- [ ] Log any decisions made today
- [ ] Prepare tomorrow's priorities
- [ ] Check phase gate criteria progress

### For All Agents

**Morning Checklist:**
- [ ] Pull latest code: `git pull origin main`
- [ ] Check Slack for updates
- [ ] Review today's tasks on project board
- [ ] Attend daily standup
- [ ] Start highest priority task

**End of Day Checklist:**
- [ ] Commit and push work: `git add . && git commit -m "..." && git push`
- [ ] Update task status on project board
- [ ] Post progress update to Slack
- [ ] Document any blockers
- [ ] Plan tomorrow's work

### For Infrastructure Agent

**Deployment Checklist (Before Deploying):**
- [ ] All tests passing in CI/CD
- [ ] Staging verification complete
- [ ] Environment variables verified
- [ ] Backup taken (if production)
- [ ] Rollback procedure ready
- [ ] Team notified of deployment
- [ ] Monitoring dashboard open

**Post-Deployment Checklist:**
- [ ] Deployment succeeded (check Vercel dashboard)
- [ ] Health check endpoint returns 200 OK
- [ ] All pages accessible
- [ ] No errors in logs (first 15 minutes)
- [ ] Monitoring alerts configured
- [ ] Team notified of completion
- [ ] Document any issues

---

## 📊 Progress Tracking Dashboard

### Overall Progress

| Phase | Status | Days | Start Date | End Date | Gate Passed |
|-------|--------|------|------------|----------|-------------|
| Phase 0 | ⬜ Not Started | 1 | - | - | ❌ |
| Phase 1 | ⬜ Not Started | 3 | - | - | ❌ |
| Phase 2 | ⬜ Not Started | 2 | - | - | ❌ |
| Phase 3 | ⬜ Not Started | 2 | - | - | ❌ |
| Phase 4 | ⬜ Not Started | 1 | - | - | ❌ |
| Phase 5 | ⬜ Not Started | 2 | - | - | ❌ |

**Legend:**
- ⬜ Not Started
- 🔵 In Progress
- ✅ Completed
- ⚠️ Delayed
- 🔴 Blocked

### Agent Workload

| Agent | Tasks Assigned | Tasks Completed | Tasks In Progress | Blocked |
|-------|----------------|-----------------|-------------------|---------|
| Orchestrator | - | - | - | - |
| Infrastructure | - | - | - | - |
| Backend | - | - | - | - |
| Frontend | - | - | - | - |
| Integration | - | - | - | - |
| QA | - | - | - | - |
| Documentation | - | - | - | - |

### Critical Metrics (Update Daily)

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| Days Elapsed | 11 | 0 | ⏳ |
| Tasks Completed | 100% | 0% | ⏳ |
| Critical Blockers | 0 | 0 | ✅ |
| Tests Passing | 100% | - | ⏳ |
| Uptime (Production) | 99.9% | - | ⏳ |
| API Response Time | <200ms | - | ⏳ |
| Page Load Time | <3s | - | ⏳ |

---

## 🎯 Quick Decision Matrix

### When to Escalate to Orchestrator

| Situation | Escalate? | Timeframe |
|-----------|-----------|-----------|
| Blocked >30 min by another agent | ✅ YES | Immediately |
| Technical decision needed (architecture) | ✅ YES | Within 1 hour |
| Scope change suggested | ✅ YES | Immediately |
| Timeline at risk | ✅ YES | Immediately |
| Bug found but unsure priority | ✅ YES | Within 30 min |
| Credentials missing | ✅ YES | Immediately |
| Need help with task | ⚠️ MAYBE | Try peer first, then escalate |
| Question about documentation | ❌ NO | Ask Documentation Agent |
| General questions | ❌ NO | Post in #deployment-general |

### When to Trigger Rollback

| Situation | Rollback? | Who Decides |
|-----------|-----------|-------------|
| Deployment fails completely | ✅ YES | Infrastructure Agent (immediate) |
| Critical endpoint returns 500 | ✅ YES | Orchestrator |
| Database connection fails | ✅ YES | Orchestrator |
| >50% error rate | ✅ YES | Orchestrator |
| Security vulnerability found | ✅ YES | Orchestrator + Stakeholder |
| Minor UI bug | ❌ NO | Fix in next deployment |
| Performance slightly slower | ❌ NO | Optimize and redeploy |
| Single integration failing | ⚠️ MAYBE | Orchestrator decides |

---

## 📞 Quick Contact Reference

| Agent | Slack Handle | Email | Emergency Phone |
|-------|--------------|-------|-----------------|
| Orchestrator | @orchestrator | [TBD] | [TBD] |
| Infrastructure | @infra-agent | [TBD] | [TBD] |
| Backend | @backend-agent | [TBD] | [TBD] |
| Frontend | @frontend-agent | [TBD] | [TBD] |
| Integration | @integration-agent | [TBD] | [TBD] |
| QA | @qa-agent | [TBD] | [TBD] |
| Documentation | @docs-agent | [TBD] | [TBD] |

### Slack Channels

- **#deployment-general** - General team chat
- **#deployment-alerts** - Automated alerts (CI/CD, monitoring)
- **#deployment-blockers** - Urgent blockers
- **#deployment-decisions** - Decision log
- **#deployment-celebrations** - Wins! 🎉

---

## 🎉 Motivation & Team Spirit

### Daily Celebration Moments

**When a phase gate is passed:**
```
🎉 PHASE [X] COMPLETE! 🎉

Great work team! We're one step closer to launch.
[X] days down, [Y] days to go!

Special shoutout to: [agents who went above and beyond]
```

**When a blocker is unblocked:**
```
✅ BLOCKER RESOLVED!

Thanks @agent-name for unblocking @agent-name!
Keep the momentum going! 💪
```

**When production deploys successfully:**
```
🚀 PRODUCTION LAUNCH! 🚀

We did it! The BMC Uruguay system is LIVE!
Thank you all for your hard work and dedication.
This is just the beginning! 🌟

Time to celebrate! 🎊
```

### Team Values

- **Transparency:** Share progress, blockers, and decisions openly
- **Collaboration:** Help each other, no silos
- **Quality:** Don't cut corners, test thoroughly
- **Ownership:** Take responsibility for your domain
- **Continuous Improvement:** Learn from mistakes, iterate
- **Respect:** Respect each other's time and expertise

---

**END OF TASK MATRIX**

**Remember:** This is a team effort. We succeed together! 💪
