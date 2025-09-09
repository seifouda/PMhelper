#!/usr/bin/env python3
"""
RCPS Crashing Bug Fix
=====================

This script fixes the critical bug where RCPS Crashing shows "no RCPS data available" 
despite successful RCPS analysis. The issue is that the network graph and analyzer 
are not being stored after RCPS analysis completion.

Root Cause: Missing network graph storage in run_rcps method
Solution: Add network graph storage after successful RCPS analysis
"""

import re
import os
import shutil
from pathlib import Path

class RCPSCrashingBugFix:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.rcps_file = self.project_root / "src" / "pmhelper" / "gui" / "tabs" / "rcps_tab.py"
        
    def create_backup(self):
        """Create backup of corrupted file"""
        backup_path = self.rcps_file.with_suffix('.py.backup_corrupted')
        shutil.copy2(self.rcps_file, backup_path)
        print(f"✅ Created backup: {backup_path}")
        return backup_path
        
    def fix_rcps_data_storage(self):
        """Fix the RCPS data storage bug by adding network graph storage"""
        
        # Read the file content
        with open(self.rcps_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Storage code to add after fullscreen button enabling
        storage_code = '''
            # Build and store network graph for RCPS Crashing feature
            print("[DEBUG STORAGE] Building network graph for RCPS Crashing...")
            self.rcps_network_graph = self._build_rcps_network_graph(df_gantt)
            self.rcps_analyzer = analyzer
            print(f"[DEBUG STORAGE] Network graph built: {self.rcps_network_graph is not None}")
            print(f"[DEBUG STORAGE] Analyzer stored: {self.rcps_analyzer is not None}")'''
        
        # Pattern to find the fullscreen button enabling in run_rcps method
        pattern = r'(self\.fullscreen_btn\.config\(state=\'normal\'\)\s*\n)(\s*)(except ValueError as ve:)'
        
        def replacement_func(match):
            button_line = match.group(1)
            whitespace = match.group(2)
            except_line = match.group(3)
            return f"{button_line}{storage_code}\n{whitespace}\n        {except_line}"
        
        # Apply the fix
        new_content = re.sub(pattern, replacement_func, content, count=1)
        
        if new_content != content:
            # Write the fixed content
            with open(self.rcps_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print("✅ Applied network graph storage fix to run_rcps method")
            return True
        else:
            print("❌ Pattern not found - manual fix required")
            return False
    
    def validate_fix(self):
        """Validate the fix was applied correctly"""
        with open(self.rcps_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for required components
        checks = [
            ("[DEBUG STORAGE]" in content, "Debug storage prints"),
            ("self.rcps_network_graph = self._build_rcps_network_graph" in content, "Network graph building"),
            ("self.rcps_analyzer = analyzer" in content, "Analyzer storage"),
        ]
        
        all_passed = True
        for check_passed, description in checks:
            status = "✅" if check_passed else "❌"
            print(f"{status} {description}")
            if not check_passed:
                all_passed = False
        
        return all_passed
    
    def run_test(self):
        """Run the test to verify the fix works"""
        print("\n🧪 Running RCPS Crashing bug test...")
        import subprocess
        result = subprocess.run(['python', 'test_rcps_crashing_bug.py'], 
                              capture_output=True, text=True, cwd=self.project_root)
        
        if result.returncode == 0:
            print("✅ Test passed - bug fixed!")
            return True
        else:
            print("❌ Test failed - bug still exists")
            print("Error output:", result.stderr[-500:] if result.stderr else "No error output")
            return False
    
    def execute_fix(self):
        """Execute the complete fix process"""
        print("🔧 Starting RCPS Crashing Bug Fix...")
        print("=" * 50)
        
        # Step 1: Create backup
        backup_path = self.create_backup()
        
        # Step 2: Apply the fix
        print("\n📝 Applying fix...")
        if not self.fix_rcps_data_storage():
            print("❌ Fix failed to apply - file may be corrupted")
            return False
        
        # Step 3: Validate fix
        print("\n🔍 Validating fix...")
        if not self.validate_fix():
            print("❌ Fix validation failed")
            return False
        
        # Step 4: Test the fix
        if not self.run_test():
            print("❌ Fix test failed")
            return False
        
        print("\n🎉 RCPS Crashing bug successfully fixed!")
        print("=" * 50)
        print("✅ Network graph now stored after RCPS analysis")
        print("✅ RCPS Crashing feature can access RCPS data")
        print("✅ Bug reproduction test passes")
        return True

if __name__ == "__main__":
    fixer = RCPSCrashingBugFix()
    success = fixer.execute_fix()
    exit(0 if success else 1)
