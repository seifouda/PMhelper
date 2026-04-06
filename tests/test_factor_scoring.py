"""
Tests for pmhelper.core.factor_scoring  (V2 Phase 3B).

Coverage
--------
- Unweighted 0-1 model
- Unweighted Factor model
- Weighted Factor model
- Ranking logic (ties handled, rank 1 = highest)
- Weight normalisation
- Input validation
- FactorScoringResult properties (winner, criteria, projects)
"""

import pytest
from pmhelper.core.factor_scoring import (
    FactorScoringEngine,
    FactorScoringResult,
    ProjectScore,
    ScoringCriterion,
)


# ── Fixtures ──────────────────────────────────────────────────────────

@pytest.fixture
def three_criteria():
    return [
        ScoringCriterion("Cost",     weight=0.5),
        ScoringCriterion("Risk",     weight=0.3),
        ScoringCriterion("Schedule", weight=0.2),
    ]


@pytest.fixture
def three_projects():
    return ["Alpha", "Beta", "Gamma"]


@pytest.fixture
def weighted_matrix():
    """
    Scores (3 projects × 3 criteria):
      Alpha:  5, 3, 4
      Beta:   3, 5, 5
      Gamma:  4, 4, 3

    Weighted totals (weights 0.5, 0.3, 0.2 normalised → same since already sum=1):
      Alpha : 0.5×5 + 0.3×3 + 0.2×4 = 2.5+0.9+0.8 = 4.2
      Beta  : 0.5×3 + 0.3×5 + 0.2×5 = 1.5+1.5+1.0 = 4.0
      Gamma : 0.5×4 + 0.3×4 + 0.2×3 = 2.0+1.2+0.6 = 3.8
    """
    return [
        [5, 3, 4],
        [3, 5, 5],
        [4, 4, 3],
    ]


@pytest.fixture
def factor_matrix():
    """Factor scores (same matrix, all > 0.5 so 0-1 maps to all-1)."""
    return [
        [5, 3, 4],
        [3, 5, 5],
        [4, 4, 3],
    ]


@pytest.fixture
def binary_matrix():
    """0-1 matrix."""
    return [
        [1, 0, 1],   # Alpha: 2
        [1, 1, 1],   # Beta:  3
        [0, 1, 0],   # Gamma: 1
    ]


# ── Weighted Factor model ─────────────────────────────────────────────

class TestWeightedModel:

    def test_winner_is_alpha(self, three_criteria, three_projects, weighted_matrix):
        result = FactorScoringEngine.calculate(
            three_criteria, three_projects, weighted_matrix,
            model=FactorScoringEngine.MODEL_WEIGHTED)
        assert result.winner == "Alpha"

    def test_ranking_order(self, three_criteria, three_projects, weighted_matrix):
        result = FactorScoringEngine.calculate(
            three_criteria, three_projects, weighted_matrix,
            model=FactorScoringEngine.MODEL_WEIGHTED)
        by_rank = sorted(result.projects, key=lambda p: p.rank)
        names = [p.project_name for p in by_rank]
        assert names == ["Alpha", "Beta", "Gamma"]

    def test_alpha_total(self, three_criteria, three_projects, weighted_matrix):
        result = FactorScoringEngine.calculate(
            three_criteria, three_projects, weighted_matrix,
            model=FactorScoringEngine.MODEL_WEIGHTED)
        alpha = next(p for p in result.projects if p.project_name == "Alpha")
        assert abs(alpha.total - 4.2) < 0.01

    def test_weighted_scores_per_criterion(self, three_criteria, three_projects,
                                           weighted_matrix):
        result = FactorScoringEngine.calculate(
            three_criteria, three_projects, weighted_matrix,
            model=FactorScoringEngine.MODEL_WEIGHTED)
        alpha = next(p for p in result.projects if p.project_name == "Alpha")
        # cost weighted: 5 × 0.5 = 2.5
        assert abs(alpha.weighted_scores[0] - 2.5) < 0.001

    def test_model_stored(self, three_criteria, three_projects, weighted_matrix):
        result = FactorScoringEngine.calculate(
            three_criteria, three_projects, weighted_matrix,
            model=FactorScoringEngine.MODEL_WEIGHTED)
        assert result.model == "Weighted"

    def test_returns_result_type(self, three_criteria, three_projects, weighted_matrix):
        result = FactorScoringEngine.calculate(
            three_criteria, three_projects, weighted_matrix,
            model=FactorScoringEngine.MODEL_WEIGHTED)
        assert isinstance(result, FactorScoringResult)

    def test_unnormalised_weights(self, three_projects, weighted_matrix):
        """Weights 50, 30, 20 should normalise to 0.5, 0.3, 0.2 — same result."""
        crits = [
            ScoringCriterion("Cost",     weight=50),
            ScoringCriterion("Risk",     weight=30),
            ScoringCriterion("Schedule", weight=20),
        ]
        result = FactorScoringEngine.calculate(
            crits, three_projects, weighted_matrix,
            model=FactorScoringEngine.MODEL_WEIGHTED)
        assert result.winner == "Alpha"
        alpha = next(p for p in result.projects if p.project_name == "Alpha")
        assert abs(alpha.total - 4.2) < 0.01


# ── Unweighted Factor model ───────────────────────────────────────────

class TestFactorModel:

    def test_winner(self, three_criteria, three_projects, factor_matrix):
        result = FactorScoringEngine.calculate(
            three_criteria, three_projects, factor_matrix,
            model=FactorScoringEngine.MODEL_FACTOR)
        # Alpha: 12, Beta: 13, Gamma: 11 → Beta wins
        assert result.winner == "Beta"

    def test_total_is_sum(self, three_criteria, three_projects, factor_matrix):
        result = FactorScoringEngine.calculate(
            three_criteria, three_projects, factor_matrix,
            model=FactorScoringEngine.MODEL_FACTOR)
        beta = next(p for p in result.projects if p.project_name == "Beta")
        assert abs(beta.total - 13.0) < 0.001

    def test_rank_1_is_best(self, three_criteria, three_projects, factor_matrix):
        result = FactorScoringEngine.calculate(
            three_criteria, three_projects, factor_matrix,
            model=FactorScoringEngine.MODEL_FACTOR)
        best = next(p for p in result.projects if p.rank == 1)
        assert best.project_name == "Beta"

    def test_model_stored(self, three_criteria, three_projects, factor_matrix):
        result = FactorScoringEngine.calculate(
            three_criteria, three_projects, factor_matrix,
            model=FactorScoringEngine.MODEL_FACTOR)
        assert result.model == "Factor"

    def test_weighted_scores_equal_raw_in_factor_model(
            self, three_criteria, three_projects, factor_matrix):
        result = FactorScoringEngine.calculate(
            three_criteria, three_projects, factor_matrix,
            model=FactorScoringEngine.MODEL_FACTOR)
        alpha = next(p for p in result.projects if p.project_name == "Alpha")
        assert alpha.scores == alpha.weighted_scores


# ── Unweighted 0-1 model ──────────────────────────────────────────────

class TestBinaryModel:

    def test_winner(self, three_criteria, three_projects, binary_matrix):
        result = FactorScoringEngine.calculate(
            three_criteria, three_projects, binary_matrix,
            model=FactorScoringEngine.MODEL_01)
        # Alpha: 2, Beta: 3, Gamma: 1 → Beta
        assert result.winner == "Beta"

    def test_beta_total_is_3(self, three_criteria, three_projects, binary_matrix):
        result = FactorScoringEngine.calculate(
            three_criteria, three_projects, binary_matrix,
            model=FactorScoringEngine.MODEL_01)
        beta = next(p for p in result.projects if p.project_name == "Beta")
        assert abs(beta.total - 3.0) < 0.001

    def test_values_clamped_to_0_or_1(self, three_criteria, three_projects):
        """Any value > 0.5 treated as 1."""
        matrix = [[0.8, 0.2, 1.0], [0, 1, 0], [1, 0, 1]]
        result = FactorScoringEngine.calculate(
            three_criteria, three_projects, matrix,
            model=FactorScoringEngine.MODEL_01)
        alpha = next(p for p in result.projects if p.project_name == "Alpha")
        # 0.8→1, 0.2→0, 1.0→1 → total=2
        assert abs(alpha.total - 2.0) < 0.001

    def test_model_stored(self, three_criteria, three_projects, binary_matrix):
        result = FactorScoringEngine.calculate(
            three_criteria, three_projects, binary_matrix,
            model=FactorScoringEngine.MODEL_01)
        assert result.model == "0-1"


# ── Validation ────────────────────────────────────────────────────────

class TestValidation:

    def test_invalid_model_raises(self, three_criteria, three_projects,
                                   weighted_matrix):
        with pytest.raises(ValueError):
            FactorScoringEngine.calculate(
                three_criteria, three_projects, weighted_matrix,
                model="BadModel")

    def test_mismatched_row_count(self, three_criteria):
        """Different number of project rows vs project name list."""
        with pytest.raises((ValueError, IndexError, Exception)):
            FactorScoringEngine.calculate(
                three_criteria,
                ["P1", "P2"],
                [[1, 2, 3], [4, 5, 6], [7, 8, 9]],  # 3 rows but 2 projects
                model=FactorScoringEngine.MODEL_FACTOR)


# ── Result properties ─────────────────────────────────────────────────

class TestResultProperties:

    def test_criteria_preserved(self, three_criteria, three_projects,
                                 weighted_matrix):
        result = FactorScoringEngine.calculate(
            three_criteria, three_projects, weighted_matrix,
            model=FactorScoringEngine.MODEL_WEIGHTED)
        assert len(result.criteria) == 3
        assert result.criteria[0].name == "Cost"

    def test_projects_count(self, three_criteria, three_projects, weighted_matrix):
        result = FactorScoringEngine.calculate(
            three_criteria, three_projects, weighted_matrix,
            model=FactorScoringEngine.MODEL_WEIGHTED)
        assert len(result.projects) == 3

    def test_ranks_are_unique(self, three_criteria, three_projects, weighted_matrix):
        result = FactorScoringEngine.calculate(
            three_criteria, three_projects, weighted_matrix,
            model=FactorScoringEngine.MODEL_WEIGHTED)
        ranks = [p.rank for p in result.projects]
        assert len(set(ranks)) == len(ranks)

    def test_rank_1_has_highest_total(self, three_criteria, three_projects,
                                       weighted_matrix):
        result = FactorScoringEngine.calculate(
            three_criteria, three_projects, weighted_matrix,
            model=FactorScoringEngine.MODEL_WEIGHTED)
        rank1 = next(p for p in result.projects if p.rank == 1)
        others = [p for p in result.projects if p.rank != 1]
        assert all(rank1.total >= o.total for o in others)

    def test_single_project(self):
        crit = [ScoringCriterion("X")]
        result = FactorScoringEngine.calculate(
            crit, ["Lone Wolf"], [[4]],
            model=FactorScoringEngine.MODEL_FACTOR)
        assert result.winner == "Lone Wolf"
        assert result.projects[0].rank == 1

    def test_two_criteria_two_projects(self):
        crits = [ScoringCriterion("A", weight=0.6),
                 ScoringCriterion("B", weight=0.4)]
        projs = ["X", "Y"]
        matrix = [[4, 2], [2, 4]]
        result = FactorScoringEngine.calculate(
            crits, projs, matrix, model=FactorScoringEngine.MODEL_WEIGHTED)
        # X: 0.6×4+0.4×2 = 3.2  Y: 0.6×2+0.4×4 = 2.8 → X wins
        assert result.winner == "X"
