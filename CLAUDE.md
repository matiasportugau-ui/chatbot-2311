# CRM Dashboard Project - Claude Memory

**Last Updated:** 2025-12-16
**Project Status:** Phase 5 Complete, Phase 6 Planning
**Repository:** https://github.com/matiasportugau-ui/chatbot-2311
**Branch:** fusion

---

## Project Overview

**Goal:** Build a comprehensive CRM dashboard system with authentication, Kanban boards, Google Sheets integration, and analytics.

**Tech Stack:**
- Next.js 14 (App Router)
- TypeScript
- MongoDB (Database)
- NextAuth.js v5 (Authentication)
- React Query (Server State)
- Zustand (Client State)
- Shadcn/ui + Radix UI (Components)
- @dnd-kit (Drag & Drop)
- Tailwind CSS (Styling)

---

## Completed Phases

### ✅ Phase 1: Foundation (Commit: `f40dc740`)
- Architecture design (CRM_ARCHITECTURE.md)
- Dependencies installed
- Project structure initialized
- Shadcn/ui configuration

### ✅ Phase 2: Authentication System (Commit: `b18776aa`)
- NextAuth v5 with Credentials provider
- MongoDB user management (CRUD)
- RBAC system: 4 roles (admin, manager, sales, viewer)
- 24 granular permissions
- Bcrypt password hashing (12 rounds)
- JWT sessions (30-day expiry)
- Route protection middleware
- **Files:** 18 files (2,552 insertions)

### ✅ Phase 3: Dashboard Layout (Commit: `ff9a8b11`)
- Responsive header with mobile menu
- User dropdown with avatar and role badge
- Sidebar navigation (6 menu items)
- Mobile-first responsive design
- SessionProvider integration
- **Files:** 13 files (832 insertions)

### ✅ Phase 4: State Management (Commit: `4816892a`)
- React Query provider (60s stale time, 1 retry)
- Zustand stores (auth, UI with localStorage)
- User management hooks (useUsers, useUser, CRUD mutations)
- Query invalidation on mutations
- **Files:** 6 files (335 insertions)

### ✅ Phase 5: Kanban Board (Commit: `e56e60ce`)
- Quote type system (status, priority, full Quote interface)
- KanbanBoard component with @dnd-kit
- KanbanColumn and QuoteCard components
- Touch-friendly drag & drop (8px activation)
- Demo data (4 sample quotes)
- Real-time statistics dashboard
- **Files:** 6 files (589 insertions)

---

## Current Architecture

### Database Collections (MongoDB)
- `users` - User accounts with RBAC
- `crm_customers` - Customer records
- `crm_quotes` - Quote documents
- `crm_interactions` - Customer interactions
- `crm_notes` - Notes and comments

### API Routes Structure
```
/api/auth/[...nextauth]/     - NextAuth handlers
/api/users/                   - User list & create
/api/users/[id]/              - User get/update/delete
/api/seed-users/              - Demo user seeding
/api/crm/customers/           - Customer CRUD (existing)
/api/crm/customers/[id]/      - Customer operations
/api/crm/interactions/        - Interaction tracking
/api/crm/notes/               - Notes management
/api/crm/stats/               - CRM statistics
```

### File Structure
```
src/
├── app/
│   ├── (auth)/               - Login pages
│   ├── (dashboard)/crm/      - Protected CRM routes
│   └── api/                  - API endpoints
├── components/
│   ├── ui/                   - Shadcn primitives
│   ├── layout/               - Header, Sidebar, DashboardLayout
│   ├── features/kanban/      - Kanban board components
│   └── providers/            - SessionProvider, QueryProvider
├── lib/
│   ├── auth/                 - Auth config, service, RBAC, session
│   ├── crm/                  - CRM service layer
│   └── mongodb.ts            - MongoDB connection
├── hooks/                    - React Query hooks
├── stores/                   - Zustand stores
└── types/                    - TypeScript definitions
```

---

## Key Patterns Established

### API Route Pattern
```typescript
export async function GET(request: NextRequest) {
  await requirePermission('resource:action')
  const db = await connectDB()
  // ... operation
  return NextResponse.json({ success: true, data })
}
```

### Error Handling Pattern
- 200: Success
- 201: Created
- 400: Bad request (validation)
- 401: Unauthorized
- 403: Forbidden (permission)
- 404: Not found
- 409: Conflict (duplicate)
- 500: Server error

### MongoDB Connection Pattern
- Singleton with connection pooling
- URI validation (mongodb:// or mongodb+srv://)
- Reuse existing connections
- Auto-reconnect on failure

### RBAC Pattern
```typescript
// Check permission
await requirePermission('quotes:create')

// Get current user
const userId = await getCurrentUserId()

// Prevent self-modification
if (userId === targetId) throw new Error('Cannot modify self')
```

---

## Environment Variables Required

```bash
# MongoDB
MONGODB_URI=mongodb://localhost:27017/bmc-cotizaciones

# NextAuth
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=<generate-with-openssl-rand-base64-32>

# Optional: Google Sheets (Phase 6)
GOOGLE_SHEETS_API_KEY=<your-key>
GOOGLE_SHEETS_SPREADSHEET_ID=<your-id>
```

---

## Demo Credentials

After running seed:
- **Admin:** admin@example.com / admin123
- **Manager:** manager@example.com / manager123
- **Sales:** sales@example.com / sales123
- **Viewer:** viewer@example.com / viewer123

---

## Known Issues & Limitations

1. **Phase 5:** Currently using demo data (not connected to MongoDB)
2. **Cache files:** .next/cache files caused git push warnings (71 MB)
3. **No real-time sync:** WebSocket/SSE not implemented yet
4. **No quote creation UI:** Kanban only displays, doesn't create

---

## Next Phases (Planned)

### Phase 6: CRM API & Google Sheets Integration
- Real quote CRUD API endpoints
- Quote creation/editing UI
- Quote detail modal
- Search and filters
- Bidirectional Google Sheets sync

### Phase 7: Analytics Dashboard
- Quote analytics (conversion rate, average value)
- Customer analytics (lifetime value, status distribution)
- Charts and visualizations
- Date range filters

### Phase 8: Polish & Testing
- Error boundaries
- Loading states
- Toast notifications
- E2E tests with Playwright
- Performance optimization
- Accessibility audit

---

## Development Workflow

1. **Plan:** Review requirements, explore codebase
2. **Implement:** Write code following established patterns
3. **Test:** Manual testing + automated tests
4. **Document:** Update CRM_BUILD_PROGRESS.md
5. **Commit:** Git commit with detailed message
6. **Push:** Push to GitHub (fusion branch)

---

## Cost & Performance Notes

### Token Usage Patterns
- Phase planning: ~5,000-10,000 tokens
- Implementation: ~20,000-40,000 tokens per phase
- Documentation: ~5,000 tokens
- Testing & debugging: ~10,000-20,000 tokens

### Session Budget
- Token cap: 200,000 tokens per session
- Current usage (Phase 5 complete): ~68,000 tokens (34% used)
- Remaining: ~132,000 tokens (66% available)

### Build Performance
- Development server start: ~3-5s
- Hot reload: <1s
- Production build: ~30-45s
- Page load (dev): ~200-400ms

---

## Testing Strategy

### Manual Testing
1. Authentication flow (login/logout)
2. User management (CRUD operations)
3. Kanban drag & drop
4. Responsive design (mobile/desktop)
5. Dark mode toggle

### Automated Testing (Planned)
- Unit tests: Component logic
- Integration tests: API routes
- E2E tests: User flows
- Visual regression: Chromatic/Percy

---

## References

- **Architecture:** [CRM_ARCHITECTURE.md](CRM_ARCHITECTURE.md)
- **Build Progress:** [CRM_BUILD_PROGRESS.md](CRM_BUILD_PROGRESS.md)
- **Design:** [CRM_DASHBOARD_DESIGN.md](CRM_DASHBOARD_DESIGN.md)
- **API Patterns:** Documented in exploration agent (efcd1ee9)

---

## Git Status

- **Current branch:** fusion
- **Commits ahead:** 9 commits (Phases 2-5 + docs)
- **Pushed to GitHub:** ✅ Yes (cleaned history, large files removed)
- **Backup branch:** fusion-backup-before-filter

---

## Contact & Collaboration

- **Developer:** Matias (matiasportugau-ui)
- **AI Assistant:** Claude Sonnet 4.5 (claude-sonnet-4-5-20250929)
- **Collaboration mode:** Autopilot (user approves major decisions)

---

**End of Project Memory**
*This file is automatically updated after each phase completion*
