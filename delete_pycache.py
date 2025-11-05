import argparse
import fnmatch
import os
import shutil
import sys
from typing import Iterable, List


DEFAULT_DIR_NAMES = {
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".hypothesis",
    "htmlcov",
    ".tox",
    ".ipynb_checkpoints",
    ".cache",
    "build",
    "dist",
}

DEFAULT_DIR_PATTERNS = ["*.egg-info", "pip-wheel-metadata"]

DEFAULT_FILE_PATTERNS = [
    "*.pyc",
    "*.pyo",
    "*.pyd",
    ".coverage",
    "coverage.xml",
    ".coverage.*",
    "*.log",
    ".DS_Store",
    "Thumbs.db",
]


def matches_any(name: str, patterns: Iterable[str]) -> bool:
    for pat in patterns:
        if fnmatch.fnmatch(name, pat):
            return True
    return False


def delete_temporary_items(root_dir: str, dry_run: bool = False, verbose: bool = True):
    """Delete common temporary directories and files under root_dir.

    - Removes directories in DEFAULT_DIR_NAMES and those matching DEFAULT_DIR_PATTERNS.
    - Removes files matching DEFAULT_FILE_PATTERNS.
    - Removes directories matching patterns (like '*.egg-info').

    This function avoids descending into removed directories by modifying dirnames in-place.
    """
    for dirpath, dirnames, filenames in os.walk(root_dir, topdown=True):
        # copy list because we may modify dirnames
        for d in list(dirnames):
            full_d = os.path.join(dirpath, d)
            if d in DEFAULT_DIR_NAMES or matches_any(d, DEFAULT_DIR_PATTERNS):
                if dry_run:
                    if verbose:
                        print(f"Would remove directory: {full_d}")
                else:
                    try:
                        shutil.rmtree(full_d, ignore_errors=False)
                        if verbose:
                            print(f"Removed directory: {full_d}")
                    except Exception as e:
                        print(f"Error removing directory {full_d}: {e}")
                # prevent os.walk from descending into it
                if d in dirnames:
                    dirnames.remove(d)

        # files
        for f in list(filenames):
            full_f = os.path.join(dirpath, f)
            if f in DEFAULT_FILE_PATTERNS or matches_any(f, DEFAULT_FILE_PATTERNS):
                if dry_run:
                    if verbose:
                        print(f"Would remove file: {full_f}")
                else:
                    try:
                        os.remove(full_f)
                        if verbose:
                            print(f"Removed file: {full_f}")
                    except Exception as e:
                        print(f"Error removing file {full_f}: {e}")


def clear_log_files(root_dir: str, delete_logs_dir: bool = False, dry_run: bool = False, verbose: bool = True):
    """Either truncate files under a `logs` dir, or delete the logs directory entirely.

    - If delete_logs_dir is True, the whole logs directory is removed.
    - If False, each file is truncated to 0 bytes.
    """
    log_dir = os.path.join(root_dir, "logs")

    if not os.path.exists(log_dir):
        if verbose:
            print(f"Log directory not found at: {log_dir}")
        return

    if delete_logs_dir:
        if dry_run:
            if verbose:
                print(f"Would remove logs directory: {log_dir}")
        else:
            try:
                shutil.rmtree(log_dir, ignore_errors=False)
                if verbose:
                    print(f"Removed logs directory: {log_dir}")
            except Exception as e:
                print(f"Error removing logs directory {log_dir}: {e}")
        return

    # otherwise truncate files inside logs
    for root, dirs, files in os.walk(log_dir):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                if dry_run:
                    if verbose:
                        print(f"Would clear file: {file_path}")
                else:
                    with open(file_path, "w"):
                        pass
                    if verbose:
                        print(f"Cleared: {file_path}")
            except Exception as e:
                print(f"Error clearing {file_path}: {str(e)}")


def parse_args(argv: List[str] = None):
    p = argparse.ArgumentParser(description="Remove temporary files and folders from a project tree")
    p.add_argument("root", nargs="?", default=None, help="Root directory to clean (defaults to script dir)")
    p.add_argument("--dry-run", action="store_true", help="Show what would be removed without deleting")
    p.add_argument("--yes", action="store_true", help="Don't prompt for confirmation")
    p.add_argument("--delete-logs", action="store_true", help="Remove the entire logs directory instead of truncating files")
    p.add_argument("--quiet", action="store_true", help="Reduce output")
    return p.parse_args(argv)


def main(argv: List[str] = None):
    args = parse_args(argv)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_directory = os.path.abspath(args.root) if args.root else current_dir

    dry_run = args.dry_run
    verbose = not args.quiet

    if not args.yes and not dry_run:
        print(f"About to clean temporary files under: {root_directory}")
        resp = input("Proceed? [y/N]: ").strip().lower()
        if resp not in ("y", "yes"):
            print("Aborted by user.")
            return 1

    if verbose:
        print("Starting cleanup process...")

    delete_temporary_items(root_directory, dry_run=dry_run, verbose=verbose)
    clear_log_files(root_directory, delete_logs_dir=args.delete_logs, dry_run=dry_run, verbose=verbose)

    if verbose:
        print("\nCleanup completed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
