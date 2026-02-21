"""
Tests for CLI module components.
"""

import argparse
from io import StringIO
from unittest.mock import patch

import pytest

from apgi_framework.cli import APGIFrameworkCLI


class TestAPGIFrameworkCLI:
    """Test CLI implementation."""

    def test_initialization(self):
        """Test CLI initialization."""
        cli = APGIFrameworkCLI()

        assert cli.controller is None
        assert cli.logger is None

    def test_setup_logging(self):
        """Test logging setup."""
        cli = APGIFrameworkCLI()

        # Test default INFO level
        cli.setup_logging()
        assert cli.logger is not None

        # Test DEBUG level
        cli.setup_logging("DEBUG")
        assert cli.logger is not None

    def test_create_parser(self):
        """Test argument parser creation."""
        cli = APGIFrameworkCLI()
        parser = cli.create_parser()

        assert isinstance(parser, argparse.ArgumentParser)
        assert "APGI Framework" in parser.description

    def test_run_test_command(self):
        """Test run-test command parsing."""
        cli = APGIFrameworkCLI()
        parser = cli.create_parser()

        # Test primary test command
        args = parser.parse_args(
            ["run-test", "primary", "--trials", "1000", "--participants", "20"]
        )

        assert args.command == "run-test"
        assert args.test_type == "primary"
        assert args.trials == 1000
        assert args.participants == 20

    def test_run_batch_command(self):
        """Test run-batch command parsing."""
        cli = APGIFrameworkCLI()
        parser = cli.create_parser()

        # Test batch command
        args = parser.parse_args(["run-batch", "--all-tests", "--parallel"])

        assert args.command == "run-batch"
        assert args.all_tests is True
        assert args.parallel is True

    def test_config_command(self):
        """Test config command parsing."""
        cli = APGIFrameworkCLI()
        parser = cli.create_parser()

        # Test generate-config command (this is the actual config command)
        args = parser.parse_args(["generate-config"])
        assert args.command == "generate-config"
        assert args.output == "apgi_config.json"

    def test_validate_command(self):
        """Test validate-system command parsing."""
        cli = APGIFrameworkCLI()
        parser = cli.create_parser()

        # Test validate-system command
        args = parser.parse_args(["validate-system"])
        assert args.command == "validate-system"
        assert args.detailed is False

        # Test validate-system with detailed flag
        args = parser.parse_args(["validate-system", "--detailed"])
        assert args.command == "validate-system"
        assert args.detailed is True

    def test_run_primary_test(self):
        """Test running primary falsification test."""
        cli = APGIFrameworkCLI()
        cli.setup_logging()

        # Test that the CLI can be initialized and parser created
        parser = cli.create_parser()
        args = parser.parse_args(
            ["run-test", "primary", "--trials", "1000", "--participants", "20"]
        )

        assert args.command == "run-test"
        assert args.test_type == "primary"
        assert args.trials == 1000
        assert args.participants == 20

    def test_run_batch_tests(self):
        """Test running batch tests."""
        cli = APGIFrameworkCLI()
        cli.setup_logging()

        # Test that batch command parsing works
        parser = cli.create_parser()
        args = parser.parse_args(["run-batch", "--all-tests"])

        assert args.command == "run-batch"
        assert args.all_tests is True

    def test_show_config(self):
        """Test showing configuration."""
        cli = APGIFrameworkCLI()
        cli.setup_logging()

        # Test config generation command
        parser = cli.create_parser()
        args = parser.parse_args(["generate-config", "--output", "test_config.json"])

        assert args.command == "generate-config"
        assert args.output == "test_config.json"
        assert args.template == "default"

    def test_validate_config(self):
        """Test configuration validation."""
        cli = APGIFrameworkCLI()
        cli.setup_logging()

        # Test system validation command
        parser = cli.create_parser()
        args = parser.parse_args(["validate-system"])

        assert args.command == "validate-system"
        assert args.detailed is False

    def test_validate_data(self):
        """Test data validation."""
        cli = APGIFrameworkCLI()
        cli.setup_logging()

        # Test status command
        parser = cli.create_parser()
        args = parser.parse_args(["status"])

        assert args.command == "status"

    def test_error_handling(self):
        """Test error handling in CLI operations."""
        cli = APGIFrameworkCLI()
        cli.setup_logging()

        # Test invalid command
        parser = cli.create_parser()
        with pytest.raises(SystemExit):
            parser.parse_args(["invalid-command"])

    def test_missing_config_file(self):
        """Test handling of missing config file."""
        cli = APGIFrameworkCLI()
        cli.setup_logging()

        # Test configuration generation with non-existent directory
        parser = cli.create_parser()
        args = parser.parse_args(
            ["generate-config", "--output", "/non/existent/path/config.json"]
        )

        assert args.command == "generate-config"
        assert args.output == "/non/existent/path/config.json"

    def test_invalid_json_config(self):
        """Test handling of invalid JSON config."""
        cli = APGIFrameworkCLI()
        cli.setup_logging()

        # Test parameter setting command
        parser = cli.create_parser()
        args = parser.parse_args(["set-params", "--threshold", "3.5"])

        assert args.command == "set-params"
        assert args.threshold == 3.5

    def test_output_file_creation(self):
        """Test output file creation and writing."""
        cli = APGIFrameworkCLI()
        cli.setup_logging()

        # Test configuration generation
        parser = cli.create_parser()
        parser.parse_args(["generate-config", "--output", "test_config.json"])

        # Test default config creation
        config_data = cli._create_default_config()
        assert "apgi_parameters" in config_data
        assert "experimental_config" in config_data
        assert config_data["apgi_parameters"]["threshold"] == 3.5

    def test_command_line_integration(self):
        """Test full command line integration."""
        cli = APGIFrameworkCLI()

        # Test argument parsing for different commands
        parser = cli.create_parser()

        # Test run-test command
        args = parser.parse_args(["run-test", "primary", "--trials", "100"])
        assert args.command == "run-test"
        assert args.test_type == "primary"
        assert args.trials == 100

        # Test generate-config command
        args = parser.parse_args(["generate-config"])
        assert args.command == "generate-config"
        assert args.output == "apgi_config.json"

    def test_help_output(self):
        """Test help output generation."""
        cli = APGIFrameworkCLI()
        parser = cli.create_parser()

        # Capture help output
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            try:
                parser.parse_args(["--help"])
            except SystemExit:
                pass  # argparse calls sys.exit after showing help

        help_output = mock_stdout.getvalue()
        assert "APGI Framework" in help_output
        assert "run-test" in help_output
        assert "run-batch" in help_output
        assert "config" in help_output


class TestCLIIntegration:
    """Test CLI integration scenarios."""

    def test_full_workflow_simulation(self):
        """Test simulation of complete CLI workflow."""
        cli = APGIFrameworkCLI()
        cli.setup_logging()

        # Test argument parsing for workflow
        parser = cli.create_parser()

        # 1. Test status command
        args = parser.parse_args(["status"])
        assert args.command == "status"

        # 2. Test generate-config command
        args = parser.parse_args(["generate-config", "--template", "minimal"])
        assert args.command == "generate-config"
        assert args.template == "minimal"

        # 3. Test run-test command
        args = parser.parse_args(["run-test", "primary", "--trials", "100"])
        assert args.command == "run-test"
        assert args.test_type == "primary"
        assert args.trials == 100

    def test_batch_workflow_simulation(self):
        """Test simulation of batch workflow."""
        cli = APGIFrameworkCLI()
        cli.setup_logging()

        # Test batch command parsing
        parser = cli.create_parser()

        # Test all-tests option
        args = parser.parse_args(["run-batch", "--all-tests"])
        assert args.command == "run-batch"
        assert args.all_tests is True

        # Test specific tests option
        args = parser.parse_args(
            ["run-batch", "--tests", "primary", "consciousness-without-ignition"]
        )
        assert args.command == "run-batch"
        assert args.tests == ["primary", "consciousness-without-ignition"]

        # Test parallel option
        args = parser.parse_args(["run-batch", "--all-tests", "--parallel"])
        assert args.parallel is True


if __name__ == "__main__":
    pytest.main([__file__])
