#!/usr/bin/env python3
"""
Risk Analysis Module

Handles project delay risk assessment, contingency planning, variance reduction
strategies, and activity risk prioritization for project management.

Based on IM 738 Risk Analysis and PERT methodologies.
"""

import numpy as np
import pandas as pd
from typing import Optional
import warnings

# Make scipy import optional for PyInstaller compatibility
try:
    from scipy.stats import norm
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    warnings.warn(
        "scipy not available. Risk analysis will use simplified calculations.",
        ImportWarning
    )

    # Fallback implementations
    class FallbackNorm:
        @staticmethod
        def cdf(x):
            """Simple normal CDF approximation using error function"""
            import math
            return 0.5 * (1 + math.erf(x / math.sqrt(2)))

        @staticmethod
        def pdf(x):
            """Simple normal PDF"""
            import math
            return (1 / math.sqrt(2 * math.pi)) * math.exp(-0.5 * x**2)

        @staticmethod
        def ppf(p):
            """Inverse CDF approximation"""
            import math
            # Abramowitz and Stegun approximation
            if p < 0.5:
                sign = -1
                p = 1 - p
            else:
                sign = 1

            t = math.sqrt(-2 * math.log(1 - p))
            c0 = 2.515517
            c1 = 0.802853
            c2 = 0.010328
            d1 = 1.432788
            d2 = 0.189269
            d3 = 0.001308

            result = t - ((c0 + c1 * t + c2 * t**2) /
                          (1 + d1 * t + d2 * t**2 + d3 * t**3))
            return sign * result

    norm = FallbackNorm()


class DelayRiskAnalyzer:
    """
    Project delay risk assessment and cost analysis.

    Calculates probability of project delay, expected delay period using
    truncated normal distribution, and associated risk costs.
    """

    def __init__(self, pert_results: dict):
        """
        Initialize with PERT analysis results.

        Args:
            pert_results: Dict with keys:
                - expected_duration: Expected project completion time
                - variance: Project variance (time units squared)
                - critical_path: List of critical path activities
                - activities: Dict of activity data (optional)
        """
        self.expected_duration = pert_results.get('expected_duration', 0)
        self.variance = pert_results.get('variance', 0)
        self.std_dev = np.sqrt(max(self.variance, 0))  # Prevent negative sqrt
        self.critical_path = pert_results.get('critical_path', [])
        self.activities = pert_results.get('activities', {})

        if self.expected_duration <= 0:
            raise ValueError("Expected duration must be positive")

    def calculate_delay_probability(self, contract_time: float) -> float:
        """
        Calculate P(T > contract_time) using normal distribution.

        Formula: P(T > T_c) = 1 - Φ((T_c - μ) / σ)
        where Φ is the standard normal CDF

        Args:
            contract_time: Contracted completion time

        Returns:
            Probability of delay (0 to 1)
        """
        if contract_time <= 0:
            raise ValueError("Contract time must be positive")

        # Handle zero variance case
        if self.std_dev == 0:
            return 1.0 if contract_time < self.expected_duration else 0.0

        z_score = (contract_time - self.expected_duration) / self.std_dev
        delay_probability = 1 - norm.cdf(z_score)

        return float(delay_probability)

    def calculate_expected_delay(self, contract_time: float) -> float:
        """
        Calculate E[Delay | T > T_c] using truncated normal distribution.

        Formula: E[X|X > a] = μ + σ * φ((a-μ)/σ) / (1 - Φ((a-μ)/σ))
        where φ is standard normal PDF, Φ is standard normal CDF

        Args:
            contract_time: Contracted completion time

        Returns:
            Expected delay period (time units)
        """
        if contract_time <= 0:
            raise ValueError("Contract time must be positive")

        # Handle zero variance case
        if self.std_dev == 0:
            return max(0, self.expected_duration - contract_time)

        z_score = (contract_time - self.expected_duration) / self.std_dev
        phi = norm.pdf(z_score)  # PDF at z
        Phi = norm.cdf(z_score)  # CDF at z

        # Avoid division by zero
        if (1 - Phi) < 1e-10:
            return 0.0

        # Expected value of truncated normal
        expected_completion = self.expected_duration + \
            self.std_dev * phi / (1 - Phi)
        expected_delay = max(0, expected_completion - contract_time)

        return float(expected_delay)

    def calculate_risk_cost(
        self,
        contract_time: float,
        penalty_rate: float,
        max_penalty_percent: float = 0.20,
        contract_value: Optional[float] = None
    ) -> dict:
        """
        Calculate delay risk cost.

        Risk = P(delay) × E[delay | delay occurs] × penalty_rate

        Args:
            contract_time: Contracted completion time
            penalty_rate: Penalty cost per time unit of delay
            max_penalty_percent: Maximum penalty as fraction of contract (default 20%)
            contract_value: Contract value for penalty cap calculation (optional)

        Returns:
            Dict with:
                - delay_probability: P(T > contract_time)
                - expected_delay: E[delay | delay occurs]
                - risk_cost: Uncapped risk cost
                - capped_risk_cost: Risk cost with penalty cap applied
                - max_penalty: Maximum allowable penalty
                - z_score: Standard score for contract time
        """
        if penalty_rate < 0:
            raise ValueError("Penalty rate must be non-negative")

        delay_prob = self.calculate_delay_probability(contract_time)
        expected_delay = self.calculate_expected_delay(contract_time)

        # Calculate uncapped risk cost
        risk_cost = delay_prob * expected_delay * penalty_rate

        # Apply cap if specified and contract value provided
        max_penalty = None
        capped_risk_cost = risk_cost

        if max_penalty_percent is not None and max_penalty_percent > 0 and contract_value:
            max_penalty = contract_value * max_penalty_percent
            capped_risk_cost = min(risk_cost, max_penalty)
        elif max_penalty_percent is not None and max_penalty_percent > 0:
            # Estimate contract value from activities if available
            estimated_value = self.estimate_contract_value()
            if estimated_value > 0:
                max_penalty = estimated_value * max_penalty_percent
                capped_risk_cost = min(risk_cost, max_penalty)

        return {
            'delay_probability': delay_prob,
            'expected_delay': expected_delay,
            'risk_cost': risk_cost,
            'capped_risk_cost': capped_risk_cost,
            'max_penalty': max_penalty,
            'z_score': (
                contract_time -
                self.expected_duration) /
            self.std_dev if self.std_dev > 0 else 0}

    def estimate_contract_value(self) -> float:
        """
        Estimate contract value from activity costs (if available).

        Returns:
            Estimated contract value
        """
        if not self.activities:
            return 0

        total_cost = 0
        for activity_id, activity in self.activities.items():
            # Try different possible cost field names
            cost = (
                activity.get('cost', 0) or
                activity.get('normal_cost', 0) or
                activity.get('budget', 0)
            )
            total_cost += cost

        return total_cost


class ContingencyPlanner:
    """
    Contingency time and budget estimation.

    Calculates buffer times and associated costs based on desired
    confidence levels for project completion.
    """

    def __init__(self, pert_results: dict):
        """
        Initialize with PERT analysis results.

        Args:
            pert_results: Dict with expected_duration, variance, etc.
        """
        self.expected_duration = pert_results.get('expected_duration', 0)
        self.variance = pert_results.get('variance', 0)
        self.std_dev = np.sqrt(max(self.variance, 0))
        self.activities = pert_results.get('activities', {})

        if self.expected_duration <= 0:
            raise ValueError("Expected duration must be positive")

    def calculate_contingency(
        self,
        confidence_level: float = 0.95,
        daily_cost_rate: Optional[float] = None
    ) -> dict:
        """
        Calculate contingency time buffer and cost.

        Formula: Buffer = Z_α × σ
        where Z_α is the z-score for confidence level α

        Args:
            confidence_level: Desired probability of completion (0 to 1)
            daily_cost_rate: Cost per time unit (optional)

        Returns:
            Dict with:
                - confidence_level: Requested confidence level
                - z_score: Z-score for confidence level
                - time_buffer: Required time buffer
                - buffer_percentage: Buffer as % of expected duration
                - completion_time: Expected duration + buffer
                - contingency_cost: Cost of buffer (if rate provided)
                - recommendation: Actionable recommendation
        """
        if not (0.5 <= confidence_level <= 0.999):
            raise ValueError("Confidence level must be between 0.5 and 0.999")

        # Handle zero variance case
        if self.std_dev == 0:
            return {
                'confidence_level': confidence_level,
                'z_score': 0,
                'time_buffer': 0,
                'buffer_percentage': 0,
                'completion_time': self.expected_duration,
                'contingency_cost': 0 if daily_cost_rate else None,
                'recommendation': 'No buffer needed - project has zero variance on critical path'
            }

        # Calculate z-score for confidence level
        z_score = norm.ppf(confidence_level)

        # Calculate time buffer
        time_buffer = z_score * self.std_dev
        buffer_percentage = (time_buffer / self.expected_duration) * 100
        completion_time = self.expected_duration + time_buffer

        # Calculate cost if rate provided
        contingency_cost = None
        if daily_cost_rate is not None:
            contingency_cost = time_buffer * daily_cost_rate

        # Generate recommendation
        recommendation = self._generate_recommendation(
            buffer_percentage,
            confidence_level
        )

        return {
            'confidence_level': confidence_level,
            'z_score': z_score,
            'time_buffer': time_buffer,
            'buffer_percentage': buffer_percentage,
            'completion_time': completion_time,
            'contingency_cost': contingency_cost,
            'recommendation': recommendation
        }

    def _generate_recommendation(
        self,
        buffer_percentage: float,
        confidence_level: float
    ) -> str:
        """
        Generate actionable recommendation based on buffer analysis.

        Args:
            buffer_percentage: Buffer as percentage of expected duration
            confidence_level: Target confidence level

        Returns:
            Recommendation text
        """
        if buffer_percentage < 5:
            return (
                f"Low buffer ({buffer_percentage:.1f}%) - Project has low uncertainty. "
                f"Consider {confidence_level * 100:.0f}% confidence adequate for low-risk projects."
            )
        elif buffer_percentage < 15:
            return (
                f"Moderate buffer ({buffer_percentage:.1f}%) - Typical for most projects. "
                f"Recommended for {confidence_level * 100:.0f}% confidence level."
            )
        elif buffer_percentage < 25:
            return (
                f"High buffer ({buffer_percentage:.1f}%) - Significant uncertainty detected. "
                f"Consider risk mitigation or reduce confidence level to 90-95%."
            )
        else:
            return (
                f"Very high buffer ({buffer_percentage:.1f}%) - Critical uncertainty. "
                f"Strongly recommend variance reduction strategies before committing to timeline."
            )


class VarianceReductionAnalyzer:
    """
    Compare strategies for reducing project risk through time
    and/or variance reduction.
    """

    def __init__(self, pert_results: dict):
        """
        Initialize with PERT analysis results.

        Args:
            pert_results: Dict with expected_duration, variance, critical_path, activities
        """
        self.expected_duration = pert_results.get('expected_duration', 0)
        self.variance = pert_results.get('variance', 0)
        self.std_dev = np.sqrt(max(self.variance, 0))
        self.activities = pert_results.get('activities', {})
        self.critical_path = pert_results.get('critical_path', [])

        if self.expected_duration <= 0:
            raise ValueError("Expected duration must be positive")

    def analyze_strategies(
        self,
        contract_time: float,
        penalty_rate: float,
        time_reduction_cost: float,
        variance_reduction_cost: float,
        max_budget: Optional[float] = None
    ) -> dict:
        """
        Compare Strategy A (reduce time), Strategy B (reduce variance),
        and mixed strategies.

        Args:
            contract_time: Contract completion deadline
            penalty_rate: Penalty per time unit of delay
            time_reduction_cost: Cost per unit time reduction
            variance_reduction_cost: Cost per unit variance reduction
            max_budget: Maximum budget for improvements (optional)

        Returns:
            Dict with:
                - baseline: Current risk analysis
                - strategy_a: Time reduction results
                - strategy_b: Variance reduction results
                - mixed_strategy: Optimal combination
                - best_strategy: Recommended strategy
                - summary: Executive summary
        """
        # Calculate baseline risk
        baseline_analyzer = DelayRiskAnalyzer({
            'expected_duration': self.expected_duration,
            'variance': self.variance,
            'critical_path': self.critical_path,
            'activities': self.activities
        })
        baseline = baseline_analyzer.calculate_risk_cost(
            contract_time, penalty_rate)
        baseline['investment'] = 0
        baseline['net_benefit'] = 0

        # Set default max budget if not provided
        if max_budget is None:
            max_budget = baseline['risk_cost'] * 2  # Default: 2x the risk cost

        # Analyze each strategy
        strategy_a = self._analyze_time_reduction(
            contract_time, penalty_rate, time_reduction_cost, max_budget
        )

        strategy_b = self._analyze_variance_reduction(
            contract_time, penalty_rate, variance_reduction_cost, max_budget
        )

        mixed = self._optimize_mixed_strategy(
            contract_time, penalty_rate,
            time_reduction_cost, variance_reduction_cost,
            max_budget
        )

        # Determine best strategy
        strategies = {
            'Strategy A (Reduce Time)': strategy_a,
            'Strategy B (Reduce Variance)': strategy_b,
            'Mixed Strategy': mixed
        }

        best_name = max(
            strategies.keys(),
            key=lambda k: strategies[k]['net_benefit'])
        best_strategy = strategies[best_name]
        best_strategy['name'] = best_name

        # Generate summary
        summary = self._generate_strategy_summary(
            baseline, strategies, best_name)

        return {
            'baseline': baseline,
            'strategy_a': strategy_a,
            'strategy_b': strategy_b,
            'mixed_strategy': mixed,
            'best_strategy': best_strategy,
            'summary': summary
        }

    def _analyze_time_reduction(
        self,
        contract_time: float,
        penalty_rate: float,
        time_reduction_cost: float,
        max_budget: float
    ) -> dict:
        """
        Analyze Strategy A: Reduce expected time (keep variance constant).

        Args:
            contract_time: Contract deadline
            penalty_rate: Penalty per time unit
            time_reduction_cost: Cost per time unit reduced
            max_budget: Maximum budget

        Returns:
            Strategy analysis results
        """
        # Calculate maximum time reduction within budget
        max_time_reduction = min(
            max_budget / time_reduction_cost,
            self.expected_duration - contract_time + 5  # Leave some margin
        )

        if max_time_reduction <= 0:
            return {
                'time_reduction': 0,
                'variance_reduction': 0,
                'new_expected_duration': self.expected_duration,
                'new_variance': self.variance,
                'new_risk_cost': 0,
                'investment': 0,
                'benefit': 0,
                'net_benefit': 0,
                'roi': 0,
                'feasible': False,
                'message': 'Insufficient budget for time reduction'
            }

        # Find optimal time reduction
        best_benefit = -float('inf')
        best_reduction = 0

        for reduction in np.linspace(0, max_time_reduction, 50):
            new_duration = self.expected_duration - reduction
            investment = reduction * time_reduction_cost

            if investment > max_budget:
                continue

            # Calculate new risk
            new_analyzer = DelayRiskAnalyzer({
                'expected_duration': new_duration,
                'variance': self.variance,  # Unchanged
                'critical_path': self.critical_path,
                'activities': self.activities
            })
            new_risk = new_analyzer.calculate_risk_cost(
                contract_time, penalty_rate)

            # Calculate baseline risk for comparison
            baseline_analyzer = DelayRiskAnalyzer({
                'expected_duration': self.expected_duration,
                'variance': self.variance,
                'critical_path': self.critical_path,
                'activities': self.activities
            })
            baseline_risk = baseline_analyzer.calculate_risk_cost(
                contract_time, penalty_rate)

            benefit = baseline_risk['risk_cost'] - new_risk['risk_cost']
            net_benefit = benefit - investment

            if net_benefit > best_benefit:
                best_benefit = net_benefit
                best_reduction = reduction

        # Calculate final results with optimal reduction
        new_duration = self.expected_duration - best_reduction
        investment = best_reduction * time_reduction_cost

        new_analyzer = DelayRiskAnalyzer({
            'expected_duration': new_duration,
            'variance': self.variance,
            'critical_path': self.critical_path,
            'activities': self.activities
        })
        new_risk = new_analyzer.calculate_risk_cost(
            contract_time, penalty_rate)

        baseline_analyzer = DelayRiskAnalyzer({
            'expected_duration': self.expected_duration,
            'variance': self.variance,
            'critical_path': self.critical_path,
            'activities': self.activities
        })
        baseline_risk = baseline_analyzer.calculate_risk_cost(
            contract_time, penalty_rate)

        benefit = baseline_risk['risk_cost'] - new_risk['risk_cost']
        roi = (benefit / investment * 100) if investment > 0 else 0

        return {
            'time_reduction': best_reduction,
            'variance_reduction': 0,
            'new_expected_duration': new_duration,
            'new_variance': self.variance,
            'new_risk_cost': new_risk['risk_cost'],
            'investment': investment,
            'benefit': benefit,
            'net_benefit': best_benefit,
            'roi': roi,
            'feasible': True
        }

    def _analyze_variance_reduction(
        self,
        contract_time: float,
        penalty_rate: float,
        variance_reduction_cost: float,
        max_budget: float
    ) -> dict:
        """
        Analyze Strategy B: Reduce variance (keep expected time constant).

        Args:
            contract_time: Contract deadline
            penalty_rate: Penalty per time unit
            variance_reduction_cost: Cost per variance unit reduced
            max_budget: Maximum budget

        Returns:
            Strategy analysis results
        """
        # Calculate maximum variance reduction within budget
        max_variance_reduction = min(
            max_budget / variance_reduction_cost,
            self.variance * 0.9  # Can't reduce more than 90%
        )

        if max_variance_reduction <= 0 or self.variance == 0:
            return {
                'time_reduction': 0,
                'variance_reduction': 0,
                'new_expected_duration': self.expected_duration,
                'new_variance': self.variance,
                'new_risk_cost': 0,
                'investment': 0,
                'benefit': 0,
                'net_benefit': 0,
                'roi': 0,
                'feasible': False,
                'message': 'Insufficient budget or zero variance'
            }

        # Find optimal variance reduction
        best_benefit = -float('inf')
        best_reduction = 0

        for reduction in np.linspace(0, max_variance_reduction, 50):
            new_variance = max(
                self.variance - reduction,
                0.01)  # Keep small positive variance
            investment = reduction * variance_reduction_cost

            if investment > max_budget:
                continue

            # Calculate new risk
            new_analyzer = DelayRiskAnalyzer({
                'expected_duration': self.expected_duration,  # Unchanged
                'variance': new_variance,
                'critical_path': self.critical_path,
                'activities': self.activities
            })
            new_risk = new_analyzer.calculate_risk_cost(
                contract_time, penalty_rate)

            # Calculate baseline risk
            baseline_analyzer = DelayRiskAnalyzer({
                'expected_duration': self.expected_duration,
                'variance': self.variance,
                'critical_path': self.critical_path,
                'activities': self.activities
            })
            baseline_risk = baseline_analyzer.calculate_risk_cost(
                contract_time, penalty_rate)

            benefit = baseline_risk['risk_cost'] - new_risk['risk_cost']
            net_benefit = benefit - investment

            if net_benefit > best_benefit:
                best_benefit = net_benefit
                best_reduction = reduction

        # Calculate final results
        new_variance = max(self.variance - best_reduction, 0.01)
        investment = best_reduction * variance_reduction_cost

        new_analyzer = DelayRiskAnalyzer({
            'expected_duration': self.expected_duration,
            'variance': new_variance,
            'critical_path': self.critical_path,
            'activities': self.activities
        })
        new_risk = new_analyzer.calculate_risk_cost(
            contract_time, penalty_rate)

        baseline_analyzer = DelayRiskAnalyzer({
            'expected_duration': self.expected_duration,
            'variance': self.variance,
            'critical_path': self.critical_path,
            'activities': self.activities
        })
        baseline_risk = baseline_analyzer.calculate_risk_cost(
            contract_time, penalty_rate)

        benefit = baseline_risk['risk_cost'] - new_risk['risk_cost']
        roi = (benefit / investment * 100) if investment > 0 else 0

        return {
            'time_reduction': 0,
            'variance_reduction': best_reduction,
            'new_expected_duration': self.expected_duration,
            'new_variance': new_variance,
            'new_risk_cost': new_risk['risk_cost'],
            'investment': investment,
            'benefit': benefit,
            'net_benefit': best_benefit,
            'roi': roi,
            'feasible': True
        }

    def _optimize_mixed_strategy(
        self,
        contract_time: float,
        penalty_rate: float,
        time_reduction_cost: float,
        variance_reduction_cost: float,
        max_budget: float
    ) -> dict:
        """
        Find optimal combination of time and variance reduction.

        Uses grid search to find the best allocation of budget between
        time and variance reduction.

        Args:
            contract_time: Contract deadline
            penalty_rate: Penalty per time unit
            time_reduction_cost: Cost per time unit reduced
            variance_reduction_cost: Cost per variance unit reduced
            max_budget: Maximum budget

        Returns:
            Optimal mixed strategy results
        """
        best_benefit = -float('inf')
        best_time_reduction = 0
        best_variance_reduction = 0

        # Grid search over possible allocations
        max_time = min(
            max_budget / time_reduction_cost,
            self.expected_duration - contract_time + 5
        )
        max_variance = min(
            max_budget / variance_reduction_cost,
            self.variance * 0.9
        )

        for time_reduction in np.linspace(0, max_time, 20):
            for variance_reduction in np.linspace(0, max_variance, 20):
                investment = (
                    time_reduction * time_reduction_cost +
                    variance_reduction * variance_reduction_cost
                )

                if investment > max_budget:
                    continue

                new_duration = self.expected_duration - time_reduction
                new_variance = max(self.variance - variance_reduction, 0.01)

                # Calculate new risk
                new_analyzer = DelayRiskAnalyzer({
                    'expected_duration': new_duration,
                    'variance': new_variance,
                    'critical_path': self.critical_path,
                    'activities': self.activities
                })
                new_risk = new_analyzer.calculate_risk_cost(
                    contract_time, penalty_rate)

                # Calculate baseline risk
                baseline_analyzer = DelayRiskAnalyzer({
                    'expected_duration': self.expected_duration,
                    'variance': self.variance,
                    'critical_path': self.critical_path,
                    'activities': self.activities
                })
                baseline_risk = baseline_analyzer.calculate_risk_cost(
                    contract_time, penalty_rate)

                benefit = baseline_risk['risk_cost'] - new_risk['risk_cost']
                net_benefit = benefit - investment

                if net_benefit > best_benefit:
                    best_benefit = net_benefit
                    best_time_reduction = time_reduction
                    best_variance_reduction = variance_reduction

        # Calculate final results
        new_duration = self.expected_duration - best_time_reduction
        new_variance = max(self.variance - best_variance_reduction, 0.01)
        investment = (
            best_time_reduction * time_reduction_cost +
            best_variance_reduction * variance_reduction_cost
        )

        new_analyzer = DelayRiskAnalyzer({
            'expected_duration': new_duration,
            'variance': new_variance,
            'critical_path': self.critical_path,
            'activities': self.activities
        })
        new_risk = new_analyzer.calculate_risk_cost(
            contract_time, penalty_rate)

        baseline_analyzer = DelayRiskAnalyzer({
            'expected_duration': self.expected_duration,
            'variance': self.variance,
            'critical_path': self.critical_path,
            'activities': self.activities
        })
        baseline_risk = baseline_analyzer.calculate_risk_cost(
            contract_time, penalty_rate)

        benefit = baseline_risk['risk_cost'] - new_risk['risk_cost']
        roi = (benefit / investment * 100) if investment > 0 else 0

        return {
            'time_reduction': best_time_reduction,
            'variance_reduction': best_variance_reduction,
            'new_expected_duration': new_duration,
            'new_variance': new_variance,
            'new_risk_cost': new_risk['risk_cost'],
            'investment': investment,
            'benefit': benefit,
            'net_benefit': best_benefit,
            'roi': roi,
            'feasible': True
        }

    def _generate_strategy_summary(
        self,
        baseline: dict,
        strategies: dict,
        best_strategy_name: str
    ) -> str:
        """
        Generate executive summary of strategy comparison.

        Args:
            baseline: Baseline risk analysis
            strategies: Dict of strategy results
            best_strategy_name: Name of recommended strategy

        Returns:
            Executive summary text
        """
        best = strategies[best_strategy_name]

        summary = f"""
Risk Reduction Strategy Analysis
=================================

Baseline Risk: ${baseline['risk_cost']:,.2f}

Recommended Strategy: {best_strategy_name}
- Investment: ${best['investment']:,.2f}
- Risk Reduction: ${best['benefit']:,.2f}
- Net Benefit: ${best['net_benefit']:,.2f}
- ROI: {best['roi']:.1f}%

All Strategies:
"""

        for name, strategy in strategies.items():
            indicator = "✓" if name == best_strategy_name else " "
            summary += f"{indicator} {name}: Net Benefit ${
                strategy['net_benefit']:,.2f} (ROI: {
                strategy['roi']:.1f}%)\n"

        return summary


class ActivityRiskPrioritizer:
    """
    Identify and prioritize high-risk activities for mitigation.

    Calculates risk scores based on criticality, cruciality (variance contribution),
    schedule sensitivity, and uncertainty metrics.
    """

    def __init__(self, pert_results: dict):
        """
        Initialize with PERT analysis results.

        Args:
            pert_results: Dict with activities, critical_path, variance, network
        """
        self.activities = pert_results.get('activities', {})
        self.critical_path = pert_results.get('critical_path', [])
        self.project_variance = pert_results.get('variance', 0)
        self.expected_duration = pert_results.get('expected_duration', 0)
        self.network = pert_results.get('network', None)

        if not self.activities:
            raise ValueError(
                "Activities data is required for risk prioritization")

    def calculate_risk_scores(self) -> pd.DataFrame:
        """
        Calculate comprehensive risk scores for all activities.

        Formula: Risk Score = 0.40 × Criticality + 0.30 × Cruciality +
                              0.20 × Schedule_Sensitivity + 0.10 × Uncertainty

        Where:
        - Criticality: 1 if on critical path, 0 otherwise
        - Cruciality: Activity variance / Project variance
        - Schedule Sensitivity: 1 / (1 + Total Float)
        - Uncertainty: Coefficient of Variation = σ / μ

        Returns:
            DataFrame with activity risk analysis
        """
        risk_data = []

        for activity_id, activity in self.activities.items():
            # Skip START/END nodes
            if activity_id in ['START', 'END']:
                continue

            # Get activity properties
            variance = activity.get('variance', 0)
            expected_time = activity.get(
                'expected_time', activity.get(
                    'expected_duration', 0))
            total_float = activity.get('float', activity.get('total_float', 0))

            # Calculate metrics
            # 1. Criticality Index (on critical path)
            criticality = 1.0 if activity_id in self.critical_path else 0.0

            # 2. Cruciality Index (variance contribution)
            cruciality = 0.0
            if self.project_variance > 0:
                cruciality = variance / self.project_variance

            # 3. Schedule Sensitivity (inverse of float)
            schedule_sensitivity = 1.0 / (1.0 + total_float)

            # 4. Uncertainty (coefficient of variation)
            uncertainty = 0.0
            if expected_time > 0 and variance > 0:
                std_dev = np.sqrt(variance)
                uncertainty = std_dev / expected_time

            # Calculate weighted risk score
            risk_score = (
                0.40 * criticality +
                0.30 * cruciality +
                0.20 * schedule_sensitivity +
                0.10 * uncertainty
            )

            # Generate recommendation
            recommendation = self._generate_activity_recommendation(
                criticality, cruciality, schedule_sensitivity, uncertainty
            )

            risk_data.append({
                'activity_id': activity_id,
                'activity_name': activity.get('activity', activity_id),
                'expected_time': expected_time,
                'variance': variance,
                'std_dev': np.sqrt(variance) if variance > 0 else 0,
                'total_float': total_float,
                'criticality': criticality,
                'cruciality': cruciality,
                'schedule_sensitivity': schedule_sensitivity,
                'uncertainty': uncertainty,
                'risk_score': risk_score,
                'recommendation': recommendation
            })

        # Create DataFrame and sort by risk score
        df = pd.DataFrame(risk_data)
        df = df.sort_values(
            'risk_score',
            ascending=False).reset_index(
            drop=True)

        return df

    def _generate_activity_recommendation(
        self,
        criticality: float,
        cruciality: float,
        schedule_sensitivity: float,
        uncertainty: float
    ) -> str:
        """
        Generate specific recommendation for activity.

        Args:
            criticality: Criticality index (0 or 1)
            cruciality: Cruciality index (variance contribution)
            schedule_sensitivity: Schedule sensitivity (0 to 1)
            uncertainty: Coefficient of variation

        Returns:
            Recommendation text
        """
        recommendations = []

        if criticality == 1.0:
            recommendations.append("CRITICAL PATH - Monitor closely")

        if cruciality > 0.3:
            recommendations.append(
                "High variance contributor - Reduce uncertainty")

        if schedule_sensitivity > 0.7:
            recommendations.append("Low float - Schedule risk")

        if uncertainty > 0.3:
            recommendations.append("High uncertainty - Improve estimates")

        if not recommendations:
            recommendations.append("Low risk - Standard monitoring")

        return "; ".join(recommendations)

    def get_top_risks(self, n: int = 10) -> pd.DataFrame:
        """
        Get top N highest risk activities.

        Args:
            n: Number of top risks to return

        Returns:
            DataFrame with top N risks
        """
        df = self.calculate_risk_scores()
        return df.head(n)

    def generate_mitigation_plan(
        self,
        budget_available: Optional[float] = None,
        focus_critical_path: bool = True
    ) -> dict:
        """
        Generate prioritized mitigation plan.

        Args:
            budget_available: Budget available for mitigation (optional)
            focus_critical_path: Prioritize critical path activities

        Returns:
            Dict with:
                - high_priority: High-risk activities requiring immediate attention
                - medium_priority: Medium-risk activities
                - low_priority: Low-risk activities for monitoring
                - critical_path_risks: Risks on critical path
                - variance_contributors: Top variance contributors
                - total_activities: Total number of activities analyzed
        """
        df = self.calculate_risk_scores()

        # Categorize by risk score
        high_priority = df[df['risk_score'] >= 0.6].to_dict('records')
        medium_priority = df[(df['risk_score'] >= 0.3) & (
            df['risk_score'] < 0.6)].to_dict('records')
        low_priority = df[df['risk_score'] < 0.3].to_dict('records')

        # Identify critical path risks
        critical_path_risks = df[df['criticality'] == 1.0].to_dict('records')

        # Top variance contributors
        variance_contributors = df.nlargest(5, 'cruciality').to_dict('records')

        return {
            'high_priority': high_priority,
            'medium_priority': medium_priority,
            'low_priority': low_priority,
            'critical_path_risks': critical_path_risks,
            'variance_contributors': variance_contributors,
            'total_activities': len(df),
            'summary': f"""
Mitigation Plan Summary
=======================
Total Activities: {len(df)}
High Priority Risks: {len(high_priority)}
Critical Path Risks: {len(critical_path_risks)}

Immediate Actions Required:
- Focus on {len(high_priority)} high-priority activities
- Monitor {len(critical_path_risks)} critical path activities
- Address top {len(variance_contributors)} variance contributors
"""
        }
