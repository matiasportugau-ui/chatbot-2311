#!/usr/bin/env python3
"""
RecoveryAgent: Parse composerData to extract full conversation context
"""
import json
import os
from datetime import datetime

def extract_all_conversations_from_composer(composer_data):
    """Extract all conversations from composer data structure"""
    conversations = []
    
    if isinstance(composer_data, dict):
        # Check for allComposers
        if 'allComposers' in composer_data:
            composers = composer_data['allComposers']
            
            if isinstance(composers, dict):
                # Dictionary of composers by ID
                for composer_id, composer in composers.items():
                    conv = extract_conversation_from_composer(composer, composer_id)
                    if conv:
                        conversations.append(conv)
            elif isinstance(composers, list):
                # List of composers
                for i, composer in enumerate(composers):
                    composer_id = composer.get('id', f'composer_{i}')
                    conv = extract_conversation_from_composer(composer, composer_id)
                    if conv:
                        conversations.append(conv)
    
    return conversations

def extract_conversation_from_composer(composer, composer_id):
    """Extract conversation from a single composer object"""
    if not isinstance(composer, dict):
        return None
    
    conv = {
        'composer_id': composer_id,
        'messages': [],
        'metadata': {}
    }
    
    # Look for messages in various possible locations
    if 'messages' in composer:
        conv['messages'] = composer['messages']
    elif 'conversation' in composer:
        if isinstance(composer['conversation'], list):
            conv['messages'] = composer['conversation']
        elif isinstance(composer['conversation'], dict) and 'messages' in composer['conversation']:
            conv['messages'] = composer['conversation']['messages']
    elif 'thread' in composer:
        if isinstance(composer['thread'], list):
            conv['messages'] = composer['thread']
        elif isinstance(composer['thread'], dict) and 'messages' in composer['thread']:
            conv['messages'] = composer['thread']['messages']
    
    # Extract metadata
    for key in ['title', 'created', 'updated', 'timestamp', 'lastMessage', 'filePath']:
        if key in composer:
            conv['metadata'][key] = composer[key]
    
    # If we found messages, return the conversation
    if conv['messages']:
        return conv
    
    # Otherwise, return the whole composer as raw data
    if composer:
        conv['raw_data'] = composer
        return conv
    
    return None

def format_message(msg):
    """Format a message for display"""
    if isinstance(msg, dict):
        role = msg.get('role', msg.get('type', 'unknown'))
        content = msg.get('content', msg.get('text', msg.get('message', '')))
        
        # Handle code blocks
        if isinstance(content, dict):
            if 'parts' in content:
                content = '\n'.join(str(part) for part in content['parts'])
            elif 'text' in content:
                content = content['text']
            else:
                content = str(content)
        
        return {
            'role': role,
            'content': str(content),
            'timestamp': msg.get('timestamp') or msg.get('time') or msg.get('created'),
            'raw': msg
        }
    else:
        return {
            'role': 'unknown',
            'content': str(msg),
            'timestamp': None,
            'raw': msg
        }

def main():
    """Main function"""
    project_path = "/Users/matias/chatbot2511/chatbot-2311"
    composer_file = os.path.join(project_path, "composer_data_full.json")
    output_file = os.path.join(project_path, "FULL_CONTEXT_RECOVERED.md")
    
    print("Loading composer data...")
    with open(composer_file, 'r', encoding='utf-8') as f:
        composer_data = json.load(f)
    
    value = composer_data.get('value', {})
    if isinstance(value, str):
        value = json.loads(value)
    
    print("Extracting conversations from composer data...")
    conversations = extract_all_conversations_from_composer(value)
    print(f"Found {len(conversations)} conversations")
    
    # Write comprehensive recovery document
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# 🔄 FULL CONTEXT RECOVERED - Complete Session Reconstruction\n\n")
        f.write(f"**Recovery Date:** {datetime.now().isoformat()}\n\n")
        f.write(f"**Total Conversations Found:** {len(conversations)}\n\n")
        f.write("---\n\n")
        
        # Write each conversation
        for i, conv in enumerate(conversations, 1):
            f.write(f"## 💬 Conversation {i}\n\n")
            f.write(f"**Composer ID:** `{conv['composer_id']}`\n\n")
            
            if conv.get('metadata'):
                f.write("**Metadata:**\n\n")
                for key, val in conv['metadata'].items():
                    f.write(f"- **{key}:** `{val}`\n\n")
            
            messages = conv.get('messages', [])
            if messages:
                f.write(f"**Message Count:** {len(messages)}\n\n")
                f.write("### Messages:\n\n")
                
                for j, msg in enumerate(messages, 1):
                    formatted = format_message(msg)
                    f.write(f"#### Message {j} - {formatted['role']}\n\n")
                    
                    if formatted['timestamp']:
                        f.write(f"**Timestamp:** {formatted['timestamp']}\n\n")
                    
                    f.write("**Content:**\n\n")
                    content = formatted['content']
                    if len(content) > 50000:
                        f.write("```\n")
                        f.write(content[:25000])
                        f.write("\n\n... (truncated, showing first 25k chars) ...\n\n")
                        f.write(content[-25000:])
                        f.write("\n```\n\n")
                    else:
                        f.write("```\n")
                        f.write(content)
                        f.write("\n```\n\n")
            else:
                f.write("**No messages found, showing raw data:**\n\n")
                f.write("```json\n")
                f.write(json.dumps(conv.get('raw_data', conv), indent=2, ensure_ascii=False, default=str))
                f.write("\n```\n\n")
            
            f.write("---\n\n")
        
        # Summary
        f.write("## 📊 Recovery Summary\n\n")
        f.write(f"- **Total Conversations:** {len(conversations)}\n\n")
        total_messages = sum(len(c.get('messages', [])) for c in conversations)
        f.write(f"- **Total Messages:** {total_messages}\n\n")
        
        # Count by role
        role_counts = {}
        for conv in conversations:
            for msg in conv.get('messages', []):
                formatted = format_message(msg)
                role = formatted['role']
                role_counts[role] = role_counts.get(role, 0) + 1
        
        if role_counts:
            f.write("**Messages by Role:**\n\n")
            for role, count in sorted(role_counts.items(), key=lambda x: x[1], reverse=True):
                f.write(f"- **{role}:** {count}\n\n")
    
    print(f"\n✅ Full context recovery complete!")
    print(f"   Written to: {output_file}")
    print(f"   - {len(conversations)} conversations extracted")
    total_messages = sum(len(c.get('messages', [])) for c in conversations)
    print(f"   - {total_messages} total messages")

if __name__ == "__main__":
    main()

