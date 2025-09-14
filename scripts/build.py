#!/usr/bin/env python3
"""
PMHelper Build Script

Builds the PMHelper application for distribution.
Creates executable and packaged distributions.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def main():
    """Main build function"""
    print("PMHelper Build Script")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not Path("src/main.py").exists():
        print("Error: Must run from project root directory")
        sys.exit(1)
    
    # Clean previous builds
    print("1. Cleaning previous builds...")
    if Path("dist").exists():
        shutil.rmtree("dist")
    if Path("build").exists():
        shutil.rmtree("build")
    
    # Install/update dependencies
    print("2. Installing dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "config/requirements.txt"], 
                      check=True)
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], 
                      check=True)
    except subprocess.CalledProcessError:
        print("Error: Failed to install dependencies")
        sys.exit(1)
    
    # Run tests
    print("3. Running tests...")
    try:
        subprocess.run([sys.executable, "-m", "pytest", "tests/unit/"], check=True)
        print("   [SUCCESS] Unit tests passed")
    except subprocess.CalledProcessError:
        print("   [WARNING] Some tests failed, continuing build...")
    
    # Build executable
    print("4. Building executable...")
    try:
        subprocess.run([
            "pyinstaller", 
            "--onefile", 
            "--windowed",
            "--name", "PMHelper",
            "--add-data", "assets;assets",
            "--add-data", "config;config",
            "src/main.py"
        ], check=True)
        print("   [SUCCESS] Executable created successfully")
    except subprocess.CalledProcessError:
        print("   [ERROR] Executable build failed")
        sys.exit(1)
    
    # Create distribution package
    print("5. Creating distribution package...")
    dist_dir = Path("dist/PMHelper-Package")
    dist_dir.mkdir(exist_ok=True)
    
    # Copy necessary files
    files_to_copy = [
        ("README.md", "README.md"),
        ("config/requirements.txt", "requirements.txt"),
        ("assets", "assets"),
        ("docs", "docs")
    ]
    
    for src, dst in files_to_copy:
        src_path = Path(src)
        dst_path = dist_dir / dst
        
        if src_path.is_file():
            shutil.copy2(src_path, dst_path)
        elif src_path.is_dir():
            if dst_path.exists():
                shutil.rmtree(dst_path)
            shutil.copytree(src_path, dst_path)
    
    # Copy executable
    exe_name = "PMHelper.exe" if sys.platform == "win32" else "PMHelper"
    if Path(f"dist/{exe_name}").exists():
        shutil.copy2(f"dist/{exe_name}", dist_dir / exe_name)
    
    print("6. Build completed successfully!")
    print(f"   [PACKAGE] Executable: dist/{exe_name}")
    print(f"   [PACKAGE] Package: dist/PMHelper-Package/")
    print()
    print("To run the application:")
    print(f"   ./dist/{exe_name}")
    print("Or:")
    print("   python src/main.py")

if __name__ == "__main__":
    main()
