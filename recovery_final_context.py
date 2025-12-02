#!/usr/bin/env python3
"""
RecoveryAgent: Final context extraction - parse composerData and all conversations
"""
import json
import os
from datetime import datetime

def extract_composer_conversations(data):
    """Extract conversations from composerData"""
    conversations = []
    
    for item in data:
        key = str(item.get('key', ''))
        value = item.get('value', {})
        
        # Parse composerData
        if 'composerData' in key.lower() or 'composer' in key.lower():
            if isinstance(value, str):
                try:
                    value = json.loads(value)
                except:
                    continue
            
            if isinstance(value, dict):
                # Look for conversation structures
                if 'conversations' in value:
                    conversations.extend(value['conversations'])
                elif 'messages' in value:
                    conversations.append({'messages': value['messages']})
                elif 'threads' in value:
                    for thread in value['threads']:
                        if 'messages' in thread:
                            conversations.append(thread)
                # Sometimes the whole value is a conversation
                elif 'content' in value or 'text' in value:
                    conversations.append(value)
        
        # Also check for chat-related data
        if 'chat' in key.lower() and isinstance(value, (dict, str)):
            if isinstance(value, str):
                try:
                    value = json.loads(value)
                except:
                    pass
            
            if isinstance(value, dict):
                if 'messages' in value or 'conversations' in value:
                    conversations.append(value)
    
    return conversations

def format_conversation_for_markdown(conv, index):
    """Format a conversation for markdown output"""
    output = []
    output.append(f"### Conversation {index}\n\n")
    
    if isinstance(conv, dict):
        # Extract messages
        messages = conv.get('messages', [])
        if not messages and 'content' in conv:
            # Single message
            messages = [conv]
        
        if messages:
            output.append(f"**Message Count:** {len(messages)}\n\n")
            
            for i, msg in enumerate(messages, 1):
                role = msg.get('role', msg.get('type', 'unknown'))
                content = msg.get('content', msg.get('text', msg.get('message', str(msg))))
                
                output.append(f"#### Message {i} - {role}\n\n")
                
                # Try to extract timestamp
                timestamp = msg.get('timestamp') or msg.get('time') or msg.get('created')
                if timestamp:
                    output.append(f"**Timestamp:** {timestamp}\n\n")
                
                output.append("**Content:**\n\n")
                output.append("```\n")
                output.append(str(content))
                output.append("\n```\n\n")
        else:
            # Just dump the whole thing
            output.append("**Raw Data:**\n\n")
            output.append("```json\n")
            output.append(json.dumps(conv, indent=2, ensure_ascii=False))
            output.append("\n```\n\n")
    else:
        # Not a dict, just stringify
        output.append("**Content:**\n\n")
        output.append("```\n")
        output.append(str(conv))
        output.append("\n```\n\n")
    
    return "".join(output)

def main():
    """Main function"""
    project_path = "/Users/matias/chatbot2511/chatbot-2311"
    chat_file = os.path.join(project_path, "recovered_chats.json")
    output_file = os.path.join(project_path, "FULL_CONTEXT_RECOVERED.md")
    
    print("Loading recovered chat data...")
    with open(chat_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"Loaded {len(data)} items")
    print("Extracting composer conversations...")
    
    conversations = extract_composer_conversations(data)
    print(f"Found {len(conversations)} conversation structures")
    
    # Also extract all text content that looks like conversations
    all_text_content = []
    for item in data:
        key = str(item.get('key', ''))
        value = item.get('value', {})
        
        # Get text content
        text = None
        if isinstance(value, str) and len(value) > 200:
            text = value
        elif isinstance(value, dict):
            # Try to extract text
            for field in ['content', 'text', 'message', 'prompt', 'response']:
                if field in value and isinstance(value[field], str) and len(value[field]) > 200:
                    text = value[field]
                    break
        
        if text and any(term in text.lower() for term in ['user', 'assistant', 'message', 'prompt', 'code', 'file']):
            all_text_content.append({
                'key': key,
                'content': text,
                'length': len(text)
            })
    
    # Sort by length
    all_text_content.sort(key=lambda x: x['length'], reverse=True)
    print(f"Found {len(all_text_content)} text items with conversation-like content")
    
    # Write final context
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# 🔄 FULL CONTEXT RECOVERED - Complete Session Reconstruction\n\n")
        f.write(f"**Recovery Date:** {datetime.now().isoformat()}\n\n")
        f.write(f"**Total Items Analyzed:** {len(data)}\n\n")
        f.write(f"**Conversations Found:** {len(conversations)}\n\n")
        f.write(f"**Text Content Items:** {len(all_text_content)}\n\n")
        f.write("---\n\n")
        
        # Structured conversations
        if conversations:
            f.write("## 💬 Structured Conversations\n\n")
            for i, conv in enumerate(conversations[:50], 1):  # Top 50
                f.write(format_conversation_for_markdown(conv, i))
                f.write("---\n\n")
        
        # All text content (most relevant first)
        f.write("## 📝 All Recovered Text Content\n\n")
        f.write("These are all text items that appear to contain conversations, code, or context:\n\n")
        
        for i, text_item in enumerate(all_text_content[:200], 1):  # Top 200
            f.write(f"### Text Item {i}\n\n")
            f.write(f"**Key:** `{text_item['key']}`\n\n")
            f.write(f"**Length:** {text_item['length']:,} characters\n\n")
            f.write("**Content:**\n\n")
            
            content = text_item['content']
            # For very long content, show beginning and end
            if len(content) > 50000:
                f.write("```\n")
                f.write(content[:25000])
                f.write("\n\n... (middle section truncated) ...\n\n")
                f.write(content[-25000:])
                f.write("\n```\n\n")
            else:
                f.write("```\n")
                f.write(content)
                f.write("\n```\n\n")
            
            f.write("---\n\n")
        
        # Summary
        f.write("## 📊 Recovery Summary\n\n")
        f.write(f"- **Total Items Processed:** {len(data):,}\n\n")
        f.write(f"- **Structured Conversations:** {len(conversations)}\n\n")
        f.write(f"- **Text Content Items:** {len(all_text_content)}\n\n")
        f.write(f"- **Total Characters Recovered:** {sum(t['length'] for t in all_text_content):,}\n\n")
        f.write(f"- **Average Content Length:** {sum(t['length'] for t in all_text_content) // max(len(all_text_content), 1):,} characters\n\n")
    
    print(f"\n✅ Full context recovery complete!")
    print(f"   Written to: {output_file}")
    print(f"   - {len(conversations)} structured conversations")
    print(f"   - {len(all_text_content)} text content items")
    print(f"   - {sum(t['length'] for t in all_text_content):,} total characters")

if __name__ == "__main__":
    main()

