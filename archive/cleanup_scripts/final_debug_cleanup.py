#!/usr/bin/env python3
"""
FINAL DEBUG CLEANUP - Remove ALL debug prints without breaking functionality
This script will remove debug, analysis, and verbose prints while preserving all logic.
"""
import os
import re

def clean_debug_prints_from_file(file_path):
    """Remove debug prints from a single file"""
    if not os.path.exists(file_path):
        return False, f"File not found: {file_path}"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        lines = content.split('\n')
        cleaned_lines = []
        
        i = 0
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()
            
            # Skip debug print patterns but preserve all logic
            if (stripped.startswith('print(') and any(debug_indicator in stripped.lower() for debug_indicator in [
                'debug', 'analysis', 'cost data', '[rcps', '[crashing', 'verification', 
                'iteration', 'strategy', 'warning:', 'success:', 'error:', 'checking',
                'graph nodes', 'activities:', 'analyzer', 'duration:', 'timing',
                'critical activities', 'crashable', 'final crash', 'enhancement',
                'integration test', 'gantt chart', 'fixes implemented', 'ready for testing',
                'manual', 'table', 'columns:', 'rows:', 'shape:', 'found:', 'created'
            ])):
                # Skip this print line completely
                i += 1
                continue
            
            # Skip standalone print statements with complex debug output
            if stripped.startswith('print(f"') and any(pattern in stripped for pattern in [
                '🔍', '📊', '✅', '❌', '🎯', '📋', '🔨', '💰', '📈', '🚀', '⚠️', 
                'DEBUG', 'ANALYSIS', 'VERIFICATION', 'COST DATA', 'ITERATION',
                'STRATEGY', 'RCPS', 'CRASHING', 'GANTT', 'INTEGRATION'
            ]):
                # Skip this debug print
                i += 1
                continue
            
            # Skip print statements with debug content
            if 'print(' in stripped and any(pattern in stripped for pattern in [
                'Graph nodes:', 'Critical activities:', 'Project duration:', 
                'Analyzer type:', 'Activities data count:', 'Sample activity data:',
                'Analysis mode:', 'Current analyzer:', 'Close the application window',
                'Application initialized', 'Application launched successfully',
                'Features available:', 'Starting PMHelper', 'SUCCESS:', 'tksheet imported'
            ]):
                # Keep essential startup messages, remove detailed debug
                if any(keep in stripped for keep in [
                    'Starting PMHelper', 'Application launched successfully', 
                    'Close the application window'
                ]):
                    cleaned_lines.append(line)
                i += 1
                continue
            
            # Skip complex debug blocks
            if stripped.startswith('print("=') and '=' in stripped[10:]:
                # Skip separator lines
                i += 1
                continue
                
            # Remove specific verbose output patterns
            if any(pattern in stripped for pattern in [
                'entry_text widget available', 'log_text widget available',
                'summary_text widget available', 'metrics_text widget available'
            ]) and 'print(' in stripped:
                i += 1
                continue
            
            # Keep the line
            cleaned_lines.append(line)
            i += 1
        
        cleaned_content = '\n'.join(cleaned_lines)
        
        # Additional cleanup for multi-line debug blocks
        # Remove complex f-string debug prints
        debug_patterns = [
            r'print\(f"\s*🔍.*?\)\s*\n',
            r'print\(f"\s*📊.*?\)\s*\n', 
            r'print\(f"\s*✅.*?\)\s*\n',
            r'print\(f"\s*❌.*?\)\s*\n',
            r'print\(f"\s*🎯.*?\)\s*\n',
            r'print\(f"\s*📋.*?\)\s*\n',
            r'print\(f"\s*🔨.*?\)\s*\n',
            r'print\(f"\s*💰.*?\)\s*\n',
            r'print\(f"\s*📈.*?\)\s*\n',
            r'print\(f"\s*\[DEBUG.*?\)\s*\n',
            r'print\(f"\s*\[RCPS.*?\)\s*\n',
            r'print\(f"\s*\[CRASHING.*?\)\s*\n',
            r'print\(f"\s*\[ANALYSIS.*?\)\s*\n',
        ]
        
        for pattern in debug_patterns:
            cleaned_content = re.sub(pattern, '', cleaned_content, flags=re.MULTILINE | re.DOTALL)
        
        # Check if any changes were made
        if cleaned_content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(cleaned_content)
            return True, f"Cleaned debug prints from: {file_path}"
        else:
            return False, f"No debug prints found in: {file_path}"
            
    except Exception as e:
        return False, f"Error processing {file_path}: {str(e)}"

def main():
    """Main cleanup function"""
    print("🎯 FINAL DEBUG CLEANUP - Removing ALL debug prints")
    print("=" * 60)
    
    # Target files with debug output
    files_to_clean = [
        "launch_app.py",
        "src/pmhelper/gui/main_window.py", 
        "src/pmhelper/gui/tabs/network_tab.py",
        "src/pmhelper/gui/tabs/gantt_tab.py",
        "src/pmhelper/gui/tabs/rcps_tab.py",
        "src/pmhelper/gui/tabs/rcps_crashing_tab_gui.py",
        "src/pmhelper/gui/tabs/project_crashing_core.py",
        "src/pmhelper/gui/tabs/crashing_tab_gui.py",
        "src/pmhelper/core/cpm_analyzer.py",
        "src/pmhelper/core/rcps_analyzer.py",
        "src/pmhelper/core/network_builder.py"
    ]
    
    total_cleaned = 0
    
    for file_path in files_to_clean:
        if os.path.exists(file_path):
            success, message = clean_debug_prints_from_file(file_path)
            if success:
                total_cleaned += 1
                print(f"✅ {message}")
            else:
                print(f"⏭️  {message}")
        else:
            print(f"❌ File not found: {file_path}")
    
    print("=" * 60)
    print(f"🎉 CLEANUP COMPLETE! Cleaned {total_cleaned} files")
    print("🚀 Application should now have minimal console output")
    print("=" * 60)

if __name__ == "__main__":
    main()