# Auto-Save Feature

Automatic saving of your work every 15 minutes (configurable).

## Overview

The auto-save feature creates lightweight snapshots of your current work at regular intervals. This provides:

- **Quick recovery** if something goes wrong
- **Minimal overhead** (only saves recent changes)
- **Automatic cleanup** (keeps last 24 hours)
- **Configurable intervals** (default: 15 minutes)

## Configuration

Edit `backup_system/backup_config.json`:

```json
{
  "autosave": {
    "enabled": true,
    "interval_minutes": 15,
    "scope": ["filesystem", "mongodb"],
    "lightweight": true
  }
}
```

### Options

- **enabled**: Enable/disable auto-save (default: true)
- **interval_minutes**: How often to auto-save (default: 15)
- **scope**: What to save (filesystem, mongodb, or both)
- **lightweight**: Only save recent changes (default: true)
  - Files: Only files modified in last 24 hours
  - MongoDB: Only most recent 100 documents per collection

## Usage

### Automatic (via Scheduler)

Start the scheduler and auto-save runs automatically:

```bash
python3 backup_system/scheduler.py
```

Auto-save will run every 15 minutes (or your configured interval).

### Manual

Create an autosave now:

```bash
# Via CLI
python3 backup_system/autosave.py --create

# Via API
curl -X POST http://localhost:3000/api/backup/autosave
```

List recent autosaves:

```bash
# Via CLI
python3 backup_system/autosave.py --list

# Via API
curl http://localhost:3000/api/backup/autosave?action=list
```

## How It Works

1. **Every 15 minutes** (or configured interval), the scheduler triggers auto-save
2. **Lightweight snapshot** is created:
   - Only files modified in last 24 hours
   - Only recent MongoDB documents (100 per collection)
3. **Saved to** `./autosaves/` directory
4. **Compressed** if compression is enabled
5. **Old autosaves cleaned up** (keeps last 24 hours = ~96 autosaves)

## Recovery from Auto-Save

Auto-saves can be restored like regular backups:

```bash
# List autosaves
python3 backup_system/autosave.py --list

# Restore from autosave (use recover.py)
python3 recover.py restore autosave_20251201_180000 --scope filesystem
```

## Storage

- **Location**: `./autosaves/`
- **Format**: JSON (compressed if enabled)
- **Retention**: Last 24 hours (~96 autosaves at 15-min intervals)
- **Size**: Typically much smaller than full backups (only recent changes)

## Integration

Auto-save is automatically integrated with:

- ✅ **Scheduler** - Runs every 15 minutes
- ✅ **Monitoring** - Tracks autosave status
- ✅ **API** - Available via REST endpoints
- ✅ **Recovery** - Can restore from autosaves

## Example Output

```bash
$ python3 backup_system/autosave.py --create

{
  "success": true,
  "autosave_id": "autosave_20251201_181500",
  "timestamp": "2025-12-01T18:15:00",
  "file": "./autosaves/autosave_20251201_181500.json.gz",
  "size": 45678
}
```

## Notes

- Auto-saves are **lightweight** and fast
- They complement regular backups (don't replace them)
- Use for quick recovery of recent work
- For complete recovery, use full backups
- Auto-saves are automatically cleaned up after 24 hours

