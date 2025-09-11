#!/usr/bin/env python3
"""
Identify essential files needed to run the PMHelper application
"""

import os
from pathlib import Path

def get_essential_files():
    """Identify files needed for the application to run"""
    
    # Core application files
    essential_files = [
        # Main launcher
        "launch_app.py",
        
        # README and configuration
        "README.md",
        "config/requirements.txt",
        
        # Source code directory - entire src folder is needed
        "src/",
        
        # Assets (if any images/icons are needed)
        "assets/",
        
        # Git configuration
        ".gitignore",
        
        # Documentation that should be included in production
        "docs/",
    ]
    
    # Files that are NOT needed in production
    excluded_patterns = [
        # Debug and test files
        "debug_*.py",
        "test_*.py",
        "quick_*.py",
        "analyze_*.py",
        "compare_*.py",
        "fix_*.py",
        "validate_*.py",
        "verify_*.py",
        "investigate_*.py",
        "implement_*.py",
        "integrate_*.py",
        "execute_*.py",
        "extract_*.py",
        "final_verification.py",
        "foundation_methods.py",
        "minimal_toolbar_test.py",
        "rcps_*.py",
        "simple_*.py",
        "demo_*.py",
        
        # Documentation files (markdown reports)
        "*.md",
        
        # Build artifacts
        "build/",
        "dist/",
        "__pycache__/",
        "*.pyc",
        ".pytest_cache/",
        "htmlcov/",
        ".coverage",
        
        # Development environment
        ".venv/",
        ".vscode/",
        
        # Git history (though .git might be needed)
        # ".git/",
        
        # Extensions and templates (unless needed)
        "extensions/",
        "templates/",
        
        # Scripts (unless needed)
        "scripts/",
        
        # Test directories
        "tests/",
        
        # Code directory (seems to be duplicate/old)
        "code/",
        
        # Log files
        "*.txt",
        "*.log",
        
        # New folder
        "New folder/",
    ]
    
    return essential_files, excluded_patterns

def analyze_workspace():
    """Analyze the current workspace"""
    root = Path(".")
    essential_files, excluded_patterns = get_essential_files()
    
    print("=== ESSENTIAL FILES FOR PREPRODUCTION ===\n")
    
    print("1. CORE APPLICATION FILES:")
    core_files = [
        "launch_app.py",
        "README.md", 
        "config/requirements.txt"
    ]
    
    for file in core_files:
        if (root / file).exists():
            print(f"   ✓ {file}")
        else:
            print(f"   ✗ {file} (MISSING)")
    
    print("\n2. SOURCE CODE STRUCTURE:")
    src_path = root / "src"
    if src_path.exists():
        print(f"   ✓ src/ directory")
        for py_file in src_path.rglob("*.py"):
            rel_path = py_file.relative_to(root)
            print(f"     - {rel_path}")
    else:
        print("   ✗ src/ directory (MISSING)")
    
    print("\n3. ASSETS AND CONFIGURATION:")
    config_dirs = ["assets", "config", "docs"]
    for dir_name in config_dirs:
        dir_path = root / dir_name
        if dir_path.exists():
            print(f"   ✓ {dir_name}/ directory")
            # Show some contents
            files = list(dir_path.rglob("*"))[:5]  # First 5 files
            for file in files:
                if file.is_file():
                    rel_path = file.relative_to(root)
                    print(f"     - {rel_path}")
        else:
            print(f"   ✗ {dir_name}/ directory")
    
    print("\n=== FILES TO EXCLUDE FROM PREPRODUCTION ===\n")
    
    all_files = list(root.rglob("*"))
    excluded_files = []
    
    for file_path in all_files:
        if file_path.is_file():
            rel_path = file_path.relative_to(root)
            rel_str = str(rel_path)
            
            # Check against exclusion patterns
            should_exclude = False
            for pattern in excluded_patterns:
                if pattern.endswith("/"):
                    # Directory pattern
                    if pattern[:-1] in rel_str:
                        should_exclude = True
                        break
                elif pattern.startswith("*."):
                    # Extension pattern
                    if rel_str.endswith(pattern[1:]):
                        should_exclude = True
                        break
                elif "*" in pattern:
                    # Wildcard pattern
                    pattern_parts = pattern.split("*")
                    if all(part in rel_str for part in pattern_parts if part):
                        should_exclude = True
                        break
                else:
                    # Exact match
                    if rel_str == pattern or rel_str.endswith("/" + pattern):
                        should_exclude = True
                        break
            
            if should_exclude:
                excluded_files.append(rel_str)
    
    # Group excluded files by type
    debug_files = [f for f in excluded_files if f.startswith("debug_") or f.startswith("test_")]
    md_files = [f for f in excluded_files if f.endswith(".md")]
    build_files = [f for f in excluded_files if any(x in f for x in ["__pycache__", "build", "dist", ".venv"])]
    other_files = [f for f in excluded_files if f not in debug_files and f not in md_files and f not in build_files]
    
    if debug_files:
        print("DEBUG/TEST FILES:")
        for f in debug_files[:10]:  # Show first 10
            print(f"   - {f}")
        if len(debug_files) > 10:
            print(f"   ... and {len(debug_files) - 10} more debug/test files")
    
    if md_files:
        print(f"\nMARKDOWN DOCUMENTATION ({len(md_files)} files):")
        for f in md_files[:5]:  # Show first 5
            print(f"   - {f}")
        if len(md_files) > 5:
            print(f"   ... and {len(md_files) - 5} more .md files")
    
    if build_files:
        print(f"\nBUILD ARTIFACTS ({len(build_files)} files):")
        for f in build_files[:5]:
            print(f"   - {f}")
        if len(build_files) > 5:
            print(f"   ... and {len(build_files) - 5} more build files")
    
    if other_files:
        print(f"\nOTHER EXCLUDED FILES ({len(other_files)} files):")
        for f in other_files[:10]:
            print(f"   - {f}")
        if len(other_files) > 10:
            print(f"   ... and {len(other_files) - 10} more files")
    
    print(f"\nTOTAL FILES TO EXCLUDE: {len(excluded_files)}")
    
    return essential_files, excluded_files

if __name__ == "__main__":
    analyze_workspace()
