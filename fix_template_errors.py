#!/usr/bin/env python3
"""
Automated script to fix common HTML template errors:
- Remove inline style="display: none;" and replace with Bootstrap d-none class
- Add accessibility attributes (aria-label, title, rel="noopener")
"""

import re
import os
from pathlib import Path

def fix_html_file(filepath):
    """Fix common HTML errors in a file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    changes_made = []
    
    # Fix 1: Replace style="display: none;" with d-none class
    pattern1 = r'(\s+style="display:\s*none;?")'
    if re.search(pattern1, content):
        # Check if element already has d-none class
        content = re.sub(
            r'(<[^>]+class="[^"]*")(\s+style="display:\s*none;?")',
            lambda m: m.group(1) + ' d-none"' if 'd-none' not in m.group(1) else m.group(1),
            content
        )
        # For elements without class attribute
        content = re.sub(
            r'(<[^>]+)(\s+style="display:\s*none;?")([^>]*>)',
            r'\1 class="d-none"\3',
            content
        )
        changes_made.append("Replaced inline display:none with d-none class")
    
    # Fix 2: Remove other inline styles and move to style block
    # This is more complex and needs manual review, so we'll skip for automation
    
    # Fix 3: Add rel="noopener" to target="_blank" links
    pattern3 = r'<a\s+([^>]*href="[^"]*"[^>]*)target="_blank"([^>]*)>'
    def add_noopener(match):
        full_tag = match.group(0)
        if 'rel=' not in full_tag:
            return full_tag.replace('target="_blank"', 'target="_blank" rel="noopener"')
        elif 'noopener' not in full_tag:
            return full_tag.replace('rel="', 'rel="noopener ')
        return full_tag
    
    if re.search(pattern3, content):
        content = re.sub(pattern3, add_noopener, content)
        changes_made.append("Added rel='noopener' to external links")
    
    # Fix 4: Add aria-label to buttons without text
    pattern4 = r'<button([^>]*)>\s*<i[^>]*></i>\s*</button>'
    def add_aria_label_button(match):
        button_attrs = match.group(1)
        if 'aria-label' not in button_attrs and 'title' not in button_attrs:
            # Try to extract button purpose from onclick or class
            if 'clear' in button_attrs.lower():
                return f'<button{button_attrs} aria-label="Clear"><i class="fas fa-times"></i></button>'
            elif 'remove' in button_attrs.lower():
                return f'<button{button_attrs} aria-label="Remove"><i class="fas fa-times"></i></button>'
            elif 'close' in button_attrs.lower():
                return f'<button{button_attrs} aria-label="Close"><i class="fas fa-times"></i></button>'
        return match.group(0)
    
    if re.search(pattern4, content):
        content = re.sub(pattern4, add_aria_label_button, content)
        changes_made.append("Added aria-label to icon-only buttons")
    
    # Fix 5: Add title to select elements without labels
    pattern5 = r'<select\s+class="form-select"([^>]*)id="([^"]*)"([^>]*)>'
    def add_select_title(match):
        attrs1 = match.group(1)
        select_id = match.group(2)
        attrs2 = match.group(3)
        full_attrs = attrs1 + attrs2
        
        if 'title=' not in full_attrs and 'aria-label=' not in full_attrs:
            # Generate title from ID
            title = select_id.replace('_', ' ').replace('-', ' ').title()
            if 'Filter' in title:
                title_text = f'title="{title}"'
            elif 'Depth' in title:
                title_text = f'title="Select {title.lower()}"'
            else:
                title_text = f'title="{title}"'
            return f'<select class="form-select"{attrs1}id="{select_id}"{attrs2} {title_text}>'
        return match.group(0)
    
    if re.search(pattern5, content):
        content = re.sub(pattern5, add_select_title, content)
        changes_made.append("Added title attributes to select elements")
    
    # Fix 6: Add aria-label to file inputs
    pattern6 = r'<input\s+type="file"([^>]*)>'
    def add_file_input_label(match):
        attrs = match.group(1)
        if 'aria-label' not in attrs and 'title' not in attrs:
            return f'<input type="file"{attrs} aria-label="Upload file">'
        return match.group(0)
    
    if re.search(pattern6, content):
        content = re.sub(pattern6, add_file_input_label, content)
        changes_made.append("Added aria-label to file inputs")
    
    # Only write if changes were made
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return changes_made
    return None

def main():
    templates_dir = Path(__file__).parent / "templates"
    
    print("🔧 Fixing HTML template errors...\n")
    
    html_files = list(templates_dir.glob("*.html"))
    fixed_count = 0
    
    for html_file in html_files:
        changes = fix_html_file(html_file)
        if changes:
            fixed_count += 1
            print(f"✓ {html_file.name}")
            for change in changes:
                print(f"  - {change}")
        else:
            print(f"  {html_file.name} (no changes needed)")
    
    print(f"\n✅ Fixed {fixed_count} files")

if __name__ == "__main__":
    main()
