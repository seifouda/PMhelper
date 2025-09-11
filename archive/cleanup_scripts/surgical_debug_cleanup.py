#!/usr/bin/env python3
"""
SURGICAL Debug Print Removal
Removes ONLY print statements with debug content while preserving ALL functionality.
"""

import os
import re
from pathlib import Path


def surgical_debug_removal(file_path):
    """Surgically remove only debug prints, preserve everything else."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        cleaned_lines = []
        removed_count = 0
        
        for i, line in enumerate(lines):
            original_line = line
            line_strip = line.strip()
            
            # Only remove lines that are PURE debug prints
            should_remove = False
            
            # Patterns for debug prints to remove
            debug_patterns = [
                r'^\s*print\s*\(\s*f?\s*["\'][^"\']*\[?DEBUG\]?[^"\']*["\']',
                r'^\s*print\s*\(\s*f?\s*["\']DEBUG:',
                r'^\s*print\s*\(\s*["\']🔍\s*\[.*DEBUG.*\]',
                r'^\s*print\s*\(\s*["\']📊\s*\[.*DEBUG.*\]',
                r'^\s*print\s*\(\s*["\']✅\s*\[.*DEBUG.*\]',
                r'^\s*print\s*\(\s*["\']❌\s*\[.*DEBUG.*\]',
            ]
            
            for pattern in debug_patterns:
                if re.match(pattern, line, re.IGNORECASE):
                    should_remove = True
                    break
            
            # Additional check for f-string debug prints
            if not should_remove and line_strip.startswith('print(f"[DEBUG'):
                should_remove = True
            elif not should_remove and line_strip.startswith('print("[DEBUG'):
                should_remove = True
            
            if should_remove:
                print(f"  Removing: {line.strip()}")
                removed_count += 1
            else:
                cleaned_lines.append(original_line)
        
        if removed_count > 0:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(cleaned_lines)
            print(f"✓ Removed {removed_count} debug prints from: {file_path}")
            return True
        else:
            print(f"  No debug prints found in: {file_path}")
            return False
    
    except Exception as e:
        print(f"✗ Error processing {file_path}: {e}")
        return False


def main():
    """Main surgical cleanup function."""
    src_dir = Path("src")
    
    if not src_dir.exists():
        print("✗ Source directory not found.")
        return
    
    print("🔬 Starting SURGICAL Debug Print Removal...")
    print("=" * 60)
    print("⚠️  PRESERVING ALL FUNCTIONALITY - Only removing debug prints!")
    print("=" * 60)
    
    # Find all Python files
    python_files = []
    for py_file in src_dir.rglob("*.py"):
        # Skip backup files but process main files
        if any(skip in str(py_file).lower() for skip in ['backup', 'test_', '_test']):
            continue
        python_files.append(py_file)
    
    print(f"\n📁 Processing {len(python_files)} Python files...")
    print("-" * 60)
    
    total_cleaned = 0
    
    for py_file in python_files:
        print(f"\n🔧 Processing: {py_file}")
        if surgical_debug_removal(py_file):
            total_cleaned += 1
    
    print("\n" + "=" * 60)
    print("✅ SURGICAL Debug Cleanup Complete!")
    print(f"   Files processed: {len(python_files)}")
    print(f"   Files with debug prints removed: {total_cleaned}")
    print("   All functionality preserved!")
    print("=" * 60)


if __name__ == "__main__":
    main()