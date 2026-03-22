import argparse
import fnmatch
import os
import shutil
import sys
from typing import Iterable, List, Optional

DEFAULT_DIR_NAMES = {
    "__pycache__",
    "apgi_output",
    "cache",
    "backups",
    "coverage_html_report",
    ".pytest_cache",
    ".mypy_cache",
    ".hypothesis",
    "htmlcov",
    ".tox",
    ".ipynb_checkpoints",
    ".cache",
    "build",
    "dist",
    "test-results",
    "reports",
    "output",
    "outputs",
    "results",
    "experiments",
    "debug",
    "temp",
    "tmp",
    "coverage",
    "site",
    "MagickMock",
    "session_state",
    "session_data",
    ".pytest_cache",
    "apgi_outputs",
}

DEFAULT_DIR_PATTERNS = [
    "*.egg-info",
    "pip-wheel-metadata",
    "results_*",
    "output_*",
    "experiment_*",
    "debug_*",
    "test_*",
    "run_*",
    "MagickMock*",
]

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
    "*.out",
    "*.err",
    "*.trace",
    "*.prof",
    "*.profile",
    "*.stats",
    "*.benchmark",
    "*.metrics",
    "*.results",
    "*.output",
    "*.debug",
    "*.dump",
    "*.crash",
    "*.core",
    "*.stack",
    "*.traceback",
    "error.log",
    "debug.log",
    "experiment.log",
    "run.log",
    "test.log",
    "*.pkl",
    "*.pickle",
    "*.json.bak",
    "*.csv.bak",
    "*.txt.bak",
    "apgi_demo_visualization.png",
    "apgi_framework_gui.log",
    "test_physio_data.npz",
    "test_pupil_data.npz",
]

DEFAULT_EXTRA_DIR_NAMES = {
    ".nox",
    ".ruff_cache",
    ".benchmarks",
    "test-reports",
    "experiment-logs",
    "debug-logs",
    "run-logs",
    "checkpoints",
    "models",
    "data-temp",
    "plots",
    "figures",
    "visualizations",
    "notebooks-checkpoint",
    ".jupyter_cache",
}

DEFAULT_SKIP_TRAVERSE_DIRS = {".git", ".svn", ".hg"}

DEFAULT_EXTRA_FILE_PATTERNS = [
    "*.tmp",
    "*.temp",
    "*~",
    "*.swp",
    "*.swo",
    "*.bak",
    "*.orig",
    "*.rej",
    "*.patch",
    "*.diff",
    "*.old",
    "*.save",
    "*.backup",
    "*.lock",
    "*.pid",
    "*.socket",
    "*.fifo",
    "*.db-shm",
    "*.db-wal",
    "*.sqlite-journal",
    "*.checkpoint",
    "*.tmp.*",
    "*.temp.*",
    "*_tmp.*",
    "*_temp.*",
    "*_backup.*",
    "*_old.*",
    "*_save.*",
]


def matches_any(name: str, patterns: Iterable[str]) -> bool:
    for pat in patterns:
        if fnmatch.fnmatch(name, pat):
            return True
    return False


def delete_temporary_items(
    root_dir: str,
    dry_run: bool = False,
    verbose: bool = True,
    include_dir_patterns: Iterable[str] = (),
    include_file_patterns: Iterable[str] = (),
    exclude_dir_patterns: Iterable[str] = (),
    exclude_file_patterns: Iterable[str] = (),
    remove_node_modules: bool = False,
    remove_venvs: bool = False,
    venv_names: Iterable[str] = (".venv", "venv", ".env", "env"),
    follow_links: bool = False,
    max_depth: Optional[int] = None,
    remove_experiments: bool = False,
    remove_outputs: bool = False,
    remove_debug: bool = False,
    remove_logs: bool = False,
    remove_checkpoints: bool = False,
):
    """Delete temporary files, debugging artifacts, and experiment outputs from project tree.

    Comprehensive cleanup that removes:
    - Python cache files and directories (__pycache__, *.pyc, etc.)
    - Testing and coverage artifacts (.pytest_cache, coverage reports)
    - Build artifacts (build/, dist/, *.egg-info)
    - IDE and editor temporary files (.swp, *.tmp, etc.)
    - Database temporary files (*.db-shm, *.db-wal, *.sqlite-journal)
    - Experiment outputs and debugging files (when enabled)
    - Log files and crash reports
    - Backup and temporary files

    Args:
        root_dir: Root directory to clean
        dry_run: Show what would be removed without actually deleting
        verbose: Print detailed progress information
        include_dir_patterns: Additional directory patterns to remove
        include_file_patterns: Additional file patterns to remove
        exclude_dir_patterns: Directory patterns to exclude from deletion
        exclude_file_patterns: File patterns to exclude from deletion
        remove_node_modules: Also remove node_modules directories
        remove_venvs: Also remove virtual environment directories
        venv_names: Names considered as virtual environment directories
        follow_links: Follow symbolic links during traversal
        max_depth: Limit traversal depth relative to root directory
        remove_experiments: Remove experiment-related directories
        remove_outputs: Remove output and results directories
        remove_debug: Remove debugging and profiling files
        remove_logs: Remove log files and directories
        remove_checkpoints: Remove checkpoint and model directories

    This function avoids descending into removed directories by modifying dirnames in-place.
    """
    default_dir_names = set(DEFAULT_DIR_NAMES) | set(DEFAULT_EXTRA_DIR_NAMES)
    default_dir_patterns = list(DEFAULT_DIR_PATTERNS)
    default_file_patterns = list(DEFAULT_FILE_PATTERNS) + list(
        DEFAULT_EXTRA_FILE_PATTERNS
    )

    for dirpath, dirnames, filenames in os.walk(
        root_dir, topdown=True, followlinks=follow_links
    ):
        _max_depth = max_depth
        if _max_depth is not None:
            rel = os.path.relpath(dirpath, root_dir)
            depth = 0 if rel == "." else rel.count(os.sep) + 1
            if depth > _max_depth:
                dirnames.clear()
                continue

        # copy list because we may modify dirnames
        for d in list(dirnames):
            full_d = os.path.join(dirpath, d)
            if d in DEFAULT_SKIP_TRAVERSE_DIRS:
                dirnames.remove(d)
                continue

            if d in DEFAULT_SKIP_TRAVERSE_DIRS or matches_any(d, exclude_dir_patterns):
                continue

            should_remove_dir = (
                d in default_dir_names
                or matches_any(d, default_dir_patterns)
                or matches_any(d, include_dir_patterns)
                or (remove_node_modules and d == "node_modules")
                or (remove_venvs and d in set(venv_names))
                or (
                    remove_experiments
                    and d
                    in {
                        "experiments",
                        "experiment",
                        "experiment-logs",
                        "experiment-results",
                    }
                )
                or (
                    remove_outputs
                    and d in {"output", "outputs", "results", "test-results", "reports"}
                )
                or (
                    remove_debug and d in {"debug", "debug-logs", "profiling", "traces"}
                )
                or (remove_logs and d in {"logs", "log", "run-logs", "test-logs"})
                or (
                    remove_checkpoints
                    and d in {"checkpoints", "models", "model-checkpoints", "saves"}
                )
            )

            if should_remove_dir:
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
            if matches_any(f, exclude_file_patterns):
                continue

            if (
                f in default_file_patterns
                or matches_any(f, default_file_patterns)
                or matches_any(f, include_file_patterns)
            ):
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


def prune_empty_dirs(root_dir: str, dry_run: bool = False, verbose: bool = True):
    for dirpath, dirnames, filenames in os.walk(root_dir, topdown=False):
        # don't prune the root itself
        if dirpath == root_dir:
            continue
        try:
            if not os.listdir(dirpath):
                if dry_run:
                    if verbose:
                        print(f"Would remove empty directory: {dirpath}")
                else:
                    os.rmdir(dirpath)
                    if verbose:
                        print(f"Removed empty directory: {dirpath}")
        except Exception as e:
            print(f"Error pruning directory {dirpath}: {e}")


def clear_experiment_files(
    root_dir: str,
    dry_run: bool = False,
    verbose: bool = True,
    remove_plots: bool = True,
    remove_models: bool = True,
    remove_data_temp: bool = True,
):
    """Clean up experiment-specific files and directories.

    Args:
        root_dir: Root directory to clean
        dry_run: Show what would be removed without actually deleting
        verbose: Print detailed progress information
        remove_plots: Remove plot and visualization directories
        remove_models: Remove model and checkpoint directories
        remove_data_temp: Remove temporary data directories
    """
    experiment_dirs = []

    if remove_plots:
        experiment_dirs.extend(["plots", "figures", "visualizations", "charts"])

    if remove_models:
        experiment_dirs.extend(["models", "checkpoints", "saves", "model-checkpoints"])

    if remove_data_temp:
        experiment_dirs.extend(["data-temp", "temp-data", "cache-data"])

    for dirpath, dirnames, filenames in os.walk(root_dir, topdown=True):
        for d in list(dirnames):
            if d in experiment_dirs:
                full_d = os.path.join(dirpath, d)
                if dry_run:
                    if verbose:
                        print(f"Would remove experiment directory: {full_d}")
                else:
                    try:
                        shutil.rmtree(full_d, ignore_errors=False)
                        if verbose:
                            print(f"Removed experiment directory: {full_d}")
                    except Exception as e:
                        print(f"Error removing experiment directory {full_d}: {e}")
                dirnames.remove(d)


def clear_log_files(
    root_dir: str,
    delete_logs_dir: bool = False,
    dry_run: bool = False,
    verbose: bool = True,
):
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


def parse_args(argv: Optional[List[str]] = None):
    p = argparse.ArgumentParser(
        description="Comprehensive cleanup of temporary files, debugging artifacts, and experiment outputs"
    )
    p.add_argument(
        "root",
        nargs="?",
        default=None,
        help="Root directory to clean (defaults to script dir)",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be removed without deleting",
    )
    p.add_argument("--yes", action="store_true", help="Don't prompt for confirmation")
    p.add_argument(
        "--delete-logs",
        action="store_true",
        help="Remove the entire logs directory instead of truncating files",
    )
    p.add_argument("--quiet", action="store_true", help="Reduce output")

    # Experiment and debugging cleanup options
    p.add_argument(
        "--remove-experiments",
        action="store_true",
        default=True,
        help="Remove experiment-related directories (experiments/, experiment-logs/, etc.)",
    )
    p.add_argument(
        "--no-remove-experiments",
        action="store_false",
        dest="remove_experiments",
        help="Do NOT remove experiment-related directories",
    )
    p.add_argument(
        "--remove-outputs",
        action="store_true",
        default=True,
        help="Remove output and results directories (output/, results/, test-results/, etc.)",
    )
    p.add_argument(
        "--no-remove-outputs",
        action="store_false",
        dest="remove_outputs",
        help="Do NOT remove output and results directories",
    )
    p.add_argument(
        "--remove-debug",
        action="store_true",
        default=True,
        help="Remove debugging and profiling files (debug/, traces/, profiling/, etc.)",
    )
    p.add_argument(
        "--no-remove-debug",
        action="store_false",
        dest="remove_debug",
        help="Do NOT remove debugging and profiling files",
    )
    p.add_argument(
        "--remove-logs",
        action="store_true",
        default=True,
        help="Remove log files and directories (logs/, run-logs/, test-logs/, etc.)",
    )
    p.add_argument(
        "--no-remove-logs",
        action="store_false",
        dest="remove_logs",
        help="Do NOT remove log files and directories",
    )
    p.add_argument(
        "--remove-checkpoints",
        action="store_true",
        default=True,
        help="Remove checkpoint and model directories (checkpoints/, models/, saves/, etc.)",
    )
    p.add_argument(
        "--no-remove-checkpoints",
        action="store_false",
        dest="remove_checkpoints",
        help="Do NOT remove checkpoint and model directories",
    )

    # Advanced controls
    p.add_argument(
        "--include-dir",
        action="append",
        default=[],
        help="Additional directory patterns to remove (glob). Can be passed multiple times.",
    )
    p.add_argument(
        "--include-file",
        action="append",
        default=[],
        help="Additional file patterns to remove (glob). Can be passed multiple times.",
    )
    p.add_argument(
        "--exclude-dir",
        action="append",
        default=[],
        help="Directory patterns to exclude from deletion (glob). Can be passed multiple times.",
    )
    p.add_argument(
        "--exclude-file",
        action="append",
        default=[],
        help="File patterns to exclude from deletion (glob). Can be passed multiple times.",
    )
    p.add_argument(
        "--remove-node-modules",
        action="store_true",
        default=True,
        help="Also remove node_modules directories",
    )
    p.add_argument(
        "--no-remove-node-modules",
        action="store_false",
        dest="remove_node_modules",
        help="Do NOT remove node_modules directories",
    )
    p.add_argument(
        "--remove-venvs",
        action="store_true",
        default=True,
        help="Also remove common virtualenv directories (.venv, venv, .env, env)",
    )
    p.add_argument(
        "--no-remove-venvs",
        action="store_false",
        dest="remove_venvs",
        help="Do NOT remove common virtualenv directories",
    )
    p.add_argument(
        "--venv-names",
        nargs="*",
        default=None,
        help="Override names considered virtualenvs (space-separated)",
    )
    p.add_argument(
        "--follow-links",
        action="store_true",
        help="Follow symbolic links during traversal (use with caution)",
    )
    p.add_argument(
        "--max-depth",
        type=int,
        default=None,
        help="Limit traversal depth relative to root (1 = only root level)",
    )
    p.add_argument(
        "--prune-empty-dirs",
        action="store_true",
        help="Remove now-empty directories after cleanup",
    )
    return p.parse_args(argv)


def main(argv: Optional[List[str]] = None):
    args = parse_args(argv)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_directory = os.path.abspath(args.root) if args.root else current_dir

    dry_run = args.dry_run
    verbose = not args.quiet

    if not args.yes and not dry_run:
        print(f"About to clean temporary files under: {root_directory}")
        while True:
            resp = input("Proceed? [y/N]: ").strip().lower()
            if resp in ("y", "yes"):
                break
            elif resp in ("n", "no", ""):
                print("Aborted by user.")
                return 1
            else:
                print("Please enter 'y' or 'n'.")
                continue

    if verbose:
        print("Starting cleanup process...")

    venv_names = (
        args.venv_names
        if args.venv_names is not None
        else (".venv", "venv", ".env", "env")
    )
    delete_temporary_items(
        root_directory,
        dry_run=dry_run,
        verbose=verbose,
        include_dir_patterns=args.include_dir,
        include_file_patterns=args.include_file,
        exclude_dir_patterns=args.exclude_dir,
        exclude_file_patterns=args.exclude_file,
        remove_node_modules=args.remove_node_modules,
        remove_venvs=args.remove_venvs,
        venv_names=venv_names,
        follow_links=args.follow_links,
        max_depth=args.max_depth,
        remove_experiments=args.remove_experiments,
        remove_outputs=args.remove_outputs,
        remove_debug=args.remove_debug,
        remove_logs=args.remove_logs,
        remove_checkpoints=args.remove_checkpoints,
    )
    clear_log_files(
        root_directory,
        delete_logs_dir=args.delete_logs,
        dry_run=dry_run,
        verbose=verbose,
    )

    if args.prune_empty_dirs:
        prune_empty_dirs(root_directory, dry_run=dry_run, verbose=verbose)

    if verbose:
        print("\nComprehensive cleanup completed")
    print("\nSummary of cleanup options:")
    print("- Python cache files and directories")
    print("- Testing and coverage artifacts")
    print("- Build and distribution artifacts")
    print("- IDE and editor temporary files")
    print("- Database temporary files")
    print("- Log files and crash reports")
    if args.remove_experiments:
        print("- Experiment-related directories")
    if args.remove_outputs:
        print("- Output and results directories")
    if args.remove_debug:
        print("- Debugging and profiling files")
    if args.remove_logs:
        print("- Log files and directories")
    if args.remove_checkpoints:
        print("- Checkpoint and model directories")
    if args.remove_node_modules:
        print("- Node.js modules")
    if args.remove_venvs:
        print("- Virtual environments")
    return 0


if __name__ == "__main__":
    sys.exit(main())
