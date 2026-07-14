"""
GUI Integration Test - Simulates user loading examples
"""
import sys
from pathlib import Path
sys.path.insert(0, 'src')

print('='*70)
print('TEST 5: GUI Integration Simulation')
print('='*70)
print('\nThis test simulates loading examples without launching full GUI')
print('Tests the example loading logic flow\n')

from pmhelper.utils.selection_io import SelectionFileHandler
from pmhelper.core.models import SelectionMethod

# Simulate the load_example function logic
def simulate_load_example(filename):
    """Simulate loading an example as the GUI would"""
    print(f'\nTesting: {filename}')
    try:
        # Simulate GUI loading
        examples_dir = Path('assets/examples')
        example_path = examples_dir / filename
        
        if not example_path.exists():
            print(f'  [FAIL] File not found')
            return False
        
        # Load problem
        problem = SelectionFileHandler.load(str(example_path))
        print(f'  [OK] Loaded: {problem.name}')
        
        # Check metadata
        if hasattr(problem, 'metadata') and problem.metadata:
            if 'expected_results' in problem.metadata:
                print(f'  [OK] Has expected results')
            else:
                print(f'  [WARN] No expected results in metadata')
        
        # Determine method and simulate tab-specific loading
        method = problem.method if isinstance(problem.method, str) else problem.method.value
        
        if method in ["ahp", SelectionMethod.AHP]:
            return simulate_load_ahp(problem)
        elif method in ["linear_scoring", SelectionMethod.LINEAR_SCORING]:
            return simulate_load_linear_scoring(problem)
        elif method in ["benefit_cost", SelectionMethod.BENEFIT_COST]:
            return simulate_load_bc(problem)
        elif method in ["portfolio", SelectionMethod.PORTFOLIO]:
            return simulate_load_portfolio(problem)
        
    except Exception as e:
        print(f'  [FAIL] {type(e).__name__}: {e}')
        import traceback
        traceback.print_exc()
        return False

def simulate_load_ahp(problem):
    """Simulate load_ahp_example logic"""
    try:
        print(f'  -> Loading AHP data...')
        
        # Check criteria
        if not problem.criteria:
            print(f'     [FAIL] No criteria')
            return False
        print(f'     [OK] {len(problem.criteria)} criteria')
        
        # Check matrix
        if not problem.ahp_matrix:
            print(f'     [FAIL] No AHP matrix')
            return False
        
        if not problem.ahp_matrix.matrix:
            print(f'     [FAIL] No matrix array')
            return False
        
        matrix = problem.ahp_matrix.matrix
        n = len(matrix)
        print(f'     [OK] Matrix {n}x{n}')
        
        # Simulate loading matrix values into GUI
        values_loaded = 0
        for i in range(n):
            for j in range(i + 1, n):
                if matrix[i][j] != 0 and matrix[i][j] != 1:
                    values_loaded += 1
        print(f'     [OK] {values_loaded} comparison values to load')
        
        # Check alternatives
        if problem.alternatives:
            print(f'     [OK] {len(problem.alternatives)} alternatives')
        else:
            print(f'     [INFO] No alternatives (optional)')
        
        return True
        
    except Exception as e:
        print(f'     [FAIL] {type(e).__name__}: {e}')
        return False

def simulate_load_linear_scoring(problem):
    """Simulate load_linear_scoring_example logic"""
    try:
        print(f'  -> Loading Linear Scoring data...')
        
        # Check criteria
        if not problem.criteria:
            print(f'     [FAIL] No criteria')
            return False
        print(f'     [OK] {len(problem.criteria)} criteria')
        
        # Check weights
        weight_sum = sum(c.weight for c in problem.criteria)
        if abs(weight_sum - 1.0) > 0.001:
            print(f'     [FAIL] Weights sum to {weight_sum}, not 1.0')
            return False
        print(f'     [OK] Weights sum to 1.0')
        
        # Check alternatives
        if not problem.alternatives:
            print(f'     [FAIL] No alternatives')
            return False
        print(f'     [OK] {len(problem.alternatives)} alternatives')
        
        # Check scores
        for alt in problem.alternatives:
            if not alt.scores:
                print(f'     [FAIL] Alternative {alt.name} has no scores')
                return False
            missing_criteria = set(c.name for c in problem.criteria) - set(alt.scores.keys())
            if missing_criteria:
                print(f'     [FAIL] Alternative {alt.name} missing scores for: {missing_criteria}')
                return False
        print(f'     [OK] All alternatives have complete scores')
        
        return True
        
    except Exception as e:
        print(f'     [FAIL] {type(e).__name__}: {e}')
        return False

def simulate_load_bc(problem):
    """Simulate load_bc_example logic"""
    try:
        print(f'  -> Loading B/C data...')
        
        # Check MARR
        if problem.marr is None:
            print(f'     [FAIL] No MARR specified')
            return False
        print(f'     [OK] MARR: {problem.marr * 100}%')
        
        # Check projects
        if not problem.projects:
            print(f'     [FAIL] No projects')
            return False
        print(f'     [OK] {len(problem.projects)} projects')
        
        # Check project attributes
        for proj in problem.projects:
            if not hasattr(proj, 'cost') and not hasattr(proj, 'initial_cost'):
                print(f'     [FAIL] Project {proj.name} missing cost')
                return False
            if not hasattr(proj, 'benefit'):
                print(f'     [FAIL] Project {proj.name} missing benefit')
                return False
        print(f'     [OK] All projects have required attributes')
        
        return True
        
    except Exception as e:
        print(f'     [FAIL] {type(e).__name__}: {e}')
        return False

def simulate_load_portfolio(problem):
    """Simulate load_portfolio_example logic"""
    try:
        print(f'  -> Loading Portfolio data...')
        
        # Check budget
        if problem.budget is None:
            print(f'     [FAIL] No budget specified')
            return False
        print(f'     [OK] Budget: ${problem.budget:,.0f}')
        
        # Check projects
        if not problem.projects:
            print(f'     [FAIL] No projects')
            return False
        print(f'     [OK] {len(problem.projects)} projects')
        
        # Check constraints
        if problem.constraints:
            print(f'     [OK] {len(problem.constraints)} constraints')
            
            # Validate constraint types
            valid_types = ['mutually_exclusive', 'dependency', 'resource']
            for constraint in problem.constraints:
                if constraint.type not in valid_types:
                    print(f'     [FAIL] Invalid constraint type: {constraint.type}')
                    return False
            print(f'     [OK] All constraints have valid types')
        else:
            print(f'     [INFO] No constraints (optional)')
        
        return True
        
    except Exception as e:
        print(f'     [FAIL] {type(e).__name__}: {e}')
        return False

# Run tests on all examples
examples = [
    'ahp_software_selection.pmsel',
    'ahp_simple_3criteria.pmsel',
    'linear_scoring_vendor.pmsel',
    'bc_infrastructure.pmsel',
    'portfolio_rd_projects.pmsel'
]

results = []
for example in examples:
    success = simulate_load_example(example)
    results.append((example, success))

print('\n' + '='*70)
print('TEST 5 SUMMARY')
print('='*70)
for filename, success in results:
    status = '[PASS]' if success else '[FAIL]'
    print(f'{filename:40s} {status}')

passed = sum(1 for _, s in results if s)
total = len(results)
print(f'\nResult: {passed}/{total} examples can be loaded successfully')

if passed == total:
    print('\n[SUCCESS] All examples ready for GUI loading!')
else:
    print(f'\n[WARNING] {total - passed} example(s) have issues')
