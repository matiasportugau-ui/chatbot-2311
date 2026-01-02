#!/usr/bin/env python3
"""
Reconstruct Conversation Context
Parses extracted chat data to reconstruct full conversation threads,
identify code changes discussed, and map to project files
"""
import json
import os
import re
from datetime import datetime
from pathlib import Path
from collections import defaultdict

def extract_file_references(text):
    """Extract file paths from text"""
    # Common file patterns
    patterns = [
        r'[\/\w\-\.]+\.(py|js|ts|tsx|jsx|json|md|txt|yml|yaml|html|css|scss)',
        r'[\/\w\-\.]+/(\w+\.\w+)',
        r'`([\/\w\-\.]+\.\w+)`',
        r'"([\/\w\-\.]+\.\w+)"',
        r"'([\/\w\-\.]+\.\w+)'"
    ]
    
    files = set()
    for pattern in patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            if isinstance(match, tuple):
                match = match[0] if match[0] else match[1]
            if match and not match.startswith('http'):
                files.add(match)
    
    return list(files)

def extract_code_blocks(text):
    """Extract code blocks from text"""
    code_blocks = []
    
    # Markdown code blocks
    pattern = r'```(?:\w+)?\n(.*?)```'
    matches = re.findall(pattern, text, re.DOTALL)
    for match in matches:
        if len(match.strip()) > 10:
            code_blocks.append(match.strip())
    
    # Inline code
    pattern = r'`([^`]+)`'
    matches = re.findall(pattern, text)
    for match in matches:
        if len(match) > 20 and any(char in match for char in ['{', '(', 'def ', 'function']):
            code_blocks.append(match)
    
    return code_blocks

def parse_session_data(session_data):
    """Parse session data to extract conversation structure"""
    conversations = []
    
    def traverse(data, path="", depth=0):
        if depth > 10:  # Prevent infinite recursion
            return
        
        if isinstance(data, dict):
            # Look for message-like structures
            if 'message' in data or 'content' in data or 'text' in data:
                msg = {
                    'path': path,
                    'content': data.get('message') or data.get('content') or data.get('text', ''),
                    'timestamp': data.get('timestamp') or data.get('date') or data.get('time'),
                    'role': data.get('role') or data.get('type') or 'unknown',
                    'metadata': {k: v for k, v in data.items() if k not in ['message', 'content', 'text', 'timestamp', 'date', 'time', 'role', 'type']}
                }
                if msg['content']:
                    conversations.append(msg)
            
            # Look for array of messages
            if 'messages' in data or 'history' in data or 'conversation' in data:
                messages = data.get('messages') or data.get('history') or data.get('conversation', [])
                for i, msg in enumerate(messages):
                    traverse(msg, f"{path}.messages[{i}]", depth + 1)
            
            # Recursively traverse
            for key, value in data.items():
                traverse(value, f"{path}.{key}", depth + 1)
        
        elif isinstance(data, list):
            for i, item in enumerate(data):
                traverse(item, f"{path}[{i}]", depth + 1)
        
        elif isinstance(data, str) and len(data) > 50:
            # Might be a serialized conversation
            if '{' in data or '[' in data:
                try:
                    parsed = json.loads(data)
                    traverse(parsed, path, depth + 1)
                except:
                    pass
    
    traverse(session_data)
    return conversations

def reconstruct_timeline(sessions):
    """Reconstruct conversation timeline from sessions"""
    timeline = []
    
    for session in sessions:
        session_id = session.get('key', 'unknown')
        data = session.get('data', {})
        
        # Extract timestamp
        timestamp = None
        if isinstance(data, dict):
            timestamp = data.get('lastMessageDate') or data.get('timestamp') or data.get('date')
        
        # Parse conversations
        conversations = parse_session_data(data)
        
        # Extract file references and code
        data_str = json.dumps(data, default=str)
        file_refs = extract_file_references(data_str)
        code_blocks = extract_code_blocks(data_str)
        
        timeline.append({
            'session_id': session_id,
            'timestamp': timestamp,
            'source_db': os.path.basename(session.get('source_db', '')),
            'conversations': conversations,
            'file_references': file_refs,
            'code_blocks': code_blocks,
            'extracted_at': session.get('extracted_at')
        })
    
    # Sort by timestamp if available
    timeline.sort(key=lambda x: x['timestamp'] if x['timestamp'] else 0, reverse=True)
    
    return timeline

def generate_summary(timeline):
    """Generate summary of recovered context"""
    summary = {
        'total_sessions': len(timeline),
        'total_conversations': sum(len(t['conversations']) for t in timeline),
        'total_code_blocks': sum(len(t['code_blocks']) for t in timeline),
        'unique_files': set(),
        'sessions_by_date': defaultdict(list)
    }
    
    for item in timeline:
        summary['unique_files'].update(item['file_references'])
        
        if item['timestamp']:
            try:
                if isinstance(item['timestamp'], (int, float)):
                    if item['timestamp'] > 1e12:
                        dt = datetime.fromtimestamp(item['timestamp'] / 1000)
                    else:
                        dt = datetime.fromtimestamp(item['timestamp'])
                else:
                    dt = datetime.fromisoformat(str(item['timestamp']))
                date_key = dt.strftime('%Y-%m-%d')
                summary['sessions_by_date'][date_key].append(item)
            except:
                pass
    
    summary['unique_files'] = list(summary['unique_files'])
    summary['total_unique_files'] = len(summary['unique_files'])
    
    return summary

def format_timeline_markdown(timeline, summary):
    """Format timeline as markdown"""
    md = "# Reconstructed Conversation Context\n\n"
    md += f"**Generated:** {datetime.now().isoformat()}\n\n"
    
    # Summary
    md += "## Summary\n\n"
    md += f"- **Total Sessions:** {summary['total_sessions']}\n"
    md += f"- **Total Conversations:** {summary['total_conversations']}\n"
    md += f"- **Total Code Blocks:** {summary['total_code_blocks']}\n"
    md += f"- **Unique Files Referenced:** {summary['total_unique_files']}\n\n"
    
    # Files referenced
    if summary['unique_files']:
        md += "### Files Referenced in Conversations\n\n"
        for file_ref in sorted(summary['unique_files'])[:50]:  # Limit to 50
            md += f"- `{file_ref}`\n"
        if len(summary['unique_files']) > 50:
            md += f"\n*... and {len(summary['unique_files']) - 50} more files*\n"
        md += "\n"
    
    # Timeline
    md += "## Conversation Timeline\n\n"
    
    for i, item in enumerate(timeline):
        md += f"### Session {i + 1}\n\n"
        md += f"**Session ID:** `{item['session_id']}`\n\n"
        md += f"**Source:** `{item['source_db']}`\n\n"
        
        if item['timestamp']:
            md += f"**Timestamp:** {item['timestamp']}\n\n"
        
        if item['file_references']:
            md += "**Files Referenced:**\n\n"
            for file_ref in item['file_references'][:10]:
                md += f"- `{file_ref}`\n"
            if len(item['file_references']) > 10:
                md += f"\n*... and {len(item['file_references']) - 10} more*\n"
            md += "\n"
        
        if item['conversations']:
            md += f"**Conversations ({len(item['conversations'])}):**\n\n"
            for j, conv in enumerate(item['conversations'][:5]):  # Limit to 5
                md += f"#### Conversation {j + 1}\n\n"
                md += f"**Role:** {conv.get('role', 'unknown')}\n\n"
                if conv.get('timestamp'):
                    md += f"**Time:** {conv['timestamp']}\n\n"
                md += "**Content:**\n\n"
                content = conv.get('content', '')
                if len(content) > 500:
                    md += content[:500] + "\n\n*... (truncated)*\n\n"
                else:
                    md += content + "\n\n"
            if len(item['conversations']) > 5:
                md += f"\n*... and {len(item['conversations']) - 5} more conversations*\n\n"
        
        if item['code_blocks']:
            md += f"**Code Blocks ({len(item['code_blocks'])}):**\n\n"
            for j, code in enumerate(item['code_blocks'][:3]):  # Limit to 3
                md += f"#### Code Block {j + 1}\n\n"
                md += "```\n"
                md += code[:500]
                if len(code) > 500:
                    md += "\n... (truncated)"
                md += "\n```\n\n"
            if len(item['code_blocks']) > 3:
                md += f"\n*... and {len(item['code_blocks']) - 3} more code blocks*\n\n"
        
        md += "---\n\n"
    
    return md

def main():
    """Main reconstruction function"""
    workspace_path = "/Users/matias/chatbot2511/chatbot-2311"
    
    # Load recent chats
    recent_chats_file = os.path.join(workspace_path, "recovery_recent_chats.json")
    if not os.path.exists(recent_chats_file):
        print(f"Error: {recent_chats_file} not found. Run recovery_extract_recent_chats.py first.")
        return
    
    with open(recent_chats_file, 'r', encoding='utf-8') as f:
        recent_data = json.load(f)
    
    sessions = recent_data.get('sessions', [])
    print(f"Loaded {len(sessions)} sessions")
    
    # Reconstruct timeline
    print("Reconstructing conversation timeline...")
    timeline = reconstruct_timeline(sessions)
    
    # Generate summary
    print("Generating summary...")
    summary = generate_summary(timeline)
    
    print(f"Summary: {summary['total_sessions']} sessions, {summary['total_conversations']} conversations, {summary['total_unique_files']} unique files")
    
    # Write markdown output
    output_md = os.path.join(workspace_path, "recovery_reconstructed_context.md")
    md_content = format_timeline_markdown(timeline, summary)
    with open(output_md, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    print(f"Markdown output written to: {output_md}")
    
    # Write JSON output
    output_json = os.path.join(workspace_path, "recovery_reconstructed_context.json")
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump({
            'generated_at': datetime.now().isoformat(),
            'summary': summary,
            'timeline': timeline
        }, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"JSON output written to: {output_json}")
    
    return len(timeline)

if __name__ == "__main__":
    main()

