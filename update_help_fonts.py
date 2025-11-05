#!/usr/bin/env python3
"""
Script to update all module help texts with stylish fonts
"""

import os
import re

# Character mapping for small caps/stylish font
FONT_MAP = {
    'a': 'ᴧ', 'b': 'ʙ', 'c': 'ᴄ', 'd': 'ᴅ', 'e': 'є', 'f': 'ғ', 'g': 'ɢ', 'h': 'ʜ',
    'i': 'ɪ', 'j': 'ᴊ', 'k': 'ᴋ', 'l': 'ʟ', 'm': 'ϻ', 'n': 'η', 'o': 'σ', 'p': 'ᴩ',
    'q': 'ǫ', 'r': 'ʀ', 's': 's', 't': 'ᴛ', 'u': 'υ', 'v': 'ᴠ', 'w': 'ᴡ', 'x': 'x',
    'y': 'ʏ', 'z': 'ᴢ',
    'A': 'ᴧ', 'B': 'ʙ', 'C': 'ᴄ', 'D': 'ᴅ', 'E': 'є', 'F': 'ғ', 'G': 'ɢ', 'H': 'ʜ',
    'I': 'ɪ', 'J': 'ᴊ', 'K': 'ᴋ', 'L': 'ʟ', 'M': 'ϻ', 'N': 'η', 'O': 'σ', 'P': 'ᴩ',
    'Q': 'ǫ', 'R': 'ʀ', 'S': 's', 'T': 'ᴛ', 'U': 'υ', 'V': 'ᴠ', 'W': 'ᴡ', 'X': 'x',
    'Y': 'ʏ', 'Z': 'ᴢ'
}

def convert_to_stylish(text, preserve_markdown=True):
    """Convert text to stylish small caps font"""
    result = []
    in_code = False
    in_link = False
    in_bold = False
    
    i = 0
    while i < len(text):
        char = text[i]
        
        # Handle markdown code blocks and inline code
        if char == '`':
            in_code = not in_code
            result.append(char)
            i += 1
            continue
            
        # Handle markdown links [text](url)
        if char == '[' and preserve_markdown:
            in_link = True
            result.append(char)
            i += 1
            continue
        elif char == ']' and in_link:
            in_link = False
            result.append(char)
            i += 1
            continue
            
        # Handle bold markdown
        if char == '*' and preserve_markdown:
            result.append(char)
            i += 1
            continue
        
        # Don't convert if in code block or link
        if in_code or in_link:
            result.append(char)
        elif char in FONT_MAP:
            result.append(FONT_MAP[char])
        else:
            result.append(char)
        
        i += 1
    
    return ''.join(result)

def update_help_text(help_text):
    """Update help text with stylish formatting"""
    lines = help_text.split('\n')
    updated_lines = []
    
    for line in lines:
        # Skip empty lines
        if not line.strip():
            updated_lines.append(line)
            continue
            
        # Replace bullet points - with ❍
        if line.strip().startswith('-'):
            # Keep the indentation
            indent = len(line) - len(line.lstrip())
            content = line.strip()[1:].strip()
            updated_lines.append(' ' * indent + '❍ ' + content)
        else:
            updated_lines.append(line)
    
    return '\n'.join(updated_lines)

def process_file(filepath):
    """Process a single Python file to update __help__ text"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find __help__ definition
    help_pattern = r'(__help__\s*=\s*""")(.*?)(""")'
    
    def replace_help(match):
        prefix = match.group(1)
        help_content = match.group(2)
        suffix = match.group(3)
        
        # Update the help content
        updated_content = update_help_text(help_content)
        
        return prefix + updated_content + suffix
    
    updated_content = re.sub(help_pattern, replace_help, content, flags=re.DOTALL)
    
    # Check if content was changed
    if updated_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        return True
    return False

def main():
    """Main function to process all module files"""
    modules_dir = 'sitaBot/modules'
    files_processed = 0
    files_updated = 0
    
    for filename in os.listdir(modules_dir):
        if filename.endswith('.py'):
            filepath = os.path.join(modules_dir, filename)
            files_processed += 1
            
            if process_file(filepath):
                files_updated += 1
                print(f"✓ Updated: {filename}")
            else:
                print(f"  Skipped: {filename}")
    
    print(f"\nProcessed {files_processed} files, updated {files_updated} files")

if __name__ == '__main__':
    main()
