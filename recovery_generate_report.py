#!/usr/bin/env python3
"""
Generate Comprehensive Recovery Report
Consolidates all recovery findings into a comprehensive report
"""
import json
import os
from datetime import datetime
from pathlib import Path

def load_json_file(filepath):
    """Load JSON file if it exists"""
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return None
    return None

def count_lines(filepath):
    """Count lines in a file"""
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return len(f.readlines())
        except:
            return 0
    return 0

def get_file_size(filepath):
    """Get file size in bytes"""
    if os.path.exists(filepath):
        return os.path.getsize(filepath)
    return 0

def format_size(size_bytes):
    """Format file size in human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"

def generate_recovery_report():
    """Generate comprehensive recovery report"""
    workspace_path = "/Users/matias/chatbot2511/chatbot-2311"
    
    report = {
        'generated_at': datetime.now().isoformat(),
        'recovery_summary': {},
        'channels': [],
        'recovered_items': [],
        'irrecoverable_items': [],
        'statistics': {},
        'recommendations': []
    }
    
    # Load recovery data
    recent_chats = load_json_file(os.path.join(workspace_path, "recovery_recent_chats.json"))
    composer_data = load_json_file(os.path.join(workspace_path, "recovery_composer_data.json"))
    reconstructed = load_json_file(os.path.join(workspace_path, "recovery_reconstructed_context.json"))
    deep_analysis = load_json_file(os.path.join(workspace_path, "recovery_deep_analysis.json"))
    
    # Git state
    git_status_lines = count_lines(os.path.join(workspace_path, "recovery_git_status.txt"))
    git_diff_lines = count_lines(os.path.join(workspace_path, "recovery_git_diff_full.txt"))
    
    # Stash analysis
    stash_list_lines = count_lines(os.path.join(workspace_path, "recovery_stash_list.txt"))
    stash_contents_lines = count_lines(os.path.join(workspace_path, "recovery_stash_contents.txt"))
    
    # Statistics
    stats = {
        'recent_chat_sessions': recent_chats.get('total_sessions', 0) if recent_chats else 0,
        'composer_items': composer_data.get('total_items', 0) if composer_data else 0,
        'unique_files_referenced': reconstructed.get('summary', {}).get('total_unique_files', 0) if reconstructed else 0,
        'code_blocks_found': reconstructed.get('summary', {}).get('total_code_blocks', 0) if reconstructed else 0,
        'git_modified_files': git_status_lines,
        'git_stashes': stash_list_lines,
        'databases_analyzed': deep_analysis.get('total_databases', 0) if deep_analysis else 0
    }
    
    report['statistics'] = stats
    
    # Recovery channels assessment
    channels = [
        {
            'name': 'cursor_chat_db',
            'likelihood': 'HIGH',
            'notes': f"Found {stats['recent_chat_sessions']} recent chat sessions. Databases accessible and previous extraction successful.",
            'items_recovered': stats['recent_chat_sessions']
        },
        {
            'name': 'composer_unsaved_buffers',
            'likelihood': 'MEDIUM',
            'notes': f"Found {stats['composer_items']} composer items. Some may contain unsaved code edits.",
            'items_recovered': stats['composer_items']
        },
        {
            'name': 'git_history',
            'likelihood': 'HIGH',
            'notes': f"Active git repository with {stats['git_modified_files']} modified files and {stats['git_stashes']} stashes available.",
            'items_recovered': stats['git_modified_files']
        },
        {
            'name': 'local_history_timeline',
            'likelihood': 'MEDIUM',
            'notes': "Requires manual check via Cursor's Timeline feature for each modified file.",
            'items_recovered': 0
        },
        {
            'name': 'temporary_files',
            'likelihood': 'LOW',
            'notes': "No temporary or backup files found in project directory or system caches.",
            'items_recovered': 0
        },
        {
            'name': 'sqlite_wal_journal',
            'likelihood': 'LOW',
            'notes': "No WAL or journal files found. Databases appear to be in consistent state.",
            'items_recovered': 0
        }
    ]
    
    report['channels'] = channels
    
    # Recovered items
    recovered = []
    
    if recent_chats:
        recovered.append({
            'type': 'chat_sessions',
            'count': stats['recent_chat_sessions'],
            'location': 'recovery_recent_chats.json',
            'description': 'Recent chat conversations from Cursor sessions'
        })
    
    if composer_data:
        recovered.append({
            'type': 'composer_data',
            'count': stats['composer_items'],
            'location': 'recovery_composer_data.json',
            'description': 'Composer state and potential unsaved buffer data'
        })
    
    if reconstructed:
        recovered.append({
            'type': 'file_references',
            'count': stats['unique_files_referenced'],
            'location': 'recovery_reconstructed_context.json',
            'description': 'Files referenced in conversations'
        })
    
    if stats['git_stashes'] > 0:
        recovered.append({
            'type': 'git_stashes',
            'count': stats['git_stashes'],
            'location': 'recovery_stash_contents.txt',
            'description': 'Git stashes containing potentially lost work'
        })
    
    report['recovered_items'] = recovered
    
    # Irrecoverable items
    irrecoverable = [
        {
            'type': 'unsaved_buffers_never_written',
            'reason': 'Code typed but never saved to disk and not captured in chat history or composer state'
        },
        {
            'type': 'ram_only_state',
            'reason': 'In-memory state that was not persisted to disk before crash'
        },
        {
            'type': 'deleted_files_no_git_history',
            'reason': 'Files deleted and not tracked by git (if any)'
        },
        {
            'type': 'recent_edits_not_autosaved',
            'reason': 'Edits made in crashed session that were not auto-saved by Cursor'
        }
    ]
    
    report['irrecoverable_items'] = irrecoverable
    
    # Recommendations
    recommendations = [
        {
            'priority': 'HIGH',
            'action': 'Review recovered chat sessions',
            'description': f"Check recovery_recent_chats.json and recovery_recent_chats.md for {stats['recent_chat_sessions']} recent chat sessions"
        },
        {
            'priority': 'HIGH',
            'action': 'Review git stashes',
            'description': f"Check recovery_stash_contents.txt for {stats['git_stashes']} git stashes that may contain lost work"
        },
        {
            'priority': 'MEDIUM',
            'action': 'Check Cursor Timeline',
            'description': 'Manually check Cursor Timeline feature for each modified file to recover previous versions'
        },
        {
            'priority': 'MEDIUM',
            'action': 'Review composer data',
            'description': f"Check recovery_composer_data.json for {stats['composer_items']} composer items that may contain unsaved edits"
        },
        {
            'priority': 'LOW',
            'action': 'Check Time Machine (if enabled)',
            'description': 'If Time Machine is enabled, check for snapshots of project folder from before crash'
        },
        {
            'priority': 'HIGH',
            'action': 'Commit current work',
            'description': f"Commit {stats['git_modified_files']} modified files to prevent future data loss"
        }
    ]
    
    report['recommendations'] = recommendations
    
    # Generate summary
    total_recovered = sum(item['count'] for item in recovered)
    report['recovery_summary'] = {
        'total_items_recovered': total_recovered,
        'recovery_success_rate': 'HIGH' if total_recovered > 0 else 'LOW',
        'primary_recovery_channels': [ch['name'] for ch in channels if ch['likelihood'] == 'HIGH'],
        'next_steps': [rec['action'] for rec in recommendations if rec['priority'] == 'HIGH']
    }
    
    # Write JSON report
    output_json = os.path.join(workspace_path, "recovery_final_report.json")
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"JSON report written to: {output_json}")
    
    # Write markdown report
    output_md = os.path.join(workspace_path, "recovery_final_report.md")
    with open(output_md, 'w', encoding='utf-8') as f:
        f.write("# Recovery Final Report\n\n")
        f.write(f"**Generated:** {report['generated_at']}\n\n")
        
        # Summary
        f.write("## Executive Summary\n\n")
        f.write(f"- **Total Items Recovered:** {report['recovery_summary']['total_items_recovered']}\n")
        f.write(f"- **Recovery Success Rate:** {report['recovery_summary']['recovery_success_rate']}\n")
        f.write(f"- **Primary Channels:** {', '.join(report['recovery_summary']['primary_recovery_channels'])}\n\n")
        
        # Statistics
        f.write("## Recovery Statistics\n\n")
        f.write("| Metric | Count |\n")
        f.write("|--------|-------|\n")
        for key, value in stats.items():
            f.write(f"| {key.replace('_', ' ').title()} | {value} |\n")
        f.write("\n")
        
        # Channels
        f.write("## Recovery Channel Assessment\n\n")
        f.write("| Channel | Likelihood | Items Recovered | Notes |\n")
        f.write("|---------|------------|-----------------|-------|\n")
        for ch in channels:
            f.write(f"| {ch['name']} | {ch['likelihood']} | {ch['items_recovered']} | {ch['notes']} |\n")
        f.write("\n")
        
        # Recovered items
        f.write("## Recovered Items\n\n")
        for item in recovered:
            f.write(f"### {item['type'].replace('_', ' ').title()}\n\n")
            f.write(f"- **Count:** {item['count']}\n")
            f.write(f"- **Location:** `{item['location']}`\n")
            f.write(f"- **Description:** {item['description']}\n\n")
        
        # Irrecoverable items
        f.write("## Irrecoverable Items\n\n")
        for item in irrecoverable:
            f.write(f"- **{item['type'].replace('_', ' ').title()}:** {item['reason']}\n")
        f.write("\n")
        
        # Recommendations
        f.write("## Recommendations\n\n")
        for rec in recommendations:
            f.write(f"### {rec['priority']} Priority: {rec['action']}\n\n")
            f.write(f"{rec['description']}\n\n")
        
        # Next steps
        f.write("## Next Steps\n\n")
        f.write("1. Review recovered chat sessions and composer data\n")
        f.write("2. Check git stashes for lost work\n")
        f.write("3. Manually check Cursor Timeline for modified files\n")
        f.write("4. Commit current work to prevent future data loss\n")
        f.write("5. Consider implementing preventive measures (see recovery_automated.py)\n")
    
    print(f"Markdown report written to: {output_md}")
    
    return report

if __name__ == "__main__":
    report = generate_recovery_report()
    print(f"\nRecovery report generated successfully!")
    print(f"Total items recovered: {report['recovery_summary']['total_items_recovered']}")

