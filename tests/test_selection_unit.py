"""
Unit Tests for Project Selection Module

Tests for AHP, Linear Scoring, B/C Analysis, and Portfolio Optimization.

Author: PMHelper Team
Version: 1.0.0
"""

import pytest
import numpy as np
import pandas as pd
from pathlib import Path

from pmhelper.core.selection import (
    AHPAnalyzer, LinearScoringAnalyzer, BenefitCostAnalyzer, PortfolioOptimizer,
    CriterionDirection
)
from pmhelper.core.models import (
    SelectionProblem, Criterion, Alternative, Project,
    SelectionMethod, AHPMatrix, PortfolioConstraint
)
from pmhelper.utils.selection_io import SelectionFileHandler, SelectionExportHandler


class TestAHPAnalyzer:
    """Tests for Analytic Hierarchy Process"""
    
    def test_ahp_initialization(self):
        """Test AHP analyzer initialization"""
        criteria = ['Cost', 'Quality', 'Speed']
        ahp = AHPAnalyzer(criteria)
        
        assert ahp.n == 3
        assert len(ahp.criteria) == 3
        assert ahp.matrix.shape == (3, 3)
        assert np.all(ahp.matrix == 1.0)  # Initially all 1s
    
    def test_ahp_set_comparison(self):
        """Test setting pairwise comparisons"""
        ahp = AHPAnalyzer(['Cost', 'Quality'])
        ahp.set_comparison('Cost', 'Quality', 3.0)
        
        assert ahp.matrix[0, 1] == 3.0
        assert ahp.matrix[1, 0] == pytest.approx(1/3, abs=0.001)
    
    def test_ahp_invalid_comparison_value(self):
        """Test that invalid comparison values raise errors"""
        ahp = AHPAnalyzer(['Cost', 'Quality'])
        
        with pytest.raises(ValueError, match="must be in range"):
            ahp.set_comparison('Cost', 'Quality', 10.0)
        
        with pytest.raises(ValueError, match="must be in range"):
            ahp.set_comparison('Cost', 'Quality', 0.05)
    
    def test_ahp_invalid_criterion(self):
        """Test that invalid criterion names raise errors"""
        ahp = AHPAnalyzer(['Cost', 'Quality'])
        
        with pytest.raises(KeyError, match="not found"):
            ahp.set_comparison('Cost', 'Invalid', 3.0)
    
    def test_ahp_calculate_weights(self):
        """Test weight calculation with simple matrix"""
        ahp = AHPAnalyzer(['Cost', 'Quality'])
        ahp.set_comparison('Cost', 'Quality', 2.0)
        
        weights = ahp.calculate_weights()
        
        assert len(weights) == 2
        assert pytest.approx(sum(weights), abs=0.001) == 1.0
        assert weights[0] > weights[1]  # Cost should have higher weight
    
    def test_ahp_lecture_example(self):
        """Test with 3 criteria from lecture example"""
        ahp = AHPAnalyzer(['Cost', 'Quality', 'Speed'])
        
        # Set up matrix from lecture (approximation)
        ahp.set_comparison('Cost', 'Quality', 3.0)
        ahp.set_comparison('Cost', 'Speed', 5.0)
        ahp.set_comparison('Quality', 'Speed', 2.0)
        
        weights = ahp.calculate_weights()
        cr = ahp.calculate_consistency_ratio()
        
        # Expected: Cost dominant, Quality second, Speed third
        assert weights[0] > weights[1] > weights[2]
        assert cr < 0.1  # Should be acceptable
        assert pytest.approx(sum(weights), abs=0.001) == 1.0
    
    def test_ahp_consistency_ratio(self):
        """Test consistency ratio calculation"""
        ahp = AHPAnalyzer(['A', 'B', 'C'])
        
        # Perfect consistency
        ahp.set_comparison('A', 'B', 2.0)
        ahp.set_comparison('A', 'C', 4.0)
        ahp.set_comparison('B', 'C', 2.0)
        
        cr = ahp.calculate_consistency_ratio()
        assert cr == pytest.approx(0.0, abs=0.01)
    
    def test_ahp_geometric_mean(self):
        """Test geometric mean aggregation for multiple decision makers"""
        ahp = AHPAnalyzer(['Cost', 'Quality'])
        
        matrix1 = np.array([[1.0, 3.0], [1/3, 1.0]])
        matrix2 = np.array([[1.0, 5.0], [1/5, 1.0]])
        
        result = ahp.calculate_geometric_mean([matrix1, matrix2])
        
        assert result.shape == (2, 2)
        assert result[0, 0] == pytest.approx(1.0)
        assert result[0, 1] > 3.0 and result[0, 1] < 5.0
    
    def test_ahp_rank_alternatives(self):
        """Test ranking alternatives with AHP weights"""
        ahp = AHPAnalyzer(['Cost', 'Quality'])
        ahp.set_comparison('Cost', 'Quality', 2.0)
        
        alternatives = {
            'A': {'Cost': 0.8, 'Quality': 0.6},
            'B': {'Cost': 0.6, 'Quality': 0.9},
            'C': {'Cost': 0.7, 'Quality': 0.7}
        }
        
        results = ahp.rank_alternatives(alternatives)
        
        assert isinstance(results, pd.DataFrame)
        assert len(results) == 3
        assert 'Rank' in results.columns
        assert 'Total Score' in results.columns
        assert results['Rank'].tolist() == [1, 2, 3]


class TestLinearScoringAnalyzer:
    """Tests for Linear Scoring Rule"""
    
    def test_linear_scoring_initialization(self):
        """Test Linear Scoring analyzer initialization"""
        criteria = ['Cost', 'Quality']
        directions = {
            'Cost': CriterionDirection.MINIMIZE,
            'Quality': CriterionDirection.MAXIMIZE
        }
        
        analyzer = LinearScoringAnalyzer(criteria, directions)
        
        assert len(analyzer.criteria) == 2
        assert analyzer.directions['Cost'] == CriterionDirection.MINIMIZE
    
    def test_linear_scoring_missing_direction(self):
        """Test that missing directions raise error"""
        with pytest.raises(ValueError, match="Missing direction"):
            LinearScoringAnalyzer(['Cost', 'Quality'], {'Cost': CriterionDirection.MINIMIZE})
    
    def test_normalize_maximize(self):
        """Test normalization for maximization criteria"""
        analyzer = LinearScoringAnalyzer(['Quality'], {'Quality': CriterionDirection.MAXIMIZE})
        
        values = [80, 85, 90, 95, 100]
        normalized = analyzer.normalize_criterion(values, CriterionDirection.MAXIMIZE)
        
        assert normalized[0] == pytest.approx(1.0)  # Min value -> 1
        assert normalized[-1] == pytest.approx(9.0)  # Max value -> 9
        assert all(1.0 <= v <= 9.0 for v in normalized)
    
    def test_normalize_minimize(self):
        """Test normalization for minimization criteria"""
        analyzer = LinearScoringAnalyzer(['Cost'], {'Cost': CriterionDirection.MINIMIZE})
        
        values = [40, 50, 60, 70, 80]
        normalized = analyzer.normalize_criterion(values, CriterionDirection.MINIMIZE)
        
        assert normalized[0] == pytest.approx(9.0)  # Min value -> 9
        assert normalized[-1] == pytest.approx(1.0)  # Max value -> 1
        assert all(1.0 <= v <= 9.0 for v in normalized)
    
    def test_normalize_equal_values(self):
        """Test edge case: all values are the same"""
        analyzer = LinearScoringAnalyzer(['Cost'], {'Cost': CriterionDirection.MINIMIZE})
        
        values = [50, 50, 50, 50]
        normalized = analyzer.normalize_criterion(values, CriterionDirection.MINIMIZE)
        
        assert all(v == pytest.approx(5.0) for v in normalized)
    
    def test_calculate_scores(self):
        """Test calculating weighted scores"""
        criteria = ['Cost', 'Quality']
        directions = {
            'Cost': CriterionDirection.MINIMIZE,
            'Quality': CriterionDirection.MAXIMIZE
        }
        analyzer = LinearScoringAnalyzer(criteria, directions)
        
        alternatives = pd.DataFrame({
            'Name': ['A', 'B', 'C'],
            'Cost': [50, 75, 40],
            'Quality': [85, 92, 78]
        })
        
        weights = {'Cost': 0.6, 'Quality': 0.4}
        
        results = analyzer.calculate_scores(alternatives, weights)
        
        assert 'Total Score' in results.columns
        assert 'Rank' in results.columns
        assert len(results) == 3
        assert results['Rank'].tolist() == [1, 2, 3]
    
    def test_invalid_weights_sum(self):
        """Test that weights not summing to 1.0 raise error"""
        analyzer = LinearScoringAnalyzer(['Cost'], {'Cost': CriterionDirection.MINIMIZE})
        alternatives = pd.DataFrame({'Cost': [50, 60, 70]})
        
        with pytest.raises(ValueError, match="must sum to 1.0"):
            analyzer.calculate_scores(alternatives, {'Cost': 0.5})
    
    def test_sensitivity_analysis(self):
        """Test sensitivity analysis for weight variations"""
        criteria = ['Cost', 'Quality']
        directions = {
            'Cost': CriterionDirection.MINIMIZE,
            'Quality': CriterionDirection.MAXIMIZE
        }
        analyzer = LinearScoringAnalyzer(criteria, directions)
        
        alternatives = pd.DataFrame({
            'Name': ['A', 'B'],
            'Cost': [50, 75],
            'Quality': [85, 92]
        })
        
        weights = {'Cost': 0.6, 'Quality': 0.4}
        weight_ranges = {'Cost': (0.4, 0.8)}
        
        results = analyzer.sensitivity_analysis(alternatives, weights, weight_ranges)
        
        assert 'base_ranking' in results
        assert 'variations' in results
        assert 'Cost' in results['variations']


class TestBenefitCostAnalyzer:
    """Tests for Benefit-to-Cost Analysis"""
    
    def test_capital_recovery(self):
        """Test capital recovery calculation"""
        analyzer = BenefitCostAnalyzer()
        
        cr = analyzer.calculate_capital_recovery(
            initial_cost=1_500_000,
            salvage=0,
            marr=0.12,
            life=25
        )
        
        assert cr > 0
        assert cr < 1_500_000  # Should be less than initial cost
    
    def test_capital_recovery_with_salvage(self):
        """Test capital recovery with salvage value"""
        analyzer = BenefitCostAnalyzer()
        
        cr_no_salvage = analyzer.calculate_capital_recovery(
            initial_cost=1_000_000,
            salvage=0,
            marr=0.10,
            life=20
        )
        
        cr_with_salvage = analyzer.calculate_capital_recovery(
            initial_cost=1_000_000,
            salvage=100_000,
            marr=0.10,
            life=20
        )
        
        assert cr_with_salvage < cr_no_salvage
    
    def test_capital_recovery_zero_marr(self):
        """Test capital recovery with zero MARR"""
        analyzer = BenefitCostAnalyzer()
        
        cr = analyzer.calculate_capital_recovery(
            initial_cost=1_000_000,
            salvage=0,
            marr=0.0,
            life=10
        )
        
        # With 0% interest, CR should be initial cost / life
        assert cr == pytest.approx(100_000, abs=1.0)
    
    def test_capital_recovery_invalid_inputs(self):
        """Test that invalid inputs raise errors"""
        analyzer = BenefitCostAnalyzer()
        
        with pytest.raises(ValueError, match="must be positive"):
            analyzer.calculate_capital_recovery(-1000, 0, 0.12, 25)
        
        with pytest.raises(ValueError, match="must be positive"):
            analyzer.calculate_capital_recovery(1000, 0, 0.12, 0)
    
    def test_bc_ratio(self):
        """Test B/C ratio calculation"""
        analyzer = BenefitCostAnalyzer()
        
        bc_ratio = analyzer.calculate_bc_ratio(
            annual_benefits=250_000,
            capital_recovery=140_000,
            annual_om=50_000
        )
        
        # B/C = 250,000 / (140,000 + 50,000) = 1.316
        assert bc_ratio == pytest.approx(1.316, abs=0.01)
    
    def test_bc_ratio_no_om(self):
        """Test B/C ratio without O&M costs"""
        analyzer = BenefitCostAnalyzer()
        
        bc_ratio = analyzer.calculate_bc_ratio(
            annual_benefits=200_000,
            capital_recovery=100_000
        )
        
        assert bc_ratio == pytest.approx(2.0, abs=0.01)
    
    def test_incremental_analysis(self):
        """Test incremental B/C analysis"""
        analyzer = BenefitCostAnalyzer()
        
        projects = pd.DataFrame({
            'name': ['A', 'B', 'C'],
            'initial_cost': [1_000_000, 1_500_000, 2_000_000],
            'life': [20, 25, 30],
            'annual_benefits': [180_000, 250_000, 300_000],
            'annual_om': [40_000, 50_000, 60_000],
            'salvage': [0, 0, 0]
        })
        
        results = analyzer.incremental_analysis(projects, marr=0.12)
        
        assert 'optimal_project' in results
        assert 'comparisons' in results
        assert results['optimal_project'] is not None
    
    def test_incremental_analysis_no_viable(self):
        """Test incremental analysis with no viable projects"""
        analyzer = BenefitCostAnalyzer()
        
        projects = pd.DataFrame({
            'name': ['A', 'B'],
            'initial_cost': [1_000_000, 1_500_000],
            'life': [20, 25],
            'annual_benefits': [50_000, 80_000],  # Very low benefits
            'annual_om': [40_000, 60_000],
            'salvage': [0, 0]
        })
        
        results = analyzer.incremental_analysis(projects, marr=0.12)
        
        assert results['optimal_project'] is None
        assert 'No projects have B/C ratio' in results['message']


class TestPortfolioOptimizer:
    """Tests for Portfolio Optimization"""
    
    def test_portfolio_initialization(self):
        """Test portfolio optimizer initialization"""
        optimizer = PortfolioOptimizer()
        assert optimizer.solver == 'pulp'
    
    def test_portfolio_simple(self):
        """Test simple portfolio optimization"""
        optimizer = PortfolioOptimizer()
        
        projects = pd.DataFrame({
            'name': ['A', 'B', 'C', 'D', 'E'],
            'cost': [1_500_000, 2_000_000, 1_000_000, 2_500_000, 1_200_000],
            'benefit': [300_000, 350_000, 180_000, 400_000, 220_000]
        })
        
        result = optimizer.optimize(projects, budget=5_000_000)
        
        assert result['status'] in ['Optimal', 'Not Solved']
        if result['status'] == 'Optimal':
            assert result['total_cost'] <= 5_000_000
            assert len(result['selected_projects']) > 0
            assert result['budget_utilization'] <= 100
    
    def test_portfolio_mutually_exclusive(self):
        """Test portfolio with mutually exclusive constraint"""
        optimizer = PortfolioOptimizer()
        
        projects = pd.DataFrame({
            'name': ['A', 'B', 'C'],
            'cost': [1_000_000, 1_500_000, 2_000_000],
            'benefit': [200_000, 250_000, 300_000]
        })
        
        constraints = [
            {'type': 'mutually_exclusive', 'projects': ['A', 'B']}
        ]
        
        result = optimizer.optimize(projects, budget=3_000_000, constraints=constraints)
        
        if result['status'] == 'Optimal':
            selected = result['selected_projects']
            # A and B should not both be selected
            assert not ('A' in selected and 'B' in selected)
    
    def test_portfolio_dependency(self):
        """Test portfolio with dependency constraint"""
        optimizer = PortfolioOptimizer()
        
        projects = pd.DataFrame({
            'name': ['A', 'B', 'C'],
            'cost': [1_000_000, 1_500_000, 500_000],
            'benefit': [200_000, 300_000, 100_000]
        })
        
        constraints = [
            {'type': 'dependency', 'projects': ['B'], 'requires': 'A'}
        ]
        
        result = optimizer.optimize(projects, budget=3_000_000, constraints=constraints)
        
        if result['status'] == 'Optimal':
            selected = result['selected_projects']
            # If B is selected, A must be selected
            if 'B' in selected:
                assert 'A' in selected
    
    def test_portfolio_infeasible(self):
        """Test handling of infeasible portfolio"""
        optimizer = PortfolioOptimizer()
        
        projects = pd.DataFrame({
            'name': ['A'],
            'cost': [10_000_000],
            'benefit': [1_000_000]
        })
        
        result = optimizer.optimize(projects, budget=1_000_000)
        
        # Should handle infeasible gracefully
        assert 'status' in result
    
    def test_portfolio_performance(self):
        """Test performance with 20 projects"""
        import time
        
        optimizer = PortfolioOptimizer()
        
        # Generate 20 projects
        np.random.seed(42)
        projects = pd.DataFrame({
            'name': [f'Project_{i}' for i in range(20)],
            'cost': np.random.uniform(500_000, 2_000_000, 20),
            'benefit': np.random.uniform(100_000, 400_000, 20)
        })
        
        start_time = time.time()
        result = optimizer.optimize(projects, budget=10_000_000, time_limit=5)
        elapsed_time = time.time() - start_time
        
        # Should complete within 5 seconds
        assert elapsed_time < 6.0
        assert result['status'] in ['Optimal', 'Not Solved']
    
    def test_budget_sensitivity(self):
        """Test budget sensitivity analysis"""
        optimizer = PortfolioOptimizer()
        
        projects = pd.DataFrame({
            'name': ['A', 'B', 'C'],
            'cost': [1_000_000, 1_500_000, 2_000_000],
            'benefit': [200_000, 300_000, 350_000]
        })
        
        results = optimizer.sensitivity_budget(
            projects,
            base_budget=3_000_000,
            budget_range=(2_000_000, 5_000_000),
            steps=5
        )
        
        assert isinstance(results, pd.DataFrame)
        assert len(results) == 5
        assert 'budget' in results.columns
        assert 'total_benefit' in results.columns


class TestDataModels:
    """Tests for Pydantic data models"""
    
    def test_criterion_model(self):
        """Test Criterion model validation"""
        criterion = Criterion(
            name="Cost",
            weight=0.5,
            direction=CriterionDirection.MINIMIZE
        )
        
        assert criterion.name == "Cost"
        assert criterion.weight == 0.5
    
    def test_criterion_invalid_weight(self):
        """Test that invalid weights raise error"""
        with pytest.raises(ValueError):
            Criterion(
                name="Cost",
                weight=1.5,  # > 1.0
                direction=CriterionDirection.MINIMIZE
            )
    
    def test_alternative_model(self):
        """Test Alternative model"""
        alternative = Alternative(
            id="alt1",
            name="Alternative A",
            scores={'Cost': 0.8, 'Quality': 0.9}
        )
        
        assert alternative.id == "alt1"
        assert alternative.scores['Cost'] == 0.8
    
    def test_project_model(self):
        """Test Project model"""
        project = Project(
            id="proj1",
            name="Bridge A",
            cost=1_500_000,
            benefit=250_000,
            life=25
        )
        
        assert project.cost == 1_500_000
        assert project.benefit == 250_000
    
    def test_selection_problem_ahp(self):
        """Test SelectionProblem for AHP method"""
        criteria = [
            Criterion(name="Cost", weight=0.6, direction=CriterionDirection.MINIMIZE),
            Criterion(name="Quality", weight=0.4, direction=CriterionDirection.MAXIMIZE)
        ]
        
        alternatives = [
            Alternative(id="a1", name="Alt A", scores={'Cost': 0.8, 'Quality': 0.7}),
            Alternative(id="a2", name="Alt B", scores={'Cost': 0.6, 'Quality': 0.9})
        ]
        
        problem = SelectionProblem(
            id="test1",
            name="Test AHP Problem",
            method=SelectionMethod.AHP,
            criteria=criteria,
            alternatives=alternatives
        )
        
        assert problem.method == SelectionMethod.AHP
        assert len(problem.alternatives) == 2
    
    def test_selection_problem_portfolio(self):
        """Test SelectionProblem for Portfolio method"""
        projects = [
            Project(id="p1", name="Project A", cost=1_000_000, benefit=200_000),
            Project(id="p2", name="Project B", cost=1_500_000, benefit=300_000)
        ]
        
        problem = SelectionProblem(
            id="test2",
            name="Test Portfolio Problem",
            method=SelectionMethod.PORTFOLIO,
            projects=projects,
            budget=3_000_000
        )
        
        assert problem.budget == 3_000_000
        assert len(problem.projects) == 2


class TestFileIO:
    """Tests for file I/O operations"""
    
    def test_save_and_load_problem(self, tmp_path):
        """Test saving and loading a selection problem"""
        criteria = [
            Criterion(name="Cost", weight=1.0, direction=CriterionDirection.MINIMIZE)
        ]
        
        alternatives = [
            Alternative(id="a1", name="Alt A", scores={'Cost': 0.8})
        ]
        
        problem = SelectionProblem(
            id="test1",
            name="Test Problem",
            method=SelectionMethod.AHP,
            criteria=criteria,
            alternatives=alternatives
        )
        
        # Save
        filepath = tmp_path / "test_problem.pmsel"
        SelectionFileHandler.save(problem, filepath)
        
        assert filepath.exists()
        
        # Load
        loaded_problem = SelectionFileHandler.load(filepath)
        
        assert loaded_problem.id == problem.id
        assert loaded_problem.name == problem.name
        assert len(loaded_problem.criteria) == 1
    
    def test_load_nonexistent_file(self):
        """Test loading non-existent file raises error"""
        with pytest.raises(FileNotFoundError):
            SelectionFileHandler.load("nonexistent.pmsel")
    
    def test_validate_file(self, tmp_path):
        """Test file validation"""
        # Create a simple alternative with valid data
        alternatives = [Alternative(id="a1", name="Alt A", scores={})]
        
        problem = SelectionProblem(
            id="test1",
            name="Test",
            method=SelectionMethod.AHP,
            criteria=[],
            alternatives=alternatives
        )
        
        filepath = tmp_path / "test.pmsel"
        SelectionFileHandler.save(problem, filepath)
        
        validation = SelectionFileHandler.validate_file(filepath)
        
        assert validation['valid'] is True
        assert validation['version'] == "1.0"
        assert validation['method'] == "ahp"


# Run tests with pytest
if __name__ == '__main__':
    pytest.main([__file__, '-v'])
