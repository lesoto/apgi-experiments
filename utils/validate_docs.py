"""
Documentation link validation utilities for APGI Framework.

This module validates that all documentation links in README.md
resolve to existing files.
"""

import os
from pathlib import Path
from typing import List, Dict, Tuple
import re


class DocumentationValidator:
    """Validates documentation links in README.md."""

    def __init__(self, readme_path: str = "README.md"):
        self.readme_path = Path(readme_path)
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def extract_links(self, content: str) -> List[Tuple[str, str]]:
        """Extract markdown links from content."""
        # Pattern to match markdown links: [text](url)
        pattern = r"\[([^\]]+)\]\(([^)]+)\)"
        matches = re.findall(pattern, content)
        return [(match[0], match[1]) for match in matches]

    def validate_link(self, link_text: str, url: str) -> Tuple[bool, str]:
        """Validate a single documentation link."""
        try:
            # Convert relative URL to absolute path
            if url.startswith("./"):
                url = url[2:]  # Remove ./
                full_path = self.readme_path.parent / url
            elif url.startswith("docs/"):
                full_path = self.readme_path.parent / url
            else:
                full_path = self.readme_path.parent / url

            # Check if file/directory exists
            exists = full_path.exists()

            if not exists:
                return False, f"Documentation not found: {full_path}"

            # For directories, check if they contain index files
            if full_path.is_dir():
                index_files = [
                    full_path / "README.md",
                    full_path / "index.md",
                    full_path / "index.html",
                ]
                has_index = any(f.exists() for f in index_files)

                if not has_index:
                    return (
                        False,
                        f"Documentation directory missing index file: {full_path}",
                    )

            return True, "Valid"

        except Exception as e:
            return False, f"Error validating link {link_text}: {e}"

    def validate_all_links(self) -> Dict[str, any]:
        """Validate all documentation links in README.md."""
        try:
            with open(self.readme_path, "r", encoding="utf-8") as f:
                content = f.read()

            links = self.extract_links(content)
            results = {
                "total_links": len(links),
                "valid_links": 0,
                "broken_links": 0,
                "warnings": 0,
                "details": [],
            }

            for link_text, url in links:
                is_valid, message = self.validate_link(link_text, url)

                if is_valid:
                    results["valid_links"] += 1
                else:
                    results["broken_links"] += 1
                    results["details"].append(
                        {"link_text": link_text, "url": url, "error": message}
                    )

            # Check for documentation structure warnings
            docs_dir = self.readme_path.parent / "docs"
            if docs_dir.exists():
                required_dirs = ["developer", "api", "experimental", "user"]
                existing_dirs = [d.name for d in docs_dir.iterdir() if d.is_dir()]

                missing_dirs = set(required_dirs) - set(existing_dirs)
                if missing_dirs:
                    results["warnings"] += len(missing_dirs)
                    for missing_dir in missing_dirs:
                        results["details"].append(
                            {
                                "type": "missing_directory",
                                "path": f"docs/{missing_dir}",
                                "message": f"Documentation directory not found: {missing_dir}",
                            }
                        )

            return results

        except FileNotFoundError:
            return {
                "error": "README.md file not found",
                "total_links": 0,
                "valid_links": 0,
                "broken_links": 0,
                "warnings": 0,
                "details": [],
            }
        except Exception as e:
            return {
                "error": f"Error reading README.md: {e}",
                "total_links": 0,
                "valid_links": 0,
                "broken_links": 0,
                "warnings": 0,
                "details": [],
            }


def validate_documentation_links(readme_path: str = "README.md") -> Dict[str, any]:
    """
    Validate all documentation links in README.md.

    Args:
        readme_path: Path to README.md file

    Returns:
        Dictionary with validation results
    """
    validator = DocumentationValidator(readme_path)
    return validator.validate_all_links()


if __name__ == "__main__":
    # Run validation when script is executed directly
    import sys

    readme_path = sys.argv[1] if len(sys.argv) > 1 else "README.md"
    results = validate_documentation_links(readme_path)

    print("Documentation Link Validation Results")
    print("=" * 50)

    if "error" in results:
        print(f"ERROR: {results['error']}")
        sys.exit(1)

    print(f"Total links found: {results['total_links']}")
    print(f"Valid links: {results['valid_links']}")
    print(f"Broken links: {results['broken_links']}")
    print(f"Warnings: {results['warnings']}")

    if results["details"]:
        print("\nDetails:")
        for detail in results["details"]:
            print(f"  - Detail: {detail}")

    if results["broken_links"] == 0 and results["warnings"] == 0:
        print("✅ All documentation links are valid!")
    else:
        print("❌ Some documentation issues found.")
        sys.exit(1)
