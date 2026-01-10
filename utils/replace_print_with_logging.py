#!/usr/bin/env python3
"""
Script to systematically replace print() statements with proper logging.

This script scans Python files and replaces print() statements with
appropriate logging calls using the standardized logging system.
"""

import ast
import re
from pathlib import Path
from typing import List, Dict, Any, Tuple
import logging


class PrintStatementTransformer(ast.NodeTransformer):
    """AST transformer to replace print() statements with logging calls."""

    def __init__(self, module_name: str):
        self.module_name = module_name
        self.imports_added = False

    def visit_Import(self, node):
        """Handle import statements."""
        for alias in node.names:
            if alias.name == "print":
                # Skip print imports (shouldn't exist but just in case)
                return None
        return node

    def visit_ImportFrom(self, node):
        """Handle from-import statements."""
        if node.module == "__future__":
            # Remove print_function from future imports
            node.names = [
                alias for alias in node.names if alias.name != "print_function"
            ]
            if not node.names:
                return None
        return node

    def visit_Call(self, node):
        """Replace print() calls with logging calls."""
        if isinstance(node.func, ast.Name) and node.func.id == "print":

            # Determine appropriate logging level based on context
            log_level = self._determine_log_level(node)

            # Create logging call
            logger_name = ast.Name(id="logger", ctx=ast.Load())
            log_method = ast.Attribute(
                value=logger_name, attr=log_level, ctx=ast.Load()
            )

            # Convert print arguments to logging arguments
            if len(node.args) == 1 and isinstance(node.args[0], ast.Str):
                # Simple string literal
                return ast.Call(func=log_method, args=node.args, keywords=[])
            else:
                # Complex expression - convert to f-string if possible
                if len(node.args) > 1:
                    # Multiple arguments - join them
                    args = []
                    for arg in node.args:
                        if isinstance(arg, ast.Str):
                            args.append(arg)
                        else:
                            # Convert non-string arguments to str()
                            args.append(
                                ast.Call(
                                    func=ast.Name(id="str", ctx=ast.Load()),
                                    args=[arg],
                                    keywords=[],
                                )
                            )

                    # Create joined string
                    joined = ast.Call(
                        func=ast.Attribute(
                            value=ast.Str(s=" "), attr="join", ctx=ast.Load()
                        ),
                        args=[ast.List(elts=args, ctx=ast.Load())],
                        keywords=[],
                    )

                    return ast.Call(func=log_method, args=[joined], keywords=[])
                else:
                    # Single argument
                    return ast.Call(func=log_method, args=node.args, keywords=[])

        return self.generic_visit(node)

    def _determine_log_level(self, node: ast.Call) -> str:
        """Determine appropriate logging level based on context."""
        # Simple heuristic - could be enhanced with more sophisticated analysis
        if len(node.args) > 0:
            if isinstance(node.args[0], ast.Str):
                msg = node.args[0].s.lower()
                if any(
                    word in msg for word in ["error", "failed", "exception", "critical"]
                ):
                    return "error"
                elif any(word in msg for word in ["warning", "warn", "deprecated"]):
                    return "warning"
                elif any(word in msg for word in ["debug", "trace", "verbose"]):
                    return "debug"

        return "info"


def replace_print_in_file(file_path: Path, dry_run: bool = True) -> Dict[str, Any]:
    """
    Replace print statements in a Python file with logging calls.

    Args:
        file_path: Path to Python file
        dry_run: If True, only report changes without modifying file

    Returns:
        Dictionary with transformation results
    """
    result = {
        "file_path": str(file_path),
        "modified": False,
        "print_count": 0,
        "changes": [],
        "errors": [],
    }

    try:
        # Read file content
        content = file_path.read_text(encoding="utf-8")

        # Parse AST
        tree = ast.parse(content)

        # Count print statements
        print_finder = PrintStatementFinder()
        print_finder.visit(tree)
        result["print_count"] = len(print_finder.print_nodes)

        if result["print_count"] == 0:
            return result

        # Transform AST
        module_name = file_path.stem
        transformer = PrintStatementTransformer(module_name)
        transformed_tree = transformer.visit(transformed_tree)

        # Fix missing locations
        ast.fix_missing_locations(transformed_tree)

        # Generate new code
        new_code = ast.unparse(transformed_tree)

        # Add logging import if needed
        if not transformer.imports_added:
            import_pattern = r"(from apgi_framework\.logging\.standardized_logging import get_logger)"
            if not re.search(import_pattern, content):
                # Add import at the top
                lines = new_code.split("\n")
                import_line = "from apgi_framework.logging.standardized_logging import get_logger\n"

                # Find good place to insert (after docstring, before other code)
                insert_pos = 0
                for i, line in enumerate(lines):
                    if line.strip().startswith('"""') and i + 1 < len(lines):
                        # Skip docstring
                        while i + 1 < len(lines) and not lines[i + 1].strip().endswith(
                            '"""'
                        ):
                            i += 1
                        insert_pos = i + 2
                        break
                    elif line.strip() and not line.strip().startswith("#"):
                        insert_pos = i
                        break

                lines.insert(insert_pos, import_line)

                # Add logger initialization
                logger_init = "logger = get_logger(__name__)\n"
                lines.insert(insert_pos + 1, logger_init)

                new_code = "\n".join(lines)
                result["changes"].append(
                    "Added logging import and logger initialization"
                )

        result["changes"].append(f'Replaced {result["print_count"]} print() statements')
        result["modified"] = True

        if not dry_run:
            file_path.write_text(new_code, encoding="utf-8")
            result["changes"].append("File updated")
        else:
            result["changes"].append("Dry run - file not modified")

    except Exception as e:
        result["errors"].append(str(e))

    return result


class PrintStatementFinder(ast.NodeVisitor):
    """AST visitor to find print statements."""

    def __init__(self):
        self.print_nodes = []

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name) and node.func.id == "print":
            self.print_nodes.append(node)
        self.generic_visit(node)


def scan_directory_for_prints(directory: Path) -> Dict[str, Any]:
    """
    Scan directory for print statements in Python files.

    Args:
        directory: Directory to scan

    Returns:
        Dictionary with scan results
    """
    results = {
        "directory": str(directory),
        "files_scanned": 0,
        "files_with_prints": 0,
        "total_print_statements": 0,
        "files": [],
    }

    for py_file in directory.rglob("*.py"):
        if "__pycache__" in str(py_file) or ".git" in str(py_file):
            continue

        try:
            content = py_file.read_text(encoding="utf-8")
            tree = ast.parse(content)

            finder = PrintStatementFinder()
            finder.visit(tree)

            if finder.print_nodes:
                results["files_with_prints"] += 1
                results["total_print_statements"] += len(finder.print_nodes)

                file_result = {
                    "path": str(py_file),
                    "print_count": len(finder.print_nodes),
                    "locations": [f"Line {node.lineno}" for node in finder.print_nodes],
                }
                results["files"].append(file_result)

            results["files_scanned"] += 1

        except Exception as e:
            results["files"].append({"path": str(py_file), "error": str(e)})

    return results


def main():
    """Main function to run the print-to-logging migration."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Replace print() statements with logging"
    )
    parser.add_argument("path", help="Path to scan (file or directory)")
    parser.add_argument(
        "--dry-run", action="store_true", help="Only show changes, don't modify"
    )
    parser.add_argument("--apply", action="store_true", help="Apply changes to files")
    parser.add_argument(
        "--scan-only", action="store_true", help="Only scan for print statements"
    )

    args = parser.parse_args()

    path = Path(args.path)

    if args.scan_only:
        # Just scan for print statements
        if path.is_file():
            results = scan_directory_for_prints(path.parent)
            file_results = [f for f in results["files"] if f["path"] == str(path)]
        else:
            results = scan_directory_for_prints(path)
            file_results = results["files"]

        print(f"Scan results for: {path}")
        print(f"Files scanned: {results['files_scanned']}")
        print(f"Files with prints: {results['files_with_prints']}")
        print(f"Total print statements: {results['total_print_statements']}")

        for file_result in file_results:
            if "error" in file_result:
                print(f"ERROR in {file_result['path']}: {file_result['error']}")
            else:
                print(f"{file_result['path']}: {file_result['print_count']} prints")

        return

    # Replace print statements
    if path.is_file():
        # Single file
        result = replace_print_in_file(path, dry_run=not args.apply)
        print(f"File: {result['file_path']}")
        print(f"Print statements found: {result['print_count']}")
        print(f"Modified: {result['modified']}")
        if result["changes"]:
            print("Changes:")
            for change in result["changes"]:
                print(f"  - {change}")
        if result["errors"]:
            print("Errors:")
            for error in result["errors"]:
                print(f"  - {error}")
    else:
        # Directory
        print(f"Scanning directory: {path}")
        for py_file in path.rglob("*.py"):
            if "__pycache__" in str(py_file) or ".git" in str(py_file):
                continue

            result = replace_print_in_file(py_file, dry_run=not args.apply)
            if result["print_count"] > 0:
                print(f"\n{result['file_path']}: {result['print_count']} prints")
                for change in result["changes"]:
                    print(f"  {change}")
                for error in result["errors"]:
                    print(f"  ERROR: {error}")


if __name__ == "__main__":
    main()
