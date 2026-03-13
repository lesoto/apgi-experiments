"""
Theme Manager for APGI Framework GUI Applications - UNIFIED VERSION
==================================================================

DEPRECATED: This module has been consolidated. 
Please import from apgi_gui.components.theme_manager for new code.

For backward compatibility, this re-exports the unified theme manager.
"""

# Re-export the unified theme manager for backward compatibility
from .theme_manager_unified import (
    ThemeManager,
    AdvancedThemeManager,
    ThemeColors,
    ThemeFonts,
    create_theme_manager,
    get_system_theme_preference,
    create_theme_dialog,
)

__all__ = [
    "ThemeManager",
    "AdvancedThemeManager",
    "ThemeColors",
    "ThemeFonts",
    "create_theme_manager",
    "get_system_theme_preference",
    "create_theme_dialog",
]
