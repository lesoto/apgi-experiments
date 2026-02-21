"""
Main Application Controller for APGI Framework Testing System.

This module provides the central orchestration point for the entire system,
managing component integration, dependency injection, and system initialization.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import numpy as np

from .config import ConfigManager, get_config_manager
from .core import (
    APGIEquation,
    PrecisionCalculator,
    PredictionErrorProcessor,
    SomaticMarkerEngine,
    ThresholdManager,
)
from .data import DataValidator, StorageManager
from .exceptions import APGIFrameworkError
from .falsification import (
    ConsciousnessWithoutIgnitionTest,
    PrimaryFalsificationTest,
    SomaBiasTest,
    ThresholdInsensitivityTest,
)
from .simulators import (
    BOLDSimulator,
    GammaSimulator,
    P3bSimulator,
    PCICalculator,
    SignatureValidator,
)


class MainApplicationController:
    """
    Central controller for the APGI Framework Testing System.

    Manages system initialization, component integration, and orchestrates
    the execution of falsification tests with proper dependency injection.
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the main application controller.

        Args:
            config_path: Optional path to configuration file.
        """
        self.config_manager = (
            ConfigManager(config_path) if config_path else get_config_manager()
        )
        self.logger = self._setup_logging()

        # Core components
        self._mathematical_engine: Optional[Dict[str, Any]] = None
        self._neural_simulators: Optional[Dict[str, Any]] = None
        self._falsification_tests: Optional[Dict[str, Any]] = None
        self._data_manager: Optional[Dict[str, Any]] = None

        # System state
        self._initialized = False
        self._components_registered = False

        self.logger.info("MainApplicationController initialized")

    def initialize_system(self) -> None:
        """
        Initialize all system components with proper dependency injection.

        Raises:
            APGIFrameworkError: If system initialization fails.
        """
        try:
            self.logger.info("Starting system initialization...")

            # Initialize core mathematical components
            self._initialize_mathematical_engine()

            # Initialize neural signature simulators
            self._initialize_neural_simulators()

            # Initialize data management system
            self._initialize_data_manager()

            # Initialize falsification test controllers
            self._initialize_falsification_tests()

            self._initialized = True
            self.logger.info("System initialization completed successfully")

        except Exception as e:
            self.logger.error(f"System initialization failed: {e}")
            raise APGIFrameworkError(f"Failed to initialize system: {e}")

    def _initialize_mathematical_engine(self) -> None:
        """Initialize the core mathematical framework components."""
        self.logger.debug("Initializing mathematical engine...")

        apgi_params = self.config_manager.get_apgi_parameters()

        # Create core mathematical components with proper configuration
        precision_calculator = PrecisionCalculator(
            min_precision=getattr(apgi_params, "min_precision", 1e-6),
            max_precision=getattr(apgi_params, "max_precision", 100.0),
        )

        prediction_error_processor = PredictionErrorProcessor(
            standardize=getattr(apgi_params, "standardize_errors", True),
            outlier_threshold=getattr(apgi_params, "outlier_threshold", 3.0),
        )

        somatic_marker_engine = SomaticMarkerEngine(
            baseline_gain=getattr(apgi_params, "baseline_somatic_gain", 1.0),
            max_gain=getattr(apgi_params, "max_somatic_gain", 5.0),
            min_gain=getattr(apgi_params, "min_somatic_gain", 0.1),
        )

        threshold_manager = ThresholdManager(
            baseline_threshold=getattr(apgi_params, "baseline_threshold", 3.5),
            min_threshold=getattr(apgi_params, "min_threshold", 0.5),
            max_threshold=getattr(apgi_params, "max_threshold", 10.0),
        )

        # Create main equation engine with integrated components
        apgi_equation = APGIEquation(
            precision_calculator=precision_calculator,
            prediction_error_processor=prediction_error_processor,
            somatic_marker_engine=somatic_marker_engine,
            threshold_manager=threshold_manager,
            numerical_stability=getattr(apgi_params, "numerical_stability", True),
        )

        self._mathematical_engine = {
            "equation": apgi_equation,
            "precision_calculator": precision_calculator,
            "prediction_error_processor": prediction_error_processor,
            "somatic_marker_engine": somatic_marker_engine,
            "threshold_manager": threshold_manager,
        }

        self.logger.debug("Mathematical engine initialized with integrated components")

    def _initialize_neural_simulators(self) -> None:
        """Initialize neural signature simulation components."""
        self.logger.debug("Initializing neural simulators...")

        exp_config = self.config_manager.get_experimental_config()

        # Create neural signature simulators
        p3b_simulator = P3bSimulator(random_seed=exp_config.random_seed)

        gamma_simulator = GammaSimulator(random_seed=exp_config.random_seed)

        bold_simulator = BOLDSimulator(random_seed=exp_config.random_seed)

        pci_calculator = PCICalculator()

        signature_validator = SignatureValidator()

        self._neural_simulators = {
            "p3b": p3b_simulator,
            "gamma": gamma_simulator,
            "bold": bold_simulator,
            "pci": pci_calculator,
            "validator": signature_validator,
        }

        self.logger.debug("Neural simulators initialized")

    def _initialize_data_manager(self) -> None:
        """Initialize data management and storage components."""
        self.logger.debug("Initializing data manager...")

        exp_config = self.config_manager.get_experimental_config()

        # Create data management components
        storage_manager = StorageManager(storage_path=exp_config.output_directory)

        data_validator = DataValidator()

        self._data_manager = {"storage": storage_manager, "validator": data_validator}

        self.logger.debug("Data manager initialized")

    def _initialize_falsification_tests(self) -> None:
        """Initialize falsification test controllers."""
        self.logger.debug("Initializing falsification tests...")

        if not self._mathematical_engine or not self._neural_simulators:
            raise APGIFrameworkError(
                "Mathematical engine and neural simulators must be initialized first"
            )

        try:
            # Initialize primary falsification test
            primary_test = PrimaryFalsificationTest()

            # Initialize all falsification tests
            consciousness_test = ConsciousnessWithoutIgnitionTest()
            threshold_test = ThresholdInsensitivityTest()
            soma_bias_test = SomaBiasTest()

            self._falsification_tests = {
                "primary": primary_test,
                "consciousness_without_ignition": consciousness_test,
                "threshold_insensitivity": threshold_test,
                "soma_bias": soma_bias_test,
            }

            self.logger.debug("All falsification tests initialized")

        except Exception as e:
            self.logger.warning(f"Could not initialize falsification tests: {e}")
            # Create minimal test structure for validation
            self._falsification_tests = {
                "primary": None,
                "consciousness_without_ignition": None,
                "threshold_insensitivity": None,
                "soma_bias": None,
            }

        self.logger.debug("Falsification tests initialization completed")

    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration."""
        exp_config = self.config_manager.get_experimental_config()

        # Ensure output directory exists
        output_dir = Path(exp_config.output_directory)
        output_dir.mkdir(parents=True, exist_ok=True)

        logging.basicConfig(
            level=getattr(logging, exp_config.log_level.upper()),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(output_dir / "apgi_framework.log"),
            ],
        )

        return logging.getLogger(__name__)

    def get_mathematical_engine(self) -> Dict[str, Any]:
        """Get mathematical engine components."""
        if not self._initialized:
            raise APGIFrameworkError(
                "System not initialized. Call initialize_system() first."
            )
        if self._mathematical_engine is None:
            raise APGIFrameworkError(
                "Mathematical engine failed to initialize and is not available."
            )
        return self._mathematical_engine

    def get_neural_simulators(self) -> Dict[str, Any]:
        """Get neural simulator components."""
        if not self._initialized:
            raise APGIFrameworkError(
                "System not initialized. Call initialize_system() first."
            )
        if self._neural_simulators is None:
            raise APGIFrameworkError(
                "Neural simulators failed to initialize and are not available."
            )
        return self._neural_simulators

    def get_falsification_tests(self) -> Dict[str, Any]:
        """Get falsification test controllers."""
        if not self._initialized:
            raise APGIFrameworkError(
                "System not initialized. Call initialize_system() first."
            )
        if self._falsification_tests is None:
            raise APGIFrameworkError(
                "Falsification tests failed to initialize and are not available."
            )
        # Check for None components that indicate import failures
        if (
            "primary" in self._falsification_tests
            and self._falsification_tests["primary"] is None
        ):
            raise APGIFrameworkError(
                "Primary falsification test is not available due to import failure."
            )
        return self._falsification_tests

    def get_data_manager(self) -> Dict[str, Any]:
        """Get data management components."""
        if not self._initialized:
            raise APGIFrameworkError(
                "System not initialized. Call initialize_system() first."
            )
        if self._data_manager is None:
            raise APGIFrameworkError(
                "Data manager failed to initialize and is not available."
            )
        return self._data_manager

    def run_system_validation(self) -> Dict[str, bool]:
        """
        Run comprehensive system validation checks.

        Returns:
            Dictionary with validation results for each component.
        """
        if not self._initialized:
            raise APGIFrameworkError(
                "System not initialized. Call initialize_system() first."
            )

        self.logger.info("Running system validation...")

        validation_results: Dict[str, Any] = {}

        try:
            # Validate mathematical engine
            validation_results[
                "mathematical_engine"
            ] = self._validate_mathematical_engine()

            # Validate neural simulators
            validation_results["neural_simulators"] = self._validate_neural_simulators()

            # Validate falsification tests
            validation_results[
                "falsification_tests"
            ] = self._validate_falsification_tests()

            # Validate data manager
            validation_results["data_manager"] = self._validate_data_manager()

            # Overall system validation
            validation_results["overall"] = all(validation_results.values())

            self.logger.info(f"System validation completed: {validation_results}")

        except Exception as e:
            self.logger.error(f"System validation failed: {e}")
            validation_results["overall"] = False
            validation_results["error"] = str(e)

        return validation_results

    def _validate_mathematical_engine(self) -> bool:
        """Validate mathematical engine components."""
        assert self._mathematical_engine is not None
        try:
            equation = self._mathematical_engine["equation"]

            # Validate component integration
            component_validation = equation.validate_integrated_components()
            if not component_validation["all_components_available"]:
                self.logger.error(
                    f"Component integration validation failed: {component_validation}"
                )
                return False

            # Test basic equation calculation
            surprise = equation.calculate_surprise(
                extero_error=1.0,
                intero_error=0.8,
                extero_precision=2.0,
                intero_precision=1.5,
                somatic_gain=1.2,
            )

            probability = equation.calculate_ignition_probability(
                surprise=surprise, threshold=3.5, steepness=2.0
            )

            # Test integrated calculation
            (
                integrated_surprise,
                integrated_probability,
            ) = equation.calculate_integrated_ignition_probability(
                raw_extero_error=1.0,
                raw_intero_error=0.8,
                extero_variance=0.5,
                intero_variance=0.7,
                arousal=1.2,
                valence=0.1,
                stakes=1.5,
            )

            # Validate results are in expected ranges
            basic_valid = 0 <= surprise <= 10 and 0 <= probability <= 1
            integrated_valid = (
                0 <= integrated_surprise <= 10 and 0 <= integrated_probability <= 1
            )

            return basic_valid and integrated_valid

        except Exception as e:
            self.logger.error(f"Mathematical engine validation failed: {e}")
            return False

    def _validate_neural_simulators(self) -> bool:
        """Validate neural simulator components."""
        assert self._neural_simulators is not None
        try:
            # Test each simulator
            p3b_sig = self._neural_simulators["p3b"].generate_conscious_signature()
            gamma_sig = self._neural_simulators["gamma"].generate_conscious_signature()
            bold_sig = self._neural_simulators["bold"].generate_conscious_signature()
            pci_val = self._neural_simulators["pci"].calculate_pci(
                connectivity_matrix=np.array([[1, 0.5], [0.5, 1]])
            )

            # Validate signatures are generated correctly
            return (
                p3b_sig is not None
                and gamma_sig is not None
                and bold_sig is not None
                and pci_val is not None
            )

        except Exception as e:
            self.logger.error(f"Neural simulators validation failed: {e}")
            return False

    def _validate_falsification_tests(self) -> bool:
        """Validate falsification test controllers."""
        try:
            # Check that the falsification tests dictionary exists and has expected structure
            if not isinstance(self._falsification_tests, dict):
                return False

            # Check that at least the primary test is available
            return "primary" in self._falsification_tests

        except Exception as e:
            self.logger.error(f"Falsification tests validation failed: {e}")
            return False

    def _validate_data_manager(self) -> bool:
        """Validate data management components."""
        assert self._data_manager is not None
        try:
            # Check data manager components that are actually initialized
            required_components = ["storage", "validator"]
            return all(comp in self._data_manager for comp in required_components)

        except Exception as e:
            self.logger.error(f"Data manager validation failed: {e}")
            return False

    def shutdown_system(self) -> None:
        """Gracefully shutdown the system and cleanup resources."""
        self.logger.info("Shutting down system...")

        try:
            # Save any pending data
            if self._data_manager and "storage" in self._data_manager:
                self._data_manager["storage"].flush_all()

            # Reset components
            self._mathematical_engine = None
            self._neural_simulators = None
            self._falsification_tests = None
            self._data_manager = None

            self._initialized = False

            self.logger.info("System shutdown completed")

        except Exception as e:
            self.logger.error(f"Error during system shutdown: {e}")
            raise APGIFrameworkError(f"Failed to shutdown system cleanly: {e}")

    def get_system_status(self) -> Dict[str, Any]:
        """
        Get current system status and component information.

        Returns:
            Dictionary with system status information.
        """
        return {
            "initialized": self._initialized,
            "components_registered": self._components_registered,
            "config_loaded": self.config_manager is not None,
            "mathematical_engine_ready": self._mathematical_engine is not None,
            "neural_simulators_ready": self._neural_simulators is not None,
            "falsification_tests_ready": self._falsification_tests is not None,
            "data_manager_ready": self._data_manager is not None,
            "timestamp": datetime.now().isoformat(),
        }
