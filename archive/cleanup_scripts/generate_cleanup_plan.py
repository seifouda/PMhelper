#!/usr/bin/env python3
"""
PMHelper Production Cleanup & File Organization
Categorizes files for cleanup, archival, or future development
"""

import os
import shutil
from datetime import datetime

def organize_workspace():
    """Organize files into appropriate categories"""
    
    # File categories
    categories = {
        "ESSENTIAL_PRODUCTION": [
            "launch_app.py",
            "README.md", 
            ".gitignore",
            "src/",
            "assets/",
            "config/",
            "docs/",
            "tests/",
            "templates/",
            "scripts/"
        ],
        
        "FUTURE_DEVELOPMENT": [
            # Core enhancement scripts that may be useful later
            "foundation_methods.py",
            "integrate_phase1_methods.py", 
            "implement_rcps_table_integration.py",
            "rcps_crashing_bypass_solution.py",
            
            # Key documentation for future reference
            "IMPLEMENTATION_RECOMMENDATIONS.md",
            "PROJECT_TIMELINE.md",
            "RCPS_CRASHING_IMPLEMENTATION_SUMMARY.md",
            "FULLSCREEN_COMPARISON_IMPLEMENTATION_SUMMARY.md",
            "PHASE3_IMPLEMENTATION_COMPLETION_SUMMARY.md",
            "PRODUCTION_CLEANUP_COMPLETE.md",
            
            # Important test files for future validation
            "test_rcps_complete.py",
            "test_enhanced_strategy.py",
            "test_fullscreen_comparison.py",
            "validate_rcps_fix.py",
            "validation_summary.py",
        ],
        
        "CLEANUP_SCRIPTS": [
            # One-time cleanup scripts - can be archived
            "final_debug_cleanup.py",
            "surgical_debug_cleanup.py", 
            "ultra_careful_cleanup.py",
            "fix_empty_blocks.py",
            "fix_syntax_errors.py",
        ],
        
        "DEBUG_ANALYSIS": [
            # Debug and analysis files - can be removed
            "analyze_rcps_crashing_issue.py",
            "analyze_rcps_integration_options.py",
            "check_rcps_table_structure.py",
            "compare_crashing_approaches.py", 
            "compare_crashing_data.py",
            "compare_tabs.py",
            "debug_cost_data.py",
            "debug_gantt_button.py",
            "debug_missing_activities.py",
            "debug_normal_crashing.py",
            "debug_rcps_access_methods.py",
            "debug_rcps_data_flow.py", 
            "debug_rcps_durations.py",
            "debug_rcps_enhancements.py",
            "debug_rcps_table_access.py",
            "debug_toolbar.py",
            "demo_fullscreen_comparison.py",
            "execute_rcps_immediate_actions.py",
            "extract_network_attributes.py",
            "final_verification.py",
            "fix_rcps_crashing_bug.py",
            "fix_rcps_method_calls.py", 
            "investigate_rcps_issue.py",
            "minimal_toolbar_test.py",
            "quick_crashing_test.py",
            "quick_debug_rcps_crashing.py",
            "quick_start_phase1.py", 
            "quick_test.py",
            "rcps_fix_summary.py",
            "rcps_issue_analysis.py",
            "simple_duration_analysis.py",
            "simple_ef_test.py",
            "simple_export_test.py",
            "simple_method_test.py",
        ],
        
        "EXTENSIVE_TESTS": [
            # Extensive test files created during development
            "test_actual_start_export_fix.py",
            "test_analyzer_access_final.py", 
            "test_cost_flow.py",
            "test_cost_format.py",
            "test_crashing_analyzer_fix.py",
            "test_crashing_duration.py",
            "test_crashing_logic.py", 
            "test_crashing_validation.py",
            "test_crashing_validation_sim.py",
            "test_direct_method.py",
            "test_duration_calculation.py",
            "test_ef_attributes_direct.py",
            "test_ef_attributes_final.py",
            "test_ef_duration_logic.py",
            "test_ef_verification.py",
            "test_enhanced_challenging.py",
            "test_enhanced_chart.py",
            "test_enhanced_costs.py",
            "test_fullscreen_feature.py",
            "test_fullscreen_fix.py",
            "test_phase1_foundation_methods.py",
            "test_phase3_intelligent_optimization.py",
            "test_prepare_crashing_dataframe.py",
            "test_rcps_actual_start_fix.py",
            "test_rcps_actual_start_fix_new.py",
            "test_rcps_bypass_instructions.py",
            "test_rcps_cost_tracking.py",
            "test_rcps_crashing_bug.py",
            "test_rcps_crashing_data_fix.py",
            "test_rcps_crashing_debugging.py",
            "test_rcps_crashing_direct.py",
            "test_rcps_crashing_fix_validation.py",
            "test_rcps_crashing_integration.py",
            "test_rcps_crashing_simple.py",
            "test_rcps_data_creation.py",
            "test_rcps_debug.py",
            "test_rcps_debug_output_fix.py",
            "test_rcps_duration_fix.py",
            "test_rcps_error_fix_validation.py",
            "test_rcps_fix.py",
            "test_rcps_fix_simple.py",
            "test_rcps_fullscreen_integration.py", 
            "test_rcps_graph_direct.py",
            "test_rcps_graph_fixed.py",
            "test_rcps_hybrid.py",
            "test_rcps_methods_simple.py",
            "test_rcps_network_graph_fix.py",
            "test_rcps_network_simple.py",
            "test_rcps_network_simple_new.py",
            "test_rcps_recalculated_scheduling.py",
            "test_rcps_table_access.py",
            "test_rcps_table_integration.py",
            "test_rcps_workflow.py",
            "test_realistic_target.py",
            "test_simple_rcps_fix.py",
            "test_table_sizing.py",
            "test_toolbar_fix.py",
            "test_toolbar_functionality.py",
            "test_updated_layout.py", 
            "test_with_selection.py",
            "verify_export_fix.py",
            "verify_phase1_integration.py",
            "validate_toolbar_fix.py",
        ],
        
        "DOCUMENTATION_MD": [
            # Markdown documentation files - some can be archived
            "COMPREHENSIVE_CRASHING_COMPARISON.md",
            "crashing_new_window_feature.md",
            "DETAILED_CODE_COMPARISON.md", 
            "EXECUTION_FLOW_COMPARISON.md",
            "FULLSCREEN_BUTTON_FIX.md",
            "FULLSCREEN_COMPARISON_FEATURE.md",
            "FULLSCREEN_GANTT_COMPARISON_GUIDE.md", 
            "FULL_EXECUTION_PLAN.md",
            "GANTT_DEBUGGING_CLEANUP_SUMMARY.md",
            "NORMAL_CRASHING_FIX_SUMMARY.md",
            "PHASE1_CHECKLIST.md",
            "PHASE1_CHECKLIST_COMPLETED.md",
            "PHASE1_COMPLETION_SUMMARY.md",
            "PHASE2_IMPLEMENTATION_COMPLETION_SUMMARY.md",
            "PHASE2_IMPLEMENTATION_PLAN.md", 
            "PYTHON_SYNTAX_ERRORS_FIX_SUMMARY.md",
            "RCPS_ACTUAL_START_EXPORT_FIX_SUMMARY.md",
            "RCPS_CRASHING_ACTUAL_START_FIX.md",
            "RCPS_CRASHING_ANALYZER_ACCESS_FIX.md",
            "RCPS_CRASHING_DATA_FIX_EXECUTION_PLAN.md",
            "RCPS_CRASHING_DATA_FIX_SUMMARY.md",
            "RCPS_CRASHING_DATA_SOURCE_FIX.md",
            "RCPS_CRASHING_DEBUGGING_IMPLEMENTATION.md",
            "RCPS_CRASHING_FIX_RESULTS_LOG.md",
            "RCPS_CRASHING_IMPROVEMENT_PLAN.md",
            "RCPS_CRASHING_RESULTS_ENHANCEMENT_SUMMARY.md",
            "RCPS_DATA_TRANSFER_PROCESS_EXPLANATION.md",
            "RCPS_DEBUGGING_CLEANUP_SUMMARY.md", 
            "RCPS_EXECUTION_SUMMARY_SUCCESS.md",
            "RCPS_FULLSCREEN_FEATURE_SUMMARY.md",
            "RCPS_IMMEDIATE_ACTION_PLAN.md",
            "RCPS_IMPROVEMENT_SUMMARY_20250825_182402.md",
            "RCPS_NETWORK_GRAPH_ERROR_FIX_SUMMARY.md",
            "TOOLBAR_FIX_SUMMARY.md",
            "TOOLBAR_INVESTIGATION_REPORT.md",
        ],
        
        "LOG_FILES": [
            # Log files - can be archived
            "rcps_improvement_log_20250825_182357.txt", 
            "rcps_improvement_log_20250827_183000.txt",
        ],
        
        "SYSTEM_FILES": [
            # System files to keep
            ".git/",
            ".vscode/", 
            "__pycache__/",
            "New folder/",
            "extensions/",
            "code/",
        ]
    }
    
    return categories

def create_archive_structure():
    """Create archive directory structure"""
    base_archive = "archive"
    archive_dirs = [
        f"{base_archive}/development_history",
        f"{base_archive}/debug_scripts", 
        f"{base_archive}/test_files",
        f"{base_archive}/documentation",
        f"{base_archive}/cleanup_scripts",
        f"{base_archive}/logs",
        "future_development"
    ]
    
    for dir_path in archive_dirs:
        os.makedirs(dir_path, exist_ok=True)
    
    return archive_dirs

def generate_cleanup_report():
    """Generate detailed cleanup report"""
    categories = organize_workspace()
    
    report = []
    report.append("# 🧹 PMHelper Production Cleanup Report")
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    report.append("## 📂 File Organization Plan")
    report.append("")
    
    # Count files in each category
    for category, files in categories.items():
        existing_files = [f for f in files if os.path.exists(f)]
        report.append(f"### {category.replace('_', ' ').title()}")
        report.append(f"**Files:** {len(existing_files)} items")
        report.append("")
        
        if category == "ESSENTIAL_PRODUCTION":
            report.append("✅ **KEEP** - Core production files")
            report.append("- These files are essential for the application to run")
            report.append("- Should remain in the root directory")
        elif category == "FUTURE_DEVELOPMENT": 
            report.append("📦 **ARCHIVE to future_development/** - Save for later")
            report.append("- Key enhancement scripts and documentation")
            report.append("- May be needed for future feature development")
        elif category == "CLEANUP_SCRIPTS":
            report.append("🗂️ **ARCHIVE to archive/cleanup_scripts/** - Completed tools")
            report.append("- One-time cleanup scripts that have served their purpose")
        elif category == "DEBUG_ANALYSIS":
            report.append("🗑️ **REMOVE** - Development debug files")
            report.append("- Debug scripts no longer needed")
        elif category == "EXTENSIVE_TESTS":
            report.append("🗂️ **ARCHIVE to archive/test_files/** - Development tests")
            report.append("- Extensive test files created during development")
        elif category == "DOCUMENTATION_MD":
            report.append("🗂️ **ARCHIVE to archive/documentation/** - Dev docs")
            report.append("- Development documentation and summaries")
        elif category == "LOG_FILES":
            report.append("🗂️ **ARCHIVE to archive/logs/** - Historical logs")
        elif category == "SYSTEM_FILES":
            report.append("✅ **KEEP** - System files and folders")
        
        report.append("")
        
        # List first few files as examples
        for i, file in enumerate(existing_files[:5]):
            report.append(f"- {file}")
        if len(existing_files) > 5:
            report.append(f"- ... and {len(existing_files) - 5} more")
        report.append("")
    
    # Summary statistics
    total_files = sum(len([f for f in files if os.path.exists(f)]) for files in categories.values())
    keep_files = len([f for f in categories["ESSENTIAL_PRODUCTION"] + categories["SYSTEM_FILES"] if os.path.exists(f)])
    archive_files = len([f for f in categories["FUTURE_DEVELOPMENT"] + categories["CLEANUP_SCRIPTS"] + 
                        categories["EXTENSIVE_TESTS"] + categories["DOCUMENTATION_MD"] + categories["LOG_FILES"] if os.path.exists(f)])
    remove_files = len([f for f in categories["DEBUG_ANALYSIS"] if os.path.exists(f)])
    
    report.append("## 📊 Cleanup Summary")
    report.append("")
    report.append(f"- **Total Files Analyzed:** {total_files}")
    report.append(f"- **Keep in Production:** {keep_files} files")
    report.append(f"- **Archive for Future:** {archive_files} files")  
    report.append(f"- **Remove (Debug/Temp):** {remove_files} files")
    report.append("")
    
    report.append("## 🎯 Recommended Actions")
    report.append("")
    report.append("1. **Create archive structure** - Set up organized folders")
    report.append("2. **Move future development files** - Preserve important scripts")
    report.append("3. **Archive documentation** - Keep development history") 
    report.append("4. **Remove debug files** - Clean up temporary scripts")
    report.append("5. **Test production build** - Verify everything still works")
    report.append("")
    
    report.append("## 🚀 Post-Cleanup Structure")
    report.append("")
    report.append("```")
    report.append("PMhelper/")
    report.append("├── launch_app.py           # Main application")
    report.append("├── src/                    # Source code")
    report.append("├── assets/                 # Application assets")
    report.append("├── config/                 # Configuration files")
    report.append("├── docs/                   # User documentation")
    report.append("├── tests/                  # Core test suite")
    report.append("├── scripts/                # Utility scripts")
    report.append("├── templates/              # Template files")
    report.append("├── README.md               # Project documentation")
    report.append("├── future_development/     # Scripts for future enhancements")
    report.append("└── archive/               # Development history")
    report.append("    ├── cleanup_scripts/   # One-time cleanup tools")
    report.append("    ├── test_files/        # Development test files")
    report.append("    ├── documentation/     # Development docs")
    report.append("    └── logs/              # Historical logs")
    report.append("```")
    
    return "\\n".join(report)

def main():
    """Generate cleanup report"""
    print("🧹 Analyzing PMHelper workspace for cleanup...")
    print("=" * 60)
    
    # Generate comprehensive report
    report_content = generate_cleanup_report()
    
    # Save report
    with open("CLEANUP_PLAN.md", "w", encoding="utf-8") as f:
        f.write(report_content)
    
    print("✅ Cleanup plan generated: CLEANUP_PLAN.md")
    print("📋 Review the plan before executing cleanup actions")
    print("=" * 60)

if __name__ == "__main__":
    main()