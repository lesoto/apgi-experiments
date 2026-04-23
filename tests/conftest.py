"""
Pytest configuration and fixtures for APGI Framework tests.
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configure xvfb for GUI tests
pytestmark = pytest.mark.filterwarnings("ignore::DeprecationWarning")

# Set up headless environment BEFORE any GUI imports
import os

# Force headless mode for GUI tests
if not os.environ.get("DISPLAY") or os.environ.get("CI"):
    os.environ.setdefault("DISPLAY", ":99")

# Set matplotlib to non-interactive backend BEFORE importing pyplot or tkagg
import matplotlib

matplotlib.use("Agg", force=True)


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Setup test environment."""
    # Set environment variables for headless testing if needed
    import os

    os.environ.setdefault("DISPLAY", ":99")

    # Set matplotlib to non-interactive backend for headless testing
    try:
        # import matplotlib
        # matplotlib.use("Agg")
        pass
    except ImportError:
        pass


# GUI test configuration
def pytest_configure(config):
    """Configure pytest for GUI tests."""
    config.addinivalue_line("markers", "gui: mark test as requiring GUI/display")
    config.addinivalue_line("markers", "slow: mark test as slow running")
    config.addinivalue_line("markers", "integration: mark test as integration test")


def pytest_collection_modifyitems(config, items):
    """Modify test collection to handle GUI tests."""
    # Add xvfb marker to GUI tests automatically
    for item in items:
        if "gui" in item.keywords or "GUI" in str(item.fspath):
            item.add_marker(pytest.mark.xvfb)
            item.add_marker(pytest.mark.gui)


@pytest.fixture(autouse=True)
def cleanup_gui_state():
    """Clean up GUI state after each test to prevent segfaults."""
    yield
    # Cleanup after test
    try:
        import matplotlib.pyplot as plt

        plt.close("all")
        plt.clf()
    except Exception:
        pass

    # Force Tkinter cleanup
    try:
        import tkinter as tk

        # Destroy any lingering root windows
        for widget in tk._default_root.children.values() if tk._default_root else []:
            try:
                widget.destroy()
            except Exception:
                pass
        if tk._default_root:
            try:
                tk._default_root.destroy()
            except Exception:
                pass
            tk._default_root = None
    except Exception:
        pass

    # Force garbage collection to clean up resources
    import gc

    gc.collect()


@pytest.fixture(scope="session", autouse=True)
def cleanup_session_gui():
    """Final cleanup after all tests complete."""
    yield
    # Final matplotlib cleanup
    try:
        import matplotlib.pyplot as plt

        plt.close("all")
    except Exception:
        pass

    # Final Tkinter cleanup
    try:
        import tkinter as tk

        if tk._default_root:
            try:
                tk._default_root.quit()
                tk._default_root.destroy()
            except Exception:
                pass
    except Exception:
        pass
