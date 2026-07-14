"""
Final comprehensive test - Run all tests together
"""
import subprocess
import sys

print('='*70)
print('FINAL COMPREHENSIVE TEST SUITE')
print('='*70)

tests = [
    ('Structure Validation', 'manual_tests/test_examples_comprehensive.py'),
    ('Edge Cases', 'manual_tests/test_edge_cases.py'),
    ('GUI Integration', 'manual_tests/test_gui_integration.py'),
    ('Original Tests', 'manual_tests/test_examples.py'),
]

results = []

for test_name, script in tests:
    print(f'\n{"="*70}')
    print(f'Running: {test_name}')
    print(f'{"="*70}')
    
    try:
        result = subprocess.run(
            [sys.executable, script],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        success = result.returncode == 0
        results.append((test_name, success))
        
        if success:
            print(f'[PASS] {test_name}')
        else:
            print(f'[FAIL] {test_name}')
            print(f'Error output:\n{result.stderr[:500]}')
            
    except subprocess.TimeoutExpired:
        print(f'[FAIL] {test_name} - Timeout')
        results.append((test_name, False))
    except Exception as e:
        print(f'[FAIL] {test_name} - {e}')
        results.append((test_name, False))

print(f'\n{"="*70}')
print('FINAL TEST SUMMARY')
print(f'{"="*70}')

for test_name, success in results:
    status = '[PASS]' if success else '[FAIL]'
    print(f'{test_name:40s} {status}')

passed = sum(1 for _, s in results if s)
total = len(results)
print(f'\nOverall: {passed}/{total} test suites passed')

if passed == total:
    print('\n[SUCCESS] ALL TESTS PASSED - FEATURE READY FOR PRODUCTION')
else:
    print(f'\n[FAILURE] {total - passed} TEST SUITE(S) FAILED')
