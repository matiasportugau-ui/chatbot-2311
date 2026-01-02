# Master Prompt: Recovered Data Integration Script

## Overview

Create a comprehensive Python script that integrates recovered Cursor chat data into the BMC Chatbot system. The script should parse recovered JSON files, transform the data to match MongoDB schemas, and import it into the appropriate collections while maintaining data integrity and providing detailed logging.

## Context

### Recovered Data Files

1. **`recovered_chats.json`** (86MB, ~570,000 lines)
   - Format: Line-delimited JSON (JSONL) - each line is a separate JSON object
   - Contains: Extracted Cursor chat history from SQLite databases
   - Structure: Unknown exact schema, needs analysis during implementation

2. **`recovery_recent_chats.json`** (61KB)
   - Format: Single JSON object
   - Structure:
     ```json
     {
       "extraction_date": "2025-12-01T17:59:19.837163",
       "time_window_hours": 24,
       "total_sessions": 5,
       "sessions": [
         {
           "key": "composer.composerData",
           "data": {
             "allComposers": [...],
             "composerId": "...",
             "name": "...",
             "lastUpdatedAt": 1764621953571,
             "createdAt": 1764621866226,
             ...
           }
         }
       ]
     }
     ```

3. **`recovery_composer_data.json`** (2.3MB, ~64,000 lines)
   - Format: Single JSON object
   - Structure:
     ```json
     {
       "extraction_date": "...",
       "total_items": 1234,
       "items": [...]
     }
     ```

4. **`recovery_report_*.json`** (Multiple files, 42KB each)
   - Format: Single JSON object
   - Contains: MongoDB scan results and filesystem backup information
   - Structure includes:
     - `mongodb.collections` - Collection counts and samples
     - `filesystem.backups` - Backup file paths and conversation counts
     - Sample conversation data with `session_id`, `phone`, `messages`, `timestamp`

### Target System

**MongoDB Database:** `bmc-cotizaciones` (or `bmc_chat` based on configuration)

**Target Collections:**
- `conversations` / `conversaciones` - Main conversation storage
- `sessions` - Session metadata
- `context` - Conversation context and state
- `quotes` / `cotizaciones` - Quotation data (if applicable)
- `analytics` - Analytics data (if applicable)

**Expected Schema (based on existing code):**
```python
{
    "session_id": str,           # Unique session identifier
    "phone": str,                # Phone number (WhatsApp format: +59898765432)
    "started_at": datetime,      # ISO format timestamp
    "timestamp": datetime,       # Message timestamp
    "createdAt": datetime,       # Creation timestamp
    "messages": [                # Array of messages
        {
            "timestamp": datetime,
            "user_message": str,
            "bot_response": {
                "mensaje": str,
                "tipo": str,     # e.g., "informativa"
                "acciones": list,
                "confianza": float,
                "necesita_datos": list,
                "sesion_id": str,
                "timestamp": datetime
            },
            "session_id": str
        }
    ],
    "metadata": {
        "source": "cursor_recovery",  # Indicate data source
        "recovery_date": datetime,
        "original_file": str
    }
}
```

## Requirements

### Functional Requirements

1. **Data Parsing**
   - Parse JSONL format from `recovered_chats.json` (line-by-line)
   - Parse single JSON objects from other recovery files
   - Handle malformed JSON gracefully with error logging
   - Support both single objects and arrays of objects

2. **Data Transformation**
   - Map Cursor chat data to MongoDB conversation schema
   - Extract session IDs, timestamps, and message content
   - Normalize timestamps to ISO format
   - Handle missing fields with sensible defaults
   - Preserve original data in metadata field

3. **Data Deduplication**
   - Check for existing conversations by `session_id` or unique message hash
   - Skip duplicates or update existing records (configurable)
   - Log duplicate detection statistics

4. **MongoDB Integration**
   - Connect to MongoDB using existing connection patterns
   - Use `mongodb_service.py` or `pymongo` directly
   - Support batch inserts for performance
   - Handle connection errors gracefully
   - Support dry-run mode (validate without inserting)

5. **Progress Tracking**
   - Show progress bar for large files
   - Log statistics: processed, inserted, skipped, failed
   - Generate summary report after completion

6. **Error Handling**
   - Continue processing on individual record failures
   - Log all errors with context (line number, record ID, error message)
   - Create error report file
   - Validate data before insertion

### Technical Requirements

1. **Script Structure**
   - Location: `scripts/integrate_recovered_data.py`
   - CLI interface with argparse
   - Configuration via command-line arguments and/or config file
   - Modular design: separate functions for parsing, transformation, insertion

2. **Dependencies**
   - Use existing project dependencies (pymongo, python-dotenv)
   - Follow project coding standards (ruff formatting, type hints)
   - Add to `requirements.txt` if new dependencies needed

3. **Configuration**
   - MongoDB URI from environment variable or config
   - Target collections configurable
   - Batch size configurable (default: 100)
   - Dry-run mode flag
   - Duplicate handling strategy (skip/update/error)

4. **Logging**
   - Use Python logging module
   - Log to both console and file
   - Log levels: INFO (progress), WARNING (duplicates), ERROR (failures)
   - Include timestamps and context in all log messages

5. **Output**
   - Console output with colored progress indicators (optional)
   - Summary report: JSON and/or markdown format
   - Error report: JSON format with failed records
   - Statistics: counts, timing, success rate

## Implementation Guidelines

### Phase 1: Data Analysis
1. Create a helper script to analyze recovered data structure
2. Sample records from each file type
3. Document actual schema vs expected schema
4. Identify transformation requirements

### Phase 2: Core Parser
1. Implement JSONL parser for `recovered_chats.json`
2. Implement JSON parser for other files
3. Add validation and error handling
4. Extract key fields (session_id, timestamps, messages)

### Phase 3: Data Transformer
1. Map Cursor data to MongoDB schema
2. Handle timestamp conversion
3. Normalize message format
4. Add metadata fields

### Phase 4: MongoDB Integration
1. Connect to MongoDB
2. Implement batch insert with error handling
3. Add duplicate detection
4. Support dry-run mode

### Phase 5: CLI and Reporting
1. Implement argparse CLI
2. Add progress tracking
3. Generate summary reports
4. Create error reports

### Phase 6: Testing and Validation
1. Test with sample data
2. Validate data integrity
3. Test error scenarios
4. Performance testing with large files

## Command-Line Interface

```bash
python3 scripts/integrate_recovered_data.py \
    --input recovered_chats.json \
    --collection conversations \
    --batch-size 100 \
    --dry-run \
    --skip-duplicates \
    --log-file integration.log \
    --report integration_report.json
```

**Arguments:**
- `--input` (required): Path to recovered data file(s), supports multiple files
- `--collection` (default: "conversations"): Target MongoDB collection
- `--batch-size` (default: 100): Number of records per batch insert
- `--dry-run`: Validate and report without inserting to MongoDB
- `--skip-duplicates`: Skip records that already exist (default: error)
- `--update-duplicates`: Update existing records instead of skipping
- `--mongodb-uri`: Override MongoDB URI from environment
- `--log-file`: Path to log file (default: integration.log)
- `--report`: Path to summary report (default: integration_report.json)
- `--verbose`: Enable debug logging
- `--max-records`: Limit number of records to process (for testing)

## Success Criteria

1. ✅ Successfully parses all three file types
2. ✅ Transforms data to match MongoDB schema
3. ✅ Inserts data into MongoDB without errors
4. ✅ Handles duplicates appropriately
5. ✅ Provides detailed logging and reporting
6. ✅ Handles errors gracefully without stopping
7. ✅ Validates data before insertion
8. ✅ Generates comprehensive summary report
9. ✅ Follows project coding standards
10. ✅ Includes documentation and usage examples

## Edge Cases to Handle

1. **Malformed JSON**: Skip with error log, continue processing
2. **Missing required fields**: Use defaults or skip with warning
3. **Invalid timestamps**: Parse or use current timestamp as fallback
4. **Duplicate session_ids**: Handle based on strategy (skip/update/error)
5. **MongoDB connection failures**: Retry with exponential backoff
6. **Large file processing**: Stream processing for memory efficiency
7. **Mixed data formats**: Detect and handle different schemas
8. **Encoding issues**: Handle UTF-8 and other encodings
9. **Empty files**: Graceful handling with informative messages
10. **Partial failures**: Continue processing, report failures separately

## Documentation Requirements

1. **Script Documentation**
   - Docstrings for all functions
   - Type hints for all parameters
   - Usage examples in docstring

2. **README Section**
   - Add section to project README or create separate doc
   - Usage instructions
   - Configuration options
   - Troubleshooting guide

3. **Code Comments**
   - Explain complex transformation logic
   - Document schema mappings
   - Note any assumptions or limitations

## Testing Strategy

1. **Unit Tests**
   - Test parsers with sample data
   - Test transformers with various input formats
   - Test duplicate detection logic

2. **Integration Tests**
   - Test MongoDB connection and insertion
   - Test with actual recovery files (small samples)
   - Test error handling scenarios

3. **Validation**
   - Verify data integrity after insertion
   - Compare source and target data
   - Check for data loss or corruption

## Deliverables

1. **Main Script**: `scripts/integrate_recovered_data.py`
2. **Helper Scripts** (if needed):
   - `scripts/analyze_recovered_data.py` - Data structure analysis
   - `scripts/validate_integration.py` - Post-integration validation
3. **Documentation**:
   - Inline code documentation
   - README section or separate doc
   - Usage examples
4. **Reports**:
   - Integration summary report template
   - Error report format specification

## Notes

- The script should be idempotent (safe to run multiple times)
- Consider memory efficiency for large files (streaming/iterators)
- Preserve original data in metadata for traceability
- Follow existing project patterns and conventions
- Use existing MongoDB connection utilities if available
- Consider adding data validation against known schemas
- Support incremental processing (resume from last position)

## Questions to Resolve During Implementation

1. What is the exact schema of `recovered_chats.json`?
2. How should Cursor composer data map to conversations?
3. Should we create separate collections for different data types?
4. How to handle timestamps that are in milliseconds vs ISO format?
5. Should we merge multiple recovery files or process separately?
6. What metadata should be preserved from original data?
7. How to handle relationships between sessions and conversations?
8. Should we update the knowledge base with recovered data?

---

**Created:** 2025-12-01  
**Purpose:** Master prompt for creating recovered data integration script  
**Status:** Ready for implementation

