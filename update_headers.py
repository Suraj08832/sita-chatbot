#!/usr/bin/env python3
"""
Script to add stylish headers to all module help texts
"""

import os
import re

# Module name to stylish header mapping
def get_stylish_header(mod_name):
    """Convert module name to stylish header"""
    mod_name_lower = mod_name.lower()
    
    headers = {
        "admin": "ᴧᴅϻɪη ᴄσϻϻᴧηᴅs",
        "ban/mute": "ʙᴧη & ϻυᴛє",
        "warns": "ᴡᴧʀηɪηɢs",
        "locks": "ʟσᴄᴋs",
        "approvals": "ᴧᴩᴩʀσᴠᴧʟ ϻσᴅє",
        "backup": "ʙᴧᴄᴋυᴩ",
        "blacklist": "ʙʟᴧᴄᴋʟɪsᴛ",
        "stickers b list": "sᴛɪᴄᴋєʀ ʙʟᴧᴄᴋʟɪsᴛ",
        "bluetext cleaning": "ʙʟυєᴛєxᴛ ᴄʟєᴧηɪηɢ",
        "control": "ᴧηᴛɪғʟσσᴅ ᴄσηᴛʀσʟ",
        "greetings": "ɢʀєєᴛɪηɢs & ᴡєʟᴄσϻє",
        "rules": "ʀυʟєs",
        "reports": "ʀєᴩσʀᴛs",
        "notes": "ησᴛєs",
        "filters": "ғɪʟᴛєʀs",
        "connections": "ᴄσηηєᴄᴛɪσηs",
        "federations": "ғєᴅєʀᴧᴛɪσηs",
        "economy": "єᴄσησϻʏ sʏsᴛєϻ",
        "couples": "ᴄσυᴩʟєs & sʜɪᴩᴩɪηɢ",
        "anime": "ᴧηɪϻє",
        "extras": "єxᴛʀᴧs",
        "quotly": "ǫυσᴛʟʏ",
        "logo": "ʟσɢσ ϻᴧᴋєʀ",
        "infos": "υsєʀ ɪηғσ",
        "users": "υsєʀs",
        "sed/regex": "sєᴅ/ʀєɢєx",
        "math": "ϻᴧᴛʜ",
        "nsfw": "ηsғᴡ",
        "forcesubs": "ғσʀᴄє sυʙsᴄʀɪʙє",
        "shield": "ɢsʜɪєʟᴅ",
        "nightmode": "ηɪɢʜᴛ ϻσᴅє",
        "dbcleanup": "ᴅᴧᴛᴧʙᴧsє ᴄʟєᴧηυᴩ",
        "modules": "ϻσᴅυʟєs",
        "shell": "sʜєʟʟ"
    }
    
    return headers.get(mod_name_lower, mod_name.upper())

def process_help_text(filepath):
    """Add stylish header to __help__ text"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find __mod_name__
    mod_name_match = re.search(r'__mod_name__\s*=\s*"([^"]+)"', content)
    if not mod_name_match:
        return False
    
    mod_name = mod_name_match.group(1)
    stylish_header = get_stylish_header(mod_name)
    
    # Find __help__ and update it
    help_pattern = r'(__help__\s*=\s*""")\n'
    
    def add_header(match):
        prefix = match.group(1)
        return f'{prefix}```\n❖ {stylish_header} ❖```\n\n'
    
    # Check if header already exists
    if '❖' in content and '__help__' in content:
        return False
    
    new_content = re.sub(help_pattern, add_header, content)
    
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    
    return False

def main():
    """Main function"""
    modules_dir = 'sitaBot/modules'
    updated = 0
    
    for filename in os.listdir(modules_dir):
        if filename.endswith('.py') and not filename.startswith('__init__'):
            filepath = os.path.join(modules_dir, filename)
            
            if process_help_text(filepath):
                print(f"✓ Added header to: {filename}")
                updated += 1
    
    print(f"\nAdded headers to {updated} files")

if __name__ == '__main__':
    main()
