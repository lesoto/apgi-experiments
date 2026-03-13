"""
Theme Manager for APGI GUI Applications - DEPRECATED
====================================================

DEPRECATED: This module has been consolidated into apgi_gui.components.theme_manager.
Please import from apgi_gui.components.theme_manager for new code.

This module exists only for backward compatibility and will be removed in a future version.
"""

import sys
from pathlib import Path

# Add project root to sys.path to enable imports
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import warnings

# Show deprecation warning when imported
warnings.warn(
    "utils.theme_manager is deprecated. Please import from apgi_gui.components.theme_manager "
    "for new code. This module will be removed in v2.0.",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export from the consolidated location for backward compatibility
from apgi_gui.components.theme_manager import (
    ThemeColors,
    ThemeFonts,
    AdvancedThemeManager,
    ThemeManager,
    create_theme_manager,
    get_system_theme_preference,
    create_theme_dialog,
)

__all__ = [
    "ThemeColors",
    "ThemeFonts",
    "AdvancedThemeManager",
    "ThemeManager",
    "create_theme_manager",
    "get_system_theme_preference",
    "create_theme_dialog",
]
