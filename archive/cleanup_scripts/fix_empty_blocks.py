#!/usr/bin/env python3
"""
Fix empty code blocks created by debug cleanup
"""
import re

def fix_empty_blocks():
    """Fix empty code blocks in main_window.py"""
    file_path = "src/pmhelper/gui/main_window.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix specific empty blocks
    fixes = [
        # Fix empty if block around line 408
        (r'if hasattr\(self\.current_analyzer, \'G\'\):\s*\n\s*else:', 
         'if hasattr(self.current_analyzer, \'G\'):\n                pass  # Graph available\n            else:'),
        
        # Fix empty except blocks
        (r'except:\s*\n\s*(?=\n|\s*def|\s*class|\s*try|\s*if|\s*else|\s*$)', 
         'except:\n            pass\n'),
        
        # Fix empty try blocks
        (r'try:\s*\n\s*(?=\n|\s*except|\s*finally)', 
         'try:\n            pass\n'),
        
        # Fix empty else blocks  
        (r'else:\s*\n\s*(?=\n|\s*def|\s*class|\s*if|\s*$)', 
         'else:\n            pass\n'),
        
        # Fix empty if blocks
        (r'if [^:]+:\s*\n\s*(?=\n|\s*else:|\s*def|\s*class)', 
         lambda m: m.group(0).rstrip() + '\n            pass\n'),
    ]
    
    for pattern, replacement in fixes:
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
    
    # Additional specific fixes
    content = re.sub(r'passed = sum\(results\.values\(\)\)\s*\n\s*(?=\n|\s*else:)', 
                     'passed = sum(results.values())\n        print(f"Test results: {passed} passed")\n', 
                     content, flags=re.MULTILINE)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Fixed empty code blocks in main_window.py")

if __name__ == "__main__":
    fix_empty_blocks()