"""
Project Selection Module - Core Algorithms

This module implements four project selection methods:
1. Analytic Hierarchy Process (AHP)
2. Linear Scoring Rule
3. Benefit-to-Cost (B/C) Analysis
4. Portfolio Optimization

Author: PMHelper Team
Version: 1.0.0
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Optional, Tuple
from enum import Enum
import warnings


class CriterionDirection(str, Enum):
    """Direction for criterion optimization"""
    MAXIMIZE = "maximize"
    MINIMIZE = "minimize"


class AHPAnalyzer:
    """
    Analytic Hierarchy Process (AHP) for multi-criteria decision making.
    
    Uses pairwise comparisons on a 1-9 scale to determine criterion weights
    and rank alternatives.
    """
    
    # Random Index (RI) values for consistency checking
    RI_TABLE = {
        1: 0.00, 2: 0.00, 3: 0.58, 4: 0.90, 5: 1.12,
        6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49
    }
    
    def __init__(self, criteria: List[str]):
        """
        Initialize AHP analyzer with criteria list.
        
        Args:
            criteria: List of criterion names
        """
        self.criteria = criteria
        self.n = len(criteria)
        self.matrix = np.ones((self.n, self.n))
        self._criterion_index = {name: i for i, name in enumerate(criteria)}
    
    def set_comparison(self, criterion_i: str, criterion_j: str, value: float):
        """
        Set pairwise comparison value (1-9 scale).
        
        Args:
            criterion_i: First criterion name
            criterion_j: Second criterion name
            value: Comparison value (1-9), where:
                   1 = Equal importance
                   3 = Moderate importance
                   5 = Strong importance
                   7 = Very strong importance
                   9 = Extreme importance
                   
        Raises:
            ValueError: If value not in valid range [1/9, 9]
            KeyError: If criterion names not found
        """
        if value < 1/9 or value > 9:
            raise ValueError(f"Comparison value must be in range [1/9, 9], got {value}")
        
        if criterion_i not in self._criterion_index:
            raise KeyError(f"Criterion '{criterion_i}' not found")
        if criterion_j not in self._criterion_index:
            raise KeyError(f"Criterion '{criterion_j}' not found")
        
        i = self._criterion_index[criterion_i]
        j = self._criterion_index[criterion_j]
        
        # Set value and reciprocal
        self.matrix[i, j] = value
        self.matrix[j, i] = 1 / value
    
    def calculate_weights(self) -> np.ndarray:
        """
        Calculate normalized weights using column normalization method.
        
        Returns:
            Array of normalized weights (sum = 1.0)
        """
        # Normalize each column
        col_sums = self.matrix.sum(axis=0)
        normalized_matrix = self.matrix / col_sums
        
        # Average each row to get weights
        weights = normalized_matrix.mean(axis=1)
        
        return weights
    
    def calculate_consistency_ratio(self) -> float:
        """
        Calculate Consistency Ratio (CR) using eigenvalue method.
        
        CR < 0.1 is considered acceptable.
        
        Returns:
            Consistency ratio value
        """
        if self.n <= 2:
            return 0.0  # CR not applicable for n <= 2
        
        # Calculate λ_max using eigenvalue decomposition
        eigenvalues = np.linalg.eigvals(self.matrix)
        lambda_max = np.max(np.real(eigenvalues))
        
        # Calculate Consistency Index (CI)
        ci = (lambda_max - self.n) / (self.n - 1)
        
        # Get Random Index (RI) from table
        ri = self.RI_TABLE.get(self.n, 1.49)
        
        # Calculate Consistency Ratio (CR)
        cr = ci / ri if ri > 0 else 0.0
        
        return cr
    
    def calculate_geometric_mean(self, matrices: List[np.ndarray]) -> np.ndarray:
        """
        Combine multiple decision makers' matrices using geometric mean.
        
        Args:
            matrices: List of comparison matrices from different decision makers
            
        Returns:
            Aggregated matrix using geometric mean
            
        Raises:
            ValueError: If matrices have different dimensions
        """
        if not matrices:
            raise ValueError("At least one matrix required")
        
        # Validate all matrices have same dimension
        expected_shape = (self.n, self.n)
        for idx, mat in enumerate(matrices):
            if mat.shape != expected_shape:
                raise ValueError(
                    f"Matrix {idx} has shape {mat.shape}, expected {expected_shape}"
                )
        
        # Stack matrices and calculate geometric mean
        stacked = np.stack(matrices)
        geometric_mean = np.exp(np.log(stacked).mean(axis=0))
        
        return geometric_mean
    
    def rank_alternatives(
        self, 
        alternative_scores: Dict[str, Dict[str, float]]
    ) -> pd.DataFrame:
        """
        Calculate final scores for alternatives using AHP weights.
        
        Args:
            alternative_scores: Dictionary mapping alternative names to 
                               criterion scores. Format:
                               {
                                   'Alternative A': {'Criterion 1': 0.8, ...},
                                   'Alternative B': {'Criterion 1': 0.6, ...}
                               }
        
        Returns:
            DataFrame with alternatives ranked by total score
        """
        weights = self.calculate_weights()
        
        results = []
        for alt_name, scores in alternative_scores.items():
            total_score = 0.0
            for criterion, weight in zip(self.criteria, weights):
                if criterion not in scores:
                    raise KeyError(
                        f"Alternative '{alt_name}' missing score for '{criterion}'"
                    )
                total_score += scores[criterion] * weight
            
            results.append({
                'Alternative': alt_name,
                'Total Score': total_score,
                **{f'{criterion} Weight': w for criterion, w in zip(self.criteria, weights)}
            })
        
        df = pd.DataFrame(results)
        df = df.sort_values('Total Score', ascending=False).reset_index(drop=True)
        df.insert(0, 'Rank', range(1, len(df) + 1))
        
        return df


class LinearScoringAnalyzer:
    """
    Linear Scoring Rule for multi-criteria decision analysis.
    
    Normalizes criterion values to 1-9 scale and applies weighted scoring.
    """
    
    def __init__(self, criteria: List[str], directions: Dict[str, CriterionDirection]):
        """
        Initialize Linear Scoring analyzer.
        
        Args:
            criteria: List of criterion names
            directions: Dictionary mapping criterion to optimization direction
                       (MAXIMIZE or MINIMIZE)
        """
        self.criteria = criteria
        self.directions = directions
        
        # Validate all criteria have directions
        for criterion in criteria:
            if criterion not in directions:
                raise ValueError(f"Missing direction for criterion '{criterion}'")
    
    def normalize_criterion(
        self, 
        values: List[float], 
        direction: CriterionDirection
    ) -> np.ndarray:
        """
        Normalize criterion values to 1-9 scale.
        
        Args:
            values: List of criterion values
            direction: MAXIMIZE or MINIMIZE
            
        Returns:
            Array of normalized scores (1-9 scale)
        """
        values = np.array(values)
        
        # Handle edge case: all values are the same
        if np.all(values == values[0]):
            return np.full_like(values, 5.0, dtype=float)
        
        x_min = values.min()
        x_max = values.max()
        
        if direction == CriterionDirection.MAXIMIZE:
            # Higher is better: S = 1 + ((X - X_min) / (X_max - X_min)) * 8
            normalized = 1 + ((values - x_min) / (x_max - x_min)) * 8
        else:  # MINIMIZE
            # Lower is better: S = 9 - ((X - X_min) / (X_max - X_min)) * 8
            normalized = 9 - ((values - x_min) / (x_max - x_min)) * 8
        
        return normalized
    
    def calculate_scores(
        self, 
        alternatives: pd.DataFrame, 
        weights: Dict[str, float]
    ) -> pd.DataFrame:
        """
        Calculate weighted scores for all alternatives.
        
        Args:
            alternatives: DataFrame with alternatives as rows, criteria as columns
            weights: Dictionary mapping criterion to weight (must sum to 1.0)
            
        Returns:
            DataFrame with normalized scores and total weighted score
            
        Raises:
            ValueError: If weights don't sum to approximately 1.0
        """
        # Validate weights sum to 1.0
        weight_sum = sum(weights.values())
        if not np.isclose(weight_sum, 1.0, atol=1e-6):
            raise ValueError(
                f"Weights must sum to 1.0, got {weight_sum:.6f}"
            )
        
        # Validate all criteria have weights
        for criterion in self.criteria:
            if criterion not in weights:
                raise ValueError(f"Missing weight for criterion '{criterion}'")
        
        results = alternatives.copy()
        
        # Normalize each criterion
        for criterion in self.criteria:
            if criterion not in alternatives.columns:
                raise ValueError(f"Criterion '{criterion}' not found in alternatives")
            
            direction = self.directions[criterion]
            normalized = self.normalize_criterion(
                alternatives[criterion].values, 
                direction
            )
            results[f'{criterion} (Normalized)'] = normalized
        
        # Calculate total weighted score
        total_scores = np.zeros(len(alternatives))
        for criterion in self.criteria:
            normalized_col = f'{criterion} (Normalized)'
            total_scores += results[normalized_col].values * weights[criterion]
        
        results['Total Score'] = total_scores
        
        # Sort by total score and add rank
        results = results.sort_values('Total Score', ascending=False).reset_index(drop=True)
        results.insert(0, 'Rank', range(1, len(results) + 1))
        
        return results
    
    def sensitivity_analysis(
        self, 
        alternatives: pd.DataFrame, 
        weights: Dict[str, float],
        weight_ranges: Dict[str, Tuple[float, float]]
    ) -> dict:
        """
        Analyze how rankings change with weight variations.
        
        Args:
            alternatives: DataFrame with alternatives data
            weights: Base weights for criteria
            weight_ranges: Dictionary mapping criterion to (min, max) weight range
            
        Returns:
            Dictionary with sensitivity analysis results
        """
        base_results = self.calculate_scores(alternatives, weights)
        base_ranking = base_results.set_index('Rank').index.tolist()
        
        sensitivity_results = {
            'base_ranking': base_ranking,
            'variations': {}
        }
        
        # Test each criterion variation
        for criterion, (min_weight, max_weight) in weight_ranges.items():
            if criterion not in self.criteria:
                warnings.warn(f"Criterion '{criterion}' not in criteria list, skipping")
                continue
            
            criterion_results = []
            
            # Test weight variations
            for test_weight in np.linspace(min_weight, max_weight, 11):
                # Adjust other weights proportionally
                adjusted_weights = weights.copy()
                base_weight = weights[criterion]
                difference = test_weight - base_weight
                
                # Redistribute difference among other criteria
                other_criteria = [c for c in self.criteria if c != criterion]
                total_other_weight = sum(weights[c] for c in other_criteria)
                
                if total_other_weight > 0:
                    for other_criterion in other_criteria:
                        adjusted_weights[other_criterion] -= (
                            difference * (weights[other_criterion] / total_other_weight)
                        )
                
                adjusted_weights[criterion] = test_weight
                
                # Calculate scores with adjusted weights
                try:
                    test_results = self.calculate_scores(alternatives, adjusted_weights)
                    test_ranking = test_results.set_index('Rank').index.tolist()
                    
                    criterion_results.append({
                        'weight': test_weight,
                        'ranking': test_ranking,
                        'rank_changed': test_ranking != base_ranking
                    })
                except ValueError:
                    # Skip if weights become invalid
                    continue
            
            sensitivity_results['variations'][criterion] = criterion_results
        
        return sensitivity_results


class BenefitCostAnalyzer:
    """
    Benefit-to-Cost (B/C) Analysis for project evaluation.
    
    Performs capital recovery calculations and incremental analysis for
    mutually exclusive projects.
    """
    
    def calculate_capital_recovery(
        self,
        initial_cost: float,
        salvage: float,
        marr: float,
        life: int
    ) -> float:
        """
        Calculate Capital Recovery (CR) using present worth factors.
        
        CR = (Initial Cost - Salvage * (P/F, i, n)) * (A/P, i, n)
        
        Args:
            initial_cost: Initial investment cost
            salvage: Salvage value at end of life
            marr: Minimum Attractive Rate of Return (as decimal, e.g., 0.12)
            life: Project life in years
            
        Returns:
            Annual capital recovery cost
            
        Raises:
            ValueError: If inputs are invalid
        """
        if initial_cost <= 0:
            raise ValueError("Initial cost must be positive")
        if life <= 0:
            raise ValueError("Project life must be positive")
        if marr < 0:
            raise ValueError("MARR must be non-negative")
        
        # Calculate (P/F, i, n) = 1 / (1 + i)^n
        pf_factor = 1 / ((1 + marr) ** life)
        
        # Calculate (A/P, i, n) = i * (1 + i)^n / ((1 + i)^n - 1)
        if marr == 0:
            ap_factor = 1 / life
        else:
            ap_factor = marr * ((1 + marr) ** life) / (((1 + marr) ** life) - 1)
        
        # CR = (Initial - Salvage * (P/F)) * (A/P)
        cr = (initial_cost - salvage * pf_factor) * ap_factor
        
        return cr
    
    def calculate_bc_ratio(
        self,
        annual_benefits: float,
        capital_recovery: float,
        annual_om: float = 0.0
    ) -> float:
        """
        Calculate Benefit-to-Cost ratio.
        
        B/C = Annual Benefits / (Capital Recovery + Annual O&M)
        
        Args:
            annual_benefits: Annual benefits
            capital_recovery: Annual capital recovery cost
            annual_om: Annual operations & maintenance cost
            
        Returns:
            B/C ratio
            
        Raises:
            ValueError: If denominator is zero or negative
        """
        denominator = capital_recovery + annual_om
        
        if denominator <= 0:
            raise ValueError("Total annual cost must be positive")
        
        if annual_benefits < 0:
            raise ValueError("Annual benefits must be non-negative")
        
        return annual_benefits / denominator
    
    def incremental_analysis(
        self,
        projects: pd.DataFrame,
        marr: float
    ) -> dict:
        """
        Perform incremental B/C analysis for mutually exclusive projects.
        
        Args:
            projects: DataFrame with columns:
                     - 'name': Project name
                     - 'initial_cost': Initial investment
                     - 'life': Project life (years)
                     - 'annual_benefits': Annual benefits
                     - 'annual_om': Annual O&M costs
                     - 'salvage': Salvage value
            marr: Minimum Attractive Rate of Return
            
        Returns:
            Dictionary with analysis results and optimal project
        """
        if projects.empty:
            raise ValueError("No projects provided")
        
        # Calculate B/C ratio for each project
        projects = projects.copy()
        projects['CR'] = projects.apply(
            lambda row: self.calculate_capital_recovery(
                row['initial_cost'],
                row.get('salvage', 0.0),
                marr,
                row['life']
            ),
            axis=1
        )
        
        projects['BC_Ratio'] = projects.apply(
            lambda row: self.calculate_bc_ratio(
                row['annual_benefits'],
                row['CR'],
                row.get('annual_om', 0.0)
            ),
            axis=1
        )
        
        # Sort by initial cost
        projects = projects.sort_values('initial_cost').reset_index(drop=True)
        
        # Filter projects with B/C >= 1.0
        viable_projects = projects[projects['BC_Ratio'] >= 1.0].copy()
        
        if viable_projects.empty:
            return {
                'optimal_project': None,
                'message': 'No projects have B/C ratio >= 1.0',
                'all_projects': projects
            }
        
        # Start with least cost viable project
        optimal_idx = 0
        comparisons = []
        
        # Perform incremental analysis
        for i in range(1, len(viable_projects)):
            current = viable_projects.iloc[optimal_idx]
            challenger = viable_projects.iloc[i]
            
            # Calculate incremental values
            delta_cost = challenger['initial_cost'] - current['initial_cost']
            delta_benefits = challenger['annual_benefits'] - current['annual_benefits']
            delta_om = challenger.get('annual_om', 0.0) - current.get('annual_om', 0.0)
            
            # Calculate incremental CR (simplified approach)
            delta_cr = challenger['CR'] - current['CR']
            
            # Incremental B/C ratio
            incremental_bc = delta_benefits / (delta_cr + delta_om) if (delta_cr + delta_om) > 0 else 0
            
            comparison = {
                'current': current['name'],
                'challenger': challenger['name'],
                'incremental_bc': incremental_bc,
                'decision': 'Accept challenger' if incremental_bc >= 1.0 else 'Keep current'
            }
            comparisons.append(comparison)
            
            # Update optimal if challenger is better
            if incremental_bc >= 1.0:
                optimal_idx = i
        
        optimal_project = viable_projects.iloc[optimal_idx]
        
        return {
            'optimal_project': optimal_project.to_dict(),
            'comparisons': comparisons,
            'all_projects': projects,
            'viable_projects': viable_projects
        }


class PortfolioOptimizer:
    """
    Portfolio Optimization using Integer Linear Programming.
    
    Selects optimal subset of projects subject to budget and other constraints.
    """
    
    def __init__(self, solver: str = 'pulp'):
        """
        Initialize portfolio optimizer.
        
        Args:
            solver: LP solver to use ('pulp' or 'cbc')
        """
        self.solver = solver
        self._check_dependencies()
    
    def _check_dependencies(self):
        """Check if required dependencies are installed."""
        try:
            import pulp
        except ImportError:
            raise ImportError(
                "PuLP package required for portfolio optimization. "
                "Install with: pip install pulp"
            )
    
    def optimize(
        self,
        projects: pd.DataFrame,
        budget: float,
        constraints: Optional[List[dict]] = None,
        time_limit: int = 60
    ) -> dict:
        """
        Optimize project portfolio to maximize benefits within budget.
        
        Args:
            projects: DataFrame with columns:
                     - 'name': Project name
                     - 'cost': Project cost
                     - 'benefit': Annual benefit
            budget: Total budget available
            constraints: Optional list of constraint dictionaries:
                        - {'type': 'mutually_exclusive', 'projects': ['A', 'B']}
                        - {'type': 'dependency', 'project': 'B', 'requires': 'A'}
                        - {'type': 'resource', 'demands': {...}, 'capacity': value}
            time_limit: Solver time limit in seconds
            
        Returns:
            Dictionary with optimization results
        """
        import pulp
        
        if projects.empty:
            raise ValueError("No projects provided")
        
        if budget <= 0:
            raise ValueError("Budget must be positive")
        
        # Create optimization problem
        prob = pulp.LpProblem("Portfolio_Optimization", pulp.LpMaximize)
        
        # Create binary decision variables for each project
        project_vars = {}
        for idx, row in projects.iterrows():
            var_name = f"x_{row['name'].replace(' ', '_')}"
            project_vars[row['name']] = pulp.LpVariable(var_name, cat='Binary')
        
        # Objective function: Maximize total benefits
        prob += pulp.lpSum(
            project_vars[row['name']] * row['benefit']
            for idx, row in projects.iterrows()
        ), "Total_Benefit"
        
        # Budget constraint
        prob += pulp.lpSum(
            project_vars[row['name']] * row['cost']
            for idx, row in projects.iterrows()
        ) <= budget, "Budget_Constraint"
        
        # Add custom constraints
        if constraints:
            for constraint in constraints:
                constraint_type = constraint.get('type')
                
                if constraint_type == 'mutually_exclusive':
                    # Sum of mutually exclusive projects <= 1
                    mutual_projects = constraint.get('projects', [])
                    prob += pulp.lpSum(
                        project_vars[p] for p in mutual_projects
                        if p in project_vars
                    ) <= 1, f"MutuallyExclusive_{len(prob.constraints)}"
                
                elif constraint_type == 'dependency':
                    # If project B selected, project A must be selected
                    project = constraint.get('project')
                    requires = constraint.get('requires')
                    if project in project_vars and requires in project_vars:
                        prob += (
                            project_vars[project] <= project_vars[requires]
                        ), f"Dependency_{project}_requires_{requires}"
                
                elif constraint_type == 'resource':
                    # Resource capacity constraint
                    demands = constraint.get('demands', {})
                    capacity = constraint.get('capacity')
                    prob += pulp.lpSum(
                        project_vars[p] * demands.get(p, 0)
                        for p in project_vars.keys()
                        if p in demands
                    ) <= capacity, f"Resource_{len(prob.constraints)}"
        
        # Solve the problem
        solver = pulp.PULP_CBC_CMD(msg=0, timeLimit=time_limit)
        prob.solve(solver)
        
        # Extract results
        status = pulp.LpStatus[prob.status]
        
        if status in ['Optimal', 'Not Solved']:
            selected_projects = [
                name for name, var in project_vars.items()
                if var.varValue and var.varValue > 0.5
            ]
            
            selected_data = projects[projects['name'].isin(selected_projects)]
            total_cost = selected_data['cost'].sum()
            total_benefit = selected_data['benefit'].sum()
            
            # Calculate shadow price of budget (marginal value of additional budget)
            shadow_price = None
            try:
                budget_constraint = prob.constraints.get('Budget_Constraint')
                if budget_constraint and hasattr(budget_constraint, 'pi'):
                    shadow_price = budget_constraint.pi
            except:
                pass
            
            return {
                'status': status,
                'selected_projects': selected_projects,
                'total_cost': total_cost,
                'total_benefit': total_benefit,
                'budget_utilization': (total_cost / budget) * 100,
                'objective_value': pulp.value(prob.objective),
                'shadow_price_budget': shadow_price,
                'selected_data': selected_data
            }
        else:
            return {
                'status': status,
                'message': 'Optimization failed or infeasible',
                'selected_projects': [],
                'total_cost': 0,
                'total_benefit': 0
            }
    
    def sensitivity_budget(
        self,
        projects: pd.DataFrame,
        base_budget: float,
        budget_range: Tuple[float, float],
        steps: int = 10,
        constraints: Optional[List[dict]] = None
    ) -> pd.DataFrame:
        """
        Perform budget sensitivity analysis.
        
        Args:
            projects: Projects DataFrame
            base_budget: Base budget value
            budget_range: (min_budget, max_budget) range to test
            steps: Number of budget points to test
            constraints: Optional constraints
            
        Returns:
            DataFrame with budget sensitivity results
        """
        min_budget, max_budget = budget_range
        budget_values = np.linspace(min_budget, max_budget, steps)
        
        results = []
        for budget in budget_values:
            optimization_result = self.optimize(
                projects, 
                budget, 
                constraints,
                time_limit=30
            )
            
            results.append({
                'budget': budget,
                'total_benefit': optimization_result.get('total_benefit', 0),
                'total_cost': optimization_result.get('total_cost', 0),
                'num_projects': len(optimization_result.get('selected_projects', [])),
                'utilization': optimization_result.get('budget_utilization', 0)
            })
        
        return pd.DataFrame(results)
