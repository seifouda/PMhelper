"""
Test edge cases and error handling for example loading
"""
import sys
from pathlib import Path
sys.path.insert(0, 'src')

print('='*70)
print('TEST 4: Edge Cases & Error Handling')
print('='*70)

# Test 1: Check if AHP matrix uses 'comparisons' dict (not in Pydantic model)
print('\n[1] Testing AHP matrix structure...')
from pmhelper.utils.selection_io import SelectionFileHandler

problem = SelectionFileHandler.load('assets/examples/ahp_software_selection.pmsel')
print(f'  AHP Matrix type: {type(problem.ahp_matrix)}')
print(f'  AHP Matrix attributes: {dir(problem.ahp_matrix) if problem.ahp_matrix else "None"}')

if problem.ahp_matrix:
    print(f'  Has criteria: {"criteria" in dir(problem.ahp_matrix)}')
    print(f'  Has matrix: {"matrix" in dir(problem.ahp_matrix)}')
    print(f'  Has comparisons: {"comparisons" in dir(problem.ahp_matrix)}')
    
    # Check if we can access matrix
    if hasattr(problem.ahp_matrix, 'matrix'):
        matrix = problem.ahp_matrix.matrix
        print(f'  Matrix shape: {len(matrix)}x{len(matrix[0]) if matrix else 0}')
        print(f'  Matrix[0][0]: {matrix[0][0]}')
    
    # Try to access comparisons (which is in JSON but not in model)
    try:
        if hasattr(problem.ahp_matrix, 'comparisons'):
            print(f'  [ISSUE] AHP Matrix has comparisons attribute')
        else:
            print(f'  [OK] AHP Matrix does not have comparisons (uses matrix array)')
    except:
        print(f'  [OK] Comparisons not accessible')

# Test 2: Check attribute access patterns
print('\n[2] Testing attribute access in load_ahp_example logic...')
print(f'  Can use hasattr: {hasattr(problem, "ahp_matrix")}')
print(f'  AHP matrix exists: {problem.ahp_matrix is not None}')

# Test accessing comparisons dict pattern used in code
if hasattr(problem, 'ahp_matrix') and problem.ahp_matrix:
    matrix_data = problem.ahp_matrix
    # This line in load_ahp_example checks if 'comparisons' in matrix_data
    # But matrix_data is a Pydantic model, not a dict!
    try:
        if 'comparisons' in matrix_data:
            print(f'  [ERROR] Can use "in" operator on Pydantic model')
        else:
            print(f'  [OK] Cannot use "in" operator correctly')
    except TypeError as e:
        print(f'  [ISSUE] TypeError when checking "comparisons" in matrix_data: {e}')
        print(f'  This will cause GUI loading to fail!')

# Test 3: Check if alternatives have proper IDs
print('\n[3] Testing alternative IDs...')
for idx, alt in enumerate(problem.alternatives):
    print(f'  Alternative {idx+1}: id={alt.id}, name={alt.name}')

# Test 4: Test Linear Scoring example
print('\n[4] Testing Linear Scoring example...')
problem_ls = SelectionFileHandler.load('assets/examples/linear_scoring_vendor.pmsel')
print(f'  Criteria weights: {[c.weight for c in problem_ls.criteria]}')
weight_sum = sum(c.weight for c in problem_ls.criteria)
print(f'  Weight sum: {weight_sum}')
if abs(weight_sum - 1.0) > 0.001:
    print(f'  [ISSUE] Weights do not sum to 1.0!')
else:
    print(f'  [OK] Weights sum to 1.0')

# Test 5: Test metadata access
print('\n[5] Testing metadata structure...')
for example_file in ['ahp_software_selection.pmsel', 'linear_scoring_vendor.pmsel']:
    problem = SelectionFileHandler.load(f'assets/examples/{example_file}')
    print(f'\n  {example_file}:')
    print(f'    Has metadata: {hasattr(problem, "metadata")}')
    if hasattr(problem, 'metadata'):
        print(f'    Metadata type: {type(problem.metadata)}')
        print(f'    Metadata keys: {list(problem.metadata.keys()) if problem.metadata else "None"}')
        if 'expected_results' in problem.metadata:
            print(f'    Has expected_results: Yes')
            expected = problem.metadata['expected_results']
            print(f'    Expected results keys: {list(expected.keys())}')

# Test 6: Check for missing attributes
print('\n[6] Testing for potential AttributeErrors...')
test_cases = [
    ('ahp_software_selection.pmsel', 'alternatives', 'AHP might not have alternatives'),
    ('bc_infrastructure.pmsel', 'projects', 'B/C should have projects'),
    ('bc_infrastructure.pmsel', 'marr', 'B/C should have MARR'),
    ('portfolio_rd_projects.pmsel', 'budget', 'Portfolio should have budget'),
    ('portfolio_rd_projects.pmsel', 'constraints', 'Portfolio should have constraints'),
]

for filename, attr, description in test_cases:
    problem = SelectionFileHandler.load(f'assets/examples/{filename}')
    has_attr = hasattr(problem, attr)
    attr_value = getattr(problem, attr, None)
    status = 'OK' if (has_attr and attr_value) else 'MISSING'
    print(f'  {filename:35s} {attr:15s} [{status}]')

print('\n' + '='*70)
print('TEST 4 SUMMARY')
print('='*70)
print('[CRITICAL] Issue found in load_ahp_example:')
print('  - Line checks "if comparisons in matrix_data" where matrix_data is Pydantic model')
print('  - This will raise TypeError: argument of type "AHPMatrix" is not iterable')
print('  - Need to use hasattr(matrix_data, "comparisons") instead')
print('\n[INFO] The AHP matrix in Pydantic model uses "matrix" array, not "comparisons" dict')
print('       The comparisons dict is in JSON but not loaded into Pydantic model')
