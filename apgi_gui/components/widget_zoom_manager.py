"""
Widget zoom manager for APGI Framework GUI applications.

Provides comprehensive zoom functionality with widget tracking,
keyboard shortcuts, and consistent zoom behavior across all widgets.
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
import logging
from enum import Enum

logger = logging.getLogger(__name__)


class ZoomType(Enum):
    """Types of zoom operations."""

    FONT_SIZE = "font_size"
    WIDGET_SCALE = "widget_scale"
    CANVAS_SCALE = "canvas_scale"
    TEXT_SCALE = "text_scale"


@dataclass
class ZoomState:
    """Represents the zoom state of a widget."""

    widget_id: str
    widget: tk.Widget
    zoom_type: ZoomType
    current_scale: float = 1.0
    min_scale: float = 0.5
    max_scale: float = 3.0
    scale_step: float = 0.1
    original_font_size: Optional[int] = None
    original_geometry: Optional[str] = None
    custom_data: Optional[Dict[str, Any]] = None


class WidgetZoomManager:
    """
    Comprehensive widget zoom management system.

    Provides zoom functionality for various widget types with
    keyboard shortcuts, mouse wheel support, and consistent behavior.
    """

    def __init__(self, root_widget: tk.Widget):
        self.root = root_widget
        self.widgets: Dict[str, ZoomState] = {}
        self.global_scale: float = 1.0
        self.zoom_callbacks: List[Callable] = []
        self.keyboard_shortcuts_enabled = True
        self.mouse_wheel_enabled = True

        # Default zoom settings
        self.default_settings = {
            "scale_step": 0.1,
            "min_scale": 0.5,
            "max_scale": 3.0,
            "font_scale_step": 1,
            "min_font_size": 6,
            "max_font_size": 48,
        }

        # Setup keyboard shortcuts
        self._setup_keyboard_shortcuts()

        logger.info("Widget zoom manager initialized")

    def _setup_keyboard_shortcuts(self):
        """Setup global keyboard shortcuts for zoom."""
        if not self.keyboard_shortcuts_enabled:
            return

        # Zoom in shortcuts
        self.root.bind("<Control-plus>", lambda e: self._global_zoom_in())
        self.root.bind(
            "<Control-equal>", lambda e: self._global_zoom_in()
        )  # For keyboards without numpad +
        self.root.bind("<Control-Shift-plus>", lambda e: self._global_zoom_in())

        # Zoom out shortcuts
        self.root.bind("<Control-minus>", lambda e: self._global_zoom_out())
        self.root.bind(
            "<Control-underscore>", lambda e: self._global_zoom_out()
        )  # For shift+-

        # Reset zoom shortcut
        self.root.bind("<Control-0>", lambda e: self._global_zoom_reset())

        # Alternative shortcuts
        self.root.bind("<Control-MouseWheel>", self._on_global_mouse_wheel)

        logger.debug("Keyboard shortcuts configured for zoom")

    def register_widget(
        self,
        widget: tk.Widget,
        zoom_type: ZoomType = ZoomType.FONT_SIZE,
        widget_id: Optional[str] = None,
        min_scale: Optional[float] = None,
        max_scale: Optional[float] = None,
        scale_step: Optional[float] = None,
    ) -> str:
        """
        Register a widget for zoom management.

        Args:
            widget: Widget to register
            zoom_type: Type of zoom to apply
            widget_id: Custom widget ID
            min_scale: Minimum scale factor
            max_scale: Maximum scale factor
            scale_step: Scale step size

        Returns:
            Widget ID for reference
        """
        if widget_id is None:
            widget_id = f"widget_{len(self.widgets)}"

        # Determine zoom type based on widget class if not specified
        if zoom_type == ZoomType.FONT_SIZE:
            zoom_type = self._determine_zoom_type(widget)

        # Get original font size if applicable
        original_font_size = None
        if zoom_type == ZoomType.FONT_SIZE:
            original_font_size = self._get_widget_font_size(widget)

        # Create zoom state
        zoom_state = ZoomState(
            widget_id=widget_id,
            widget=widget,
            zoom_type=zoom_type,
            min_scale=min_scale or self.default_settings["min_scale"],
            max_scale=max_scale or self.default_settings["max_scale"],
            scale_step=scale_step or self.default_settings["scale_step"],
            original_font_size=original_font_size,
        )

        self.widgets[widget_id] = zoom_state

        # Setup mouse wheel for this widget
        if self.mouse_wheel_enabled:
            self._setup_widget_mouse_wheel(widget, zoom_state)

        logger.debug(f"Registered widget {widget_id} for {zoom_type.value} zoom")
        return widget_id

    def _determine_zoom_type(self, widget: tk.Widget) -> ZoomType:
        """Determine the appropriate zoom type for a widget."""
        widget_class = widget.__class__.__name__

        if widget_class in [
            "Text",
            "Entry",
            "Label",
            "Button",
            "Checkbutton",
            "Radiobutton",
        ]:
            return ZoomType.FONT_SIZE
        elif widget_class == "Canvas":
            return ZoomType.CANVAS_SCALE
        elif hasattr(widget, "winfo_width") and hasattr(widget, "winfo_height"):
            return ZoomType.WIDGET_SCALE
        else:
            return ZoomType.TEXT_SCALE

    def _get_widget_font_size(self, widget: tk.Widget) -> Optional[int]:
        """Get the current font size of a widget."""
        try:
            if hasattr(widget, "cget"):
                font = widget.cget("font")
                if isinstance(font, tuple) and len(font) >= 2:
                    return font[1]
                elif isinstance(font, str):
                    # Try to parse font string
                    import tkinter.font as tkfont

                    font_obj = tkfont.Font(font=font)
                    return font_obj.actual()["size"]
                elif hasattr(font, "actual"):
                    return font.actual()["size"]
        except Exception as e:
            logger.warning(f"Failed to get font size for widget: {e}")

        return None

    def _setup_widget_mouse_wheel(self, widget: tk.Widget, zoom_state: ZoomState):
        """Setup mouse wheel zoom for a widget."""

        def on_mouse_wheel(event):
            if event.state & 0x4:  # Ctrl key
                if event.delta > 0:
                    self.zoom_in(zoom_state.widget_id)
                else:
                    self.zoom_out(zoom_state.widget_id)
                return "break"

        # Bind mouse wheel events
        widget.bind("<MouseWheel>", on_mouse_wheel)  # Windows
        widget.bind(
            "<Button-4>", lambda e: self.zoom_in(zoom_state.widget_id)
        )  # Linux scroll up
        widget.bind(
            "<Button-5>", lambda e: self.zoom_out(zoom_state.widget_id)
        )  # Linux scroll down

    def zoom_in(self, widget_id: Optional[str] = None):
        """Zoom in on a widget or globally."""
        if widget_id is None:
            self._global_zoom_in()
        elif widget_id in self.widgets:
            self._zoom_widget(widget_id, "in")

    def zoom_out(self, widget_id: Optional[str] = None):
        """Zoom out on a widget or globally."""
        if widget_id is None:
            self._global_zoom_out()
        elif widget_id in self.widgets:
            self._zoom_widget(widget_id, "out")

    def zoom_reset(self, widget_id: Optional[str] = None):
        """Reset zoom for a widget or globally."""
        if widget_id is None:
            self._global_zoom_reset()
        elif widget_id in self.widgets:
            self._zoom_widget(widget_id, "reset")

    def set_zoom(self, widget_id: str, scale: float):
        """Set zoom to a specific scale."""
        if widget_id not in self.widgets:
            logger.warning(f"Widget not registered: {widget_id}")
            return

        zoom_state = self.widgets[widget_id]

        # Clamp scale to bounds
        scale = max(zoom_state.min_scale, min(zoom_state.max_scale, scale))

        # Apply zoom based on type
        if zoom_state.zoom_type == ZoomType.FONT_SIZE:
            self._apply_font_zoom(zoom_state, scale)
        elif zoom_state.zoom_type == ZoomType.WIDGET_SCALE:
            self._apply_widget_scale(zoom_state, scale)
        elif zoom_state.zoom_type == ZoomType.CANVAS_SCALE:
            self._apply_canvas_scale(zoom_state, scale)
        elif zoom_state.zoom_type == ZoomType.TEXT_SCALE:
            self._apply_text_scale(zoom_state, scale)

        zoom_state.current_scale = scale

        # Notify callbacks
        for callback in self.zoom_callbacks:
            try:
                callback("zoom_changed", widget_id, scale)
            except Exception as e:
                logger.error(f"Zoom callback error: {e}")

        logger.debug(f"Set zoom for {widget_id} to {scale}")

    def _zoom_widget(self, widget_id: str, direction: str):
        """Zoom a widget in the specified direction."""
        zoom_state = self.widgets[widget_id]

        if direction == "reset":
            new_scale = 1.0
        elif direction == "in":
            new_scale = min(
                zoom_state.max_scale, zoom_state.current_scale + zoom_state.scale_step
            )
        elif direction == "out":
            new_scale = max(
                zoom_state.min_scale, zoom_state.current_scale - zoom_state.scale_step
            )
        else:
            return

        self.set_zoom(widget_id, new_scale)

    def _apply_font_zoom(self, zoom_state: ZoomState, scale: float):
        """Apply font-based zoom to a widget."""
        widget = zoom_state.widget

        if zoom_state.original_font_size is None:
            return

        try:
            new_font_size = int(zoom_state.original_font_size * scale)
            new_font_size = max(
                self.default_settings["min_font_size"],
                min(self.default_settings["max_font_size"], new_font_size),
            )

            if hasattr(widget, "configure"):
                current_font = widget.cget("font")

                if isinstance(current_font, tuple):
                    # Font tuple: (family, size, options...)
                    new_font = (current_font[0], new_font_size) + current_font[2:]
                elif isinstance(current_font, str):
                    # Font string - create new font
                    import tkinter.font as tkfont

                    font_obj = tkfont.Font(font=current_font)
                    family = font_obj.actual()["family"]
                    new_font = (family, new_font_size)
                elif hasattr(current_font, "configure"):
                    # Font object
                    current_font.configure(size=new_font_size)
                    return
                else:
                    new_font = ("TkDefaultFont", new_font_size)

                widget.configure(font=new_font)

        except Exception as e:
            logger.warning(f"Failed to apply font zoom: {e}")

    def _apply_widget_scale(self, zoom_state: ZoomState, scale: float):
        """Apply widget-based scaling."""
        widget = zoom_state.widget

        try:
            if hasattr(widget, "winfo_width") and hasattr(widget, "winfo_height"):
                # Store original geometry if not already stored
                if zoom_state.original_geometry is None:
                    width = widget.winfo_width()
                    height = widget.winfo_height()
                    zoom_state.original_geometry = f"{width}x{height}"

                # Parse original geometry
                if zoom_state.original_geometry:
                    parts = zoom_state.original_geometry.split("x")
                    if len(parts) == 2:
                        orig_width = int(parts[0])
                        orig_height = int(parts[1])

                        new_width = int(orig_width * scale)
                        new_height = int(orig_height * scale)

                        widget.configure(width=new_width, height=new_height)

        except Exception as e:
            logger.warning(f"Failed to apply widget scale: {e}")

    def _apply_canvas_scale(self, zoom_state: ZoomState, scale: float):
        """Apply canvas-based scaling."""
        widget = zoom_state.widget

        try:
            if hasattr(widget, "scale"):
                # For tkinter Canvas, apply scaling to all items
                widget.scale("all", 0, 0, scale, scale)

        except Exception as e:
            logger.warning(f"Failed to apply canvas scale: {e}")

    def _apply_text_scale(self, zoom_state: ZoomState, scale: float):
        """Apply text-based scaling."""
        # This is similar to font zoom but can be more comprehensive
        self._apply_font_zoom(zoom_state, scale)

    def _global_zoom_in(self):
        """Apply global zoom in."""
        self.global_scale = min(
            self.default_settings["max_scale"],
            self.global_scale + self.default_settings["scale_step"],
        )

        for widget_id in self.widgets:
            self.set_zoom(widget_id, self.global_scale)

        logger.info(f"Global zoom in: {self.global_scale}")

    def _global_zoom_out(self):
        """Apply global zoom out."""
        self.global_scale = max(
            self.default_settings["min_scale"],
            self.global_scale - self.default_settings["scale_step"],
        )

        for widget_id in self.widgets:
            self.set_zoom(widget_id, self.global_scale)

        logger.info(f"Global zoom out: {self.global_scale}")

    def _global_zoom_reset(self):
        """Reset global zoom."""
        self.global_scale = 1.0

        for widget_id in self.widgets:
            self.set_zoom(widget_id, 1.0)

        logger.info("Global zoom reset")

    def _on_global_mouse_wheel(self, event):
        """Handle global mouse wheel zoom."""
        if event.delta > 0:
            self._global_zoom_in()
        else:
            self._global_zoom_out()
        return "break"

    def unregister_widget(self, widget_id: str):
        """Unregister a widget from zoom management."""
        if widget_id in self.widgets:
            del self.widgets[widget_id]
            logger.debug(f"Unregistered widget: {widget_id}")

    def get_widget_zoom_state(self, widget_id: str) -> Optional[ZoomState]:
        """Get the zoom state of a widget."""
        return self.widgets.get(widget_id)

    def get_all_widgets(self) -> Dict[str, ZoomState]:
        """Get all registered widgets."""
        return self.widgets.copy()

    def set_keyboard_shortcuts_enabled(self, enabled: bool):
        """Enable or disable keyboard shortcuts."""
        self.keyboard_shortcuts_enabled = enabled

        if enabled:
            self._setup_keyboard_shortcuts()
        else:
            # Unbind shortcuts
            self.root.unbind("<Control-plus>")
            self.root.unbind("<Control-equal>")
            self.root.unbind("<Control-Shift-plus>")
            self.root.unbind("<Control-minus>")
            self.root.unbind("<Control-underscore>")
            self.root.unbind("<Control-0>")
            self.root.unbind("<Control-MouseWheel>")

    def set_mouse_wheel_enabled(self, enabled: bool):
        """Enable or disable mouse wheel zoom."""
        self.mouse_wheel_enabled = enabled

    def add_zoom_callback(self, callback: Callable):
        """Add a zoom callback."""
        self.zoom_callbacks.append(callback)

    def remove_zoom_callback(self, callback: Callable):
        """Remove a zoom callback."""
        if callback in self.zoom_callbacks:
            self.zoom_callbacks.remove(callback)

    def create_zoom_controls(
        self, parent: tk.Widget, widget_id: Optional[str] = None
    ) -> tk.Widget:
        """
        Create zoom control widgets.

        Args:
            parent: Parent widget
            widget_id: Widget ID to control (None for global)

        Returns:
            Frame containing zoom controls
        """
        control_frame = ttk.Frame(parent)

        # Zoom out button
        zoom_out_btn = ttk.Button(
            control_frame, text="➖", width=3, command=lambda: self.zoom_out(widget_id)
        )
        zoom_out_btn.pack(side=tk.LEFT, padx=2)

        # Zoom level label
        zoom_level_var = tk.StringVar(value="100%")
        zoom_level_label = ttk.Label(control_frame, textvariable=zoom_level_var)
        zoom_level_label.pack(side=tk.LEFT, padx=5)

        # Zoom in button
        zoom_in_btn = ttk.Button(
            control_frame, text="➕", width=3, command=lambda: self.zoom_in(widget_id)
        )
        zoom_in_btn.pack(side=tk.LEFT, padx=2)

        # Reset button
        reset_btn = ttk.Button(
            control_frame,
            text="🔄",
            width=3,
            command=lambda: self.zoom_reset(widget_id),
        )
        reset_btn.pack(side=tk.LEFT, padx=2)

        # Update function for zoom level display
        def update_zoom_level():
            if widget_id and widget_id in self.widgets:
                scale = self.widgets[widget_id].current_scale
            else:
                scale = self.global_scale

            zoom_level_var.set(f"{int(scale * 100)}%")
            parent.after(100, update_zoom_level)

        # Start update loop
        update_zoom_level()

        return control_frame

    def apply_zoom_to_children(self, parent_widget: tk.Widget, scale: float):
        """Apply zoom to all children of a widget."""

        def apply_recursive(widget):
            widget_id = None

            # Find if this widget is registered
            for wid, zoom_state in self.widgets.items():
                if zoom_state.widget == widget:
                    widget_id = wid
                    break

            if widget_id:
                self.set_zoom(widget_id, scale)

            # Apply to children
            for child in widget.winfo_children():
                apply_recursive(child)

        apply_recursive(parent_widget)


def create_zoom_manager(root_widget: tk.Widget) -> WidgetZoomManager:
    """
    Convenience function to create a widget zoom manager.

    Args:
        root_widget: Root widget for the application

    Returns:
        WidgetZoomManager instance
    """
    return WidgetZoomManager(root_widget)
