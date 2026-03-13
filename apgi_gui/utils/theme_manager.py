"""
Theme Manager for APGI Framework GUI Applications - UNIFIED VERSION
==================================================================

DEPRECATED: This module has been consolidated into apgi_gui.components.theme_manager.
Please import from apgi_gui.components.theme_manager for new code.

For backward compatibility, this re-exports the unified theme manager.
"""

# Re-export the consolidated theme manager for backward compatibility
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
