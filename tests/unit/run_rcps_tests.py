#!/usr/bin/env python3
"""
RCPS Test Runner
Executes all RCPS-related tests with proper reporting
"""

import unittest
import sys
from pathlib import Path
import time

def run_rcps_tests():
    """Run all RCPS tests with detailed reporting"""
    print("RCPS Test Suite Execution")
    print("=" * 50)
    
    # Discover and run tests
    test_dir = Path(__file__).parent
    loader = unittest.TestLoader()
    
    # Load specific test modules
    test_modules = [
        'test_rcps_algorithms'
    ]
    
    suite = unittest.TestSuite()
    
    for module_name in test_modules:
        try:
            tests = loader.loadTestsFromName(module_name)
            suite.addTests(tests)
            print(f"Loaded tests from {module_name}")
        except Exception as e:
            print(f"Failed to load {module_name}: {e}")
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(
        verbosity=2,
        stream=sys.stdout,
        failfast=False
    )
    
    start_time = time.time()
    result = runner.run(suite)
    end_time = time.time()
    
    # Summary report
    print("\\n" + "=" * 50)
    print("Test Summary Report")
    print("=" * 50)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%" if result.testsRun > 0 else "N/A")
    print(f"Execution time: {end_time - start_time:.2f} seconds")
    
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_rcps_tests()
    sys.exit(0 if success else 1)
