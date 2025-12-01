#!/bin/bash
# Automated Backup and Recovery Script
# Based on BACKUP_RECOVERY_IMPLEMENTATION_PROMPT.md

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BACKUP_ROOT="$WORKSPACE_ROOT/backups/automated"
LOG_DIR="$WORKSPACE_ROOT/logs/backup"
RETENTION_DAYS=30

# Ensure log directory exists
mkdir -p "$LOG_DIR"

# Log file
LOG_FILE="$LOG_DIR/backup_$(date +%Y%m%d).log"

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# Function to check Python availability
check_python() {
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is not installed"
        exit 1
    fi
    log_info "Python 3 found: $(python3 --version)"
}

# Function to create backup
create_backup() {
    local backup_type=${1:-"incremental"}
    
    log_info "Starting $backup_type backup..."
    
    cd "$WORKSPACE_ROOT"
    
    if python3 scripts/backup_system.py create --type "$backup_type" >> "$LOG_FILE" 2>&1; then
        log_success "$backup_type backup completed successfully"
        return 0
    else
        log_error "$backup_type backup failed"
        return 1
    fi
}

# Function to verify latest backup
verify_backup() {
    log_info "Verifying latest backup..."
    
    cd "$WORKSPACE_ROOT"
    
    # Get latest backup ID
    local latest_backup=$(python3 scripts/backup_system.py list 2>/dev/null | grep "backup_" | head -1 | awk '{print $2}')
    
    if [ -z "$latest_backup" ]; then
        log_warning "No backups found to verify"
        return 1
    fi
    
    log_info "Verifying backup: $latest_backup"
    
    if python3 scripts/backup_system.py verify --backup-id "$latest_backup" >> "$LOG_FILE" 2>&1; then
        log_success "Backup verification passed"
        return 0
    else
        log_error "Backup verification failed"
        return 1
    fi
}

# Function to scan for missing files
scan_missing_files() {
    log_info "Scanning for missing files..."
    
    cd "$WORKSPACE_ROOT"
    
    local scan_output=$(python3 scripts/recovery_engine.py scan 2>&1)
    
    if echo "$scan_output" | grep -q "Found 0 missing files"; then
        log_success "No missing files detected"
        return 0
    else
        log_warning "Missing files detected:"
        echo "$scan_output" | grep "❌" | tee -a "$LOG_FILE"
        return 1
    fi
}

# Function to auto-recover missing files
auto_recover() {
    log_info "Attempting automatic recovery of missing files..."
    
    cd "$WORKSPACE_ROOT"
    
    if python3 scripts/recovery_engine.py batch >> "$LOG_FILE" 2>&1; then
        log_success "Automatic recovery completed"
        return 0
    else
        log_error "Automatic recovery failed"
        return 1
    fi
}

# Function to cleanup old backups
cleanup_backups() {
    log_info "Cleaning up backups older than $RETENTION_DAYS days..."
    
    cd "$WORKSPACE_ROOT"
    
    if python3 scripts/backup_system.py cleanup --retention-days "$RETENTION_DAYS" >> "$LOG_FILE" 2>&1; then
        log_success "Backup cleanup completed"
        return 0
    else
        log_error "Backup cleanup failed"
        return 1
    fi
}

# Function to check storage usage
check_storage() {
    log_info "Checking backup storage usage..."
    
    if [ -d "$BACKUP_ROOT" ]; then
        local usage=$(du -sh "$BACKUP_ROOT" 2>/dev/null | awk '{print $1}')
        log_info "Backup storage usage: $usage"
        
        # Check if usage is > 80% (optional, requires additional logic)
        # This is a simplified check
        local available=$(df -h "$BACKUP_ROOT" | tail -1 | awk '{print $5}' | sed 's/%//')
        if [ "$available" -gt 80 ]; then
            log_warning "Backup storage is over 80% full!"
        fi
    else
        log_info "Backup directory not yet created"
    fi
}

# Function to generate health report
generate_health_report() {
    log_info "Generating backup health report..."
    
    cd "$WORKSPACE_ROOT"
    
    local report_file="$LOG_DIR/health_report_$(date +%Y%m%d_%H%M%S).txt"
    
    {
        echo "===== BACKUP & RECOVERY HEALTH REPORT ====="
        echo "Generated: $(date '+%Y-%m-%d %H:%M:%S')"
        echo ""
        echo "=== Backup List ==="
        python3 scripts/backup_system.py list 2>/dev/null | head -10
        echo ""
        echo "=== Missing Files ==="
        python3 scripts/recovery_engine.py scan 2>&1 | grep -E "(Found|❌|⚠️)"
        echo ""
        echo "=== Storage Usage ==="
        du -sh "$BACKUP_ROOT" 2>/dev/null
        echo ""
        echo "=== Recent Logs ==="
        tail -20 "$LOG_FILE"
    } > "$report_file"
    
    log_success "Health report generated: $report_file"
    
    # Display summary
    cat "$report_file"
}

# Main execution functions
run_hourly() {
    log_info "=== Running hourly backup routine ==="
    check_python
    create_backup "incremental"
    scan_missing_files
}

run_daily() {
    log_info "=== Running daily backup routine ==="
    check_python
    create_backup "full"
    verify_backup
    scan_missing_files
    cleanup_backups
    check_storage
}

run_weekly() {
    log_info "=== Running weekly backup routine ==="
    check_python
    create_backup "full"
    verify_backup
    scan_missing_files
    cleanup_backups
    check_storage
    generate_health_report
}

run_recovery() {
    log_info "=== Running recovery routine ==="
    check_python
    scan_missing_files
    
    if [ $? -ne 0 ]; then
        log_info "Missing files detected, attempting recovery..."
        auto_recover
    fi
}

run_emergency_recovery() {
    log_error "=== EMERGENCY RECOVERY MODE ==="
    check_python
    
    log_info "Scanning for all issues..."
    scan_missing_files
    
    log_info "Attempting batch recovery..."
    auto_recover
    
    log_info "Creating new backup after recovery..."
    create_backup "full"
    
    log_info "Generating emergency report..."
    generate_health_report
}

# Help function
show_help() {
    cat << EOF
Automated Backup and Recovery Script

Usage: $0 [COMMAND]

Commands:
    hourly          Run hourly backup routine (incremental backup + scan)
    daily           Run daily backup routine (full backup + verify + cleanup)
    weekly          Run weekly backup routine (full backup + health report)
    recovery        Run recovery routine (scan + auto-recover if needed)
    emergency       Emergency recovery mode (full recovery attempt)
    
    create-backup   Create a backup (default: incremental)
    verify          Verify latest backup
    scan            Scan for missing/corrupted files
    cleanup         Cleanup old backups
    health          Generate health report
    
    help            Show this help message

Examples:
    $0 hourly                    # Run hourly routine
    $0 daily                     # Run daily routine
    $0 create-backup full        # Create full backup
    $0 recovery                  # Run recovery
    
Configuration:
    BACKUP_ROOT=$BACKUP_ROOT
    LOG_DIR=$LOG_DIR
    RETENTION_DAYS=$RETENTION_DAYS

For more information, see BACKUP_RECOVERY_QUICKSTART.md
EOF
}

# Parse command line arguments
case "${1:-help}" in
    hourly)
        run_hourly
        ;;
    daily)
        run_daily
        ;;
    weekly)
        run_weekly
        ;;
    recovery)
        run_recovery
        ;;
    emergency)
        run_emergency_recovery
        ;;
    create-backup)
        check_python
        create_backup "${2:-incremental}"
        ;;
    verify)
        check_python
        verify_backup
        ;;
    scan)
        check_python
        scan_missing_files
        ;;
    cleanup)
        check_python
        cleanup_backups
        ;;
    health)
        check_python
        generate_health_report
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        log_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac

exit 0
