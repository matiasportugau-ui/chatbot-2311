#!/usr/bin/env python3
"""
RecoveryAgent: Deep analysis of recovered data to extract all context
"""
import json
import os
import re
from datetime import datetime
from collections import defaultdict

def analyze_item_structure(data, max_samples=100):
    """Analyze the structure of recovered items"""
    structures = defaultdict(int)
    chat_keys = []
    composer_keys = []
    
    for item in data[:max_samples]:
        key = str(item.get('key', ''))
        value = item.get('value', {})
        
        # Categorize by key patterns
        if 'chat' in key.lower():
            chat_keys.append(key)
        if 'composer' in key.lower():
            composer_keys.append(key)
        
        # Categorize by value structure
        if isinstance(value, dict):
            keys_str = ','.join(sorted(value.keys())[:5])
            structures[f"dict_with_{keys_str}"] += 1
        elif isinstance(value, str):
            if len(value) > 1000:
                structures["long_string"] += 1
            else:
                structures["short_string"] += 1
        elif isinstance(value, list):
            structures[f"list_len_{len(value)}"] += 1
        else:
            structures[str(type(value).__name__)] += 1
    
    return structures, chat_keys[:10], composer_keys[:10]

def extract_all_text_content(data):
    """Extract all text content that might be conversations"""
    all_text = []
    
    for item in data:
        key = str(item.get('key', ''))
        value = item.get('value', {})
        
        # Skip if not chat-related
        if not any(term in key.lower() for term in ['chat', 'composer', 'prompt', 'message', 'conversation']):
            continue
        
        text_content = None
        
        if isinstance(value, dict):
            # Try to extract text from various fields
            for field in ['content', 'text', 'message', 'prompt', 'response', 'input', 'output']:
                if field in value:
                    text_content = str(value[field])
                    break
            
            # If no direct text field, try to serialize the whole thing
            if not text_content:
                try:
                    text_content = json.dumps(value, indent=2)
                except:
                    pass
        
        elif isinstance(value, str):
            text_content = value
        
        if text_content and len(text_content) > 50:  # Only meaningful content
            all_text.append({
                'key': key,
                'content': text_content,
                'length': len(text_content),
                'source': item.get('source', 'unknown')
            })
    
    # Sort by length (longer = more likely to be full conversations)
    all_text.sort(key=lambda x: x['length'], reverse=True)
    return all_text

def extract_file_edits(data):
    """Extract file edit operations"""
    file_edits = []
    
    for item in data:
        key = str(item.get('key', ''))
        value = item.get('value', {})
        
        # Look for file-related data
        if isinstance(value, dict):
            file_path = None
            for field in ['filePath', 'path', 'file', 'uri', 'resource']:
                if field in value:
                    file_path = str(value[field])
                    break
            
            if file_path:
                # Extract code/content
                code = None
                for field in ['code', 'content', 'text', 'value', 'data']:
                    if field in value:
                        code = str(value[field])
                        break
                
                if code or file_path:
                    file_edits.append({
                        'file': file_path,
                        'code': code or '',
                        'key': key,
                        'source': item.get('source', 'unknown'),
                        'full_value': value
                    })
        
        # Also check if key contains file paths
        if '/' in key and any(ext in key for ext in ['.py', '.ts', '.tsx', '.js', '.jsx', '.json', '.md']):
            if isinstance(value, str) and len(value) > 100:
                file_edits.append({
                    'file': key,
                    'code': value,
                    'key': key,
                    'source': item.get('source', 'unknown'),
                    'full_value': None
                })
    
    return file_edits

def main():
    """Main deep analysis function"""
    project_path = "/Users/matias/chatbot2511/chatbot-2311"
    chat_file = os.path.join(project_path, "recovered_chats.json")
    output_file = os.path.join(project_path, "FULL_CONTEXT_RECOVERED.md")
    
    print("Loading recovered chat data...")
    with open(chat_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"Loaded {len(data)} items")
    
    # Analyze structure
    print("Analyzing data structure...")
    structures, chat_keys, composer_keys = analyze_item_structure(data, max_samples=1000)
    
    print("\nData structure analysis:")
    for struct, count in sorted(structures.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {struct}: {count}")
    
    print(f"\nChat-related keys found: {len(chat_keys)}")
    print(f"Composer-related keys found: {len(composer_keys)}")
    
    # Extract all text content
    print("\nExtracting all text content...")
    all_text = extract_all_text_content(data)
    print(f"Found {len(all_text)} text items")
    
    # Extract file edits
    print("Extracting file edits...")
    file_edits = extract_file_edits(data)
    print(f"Found {len(file_edits)} file edit operations")
    
    # Write comprehensive recovery
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# 🔄 Full Context Recovery - Complete Session Reconstruction\n\n")
        f.write(f"**Recovery Date:** {datetime.now().isoformat()}\n\n")
        f.write(f"**Total Items Analyzed:** {len(data)}\n\n")
        f.write(f"**Text Content Items:** {len(all_text)}\n\n")
        f.write(f"**File Edit Operations:** {len(file_edits)}\n\n")
        f.write("---\n\n")
        
        # Data structure analysis
        f.write("## 📊 Data Structure Analysis\n\n")
        f.write("### Most Common Structures:\n\n")
        for struct, count in sorted(structures.items(), key=lambda x: x[1], reverse=True)[:20]:
            f.write(f"- `{struct}`: {count} items\n\n")
        
        f.write("### Chat-Related Keys (Sample):\n\n")
        for key in chat_keys[:20]:
            f.write(f"- `{key}`\n\n")
        
        f.write("### Composer-Related Keys (Sample):\n\n")
        for key in composer_keys[:20]:
            f.write(f"- `{key}`\n\n")
        
        f.write("---\n\n")
        
        # All text content (top 100 by length)
        f.write("## 💬 All Recovered Text Content (Top 100 by Length)\n\n")
        f.write("These are the longest text items found, likely containing full conversations:\n\n")
        
        for i, text_item in enumerate(all_text[:100], 1):
            f.write(f"### Text Item {i}\n\n")
            f.write(f"**Key:** `{text_item['key']}`\n\n")
            f.write(f"**Length:** {text_item['length']} characters\n\n")
            f.write(f"**Source:** `{text_item['source']}`\n\n")
            f.write("**Content:**\n\n")
            
            content = text_item['content']
            # Truncate very long content
            if len(content) > 20000:
                f.write("```\n")
                f.write(content[:10000])
                f.write("\n\n... (first 10,000 chars, truncated)\n\n")
                f.write(content[-10000:])
                f.write("\n```\n\n")
            else:
                f.write("```\n")
                f.write(content)
                f.write("\n```\n\n")
            
            f.write("---\n\n")
        
        # File edits
        f.write("## 📝 File Edit Operations\n\n")
        f.write(f"Found {len(file_edits)} file-related operations:\n\n")
        
        # Group by file
        files_dict = defaultdict(list)
        for edit in file_edits:
            files_dict[edit['file']].append(edit)
        
        for file_path, edits in list(files_dict.items())[:50]:  # Top 50 files
            f.write(f"### File: `{file_path}`\n\n")
            f.write(f"**Operations:** {len(edits)}\n\n")
            
            for j, edit in enumerate(edits[:5], 1):  # First 5 edits per file
                f.write(f"#### Edit {j}\n\n")
                f.write(f"**Key:** `{edit['key']}`\n\n")
                f.write(f"**Source:** `{edit['source']}`\n\n")
                if edit['code']:
                    code_preview = edit['code'][:5000] if len(edit['code']) > 5000 else edit['code']
                    f.write("**Code:**\n\n")
                    f.write("```\n")
                    f.write(code_preview)
                    if len(edit['code']) > 5000:
                        f.write("\n\n... (truncated)")
                    f.write("\n```\n\n")
                f.write("---\n\n")
        
        # Summary
        f.write("## 📋 Recovery Summary\n\n")
        f.write(f"- **Total Items:** {len(data)}\n\n")
        f.write(f"- **Text Content Items:** {len(all_text)}\n\n")
        f.write(f"- **File Edit Operations:** {len(file_edits)}\n\n")
        f.write(f"- **Unique Files Edited:** {len(files_dict)}\n\n")
        f.write(f"- **Total Characters Recovered:** {sum(t['length'] for t in all_text):,}\n\n")
    
    print(f"\n✅ Full context recovery complete!")
    print(f"   Written to: {output_file}")
    print(f"   - {len(all_text)} text items extracted")
    print(f"   - {len(file_edits)} file edits found")
    print(f"   - {len(files_dict)} unique files identified")

if __name__ == "__main__":
    main()

