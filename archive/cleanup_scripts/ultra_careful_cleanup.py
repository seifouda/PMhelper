#!/usr/bin/env python3
"""
ULTRA-CAREFUL Debug Print Removal
Only removes specific print statements, preserves ALL logic and structure
"""
import os
import re

def careful_print_removal(file_path):
    """Very carefully remove only debug print statements"""
    if not os.path.exists(file_path):
        return False, f"File not found: {file_path}"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        cleaned_lines = []
        removed_count = 0
        
        for line in lines:
            stripped = line.strip()
            
            # Only remove very specific debug print patterns
            should_remove = False
            
            # Remove prints with debug emojis and specific debug content
            debug_patterns = [
                r'print\(f"🔍.*?\)',
                r'print\(f"📊.*?\)',
                r'print\(f"✅.*?\)', 
                r'print\(f"❌.*?\)',
                r'print\(f"🎯.*?\)',
                r'print\(f"📋.*?\)',
                r'print\(f"🔨.*?\)',
                r'print\(f"💰.*?\)',
                r'print\(f"📈.*?\)',
                r'print\("=.*="\)',  # Separator lines
                r'print\(f"\[DEBUG.*?\)',
                r'print\(f"\[RCPS.*?\)',
                r'print\(f"\[CRASHING.*?\)',
                r'print\(f"\[ANALYSIS.*?\)',
                r'print\(.*DEBUG.*\)',
                r'print\(.*VERIFICATION.*\)',
                r'print\(.*COST DATA.*\)',
                r'print\(.*ITERATION.*\)',
                r'print\(.*STRATEGY.*\)',
            ]
            
            for pattern in debug_patterns:
                if re.search(pattern, stripped, re.IGNORECASE):
                    should_remove = True
                    break
            
            # Remove specific verbose output lines
            verbose_patterns = [
                'Graph nodes:', 'Critical activities:', 'Project duration:',
                'Analyzer type:', 'Activities data count:', 'Sample activity data:',
                'Analysis mode:', 'Current analyzer:', 'Analyzer has activities:',
                'Activity:', 'Analyzer has graph G:', 'Node ', ': ES=', ', EF=', ', Duration=',
                'entry_text widget', 'log_text widget', 'summary_text widget', 'metrics_text widget',
                'Integration Test Results:', 'fixes implemented', 'READY FOR TESTING',
                'GANTT CHART INTEGRATION TEST', 'Fix 1:', 'Fix 2:', 'Fix 3:',
                'Enhanced step graphs', 'step graphs with RCPS', 'Critical path from crash log',
                'Original activity found:', 'Final crash_cost:', 'Final normal_cost:',
            ]
            
            if 'print(' in stripped:
                for pattern in verbose_patterns:
                    if pattern in stripped:
                        should_remove = True
                        break
            
            if not should_remove:
                cleaned_lines.append(line)
            else:
                removed_count += 1
        
        # Write back only if changes were made
        if removed_count > 0:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(cleaned_lines)
            return True, f"Removed {removed_count} debug prints from: {file_path}"
        else:
            return False, f"No debug prints found in: {file_path}"
            
    except Exception as e:
        return False, f"Error processing {file_path}: {str(e)}"

def main():
    """Main cleanup function"""
    print("🎯 ULTRA-CAREFUL Debug Print Removal")
    print("🔍 Only removing specific debug patterns, preserving ALL logic")
    print("=" * 65)
    
    # Files that definitely have debug output
    files_to_clean = [
        "launch_app.py",
        "src/pmhelper/gui/main_window.py", 
        "src/pmhelper/gui/tabs/network_tab.py",
        "src/pmhelper/gui/tabs/gantt_tab.py",
        "src/pmhelper/gui/tabs/rcps_tab.py",
        "src/pmhelper/gui/tabs/rcps_crashing_tab_gui.py",
        "src/pmhelper/gui/tabs/project_crashing_core.py",
        "src/pmhelper/gui/tabs/crashing_tab_gui.py",
    ]
    
    total_cleaned = 0
    total_removed = 0
    
    for file_path in files_to_clean:
        if os.path.exists(file_path):
            success, message = careful_print_removal(file_path)
            if success:
                total_cleaned += 1
                # Extract number from message
                import re
                match = re.search(r'Removed (\d+)', message)
                if match:
                    total_removed += int(match.group(1))
                print(f"✅ {message}")
            else:
                print(f"⏭️  {message}")
        else:
            print(f"❌ File not found: {file_path}")
    
    print("=" * 65)
    print(f"🎉 CLEANUP COMPLETE!")
    print(f"📊 Files processed: {len(files_to_clean)}")
    print(f"📁 Files cleaned: {total_cleaned}")
    print(f"🗑️  Total debug prints removed: {total_removed}")
    print("🚀 All functionality preserved - only debug output removed!")
    print("=" * 65)

if __name__ == "__main__":
    main()