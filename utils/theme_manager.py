"""
Theme Manager for APGI GUI Applications - DEPRECATED
====================================================

DEPRECATED: This module has been consolidated and moved to apgi_gui.utils.theme_manager_unified.
Please import from apgi_gui.components.theme_manager for new code.

This module exists only for backward compatibility and will be removed in a future version.
"""

import warnings

# Show deprecation warning when imported
warnings.warn(
    "utils.theme_manager is deprecated. Please import from apgi_gui.components.theme_manager "
    "or apgi_gui.utils.theme_manager_unified for new code. This module will be removed in v2.0.",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export from the unified location for backward compatibility
try:
    from apgi_gui.utils.theme_manager_unified import (
        ThemeManager,
        AdvancedThemeManager,
        ThemeColors,
        ThemeFonts,
        create_theme_manager,
        get_system_theme_preference,
        create_theme_dialog,
    )
except ImportError as e:
    raise ImportError(
        "Failed to import unified theme manager. Please ensure apgi_gui.utils.theme_manager_unified is available."
    ) from e

__all__ = [
    "ThemeManager",
    "AdvancedThemeManager",
    "ThemeColors",
    "ThemeFonts",
    "create_theme_manager",
    "get_system_theme_preference",
    "create_theme_dialog",
]
