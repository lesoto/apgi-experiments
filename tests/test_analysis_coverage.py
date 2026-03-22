"""
Tests for analysis modules.

This module contains comprehensive tests for statistical analysis,
parameter estimation, and effect size calculations.
"""

import pytest
import numpy as np
from apgi_framework.analysis.parameter_estimation import IndividualParameterEstimator
from apgi_framework.analysis.effect_size_calculator import EffectSizeCalculator
from apgi_framework.analysis.statistical_tester import StatisticalTester


class TestParameterEstimator:
    """Tests for IndividualParameterEstimator class."""

    @pytest.fixture
    def estimator(self):
        """Create an IndividualParameterEstimator instance."""
        return IndividualParameterEstimator()

    def test_initialization(self, estimator):
        """Test estimator initialization."""
        assert estimator is not None

    def test_estimate_mean(self, estimator):
        """Test mean parameter estimation."""
        data = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        mean_est = estimator.estimate_mean(data)

        assert isinstance(mean_est, (float, np.floating))
        assert 2.9 < mean_est < 3.1  # Approximately 3.0

    def test_estimate_std(self, estimator):
        """Test standard deviation estimation."""
        data = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        std_est = estimator.estimate_std(data)

        assert isinstance(std_est, (float, np.floating))
        assert std_est > 0

    def test_estimate_with_confidence(self, estimator):
        """Test estimation with confidence intervals."""
        data = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        result = estimator.estimate_with_ci(data, parameter="mean", confidence=0.95)

        assert isinstance(result, dict)
        assert "estimate" in result
        assert "ci_lower" in result
        assert "ci_upper" in result
        assert result["ci_lower"] < result["ci_upper"]

    def test_estimate_distribution_params(self, estimator):
        """Test distribution parameter estimation."""
        data = np.random.normal(100, 15, 1000)
        params = estimator.estimate_distribution_params(data, distribution="normal")

        assert isinstance(params, dict)
        assert "mean" in params
        assert "std" in params
        assert 99 < params["mean"] < 101
        assert 14 < params["std"] < 16


class TestEffectSizeCalculator:
    """Tests for EffectSizeCalculator class."""

    @pytest.fixture
    def calculator(self):
        """Create an EffectSizeCalculator instance."""
        return EffectSizeCalculator()

    def test_initialization(self, calculator):
        """Test calculator initialization."""
        assert calculator is not None

    def test_cohens_d(self, calculator):
        """Test Cohen's d calculation."""
        group1 = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        group2 = np.array([6.0, 7.0, 8.0, 9.0, 10.0])

        d = calculator.cohens_d(group1, group2)

        assert isinstance(d, (float, np.floating))
        assert d > 0  # Effect size should be positive

    def test_hedges_g(self, calculator):
        """Test Hedges' g calculation."""
        group1 = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        group2 = np.array([6.0, 7.0, 8.0, 9.0, 10.0])

        g = calculator.hedges_g(group1, group2)

        assert isinstance(g, (float, np.floating))
        assert g > 0

    def test_partial_eta_squared(self, calculator):
        """Test partial eta squared calculation."""
        ss_effect = 100.0
        ss_error = 50.0

        eta_sq = calculator.partial_eta_squared(ss_effect, ss_error)

        assert isinstance(eta_sq, (float, np.floating))
        assert 0 <= eta_sq <= 1

    def test_effect_size_interpretation(self, calculator):
        """Test effect size interpretation."""
        small = calculator.interpret_cohens_d(0.2)
        medium = calculator.interpret_cohens_d(0.5)
        large = calculator.interpret_cohens_d(0.8)

        assert isinstance(small, str)
        assert isinstance(medium, str)
        assert isinstance(large, str)


class TestStatisticalTester:
    """Tests for StatisticalTester class."""

    @pytest.fixture
    def tester(self):
        """Create a StatisticalTester instance."""
        return StatisticalTester()

    def test_initialization(self, tester):
        """Test tester initialization."""
        assert tester is not None

    def test_t_test_independent(self, tester):
        """Test independent samples t-test."""
        group1 = np.random.normal(100, 15, 50)
        group2 = np.random.normal(110, 15, 50)

        result = tester.t_test_independent(group1, group2)

        assert isinstance(result, dict)
        assert "t_statistic" in result
        assert "p_value" in result
        assert "degrees_freedom" in result

    def test_t_test_paired(self, tester):
        """Test paired samples t-test."""
        before = np.random.normal(100, 15, 50)
        after = before + np.random.normal(5, 5, 50)  # Small increase

        result = tester.t_test_paired(before, after)

        assert isinstance(result, dict)
        assert "t_statistic" in result
        assert "p_value" in result

    def test_one_way_anova(self, tester):
        """Test one-way ANOVA."""
        group1 = np.random.normal(100, 15, 30)
        group2 = np.random.normal(105, 15, 30)
        group3 = np.random.normal(110, 15, 30)

        result = tester.one_way_anova([group1, group2, group3])

        assert isinstance(result, dict)
        assert "f_statistic" in result
        assert "p_value" in result

    def test_correlation_pearson(self, tester):
        """Test Pearson correlation."""
        x = np.random.normal(100, 15, 100)
        y = x + np.random.normal(0, 5, 100)  # Strong correlation

        result = tester.correlation_pearson(x, y)

        assert isinstance(result, dict)
        assert "r" in result
        assert "p_value" in result
        assert -1 <= result["r"] <= 1

    def test_normality_test(self, tester):
        """Test normality testing."""
        normal_data = np.random.normal(0, 1, 100)

        result = tester.normality_test(normal_data)

        assert isinstance(result, dict)
        assert "statistic" in result
        assert "p_value" in result

    def test_levene_test(self, tester):
        """Test Levene's test for homogeneity of variance."""
        group1 = np.random.normal(100, 10, 50)
        group2 = np.random.normal(100, 10, 50)

        result = tester.levene_test([group1, group2])

        assert isinstance(result, dict)
        assert "statistic" in result
        assert "p_value" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
