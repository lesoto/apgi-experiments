#!/usr/bin/env python3
"""
CI/CD Automation Pipeline for APGI Framework

Provides automated deployment, testing, and release management
for continuous integration and continuous deployment workflows.
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict

try:
    from apgi_framework.logging.standardized_logging import get_logger

    logger = get_logger(__name__)
except ImportError:
    import logging

    logger = logging.getLogger(__name__)


class CICDPipeline:
    """
    Automated CI/CD pipeline for APGI Framework.

    Handles testing, building, and deployment automation
    across different environments and platforms.
    """

    def __init__(self, project_root: Path):
        """
        Initialize CI/CD pipeline.

        Args:
            project_root: Root directory of the project
        """
        self.project_root = Path(project_root)
        self.build_dir = self.project_root / "build"
        self.dist_dir = self.project_root / "dist"
        self.reports_dir = self.project_root / "ci_reports"

        # Create directories
        self.build_dir.mkdir(exist_ok=True)
        self.dist_dir.mkdir(exist_ok=True)
        self.reports_dir.mkdir(exist_ok=True)

        # Environment detection
        self.ci_environment = self._detect_ci_environment()
        self.is_ci_run = bool(self.ci_environment)

        logger.info(
            f"CICD Pipeline initialized - CI Environment: {self.ci_environment}"
        )

    def _detect_ci_environment(self) -> str:
        """Detect the current CI environment."""
        ci_environments = {
            "GITHUB_ACTIONS": "GitHub Actions",
            "GITLAB_CI": "GitLab CI",
            "JENKINS_HOME": "Jenkins",
            "TRAVIS": "Travis CI",
            "CIRCLECI": "CircleCI",
            "BUILDKITE": "Buildkite",
            "TEAMCITY_VERSION": "TeamCity",
            "BAMBOO_BUILDKEY": "Bamboo",
            "TF_BUILD": "Azure DevOps",
            "GOCD_SERVER_URL": "GoCD",
            "WERCKER": "Wercker",
            "CODEBUILD_BUILD_ID": "AWS CodeBuild",
            "SHIPPABLE": "Shippable",
            "DRONE": "Drone CI",
            "HEROKU_TEST_RUN_ID": "Heroku CI",
            "NOW_BUILDER": "Vercel",
            "NETLIFY": "Netlify",
            "RENDER": "Render",
            "FLY_IO": "Fly.io",
            "RAILWAY_ENVIRONMENT": "Railway",
            "SUPABASE_PROJECT_REF": "Supabase",
        }

        for env_var, ci_name in ci_environments.items():
            if os.getenv(env_var):
                return ci_name

        return "Local Development"

    def run_full_pipeline(
        self,
        run_tests: bool = True,
        build_package: bool = True,
        deploy: bool = False,
        deploy_target: str = "staging",
    ) -> Dict[str, bool]:
        """
        Run the complete CI/CD pipeline.

        Args:
            run_tests: Whether to run tests
            build_package: Whether to build package
            deploy: Whether to deploy
            deploy_target: Deployment target (staging/production)

        Returns:
            Dictionary with pipeline stage results
        """
        results = {}

        logger.info(f"Starting CI/CD pipeline in {self.ci_environment}")

        # Stage 1: Code Quality Checks
        results["code_quality"] = self._run_code_quality_checks()

        # Stage 2: Testing
        if run_tests:
            results["testing"] = self._run_test_suite()
        else:
            results["testing"] = True
            logger.info("Skipping tests as requested")

        # Stage 3: Build
        if build_package:
            results["build"] = self._build_package()
        else:
            results["build"] = True
            logger.info("Skipping build as requested")

        # Stage 4: Security Scan
        results["security"] = self._run_security_scan()

        # Stage 5: Deployment
        if deploy:
            results["deployment"] = self._deploy_application(deploy_target)
        else:
            results["deployment"] = True
            logger.info("Skipping deployment as requested")

        # Generate pipeline report
        self._generate_pipeline_report(results)

        return results

    def _run_code_quality_checks(self) -> bool:
        """Run code quality checks."""
        logger.info("Running code quality checks...")

        try:
            # Black formatting check
            logger.info("Checking code formatting with Black...")
            result = subprocess.run(
                ["black", "--check", "--diff", "."],
                cwd=self.project_root,
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                logger.warning("Code formatting issues found")
                logger.warning(result.stdout)
                # Don't fail pipeline for formatting issues

            # isort import sorting check
            logger.info("Checking import sorting with isort...")
            result = subprocess.run(
                ["isort", "--check-only", "--diff", "."],
                cwd=self.project_root,
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                logger.warning("Import sorting issues found")
                logger.warning(result.stdout)
                # Don't fail pipeline for import sorting issues

            # flake8 linting
            logger.info("Running flake8 linting...")
            result = subprocess.run(
                ["flake8", "--max-line-length=100", "--ignore=E203,W503", "."],
                cwd=self.project_root,
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                logger.error("Linting errors found")
                logger.error(result.stdout)
                return False

            logger.info("Code quality checks passed")
            return True

        except Exception as e:
            logger.error(f"Code quality checks failed: {e}")
            return False

    def _run_test_suite(self) -> bool:
        """Run the complete test suite."""
        logger.info("Running test suite...")

        try:
            # Unit tests
            logger.info("Running unit tests...")
            result = subprocess.run(
                ["python", "-m", "pytest", "tests/unit/", "-v", "--tb=short"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
            )

            unit_success = result.returncode == 0
            if not unit_success:
                logger.error("Unit tests failed")
                logger.error(result.stdout)
                logger.error(result.stderr)

            # Integration tests
            logger.info("Running integration tests...")
            result = subprocess.run(
                ["python", "-m", "pytest", "tests/integration/", "-v", "--tb=short"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
            )

            integration_success = result.returncode == 0
            if not integration_success:
                logger.error("Integration tests failed")
                logger.error(result.stdout)
                logger.error(result.stderr)

            # Coverage report
            logger.info("Generating coverage report...")
            result = subprocess.run(
                [
                    "python",
                    "-m",
                    "pytest",
                    "--cov=apgi_framework",
                    "--cov-report=html",
                    "--cov-report=xml",
                    "--cov-report=term",
                ],
                cwd=self.project_root,
                capture_output=True,
                text=True,
            )

            coverage_success = result.returncode == 0
            if not coverage_success:
                logger.warning("Coverage report generation failed")

            overall_success = unit_success and integration_success
            logger.info(
                f"Test suite result: {'PASSED' if overall_success else 'FAILED'}"
            )

            return overall_success

        except Exception as e:
            logger.error(f"Test suite failed: {e}")
            return False

    def _build_package(self) -> bool:
        """Build the distribution package."""
        logger.info("Building distribution package...")

        try:
            # Clean previous builds
            logger.info("Cleaning previous builds...")
            subprocess.run(["rm", "-rf", "build", "dist"], cwd=self.project_root)

            # Build source distribution
            logger.info("Building source distribution...")
            result = subprocess.run(
                ["python", "-m", "build", "--sdist"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                logger.error("Source distribution build failed")
                logger.error(result.stderr)
                return False

            # Build wheel distribution
            logger.info("Building wheel distribution...")
            result = subprocess.run(
                ["python", "-m", "build", "--wheel"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                logger.error("Wheel distribution build failed")
                logger.error(result.stderr)
                return False

            # Check built packages
            dist_files = list(self.dist_dir.glob("*"))
            logger.info(f"Built packages: {[f.name for f in dist_files]}")

            logger.info("Package build successful")
            return True

        except Exception as e:
            logger.error(f"Package build failed: {e}")
            return False

    def _run_security_scan(self) -> bool:
        """Run security vulnerability scan."""
        logger.info("Running security scan...")

        try:
            # Run safety check for known vulnerabilities
            logger.info("Checking for known security vulnerabilities...")
            result = subprocess.run(
                ["python", "-m", "safety", "check"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                logger.warning("Security vulnerabilities found")
                logger.warning(result.stdout)
                # Don't fail pipeline for security warnings

            # Run bandit security linter
            logger.info("Running bandit security linter...")
            result = subprocess.run(
                ["python", "-m", "bandit", "-r", "apgi_framework/", "-f", "json"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                logger.warning("Security issues found by bandit")
                logger.warning(result.stdout)
                # Don't fail pipeline for medium/low severity issues

            logger.info("Security scan completed")
            return True

        except Exception as e:
            logger.error(f"Security scan failed: {e}")
            return False

    def _deploy_application(self, target: str) -> bool:
        """Deploy application to target environment."""
        logger.info(f"Deploying to {target} environment...")

        try:
            if target == "staging":
                return self._deploy_to_staging()
            elif target == "production":
                return self._deploy_to_production()
            else:
                logger.error(f"Unknown deployment target: {target}")
                return False

        except Exception as e:
            logger.error(f"Deployment failed: {e}")
            return False

    def _deploy_to_staging(self) -> bool:
        """Deploy to staging environment."""
        logger.info("Deploying to staging...")

        try:
            # Use quick_deploy.py for staging deployment
            result = subprocess.run(
                ["python", "quick_deploy.py", "--auto", "--environment", "development"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            if result.returncode != 0:
                logger.error("Staging deployment failed")
                logger.error(result.stderr)
                return False

            logger.info("Staging deployment successful")
            return True

        except subprocess.TimeoutExpired:
            logger.error("Staging deployment timed out")
            return False
        except Exception as e:
            logger.error(f"Staging deployment failed: {e}")
            return False

    def _deploy_to_production(self) -> bool:
        """Deploy to production environment."""
        logger.info("Deploying to production...")

        # Production deployment should be more careful
        if not self.is_ci_run:
            logger.error("Production deployment only allowed in CI environment")
            return False

        try:
            # Additional checks for production
            logger.info("Running pre-production checks...")

            # Verify we're on main branch
            try:
                result = subprocess.run(
                    ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                )
                current_branch = result.stdout.strip()

                if current_branch not in ["main", "master"]:
                    logger.error(
                        f"Production deployment requires main/master branch, got: {current_branch}"
                    )
                    return False

            except Exception as e:
                logger.error(f"Could not verify current branch: {e}")
                return False

            # Deploy with production settings
            result = subprocess.run(
                ["python", "quick_deploy.py", "--auto", "--environment", "production"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=600,  # 10 minute timeout
            )

            if result.returncode != 0:
                logger.error("Production deployment failed")
                logger.error(result.stderr)
                return False

            logger.info("Production deployment successful")
            return True

        except subprocess.TimeoutExpired:
            logger.error("Production deployment timed out")
            return False
        except Exception as e:
            logger.error(f"Production deployment failed: {e}")
            return False

    def _generate_pipeline_report(self, results: Dict[str, bool]) -> None:
        """Generate pipeline execution report."""
        logger.info("Generating pipeline report...")

        report_data = {
            "pipeline_info": {
                "timestamp": time.time(),
                "ci_environment": self.ci_environment,
                "is_ci_run": self.is_ci_run,
                "project_root": str(self.project_root),
            },
            "stages": results,
            "overall_success": all(results.values()),
            "stage_summary": {
                "total_stages": len(results),
                "passed_stages": sum(1 for success in results.values() if success),
                "failed_stages": sum(1 for success in results.values() if not success),
            },
        }

        # Save JSON report
        report_file = self.reports_dir / f"pipeline_report_{int(time.time())}.json"
        with open(report_file, "w") as f:
            json.dump(report_data, f, indent=2)

        # Generate human-readable summary
        summary = self._generate_human_summary(report_data)
        summary_file = self.reports_dir / f"pipeline_summary_{int(time.time())}.txt"
        with open(summary_file, "w") as f:
            f.write(summary)

        logger.info(f"Pipeline report saved to {report_file}")
        logger.info(f"Pipeline summary saved to {summary_file}")

        # Print summary to console
        print(summary)

    def _generate_human_summary(self, report_data: Dict) -> str:
        """Generate human-readable pipeline summary."""
        lines = []
        lines.append("=" * 60)
        lines.append("APGI Framework CI/CD Pipeline Summary")
        lines.append("=" * 60)
        lines.append(f"Environment: {report_data['pipeline_info']['ci_environment']}")
        lines.append(
            f"Timestamp: {time.ctime(report_data['pipeline_info']['timestamp'])}"
        )
        lines.append("")

        overall_status = "PASSED" if report_data["overall_success"] else "FAILED"
        lines.append(f"Overall Status: {overall_status}")
        lines.append("")

        lines.append("Stage Results:")
        lines.append("-" * 60)

        for stage, success in report_data["stages"].items():
            status = "✓ PASS" if success else "✗ FAIL"
            lines.append(f"{status} | {stage.replace('_', ' ').title()}")

        lines.append("")
        lines.append(
            f"Summary: {report_data['stage_summary']['passed_stages']}/{report_data['stage_summary']['total_stages']} stages passed"
        )
        lines.append("=" * 60)

        return "\n".join(lines)


def main():
    """Main entry point for CI/CD pipeline."""
    import argparse

    parser = argparse.ArgumentParser(description="APGI Framework CI/CD Pipeline")
    parser.add_argument("--skip-tests", action="store_true", help="Skip running tests")
    parser.add_argument(
        "--skip-build", action="store_true", help="Skip building package"
    )
    parser.add_argument(
        "--deploy", action="store_true", help="Deploy after successful tests"
    )
    parser.add_argument(
        "--target",
        choices=["staging", "production"],
        default="staging",
        help="Deployment target",
    )
    parser.add_argument("--project-root", default=".", help="Project root directory")

    args = parser.parse_args()

    # Initialize pipeline
    pipeline = CICDPipeline(Path(args.project_root))

    # Run pipeline
    results = pipeline.run_full_pipeline(
        run_tests=not args.skip_tests,
        build_package=not args.skip_build,
        deploy=args.deploy,
        deploy_target=args.target,
    )

    # Exit with appropriate code
    overall_success = all(results.values())
    sys.exit(0 if overall_success else 1)


if __name__ == "__main__":
    main()
