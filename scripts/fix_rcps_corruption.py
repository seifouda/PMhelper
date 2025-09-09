#!/usr/bin/env python3
"""
RCPS File Corruption Fix Script
Automated repair and validation of rcps_tab.py file corruption
"""

import os
import shutil
from pathlib import Path
import subprocess
import sys

class RCPSFileRepair:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.rcps_main = self.project_root / "src/pmhelper/gui/tabs/rcps_tab.py"
        self.rcps_backup = self.project_root / "src/pmhelper/gui/tabs/rcps_tab_backup.py"
        self.rcps_broken = self.project_root / "src/pmhelper/gui/tabs/rcps_tab_broken.py"
        
    def backup_current_state(self):
        """Create backup of corrupted file"""
        backup_path = self.rcps_main.with_suffix('.py.corrupted_backup')
        print(f"Creating backup: {backup_path}")
        shutil.copy2(self.rcps_main, backup_path)
        return backup_path
        
    def analyze_corruption(self):
        """Analyze the corruption patterns"""
        print("=== Corruption Analysis ===")
        
        with open(self.rcps_main, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check for duplicate content
        lines = content.split('\n')
        line_counts = {}
        for i, line in enumerate(lines):
            if line.strip():
                if line in line_counts:
                    line_counts[line].append(i + 1)
                else:
                    line_counts[line] = [i + 1]
        
        duplicates = {line: positions for line, positions in line_counts.items() 
                     if len(positions) > 1}
        
        if duplicates:
            print(f"Found {len(duplicates)} duplicate lines:")
            for line, positions in list(duplicates.items())[:5]:  # Show first 5
                print(f"  Line {positions}: {line[:50]}...")
        
        # Check for syntax errors
        try:
            compile(content, self.rcps_main, 'exec')
            print("✓ File compiles successfully")
        except SyntaxError as e:
            print(f"✗ Syntax error: {e}")
            print(f"  Line {e.lineno}: {e.text}")
            
    def repair_from_backup(self):
        """Attempt repair using backup file"""
        if not self.rcps_backup.exists():
            print(f"❌ Backup file not found: {self.rcps_backup}")
            return False
            
        print(f"Restoring from backup: {self.rcps_backup}")
        
        # Test backup file first
        try:
            with open(self.rcps_backup, 'r', encoding='utf-8') as f:
                backup_content = f.read()
            compile(backup_content, self.rcps_backup, 'exec')
            print("✓ Backup file is valid")
            
            # Restore from backup
            shutil.copy2(self.rcps_backup, self.rcps_main)
            print("✓ File restored successfully")
            return True
            
        except Exception as e:
            print(f"❌ Backup file is also corrupted: {e}")
            return False
    
    def validate_repair(self):
        """Validate the repaired file"""
        print("=== Validation Tests ===")
        
        # 1. Syntax check
        try:
            result = subprocess.run([
                sys.executable, '-m', 'py_compile', str(self.rcps_main)
            ], capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode == 0:
                print("✓ Syntax validation passed")
            else:
                print(f"❌ Syntax validation failed: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ Could not run syntax check: {e}")
            return False
        
        # 2. Import test
        try:
            # Add src to path and try import
            import_script = f"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path('{self.project_root}') / 'src'))
from pmhelper.gui.tabs.rcps_tab import RCPSTab
print("✓ Import test passed")
"""
            result = subprocess.run([
                sys.executable, '-c', import_script
            ], capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode == 0:
                print("✓ Import test passed")
            else:
                print(f"❌ Import test failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Could not run import test: {e}")
            return False
        
        # 3. Method existence check
        try:
            method_check_script = f"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path('{self.project_root}') / 'src'))
from pmhelper.gui.tabs.rcps_tab import RCPSTab

required_methods = [
    'create_tab', 'run_rcps', 'display_hybrid_schedule_view',
    'create_compact_table', 'display_gantt_chart'
]

missing = []
for method in required_methods:
    if not hasattr(RCPSTab, method):
        missing.append(method)

if missing:
    print(f"❌ Missing methods: {{', '.join(missing)}}")
    exit(1)
else:
    print("✓ All required methods present")
"""
            result = subprocess.run([
                sys.executable, '-c', method_check_script
            ], capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode == 0:
                print("✓ Method existence check passed")
            else:
                print(f"❌ Method check failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Could not run method check: {e}")
            return False
            
        return True
    
    def run_repair(self):
        """Execute the full repair process"""
        print("🔧 RCPS File Corruption Repair")
        print("=" * 40)
        
        # Step 1: Backup current state
        backup_path = self.backup_current_state()
        
        # Step 2: Analyze corruption
        self.analyze_corruption()
        
        # Step 3: Attempt repair
        if self.repair_from_backup():
            # Step 4: Validate repair
            if self.validate_repair():
                print("\n🎉 Repair completed successfully!")
                print(f"Original corrupted file backed up to: {backup_path}")
                return True
            else:
                print("\n❌ Repair validation failed")
                return False
        else:
            print("\n❌ Could not repair from backup")
            return False

def main():
    # Auto-detect project root
    current_dir = Path.cwd()
    project_root = current_dir
    
    # Look for project markers
    markers = ['launch_app.py', 'src/pmhelper', 'README.md']
    for marker in markers:
        if (project_root / marker).exists():
            break
    else:
        print("❌ Could not find PMHelper project root")
        print("Please run this script from the PMHelper directory")
        return 1
    
    repairer = RCPSFileRepair(project_root)
    
    if repairer.run_repair():
        print("\n📋 Next Steps:")
        print("1. Run the hybrid test: python test_rcps_hybrid.py")
        print("2. Launch the GUI: python launch_app.py")
        print("3. Test RCPS functionality with sample data")
        return 0
    else:
        print("\n📋 Manual Intervention Required:")
        print("1. Check backup files in src/pmhelper/gui/tabs/")
        print("2. Review corruption analysis output")
        print("3. Consider manual file reconstruction")
        return 1

if __name__ == '__main__':
    exit(main())
