# Master Agent Quick Reference
**Quick checklist and commands for Master Agent**

---

## 🚀 Quick Start Checklist

### Phase 1: Response Helpers (URGENT - 30-60 min)
```bash
# 1. Create file
touch src/lib/api-response.ts

# 2. Implement all 7 functions (see MASTER_AGENT_INSTRUCTIONS.md)

# 3. Verify
test -f src/lib/api-response.ts && echo "✅ EXISTS" || echo "❌ MISSING"
npm run lint -- src/lib/api-response.ts
```

### Phase 2: Type Safety (2-3 hours)

#### Agent 1: Import/Export
```bash
# Create type file
touch src/types/import-export.ts

# Fix any types
grep -n ":\s*any\b" src/app/api/import/route.ts src/app/api/export/route.ts
# Should return 0 after fix
```

#### Agent 2: Notifications/Settings
```bash
# Create type files
touch src/types/notifications.ts src/types/settings.ts

# Fix any types
grep -n ":\s*any\b" src/app/api/notifications/route.ts src/app/api/settings/route.ts
# Should return 0 after fix
```

#### Agent 3: Recovery/Analytics
```bash
# Create type files
touch src/types/recovery.ts src/types/analytics.ts

# Fix any types
grep -n ":\s*any\b" src/app/api/recovery/route.ts src/app/api/analytics/quotes/route.ts src/app/api/trends/route.ts
# Should return 0 after fix
```

#### Agent 4: Context/Sheets
```bash
# Create type file
touch src/types/sheets.ts

# Enhance existing
# Edit src/types/context.ts (add types)

# Fix any types
grep -n ":\s*any\b" src/app/api/context/shared/route.ts src/app/api/sheets/enhanced-sync/route.ts
# Should return 0 after fix
```

### Phase 3: Python Type Hints (2-3 hours)

#### Agent 7: api_server.py
```bash
# Add type hints to all functions
# Verify:
grep -E "def [a-zA-Z_]+\([^)]*\)\s*->" api_server.py | wc -l
# Should show all functions
```

#### Agent 8: sistema_completo_integrado.py
```bash
# Add type hints to all functions
# Verify:
grep -E "def [a-zA-Z_]+\([^)]*\)\s*->" sistema_completo_integrado.py | wc -l
# Should show all functions
```

### Phase 4: Response Standardization (2-3 hours)
```bash
# Update 11 routes to use helpers
# Verify:
grep -r "from '@/lib/api-response'" src/app/api/ | wc -l
# Should show 11 files
```

---

## 📊 Progress Verification Commands

Run these after each phase:

```bash
# 1. Check any types remaining (should be 0)
echo "=== Any Types Remaining ==="
grep -rn ":\s*any\b" src/app/api/ | wc -l

# 2. Check type files created (should be 10 total)
echo "=== Type Files ==="
ls -1 src/types/*.ts | wc -l

# 3. Check api-response.ts exists
echo "=== API Response Helpers ==="
test -f src/lib/api-response.ts && echo "✅ EXISTS" || echo "❌ MISSING"

# 4. Check Python type hints
echo "=== Python Type Hints ==="
echo "api_server.py: $(grep -E "def [a-zA-Z_]+\([^)]*\)\s*->" api_server.py | wc -l) functions"
echo "sistema_completo_integrado.py: $(grep -E "def [a-zA-Z_]+\([^)]*\)\s*->" sistema_completo_integrado.py | wc -l) functions"

# 5. Check response helpers usage
echo "=== Response Helpers Usage ==="
grep -r "from '@/lib/api-response'" src/app/api/ | wc -l
```

---

## ✅ Final Verification

```bash
# Complete verification script
./verify-master-agent-work.sh
```

---

## 🎯 Success Metrics

- ✅ 0 `any` types remaining
- ✅ 10 type definition files (4 existing + 6 new)
- ✅ `api-response.ts` exists with 7 functions
- ✅ 11 routes using response helpers
- ✅ All Python functions have type hints
- ✅ Linter passes
- ✅ Type check passes

---

**Quick Reference - Keep this handy while working!**


