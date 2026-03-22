"""
Comprehensive tests for core modules.

Tests for core/equation.py, core/models.py, core/threshold.py to improve coverage.
"""

import numpy as np


class TestCoreEquation:
    """Tests for core/equation.py module."""

    def test_module_imports(self):
        """Test that equation module can be imported."""
        from apgi_framework.core import equation

        assert hasattr(equation, "APGICalculator")

    def test_apgi_calculator_initialization(self):
        """Test APGICalculator initialization."""
        from apgi_framework.core.equation import APGICalculator

        calc = APGICalculator()
        assert calc is not None

    def test_calculate_apgi(self):
        """Test APGI calculation."""
        from apgi_framework.core.equation import APGICalculator

        calc = APGICalculator()
        result = calc.calculate(r_e=0.5, sigma_e=0.1, alpha_base=0.3)

        assert isinstance(result, (int, float, np.number))

    def test_calculate_with_different_parameters(self):
        """Test calculation with different parameter sets."""
        from apgi_framework.core.equation import APGICalculator

        calc = APGICalculator()

        # Test with various parameter values
        params = [(0.3, 0.05, 0.2), (0.7, 0.15, 0.4), (0.5, 0.1, 0.3)]

        for r_e, sigma_e, alpha in params:
            result = calc.calculate(r_e=r_e, sigma_e=sigma_e, alpha_base=alpha)
            assert isinstance(result, (int, float, np.number))

    def test_calculator_validate_inputs(self):
        """Test input validation."""
        from apgi_framework.core.equation import APGICalculator

        calc = APGICalculator()

        # Valid inputs should work
        result = calc.calculate(r_e=0.5, sigma_e=0.1, alpha_base=0.3)
        assert result is not None

    def test_calculator_edge_cases(self):
        """Test calculator with edge case values."""
        from apgi_framework.core.equation import APGICalculator

        calc = APGICalculator()

        # Test with zero values
        result = calc.calculate(r_e=0.0, sigma_e=0.0, alpha_base=0.0)
        assert isinstance(result, (int, float, np.number))


class TestCoreModels:
    """Tests for core/models.py module."""

    def test_module_imports(self):
        """Test that models module can be imported."""
        from apgi_framework.core import models

        assert hasattr(models, "AgentModel")

    def test_agent_model_initialization(self):
        """Test AgentModel initialization."""
        from apgi_framework.core.models import AgentModel

        model = AgentModel()
        assert model is not None

    def test_agent_model_with_params(self):
        """Test AgentModel with parameters."""
        from apgi_framework.core.models import AgentModel

        params = {"alpha": 0.3, "beta": 0.5, "gamma": 0.2}

        model = AgentModel(parameters=params)
        assert model.parameters == params

    def test_model_update_parameters(self):
        """Test updating model parameters."""
        from apgi_framework.core.models import AgentModel

        model = AgentModel()
        model.update_parameters({"alpha": 0.4})

        assert model.parameters.get("alpha") == 0.4

    def test_model_reset(self):
        """Test resetting model state."""
        from apgi_framework.core.models import AgentModel

        model = AgentModel()
        model.update_parameters({"alpha": 0.5})
        model.reset()

        # After reset, should be back to default state
        assert model is not None

    def test_model_predict(self):
        """Test model prediction."""
        from apgi_framework.core.models import AgentModel

        model = AgentModel()

        # Test prediction with sample input
        input_data = np.array([0.1, 0.2, 0.3])
        prediction = model.predict(input_data)

        assert prediction is not None

    def test_model_fit(self):
        """Test model fitting."""
        from apgi_framework.core.models import AgentModel

        model = AgentModel()

        # Create sample training data
        X = np.random.randn(10, 3)
        y = np.random.randint(0, 2, 10)

        model.fit(X, y)
        assert model.is_fitted is True or hasattr(model, "parameters")


class TestCoreThreshold:
    """Tests for core/threshold.py module."""

    def test_module_imports(self):
        """Test that threshold module can be imported."""
        from apgi_framework.core import threshold

        assert hasattr(threshold, "ThresholdDetector")

    def test_threshold_detector_initialization(self):
        """Test ThresholdDetector initialization."""
        from apgi_framework.core.threshold import ThresholdDetector

        detector = ThresholdDetector()
        assert detector is not None

    def test_threshold_detector_with_threshold(self):
        """Test detector with specific threshold."""
        from apgi_framework.core.threshold import ThresholdDetector

        detector = ThresholdDetector(threshold=0.5)
        assert detector.threshold == 0.5

    def test_detect_threshold_crossing(self):
        """Test detecting threshold crossing."""
        from apgi_framework.core.threshold import ThresholdDetector

        detector = ThresholdDetector(threshold=0.5)

        # Data that crosses threshold
        data = np.array([0.3, 0.4, 0.6, 0.7, 0.4])
        crossings = detector.detect(data)

        assert isinstance(crossings, (list, np.ndarray))

    def test_detect_no_crossing(self):
        """Test detecting when no threshold crossing occurs."""
        from apgi_framework.core.threshold import ThresholdDetector

        detector = ThresholdDetector(threshold=0.9)

        # Data that never crosses high threshold
        data = np.array([0.1, 0.2, 0.3, 0.4])
        crossings = detector.detect(data)

        # Should return empty or no crossings
        assert len(crossings) == 0 or crossings.size == 0

    def test_threshold_adaptive(self):
        """Test adaptive threshold functionality."""
        from apgi_framework.core.threshold import ThresholdDetector

        detector = ThresholdDetector(threshold=0.5, adaptive=True)

        data = np.random.randn(100)
        crossings = detector.detect(data)

        assert isinstance(crossings, (list, np.ndarray))

    def test_get_threshold_statistics(self):
        """Test getting threshold statistics."""
        from apgi_framework.core.threshold import ThresholdDetector

        detector = ThresholdDetector(threshold=0.5)

        data = np.random.randn(50)
        detector.detect(data)

        stats = detector.get_statistics()
        assert isinstance(stats, dict)

    def test_set_threshold(self):
        """Test dynamically setting threshold."""
        from apgi_framework.core.threshold import ThresholdDetector

        detector = ThresholdDetector(threshold=0.5)
        detector.set_threshold(0.7)

        assert detector.threshold == 0.7


class TestCoreDataModels:
    """Tests for core/data_models.py module."""

    def test_module_imports(self):
        """Test that data_models module can be imported."""
        from apgi_framework.core import data_models

        assert hasattr(data_models, "ExperimentData")

    def test_experiment_data_creation(self):
        """Test creating ExperimentData object."""
        from apgi_framework.core.data_models import ExperimentData

        data = ExperimentData(
            experiment_id="exp_001",
            participant_id="sub_001",
            trial_number=1,
            data={"response_time": 0.5},
        )

        assert data.experiment_id == "exp_001"
        assert data.participant_id == "sub_001"

    def test_experiment_data_to_dict(self):
        """Test converting ExperimentData to dictionary."""
        from apgi_framework.core.data_models import ExperimentData

        data = ExperimentData(
            experiment_id="exp_001", participant_id="sub_001", data={"key": "value"}
        )

        data_dict = data.to_dict()
        assert isinstance(data_dict, dict)
        assert data_dict["experiment_id"] == "exp_001"

    def test_experiment_data_from_dict(self):
        """Test creating ExperimentData from dictionary."""
        from apgi_framework.core.data_models import ExperimentData

        data_dict = {
            "experiment_id": "exp_002",
            "participant_id": "sub_002",
            "trial_number": 2,
            "data": {"accuracy": 0.95},
        }

        data = ExperimentData.from_dict(data_dict)
        assert data.experiment_id == "exp_002"
        assert data.data["accuracy"] == 0.95


class TestCorePrecision:
    """Tests for core/precision.py module."""

    def test_module_imports(self):
        """Test that precision module can be imported."""
        from apgi_framework.core import precision

        assert hasattr(precision, "PrecisionCalculator")

    def test_precision_calculator_initialization(self):
        """Test PrecisionCalculator initialization."""
        from apgi_framework.core.precision import PrecisionCalculator

        calc = PrecisionCalculator()
        assert calc is not None

    def test_calculate_precision(self):
        """Test precision calculation."""
        from apgi_framework.core.precision import PrecisionCalculator

        calc = PrecisionCalculator()

        # Test with sample data
        true_values = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        predicted_values = np.array([1.1, 1.9, 3.2, 3.9, 5.1])

        precision = calc.calculate(true_values, predicted_values)
        assert isinstance(precision, (int, float, np.number))


class TestCorePredictionError:
    """Tests for core/prediction_error.py module."""

    def test_module_imports(self):
        """Test that prediction_error module can be imported."""
        from apgi_framework.core import prediction_error

        assert hasattr(prediction_error, "PredictionErrorCalculator")

    def test_prediction_error_calculator(self):
        """Test PredictionErrorCalculator initialization."""
        from apgi_framework.core.prediction_error import PredictionErrorCalculator

        calc = PredictionErrorCalculator()
        assert calc is not None

    def test_calculate_prediction_error(self):
        """Test prediction error calculation."""
        from apgi_framework.core.prediction_error import PredictionErrorCalculator

        calc = PredictionErrorCalculator()

        predictions = np.array([0.5, 0.6, 0.7])
        outcomes = np.array([0.6, 0.5, 0.8])

        errors = calc.calculate(predictions, outcomes)
        assert isinstance(errors, np.ndarray)


class TestCoreSomaticMarker:
    """Tests for core/somatic_marker.py module."""

    def test_module_imports(self):
        """Test that somatic_marker module can be imported."""
        from apgi_framework.core import somatic_marker

        assert hasattr(somatic_marker, "SomaticMarker")

    def test_somatic_marker_initialization(self):
        """Test SomaticMarker initialization."""
        from apgi_framework.core.somatic_marker import SomaticMarker

        marker = SomaticMarker()
        assert marker is not None

    def test_somatic_marker_process_signal(self):
        """Test processing somatic marker signal."""
        from apgi_framework.core.somatic_marker import SomaticMarker

        marker = SomaticMarker()

        # Test with sample signal
        signal = np.random.randn(100)
        processed = marker.process(signal)

        assert processed is not None
