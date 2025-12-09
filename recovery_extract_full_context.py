#!/usr/bin/env python3
"""
RecoveryAgent: Extract and reconstruct full context from recovered chat data
"""
import json
import os
import re
from datetime import datetime
from collections import defaultdict

def parse_timestamp(value):
    """Try to extract timestamp from various formats"""
    if isinstance(value, dict):
        # Look for common timestamp fields
        for field in ['timestamp', 'time', 'date', 'created', 'updated', 'timestamp_ms', 'timestamp_us']:
            if field in value:
                ts = value[field]
                if isinstance(ts, (int, float)):
                    try:
                        return datetime.fromtimestamp(ts / 1000 if ts > 1e10 else ts)
                    except:
                        pass
                elif isinstance(ts, str):
                    try:
                        # Try ISO format
                        return datetime.fromisoformat(ts.replace('Z', '+00:00'))
                    except:
                        pass
    
    if isinstance(value, str):
        # Look for ISO timestamps in strings
        iso_pattern = r'\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}'
        match = re.search(iso_pattern, value)
        if match:
            try:
                return datetime.fromisoformat(match.group().replace(' ', 'T'))
            except:
                pass
    
    return None

def extract_conversations(data):
    """Extract actual conversation threads from recovered data"""
    conversations = []
    messages_by_thread = defaultdict(list)
    
    for item in data:
        key = str(item.get('key', ''))
        value = item.get('value', {})
        
        # Look for conversation-like structures
        if isinstance(value, dict):
            # Check for message arrays
            if 'messages' in value:
                messages = value['messages']
                if isinstance(messages, list):
                    thread_id = value.get('threadId') or value.get('sessionId') or 'unknown'
                    for msg in messages:
                        if isinstance(msg, dict):
                            messages_by_thread[thread_id].append({
                                'role': msg.get('role', msg.get('type', 'unknown')),
                                'content': msg.get('content', msg.get('text', msg.get('message', ''))),
                                'timestamp': parse_timestamp(msg),
                                'source': key
                            })
            
            # Check for single message structures
            if 'content' in value or 'text' in value or 'message' in value:
                role = value.get('role', value.get('type', 'assistant'))
                content = value.get('content') or value.get('text') or value.get('message', '')
                thread_id = value.get('threadId') or value.get('sessionId') or key
                
                messages_by_thread[thread_id].append({
                    'role': role,
                    'content': str(content),
                    'timestamp': parse_timestamp(value),
                    'source': key
                })
        
        # Check if the key itself suggests a conversation
        if 'chat' in key.lower() or 'composer' in key.lower() or 'conversation' in key.lower():
            if isinstance(value, str) and len(value) > 50:
                # Might be a serialized conversation
                try:
                    parsed = json.loads(value)
                    if isinstance(parsed, dict) and ('messages' in parsed or 'content' in parsed):
                        thread_id = parsed.get('threadId') or parsed.get('sessionId') or key
                        if 'messages' in parsed:
                            for msg in parsed['messages']:
                                messages_by_thread[thread_id].append({
                                    'role': msg.get('role', 'unknown'),
                                    'content': msg.get('content', ''),
                                    'timestamp': parse_timestamp(msg),
                                    'source': key
                                })
                except:
                    # Not JSON, might be plain text conversation
                    if 'user' in value.lower() or 'assistant' in value.lower():
                        messages_by_thread[key].append({
                            'role': 'mixed',
                            'content': value,
                            'timestamp': None,
                            'source': key
                        })
    
    # Convert to conversation list
    for thread_id, messages in messages_by_thread.items():
        if messages:
            # Sort by timestamp if available
            messages.sort(key=lambda x: x['timestamp'] or datetime.min)
            conversations.append({
                'thread_id': thread_id,
                'message_count': len(messages),
                'messages': messages,
                'first_timestamp': min((m['timestamp'] for m in messages if m['timestamp']), default=None),
                'last_timestamp': max((m['timestamp'] for m in messages if m['timestamp']), default=None)
            })
    
    return conversations

def extract_code_blocks(data):
    """Extract code blocks and file edits from recovered data"""
    code_blocks = []
    
    for item in data:
        key = str(item.get('key', ''))
        value = item.get('value', {})
        
        # Look for code-related data
        if isinstance(value, dict):
            # Check for file paths and code
            file_path = value.get('filePath') or value.get('path') or value.get('file')
            code_content = value.get('code') or value.get('content') or value.get('text')
            
            if file_path and code_content:
                code_blocks.append({
                    'file': file_path,
                    'code': str(code_content),
                    'source': key,
                    'timestamp': parse_timestamp(value),
                    'type': value.get('type', 'code')
                })
        
        # Check for code in strings
        if isinstance(value, str):
            # Look for file paths and code blocks
            if '```' in value or '.py' in value or '.ts' in value or '.tsx' in value:
                code_blocks.append({
                    'file': 'unknown',
                    'code': value,
                    'source': key,
                    'timestamp': None,
                    'type': 'text_with_code'
                })
    
    return code_blocks

def filter_by_time_window(conversations, code_blocks, start_time, end_time):
    """Filter items within the crash time window"""
    filtered_convos = []
    filtered_code = []
    
    for conv in conversations:
        if conv['first_timestamp'] and start_time <= conv['first_timestamp'] <= end_time:
            filtered_convos.append(conv)
        elif conv['last_timestamp'] and start_time <= conv['last_timestamp'] <= end_time:
            filtered_convos.append(conv)
        # Also include if any message is in the window
        elif any(start_time <= msg['timestamp'] <= end_time for msg in conv['messages'] if msg['timestamp']):
            filtered_convos.append(conv)
    
    for code in code_blocks:
        if code['timestamp'] and start_time <= code['timestamp'] <= end_time:
            filtered_code.append(code)
    
    return filtered_convos, filtered_code

def main():
    """Main recovery function"""
    project_path = "/Users/matias/chatbot2511/chatbot-2311"
    chat_file = os.path.join(project_path, "recovered_chats.json")
    output_file = os.path.join(project_path, "FULL_CONTEXT_RECOVERED.md")
    
    print("Loading recovered chat data...")
    with open(chat_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"Loaded {len(data)} items")
    print("Extracting conversations...")
    conversations = extract_conversations(data)
    print(f"Found {len(conversations)} conversation threads")
    
    print("Extracting code blocks...")
    code_blocks = extract_code_blocks(data)
    print(f"Found {len(code_blocks)} code blocks")
    
    # Filter by time window (last 7 hours until now)
    from datetime import timedelta
    crash_end = datetime.now()
    crash_start = crash_end - timedelta(hours=7)
    
    print(f"Filtering for time window: {crash_start} to {crash_end}")
    window_convos, window_code = filter_by_time_window(conversations, code_blocks, crash_start, crash_end)
    print(f"Found {len(window_convos)} conversations in crash window")
    print(f"Found {len(window_code)} code blocks in crash window")
    
    # Sort conversations by timestamp
    conversations.sort(key=lambda x: x['last_timestamp'] or datetime.min, reverse=True)
    window_convos.sort(key=lambda x: x['last_timestamp'] or datetime.min, reverse=True)
    
    # Write full context recovery
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# 🔄 Full Context Recovery - Complete Session Reconstruction\n\n")
        f.write(f"**Recovery Date:** {datetime.now().isoformat()}\n\n")
        f.write(f"**Crash Time Window:** Last 7 hours (from {crash_start.isoformat()} to {crash_end.isoformat()})\n\n")
        f.write(f"**Total Conversations Found:** {len(conversations)}\n\n")
        f.write(f"**Conversations in Crash Window:** {len(window_convos)}\n\n")
        f.write(f"**Total Code Blocks Found:** {len(code_blocks)}\n\n")
        f.write(f"**Code Blocks in Crash Window:** {len(window_code)}\n\n")
        f.write("---\n\n")
        
        # Recent conversations (last 20)
        f.write("## 📝 Recent Conversations (Most Recent First)\n\n")
        for i, conv in enumerate(conversations[:20], 1):
            f.write(f"### Conversation {i}\n\n")
            f.write(f"**Thread ID:** `{conv['thread_id']}`\n\n")
            f.write(f"**Messages:** {conv['message_count']}\n\n")
            if conv['first_timestamp']:
                f.write(f"**First Message:** {conv['first_timestamp'].isoformat()}\n\n")
            if conv['last_timestamp']:
                f.write(f"**Last Message:** {conv['last_timestamp'].isoformat()}\n\n")
            f.write("**Messages:**\n\n")
            
            for j, msg in enumerate(conv['messages'], 1):
                f.write(f"#### Message {j} ({msg['role']})\n\n")
                if msg['timestamp']:
                    f.write(f"**Time:** {msg['timestamp'].isoformat()}\n\n")
                f.write("**Content:**\n\n")
                content = str(msg['content'])
                if len(content) > 5000:
                    content = content[:5000] + "\n\n... (truncated)"
                f.write("```\n")
                f.write(content)
                f.write("\n```\n\n")
            
            f.write("---\n\n")
        
        # Crash window conversations
        if window_convos:
            f.write(f"## ⚠️ Conversations During Crash Window (Last 7 Hours)\n\n")
            for i, conv in enumerate(window_convos, 1):
                f.write(f"### Crash Window Conversation {i}\n\n")
                f.write(f"**Thread ID:** `{conv['thread_id']}`\n\n")
                f.write(f"**Messages:** {conv['message_count']}\n\n")
                if conv['last_timestamp']:
                    f.write(f"**Last Message:** {conv['last_timestamp'].isoformat()}\n\n")
                f.write("**Messages:**\n\n")
                
                for j, msg in enumerate(conv['messages'], 1):
                    f.write(f"#### Message {j} ({msg['role']})\n\n")
                    if msg['timestamp']:
                        f.write(f"**Time:** {msg['timestamp'].isoformat()}\n\n")
                    f.write("**Content:**\n\n")
                    content = str(msg['content'])
                    if len(content) > 10000:
                        content = content[:10000] + "\n\n... (truncated)"
                    f.write("```\n")
                    f.write(content)
                    f.write("\n```\n\n")
                
                f.write("---\n\n")
        
        # Code blocks
        if code_blocks:
            f.write("## 💻 Code Blocks and File Edits\n\n")
            for i, code in enumerate(code_blocks[:50], 1):  # Limit to first 50
                f.write(f"### Code Block {i}\n\n")
                f.write(f"**File:** `{code['file']}`\n\n")
                f.write(f"**Type:** {code['type']}\n\n")
                if code['timestamp']:
                    f.write(f"**Timestamp:** {code['timestamp'].isoformat()}\n\n")
                f.write(f"**Source:** `{code['source']}`\n\n")
                f.write("**Code:**\n\n")
                code_content = str(code['code'])
                if len(code_content) > 5000:
                    code_content = code_content[:5000] + "\n\n... (truncated)"
                f.write("```\n")
                f.write(code_content)
                f.write("\n```\n\n")
                f.write("---\n\n")
        
        # Summary statistics
        f.write("## 📊 Recovery Statistics\n\n")
        f.write(f"- **Total Items Processed:** {len(data)}\n\n")
        f.write(f"- **Conversation Threads:** {len(conversations)}\n\n")
        f.write(f"- **Total Messages:** {sum(len(c['messages']) for c in conversations)}\n\n")
        f.write(f"- **Code Blocks:** {len(code_blocks)}\n\n")
        f.write(f"- **Crash Window Conversations:** {len(window_convos)}\n\n")
        f.write(f"- **Crash Window Code Blocks:** {len(window_code)}\n\n")
    
    print(f"\n✅ Full context recovery complete!")
    print(f"   Written to: {output_file}")
    print(f"   - {len(conversations)} conversations extracted")
    print(f"   - {len(window_convos)} conversations in crash window")
    print(f"   - {len(code_blocks)} code blocks found")
    
    # Also create a JSON summary
    json_file = os.path.join(project_path, "full_context_summary.json")
    summary = {
        'recovery_date': datetime.now().isoformat(),
        'total_conversations': len(conversations),
        'crash_window_conversations': len(window_convos),
        'total_code_blocks': len(code_blocks),
        'crash_window_code_blocks': len(window_code),
        'recent_conversations': [
            {
                'thread_id': c['thread_id'],
                'message_count': c['message_count'],
                'first_timestamp': c['first_timestamp'].isoformat() if c['first_timestamp'] else None,
                'last_timestamp': c['last_timestamp'].isoformat() if c['last_timestamp'] else None
            }
            for c in conversations[:20]
        ]
    }
    
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print(f"   Summary JSON: {json_file}")

if __name__ == "__main__":
    main()

