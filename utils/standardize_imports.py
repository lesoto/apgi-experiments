#!/usr/bin/env python3
"""
Utility script to help standardize imports across the APGI framework.

This script identifies relative imports and suggests absolute import replacements.
"""

import os
import re
from pathlib import Path
from typing import List, Tuple


def find_relative_imports(file_path: Path) -> List[Tuple[int, str, str]]:
    """Find relative imports in a Python file.

    Returns:
        List of (line_number, original_line, suggested_replacement)
    """
    relative_imports = []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return []

    for i, line in enumerate(lines, 1):
        line = line.strip()

        # Match relative imports like "from .module import something"
        if re.match(r"^from\s+\.", line):
            # Convert to absolute import
            # Extract the relative part
            match = re.match(r"^from\s+(\.[.\w]*)\s+import\s+(.+)$", line)
            if match:
                relative_part = match.group(1)
                imports = match.group(2)

                # Convert relative to absolute
                # Remove leading dots and replace with apgi_framework
                absolute_part = relative_part.lstrip(".")
                if absolute_part:
                    suggested = f"from apgi_framework.{absolute_part} import {imports}"
                else:
                    suggested = f"from apgi_framework import {imports}"

                relative_imports.append((i, line, suggested))

    return relative_imports


def scan_directory(directory: Path) -> None:
    """Scan directory for Python files with relative imports."""
    print(f"Scanning {directory} for relative imports...\n")

    total_files = 0
    files_with_relative_imports = 0
    total_relative_imports = 0

    for py_file in directory.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue

        total_files += 1
        relative_imports = find_relative_imports(py_file)

        if relative_imports:
            files_with_relative_imports += 1
            total_relative_imports += len(relative_imports)

            print(f"📁 {py_file}")
            for line_num, original, suggested in relative_imports:
                print(f"  Line {line_num:3d}: {original}")
                print(f"           → {suggested}")
            print()

    print(f"Summary:")
    print(f"  Total Python files: {total_files}")
    print(f"  Files with relative imports: {files_with_relative_imports}")
    print(f"  Total relative imports found: {total_relative_imports}")


if __name__ == "__main__":
    apgi_framework_dir = Path("apgi_framework")
    if apgi_framework_dir.exists():
        scan_directory(apgi_framework_dir)
    else:
        print("apgi_framework directory not found!")
