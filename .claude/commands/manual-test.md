---
description: "Run manual testing checklist for current phase"
---

# Manual Testing Guide

Execute comprehensive manual testing for completed phases:

## Prerequisites
```bash
npm run dev
# Ensure MongoDB is running
# Ensure demo users are seeded
```

## Test Authentication (Phase 2)
1. Login with admin credentials
2. Test RBAC (admin/manager/sales/viewer)
3. Verify session persistence
4. Test logout flow

## Test Dashboard Layout (Phase 3)
1. Check responsive design (mobile/tablet/desktop)
2. Toggle dark mode
3. Test navigation menu
4. Verify user dropdown

## Test Kanban Board (Phase 5)
1. Drag & drop quotes between columns
2. Test touch drag on mobile
3. Verify statistics update
4. Check quote card details

## API Testing
```bash
# List users
curl http://localhost:3000/api/users \
  -H "Cookie: next-auth.session-token=YOUR_SESSION"

# Create user
curl -X POST http://localhost:3000/api/users \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123","name":"Test User","role":"sales"}'
```

## Expected Results
- ✅ All authentication flows work
- ✅ Responsive design on all screen sizes
- ✅ Drag & drop smooth and accurate
- ✅ API responds with correct status codes

**Report issues:** Create GitHub issue with steps to reproduce
