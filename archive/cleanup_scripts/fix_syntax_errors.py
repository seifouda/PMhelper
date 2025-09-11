#!/usr/bin/env python3
"""
Fix syntax errors caused by aggressive debug cleanup
"""
import os
import re

def fix_syntax_errors():
    """Fix empty code blocks that cause syntax errors"""
    file_path = "src/pmhelper/gui/main_window.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix empty exception blocks
    content = re.sub(r'except Exception as e:\s*\n\s*(?=\n|\s*def|\s*class|\s*$)', 'except Exception as e:\n            pass\n', content, flags=re.MULTILINE)
    
    # Fix empty if/else blocks
    content = re.sub(r'if [^:]+:\s*\n\s*(?=\n|\s*def|\s*class|\s*else:)', lambda m: m.group(0) + '            pass\n', content, flags=re.MULTILINE)
    content = re.sub(r'else:\s*\n\s*(?=\n|\s*def|\s*class|\s*$)', 'else:\n            pass\n', content, flags=re.MULTILINE)
    
    # Fix empty try blocks  
    content = re.sub(r'try:\s*\n\s*(?=\n|\s*except|\s*finally)', 'try:\n            pass\n', content, flags=re.MULTILINE)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Fixed syntax errors in {file_path}")

if __name__ == "__main__":
    fix_syntax_errors()