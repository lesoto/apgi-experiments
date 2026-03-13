"""
APGI Framework GUI Components

This package contains reusable GUI components for the APGI Framework including:
- Theme management and switching
- Backup and restore functionality
- Help system and feature tours
- Progress monitoring and user feedback
"""

# Import main components with graceful fallback for missing dependencies
try:
    from .theme_manager import (
        AdvancedThemeManager,
        ThemeColors,
        ThemeFonts,
        create_theme_manager,
    )

    THEME_MANAGER_AVAILABLE = True
except ImportError:
    THEME_MANAGER_AVAILABLE = False

try:
    from .theme_toggle import (
        ThemeToggleDialog,
        ThemeToggleWidget,
        create_theme_toggle,
        show_theme_dialog,
    )

    THEME_TOGGLE_AVAILABLE = True
except ImportError:
    THEME_TOGGLE_AVAILABLE = False

try:
    from .backup_manager import BackupManager, BackupManagerUI, create_backup_manager_ui

    BACKUP_MANAGER_AVAILABLE = True
except ImportError:
    BACKUP_MANAGER_AVAILABLE = False

try:
    from .help_system import (
        FeatureTourManager,
        HelpContent,
        HelpSystemUI,
        create_help_system,
        show_quick_help,
    )

    HELP_SYSTEM_AVAILABLE = True
except ImportError:
    HELP_SYSTEM_AVAILABLE = False


# Convenience functions for checking component availability
def get_available_components():
    """Get list of available GUI components."""
    components = []

    if THEME_MANAGER_AVAILABLE:
        components.append("theme_manager")

    if THEME_TOGGLE_AVAILABLE:
        components.append("theme_toggle")

    if BACKUP_MANAGER_AVAILABLE:
        components.append("backup_manager")

    if HELP_SYSTEM_AVAILABLE:
        components.append("help_system")

    return components


def is_component_available(component_name: str) -> bool:
    """Check if a specific component is available."""
    availability_map = {
        "theme_manager": THEME_MANAGER_AVAILABLE,
        "theme_toggle": THEME_TOGGLE_AVAILABLE,
        "backup_manager": BACKUP_MANAGER_AVAILABLE,
        "help_system": HELP_SYSTEM_AVAILABLE,
    }

    return availability_map.get(component_name, False)


# Export availability flags
__all__ = [
    # Availability flags
    "THEME_MANAGER_AVAILABLE",
    "THEME_TOGGLE_AVAILABLE",
    "BACKUP_MANAGER_AVAILABLE",
    "HELP_SYSTEM_AVAILABLE",
    # Utility functions
    "get_available_components",
    "is_component_available",
]

# Conditionally add imports to __all__ if available
if THEME_MANAGER_AVAILABLE:
    __all__.extend(
        [
            "AdvancedThemeManager",
            "ThemeColors",
            "ThemeFonts",
            "create_theme_manager",
        ]
    )

if THEME_TOGGLE_AVAILABLE:
    __all__.extend(
        [
            "ThemeToggleWidget",
            "ThemeToggleDialog",
            "create_theme_toggle",
            "show_theme_dialog",
        ]
    )

if BACKUP_MANAGER_AVAILABLE:
    __all__.extend(["BackupManager", "BackupManagerUI", "create_backup_manager_ui"])

if HELP_SYSTEM_AVAILABLE:
    __all__.extend(
        [
            "HelpSystemUI",
            "FeatureTourManager",
            "HelpContent",
            "create_help_system",
            "show_quick_help",
        ]
    )
