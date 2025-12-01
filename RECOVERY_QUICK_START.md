# Recovery Quick Start Guide

## 🚀 Immediate Actions (Do These First)

### 1. Extract Chat History
```bash
python3 extract_cursor_chat.py --output chat_recovery.json
```

### 2. Review Timeline
- Open files that were modified during the lost session
- Right-click → "Open Timeline" 
- Restore versions from before the crash

### 3. Provide Context
Tell the agent:
- **Time window:** When did the data loss occur?
- **Keywords:** What topics were discussed?
- **Files:** Which files were being worked on?

## 📋 Files Created

- `extract_cursor_chat.py` - Chat extraction script
- `RECOVERY_PLAN.md` - Full detailed recovery plan
- `recovery_plan.json` - Machine-readable plan (formatted)
- `recovery_plan_single_line.json` - Single-line JSON (for automation)

## 📊 Recovery Likelihood

| Method | Likelihood | Status |
|--------|------------|--------|
| Cursor Chat DB | HIGH | ✅ Script ready |
| Timeline History | HIGH | ⏳ Manual review needed |
| Git Reflog | MEDIUM | ✅ Checked (clean) |
| Auto-save Files | MEDIUM | ⏳ Needs investigation |
| Temp Files | LOW | ✅ Checked (none found) |

## ⚠️ Important Notes

1. **Act quickly** - Recovery success decreases over time
2. **Timeline expires** - Check immediately for best results
3. **Work on copies** - Never modify original databases
4. **Provide context** - Helps filter and prioritize recovery

## 📖 Full Documentation

See `RECOVERY_PLAN.md` for complete details, all tasks, and enhancement suggestions.
