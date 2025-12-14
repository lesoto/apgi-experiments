"""
Command-Line Interface for APGI Framework Falsification Testing System.

This module provides a comprehensive CLI for running individual falsification tests,
batch experiment execution, and configuration management.
"""

import argparse
import sys
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

from .main_controller import MainApplicationController
from .config import ConfigManager, APGIParameters, ExperimentalConfig
from .exceptions import APGIFrameworkError, ConfigurationError


class APGIFrameworkCLI:
    """Command-line interface for the APGI Framework Falsification Testing System."""
    
    def __init__(self):
        """Initialize the CLI."""
        self.controller = None
        self.logger = None
    
    def setup_logging(self, log_level: str = "INFO") -> None:
        """Setup logging for CLI operations."""
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[logging.StreamHandler()]
        )
        self.logger = logging.getLogger(__name__)
    
    def create_parser(self) -> argparse.ArgumentParser:
        """Create and configure the argument parser."""
        parser = argparse.ArgumentParser(
            description="APGI Framework Falsification Testing System",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  # Run primary falsification test
  python -m apgi_framework.cli run-test primary --trials 1000
  
  # Run all tests in batch mode
  python -m apgi_framework.cli run-batch --config config.json
  
  # Generate default configuration
  python -m apgi_framework.cli generate-config --output config.json
  
  # Validate system components
  python -m apgi_framework.cli validate-system
            """
        )
        
        # Global options
        parser.add_argument(
            '--config', '-c',
            type=str,
            help='Path to configuration file'
        )
        
        parser.add_argument(
            '--log-level', '-l',
            choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
            default='INFO',
            help='Set logging level (default: INFO)'
        )
        
        parser.add_argument(
            '--output-dir', '-o',
            type=str,
            help='Output directory for results'
        )
        
        # Subcommands
        subparsers = parser.add_subparsers(dest='command', help='Available commands')
        
        # Run individual test command
        test_parser = subparsers.add_parser('run-test', help='Run individual falsification test')
        test_parser.add_argument(
            'test_type',
            choices=['primary', 'consciousness-without-ignition', 'threshold-insensitivity', 'soma-bias'],
            help='Type of falsification test to run'
        )
        test_parser.add_argument(
            '--trials', '-n',
            type=int,
            default=1000,
            help='Number of trials to run (default: 1000)'
        )
        test_parser.add_argument(
            '--participants', '-p',
            type=int,
            default=100,
            help='Number of participants to simulate (default: 100)'
        )
        test_parser.add_argument(
            '--seed',
            type=int,
            help='Random seed for reproducibility'
        )
        
        # Run batch experiments command
        batch_parser = subparsers.add_parser('run-batch', help='Run batch experiments')
        batch_parser.add_argument(
            '--all-tests',
            action='store_true',
            help='Run all falsification tests'
        )
        batch_parser.add_argument(
            '--tests',
            nargs='+',
            choices=['primary', 'consciousness-without-ignition', 'threshold-insensitivity', 'soma-bias'],
            help='Specific tests to run in batch'
        )
        batch_parser.add_argument(
            '--parallel',
            action='store_true',
            help='Run tests in parallel (experimental)'
        )
        
        # Configuration management commands
        config_parser = subparsers.add_parser('generate-config', help='Generate configuration file')
        config_parser.add_argument(
            '--output',
            type=str,
            default='apgi_config.json',
            help='Output path for configuration file (default: apgi_config.json)'
        )
        config_parser.add_argument(
            '--template',
            choices=['default', 'minimal', 'comprehensive'],
            default='default',
            help='Configuration template to use (default: default)'
        )
        
        # System validation command
        validate_parser = subparsers.add_parser('validate-system', help='Validate system components')
        validate_parser.add_argument(
            '--detailed',
            action='store_true',
            help='Show detailed validation results'
        )
        
        # Status command
        status_parser = subparsers.add_parser('status', help='Show system status')
        
        # Parameter override commands
        param_parser = subparsers.add_parser('set-params', help='Set APGI parameters')
        param_parser.add_argument('--extero-precision', type=float, help='Exteroceptive precision')
        param_parser.add_argument('--intero-precision', type=float, help='Interoceptive precision')
        param_parser.add_argument('--threshold', type=float, help='Ignition threshold')
        param_parser.add_argument('--steepness', type=float, help='Sigmoid steepness')
        param_parser.add_argument('--somatic-gain', type=float, help='Somatic marker gain')
        
        return parser
    
    def initialize_controller(self, config_path: Optional[str] = None) -> None:
        """Initialize the main application controller."""
        try:
            self.controller = MainApplicationController(config_path)
            self.controller.initialize_system()
            self.logger.info("System initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize system: {e}")
            sys.exit(1)
    
    def run_individual_test(self, args: argparse.Namespace) -> None:
        """Run an individual falsification test."""
        self.logger.info(f"Running {args.test_type} test with {args.trials} trials")
        
        try:
            # Update configuration if parameters provided
            if args.trials:
                self.controller.config_manager.update_experimental_config(n_trials=args.trials)
            if args.participants:
                self.controller.config_manager.update_experimental_config(n_participants=args.participants)
            if args.seed:
                self.controller.config_manager.update_experimental_config(random_seed=args.seed)
            
            # Get falsification tests
            tests = self.controller.get_falsification_tests()
            
            # Run the specified test
            if args.test_type == 'primary':
                result = tests['primary'].run_test(n_trials=args.trials)
            elif args.test_type == 'consciousness-without-ignition':
                result = tests['consciousness_without_ignition'].run_test(n_trials=args.trials)
            elif args.test_type == 'threshold-insensitivity':
                result = tests['threshold_insensitivity'].run_test()
            elif args.test_type == 'soma-bias':
                result = tests['soma_bias'].run_test(n_participants=args.participants)
            
            # Display results
            self._display_test_result(result, args.test_type)
            
            # Save results
            self._save_test_result(result, args.test_type)
            
        except Exception as e:
            self.logger.error(f"Test execution failed: {e}")
            sys.exit(1)
    
    def run_batch_experiments(self, args: argparse.Namespace) -> None:
        """Run batch experiments."""
        self.logger.info("Running batch experiments")
        
        try:
            # Determine which tests to run
            if args.all_tests:
                test_types = ['primary', 'consciousness-without-ignition', 'threshold-insensitivity', 'soma-bias']
            elif args.tests:
                test_types = args.tests
            else:
                self.logger.error("Must specify either --all-tests or --tests")
                sys.exit(1)
            
            results = {}
            tests = self.controller.get_falsification_tests()
            
            for test_type in test_types:
                self.logger.info(f"Running {test_type} test...")
                
                try:
                    if test_type == 'primary':
                        result = tests['primary'].run_test()
                    elif test_type == 'consciousness-without-ignition':
                        result = tests['consciousness_without_ignition'].run_test()
                    elif test_type == 'threshold-insensitivity':
                        result = tests['threshold_insensitivity'].run_test()
                    elif test_type == 'soma-bias':
                        result = tests['soma_bias'].run_test()
                    
                    results[test_type] = result
                    self.logger.info(f"Completed {test_type} test")
                    
                except Exception as e:
                    self.logger.error(f"Failed to run {test_type} test: {e}")
                    results[test_type] = {'error': str(e)}
            
            # Display batch results
            self._display_batch_results(results)
            
            # Save batch results
            self._save_batch_results(results)
            
        except Exception as e:
            self.logger.error(f"Batch execution failed: {e}")
            sys.exit(1)
    
    def generate_configuration(self, args: argparse.Namespace) -> None:
        """Generate a configuration file."""
        self.logger.info(f"Generating {args.template} configuration file: {args.output}")
        
        try:
            if args.template == 'minimal':
                config_data = self._create_minimal_config()
            elif args.template == 'comprehensive':
                config_data = self._create_comprehensive_config()
            else:  # default
                config_data = self._create_default_config()
            
            # Create output directory if needed
            Path(args.output).parent.mkdir(parents=True, exist_ok=True)
            
            # Save configuration
            with open(args.output, 'w') as f:
                json.dump(config_data, f, indent=2)
            
            self.logger.info(f"Configuration saved to {args.output}")
            
        except Exception as e:
            self.logger.error(f"Failed to generate configuration: {e}")
            sys.exit(1)
    
    def validate_system(self, args: argparse.Namespace) -> None:
        """Validate system components."""
        self.logger.info("Validating system components...")
        
        try:
            validation_results = self.controller.run_system_validation()
            
            if args.detailed:
                self._display_detailed_validation(validation_results)
            else:
                self._display_simple_validation(validation_results)
            
            if not validation_results.get('overall', False):
                sys.exit(1)
                
        except Exception as e:
            self.logger.error(f"System validation failed: {e}")
            sys.exit(1)
    
    def show_status(self, args: argparse.Namespace) -> None:
        """Show system status."""
        try:
            status = self.controller.get_system_status()
            self._display_system_status(status)
        except Exception as e:
            self.logger.error(f"Failed to get system status: {e}")
            sys.exit(1)
    
    def set_parameters(self, args: argparse.Namespace) -> None:
        """Set APGI parameters."""
        try:
            updates = {}
            if args.extero_precision is not None:
                updates['extero_precision'] = args.extero_precision
            if args.intero_precision is not None:
                updates['intero_precision'] = args.intero_precision
            if args.threshold is not None:
                updates['threshold'] = args.threshold
            if args.steepness is not None:
                updates['steepness'] = args.steepness
            if args.somatic_gain is not None:
                updates['somatic_gain'] = args.somatic_gain
            
            if updates:
                self.controller.config_manager.update_apgi_parameters(**updates)
                self.logger.info(f"Updated parameters: {updates}")
            else:
                self.logger.warning("No parameters specified to update")
                
        except Exception as e:
            self.logger.error(f"Failed to set parameters: {e}")
            sys.exit(1)
    
    def _display_test_result(self, result: Any, test_type: str) -> None:
        """Display individual test result."""
        print(f"\n{'='*60}")
        print(f"APGI Framework Falsification Test Results: {test_type.upper()}")
        print(f"{'='*60}")
        
        if hasattr(result, 'is_falsified'):
            print(f"Falsification Status: {'FALSIFIED' if result.is_falsified else 'NOT FALSIFIED'}")
            print(f"Confidence Level: {result.confidence_level:.3f}")
            print(f"Effect Size: {result.effect_size:.3f}")
            print(f"P-value: {result.p_value:.6f}")
            print(f"Statistical Power: {result.statistical_power:.3f}")
        else:
            print(f"Result: {result}")
        
        print(f"{'='*60}\n")
    
    def _display_batch_results(self, results: Dict[str, Any]) -> None:
        """Display batch experiment results."""
        print(f"\n{'='*80}")
        print("APGI Framework Batch Falsification Test Results")
        print(f"{'='*80}")
        
        for test_type, result in results.items():
            print(f"\n{test_type.upper()}:")
            if 'error' in result:
                print(f"  ERROR: {result['error']}")
            elif hasattr(result, 'is_falsified'):
                print(f"  Falsified: {'YES' if result.is_falsified else 'NO'}")
                print(f"  Confidence: {result.confidence_level:.3f}")
                print(f"  Effect Size: {result.effect_size:.3f}")
                print(f"  P-value: {result.p_value:.6f}")
            else:
                print(f"  Result: {result}")
        
        print(f"\n{'='*80}\n")
    
    def _display_detailed_validation(self, results: Dict[str, Any]) -> None:
        """Display detailed validation results."""
        print(f"\n{'='*60}")
        print("System Validation Results (Detailed)")
        print(f"{'='*60}")
        
        for component, status in results.items():
            if component != 'overall':
                status_str = "PASS" if status else "FAIL"
                print(f"{component.replace('_', ' ').title()}: {status_str}")
        
        overall_status = "PASS" if results.get('overall', False) else "FAIL"
        print(f"\nOverall Status: {overall_status}")
        print(f"{'='*60}\n")
    
    def _display_simple_validation(self, results: Dict[str, Any]) -> None:
        """Display simple validation results."""
        overall_status = "PASS" if results.get('overall', False) else "FAIL"
        print(f"System Validation: {overall_status}")
    
    def _display_system_status(self, status: Dict[str, Any]) -> None:
        """Display system status."""
        print(f"\n{'='*50}")
        print("APGI Framework System Status")
        print(f"{'='*50}")
        
        for key, value in status.items():
            if key != 'timestamp':
                display_key = key.replace('_', ' ').title()
                display_value = "YES" if value else "NO" if isinstance(value, bool) else str(value)
                print(f"{display_key}: {display_value}")
        
        print(f"Last Updated: {status.get('timestamp', 'Unknown')}")
        print(f"{'='*50}\n")
    
    def _save_test_result(self, result: Any, test_type: str) -> None:
        """Save individual test result to file."""
        try:
            output_dir = Path(self.controller.config_manager.get_experimental_config().output_directory)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = output_dir / f"{test_type}_result_{timestamp}.json"
            
            # Convert result to dictionary for JSON serialization
            if hasattr(result, '__dict__'):
                result_dict = result.__dict__
            else:
                result_dict = {'result': str(result)}
            
            with open(filename, 'w') as f:
                json.dump(result_dict, f, indent=2, default=str)
            
            self.logger.info(f"Results saved to {filename}")
            
        except Exception as e:
            self.logger.warning(f"Failed to save results: {e}")
    
    def _save_batch_results(self, results: Dict[str, Any]) -> None:
        """Save batch experiment results to file."""
        try:
            output_dir = Path(self.controller.config_manager.get_experimental_config().output_directory)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = output_dir / f"batch_results_{timestamp}.json"
            
            # Convert results to dictionary for JSON serialization
            results_dict = {}
            for test_type, result in results.items():
                if hasattr(result, '__dict__'):
                    results_dict[test_type] = result.__dict__
                else:
                    results_dict[test_type] = {'result': str(result)}
            
            with open(filename, 'w') as f:
                json.dump(results_dict, f, indent=2, default=str)
            
            self.logger.info(f"Batch results saved to {filename}")
            
        except Exception as e:
            self.logger.warning(f"Failed to save batch results: {e}")
    
    def _create_default_config(self) -> Dict[str, Any]:
        """Create default configuration."""
        return {
            "apgi_parameters": {
                "extero_precision": 2.0,
                "intero_precision": 1.5,
                "extero_error": 1.2,
                "intero_error": 0.8,
                "somatic_gain": 1.3,
                "threshold": 3.5,
                "steepness": 2.0
            },
            "experimental_config": {
                "n_trials": 1000,
                "n_participants": 100,
                "random_seed": None,
                "output_directory": "results",
                "log_level": "INFO",
                "save_intermediate": True,
                "p3b_threshold": 5.0,
                "gamma_plv_threshold": 0.3,
                "bold_z_threshold": 3.1,
                "pci_threshold": 0.4,
                "alpha_level": 0.05,
                "effect_size_threshold": 0.5,
                "power_threshold": 0.8
            }
        }
    
    def _create_minimal_config(self) -> Dict[str, Any]:
        """Create minimal configuration."""
        return {
            "apgi_parameters": {
                "threshold": 3.5,
                "steepness": 2.0
            },
            "experimental_config": {
                "n_trials": 100,
                "output_directory": "results"
            }
        }
    
    def _create_comprehensive_config(self) -> Dict[str, Any]:
        """Create comprehensive configuration with all options."""
        config = self._create_default_config()
        
        # Add additional comprehensive options
        config["experimental_config"].update({
            "detailed_logging": True,
            "save_raw_data": True,
            "generate_plots": True,
            "statistical_corrections": ["fdr", "bonferroni"],
            "bootstrap_iterations": 10000,
            "confidence_interval": 0.95
        })
        
        return config
    
    def run(self, args: List[str] = None) -> None:
        """Main entry point for the CLI."""
        parser = self.create_parser()
        parsed_args = parser.parse_args(args)
        
        # Setup logging
        self.setup_logging(parsed_args.log_level)
        
        # Handle case where no command is provided
        if not parsed_args.command:
            parser.print_help()
            return
        
        # Initialize controller for commands that need it
        if parsed_args.command not in ['generate-config']:
            self.initialize_controller(parsed_args.config)
        
        # Override output directory if provided
        if parsed_args.output_dir and self.controller:
            self.controller.config_manager.update_experimental_config(
                output_directory=parsed_args.output_dir
            )
        
        # Execute the requested command
        try:
            if parsed_args.command == 'run-test':
                self.run_individual_test(parsed_args)
            elif parsed_args.command == 'run-batch':
                self.run_batch_experiments(parsed_args)
            elif parsed_args.command == 'generate-config':
                self.generate_configuration(parsed_args)
            elif parsed_args.command == 'validate-system':
                self.validate_system(parsed_args)
            elif parsed_args.command == 'status':
                self.show_status(parsed_args)
            elif parsed_args.command == 'set-params':
                self.set_parameters(parsed_args)
            else:
                self.logger.error(f"Unknown command: {parsed_args.command}")
                sys.exit(1)
                
        except KeyboardInterrupt:
            self.logger.info("Operation cancelled by user")
            sys.exit(0)
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            sys.exit(1)
        finally:
            # Cleanup
            if self.controller:
                try:
                    self.controller.shutdown_system()
                except Exception as e:
                    self.logger.warning(f"Error during cleanup: {e}")


def main():
    """Entry point for the CLI when run as a module."""
    cli = APGIFrameworkCLI()
    cli.run()


if __name__ == '__main__':
    main()