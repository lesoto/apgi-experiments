"""
Centralized window sizing configuration for APGI Framework GUIs.

Provides consistent window sizing strategies across all GUI applications.
"""

from dataclasses import dataclass
from typing import Tuple


@dataclass
class WindowSizeConfig:
    """Standard window sizes for different GUI types."""

    # Standard sizes
    SMALL: Tuple[int, int] = (800, 600)
    MEDIUM: Tuple[int, int] = (900, 700)
    LARGE: Tuple[int, int] = (1200, 800)
    EXTRA_LARGE: Tuple[int, int] = (1400, 900)
    FULLSCREEN: Tuple[int, int] = (1600, 1000)

    # Minimum sizes
    MIN_WIDTH: int = 800
    MIN_HEIGHT: int = 600

    # Dialog sizes
    DIALOG_SMALL: Tuple[int, int] = (500, 400)
    DIALOG_MEDIUM: Tuple[int, int] = (600, 500)
    DIALOG_LARGE: Tuple[int, int] = (900, 700)

    @staticmethod
    def get_size_for_gui_type(gui_type: str) -> Tuple[int, int]:
        """Get appropriate window size for GUI type.

        Args:
            gui_type: Type of GUI (e.g., 'main', 'experiment', 'test', 'util')

        Returns:
            Tuple of (width, height)
        """
        sizes = {
            "experiment": WindowSizeConfig.LARGE,
            "launcher": WindowSizeConfig.MEDIUM,
            "main": WindowSizeConfig.LARGE,
            "registry": WindowSizeConfig.LARGE,
            "test": WindowSizeConfig.LARGE,
            "util": WindowSizeConfig.SMALL,
        }
        return sizes.get(gui_type, WindowSizeConfig.MEDIUM)

    @staticmethod
    def center_window(width: int, height: int, root) -> str:
        """Calculate centered window position.

        Args:
            width: Window width
            height: Window height
            root: Root widget

        Returns:
            Geometry string with centered position
        """
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        return f"{width}x{height}+{x}+{y}"
