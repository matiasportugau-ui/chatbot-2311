# 📋 Backup & Recovery Implementation Prompts

## Overview

This directory contains comprehensive prompts for implementing a backup and lost files recovery system for the chatbot application. These prompts are designed to guide developers or AI agents through building a robust, production-ready backup and recovery solution.

## Files

### 1. `BACKUP_RECOVERY_IMPLEMENTATION_PROMPT.md`
**Comprehensive detailed prompt** - Use this for:
- Full system implementation
- Understanding complete requirements
- Architecture and design decisions
- Detailed specifications
- Testing and documentation requirements

**Contents:**
- Complete system requirements (13 sections)
- Detailed architecture components
- Data structures and schemas
- Implementation phases (5 phases)
- Error handling and edge cases
- Security requirements
- Testing requirements
- Configuration examples
- Success criteria

### 2. `BACKUP_RECOVERY_QUICK_PROMPT.md`
**Quick reference prompt** - Use this for:
- Quick implementation overview
- Feature checklist
- Fast reference during development
- AI agent quick starts

**Contents:**
- Core components overview
- Key features checklist
- Implementation checklist
- Quick start commands
- Basic configuration

## How to Use These Prompts

### For Developers
1. **Start with the Quick Prompt** to get an overview
2. **Reference the Full Prompt** for detailed specifications
3. **Follow the implementation phases** sequentially
4. **Use the checklists** to track progress

### For AI Agents
1. **Read the Quick Prompt first** for context
2. **Use the Full Prompt** as the source of truth
3. **Follow the implementation phases** in order
4. **Reference data structures** from the Full Prompt
5. **Implement error handling** as specified

### For Project Managers
1. **Review the Quick Prompt** for feature overview
2. **Check the Full Prompt** for detailed requirements
3. **Use the success criteria** to validate completion
4. **Reference the implementation priority** for planning

## Implementation Approach

### Recommended Workflow

1. **Phase 1: Core Backup System** (Week 1-2)
   - Implement basic backup functionality
   - Test with small datasets
   - Verify backup integrity

2. **Phase 2: Recovery System** (Week 2-3)
   - Build recovery engine
   - Implement file scanning
   - Test recovery scenarios

3. **Phase 3: CLI & API** (Week 3-4)
   - Create command-line tools
   - Build REST API endpoints
   - Add authentication

4. **Phase 4: Automation** (Week 4-5)
   - Implement scheduling
   - Add monitoring
   - Set up alerts

5. **Phase 5: Advanced Features** (Week 5-6)
   - Incremental backups
   - Point-in-time recovery
   - Cloud storage support

## Key Features

### Backup System
- ✅ Full and incremental backups
- ✅ Scheduled automatic backups
- ✅ Compression and encryption
- ✅ Backup verification
- ✅ Retention policies
- ✅ Multiple storage backends

### Recovery System
- ✅ Multi-source scanning
- ✅ Lost file detection
- ✅ Selective restoration
- ✅ Conflict resolution
- ✅ Dry-run mode
- ✅ Audit logging

## Integration with Existing Code

The prompts are designed to work with the existing codebase:

- **Existing Recovery Script**: `scripts/recover_conversations.py`
  - Can be extended or refactored based on the new architecture
  - Current functionality should be preserved

- **Existing API**: `src/app/api/recovery/route.ts`
  - Can be enhanced with new endpoints
  - Should maintain backward compatibility

- **Existing Setup Recovery**: `scripts/recover_setup.py`
  - Can be integrated into the new recovery service
  - Should be part of the unified recovery system

## Testing Strategy

1. **Unit Tests**: Test each component independently
2. **Integration Tests**: Test backup/restore workflows
3. **Performance Tests**: Test with large datasets
4. **Disaster Recovery Tests**: Simulate data loss scenarios

## Success Metrics

The implementation is successful when:

- ✅ All data sources can be backed up reliably
- ✅ Lost files can be detected automatically
- ✅ Data can be restored with >99% success rate
- ✅ CLI and API are fully functional
- ✅ Scheduled backups run without failures
- ✅ System handles errors gracefully
- ✅ Documentation is complete

## Next Steps

1. **Review the prompts** to understand requirements
2. **Plan the implementation** using the phases
3. **Set up development environment**
4. **Start with Phase 1** (Core Backup System)
5. **Iterate and test** each phase before moving forward
6. **Document as you go** following the documentation requirements

## Questions or Issues?

If you encounter issues or need clarification:

1. Check the Full Prompt for detailed specifications
2. Review existing recovery code for patterns
3. Reference the data structures section
4. Check error handling examples

## Example Usage

### Quick Start (Using Quick Prompt)
```bash
# Read the quick prompt
cat BACKUP_RECOVERY_QUICK_PROMPT.md

# Start implementing Phase 1
# Create backup_service.py based on the checklist
```

### Full Implementation (Using Full Prompt)
```bash
# Read the comprehensive prompt
cat BACKUP_RECOVERY_IMPLEMENTATION_PROMPT.md

# Follow the implementation phases
# Reference data structures and examples
# Implement according to specifications
```

---

**These prompts provide everything needed to implement a production-ready backup and recovery system. Follow them systematically for best results.**
