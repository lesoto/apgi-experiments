"""
Undo/Redo Manager for APGI Framework GUI

Provides comprehensive undo/redo functionality for GUI applications.
Supports tracking of parameter changes, text edits, and other user actions.
"""

import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from typing import Dict, Any, Optional, List, Callable, Union
from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path


@dataclass
class UndoRedoAction:
    """Represents a single undo/redo action."""

    action_type: str  # 'parameter_change', 'text_edit', 'config_change', etc.
    description: str  # Human-readable description
    data: Any  # Action-specific data
    timestamp: datetime
    widget_id: Optional[str] = None  # ID of widget that was modified

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "action_type": self.action_type,
            "description": self.description,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
            "widget_id": self.widget_id,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UndoRedoAction":
        """Create from dictionary."""
        return cls(
            action_type=data["action_type"],
            description=data["description"],
            data=data["data"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            widget_id=data.get("widget_id"),
        )


class UndoRedoManager:
    """Manages undo/redo functionality for GUI applications."""

    def __init__(self, max_history: int = 100):
        self.max_history = max_history
        self.undo_stack: List[UndoRedoAction] = []
        self.redo_stack: List[UndoRedoAction] = []
        self.action_handlers = {}
        self.widget_trackers = {}
        self._register_default_handlers()

    def _register_default_handlers(self):
        """Register default action handlers."""
        self.action_handlers = {
            "parameter_change": self._handle_parameter_change,
            "text_edit": self._handle_text_edit,
            "config_change": self._handle_config_change,
            "widget_state": self._handle_widget_state,
            "custom": self._handle_custom_action,
        }

    def add_action(
        self,
        action_type: str,
        description: str,
        data: Any,
        widget: Optional[Any] = None,
    ) -> None:
        """Add an action to the undo stack."""
        # Create action object
        action = UndoRedoAction(
            action_type=action_type,
            description=description,
            data=data,
            timestamp=datetime.now(),
            widget_id=str(id(widget)) if widget else None,
        )

        # Add to undo stack
        self.undo_stack.append(action)

        # Limit stack size
        if len(self.undo_stack) > self.max_history:
            self.undo_stack.pop(0)

        # Clear redo stack when new action is added
        self.redo_stack.clear()

    def undo(self) -> Optional[str]:
        """Perform undo operation."""
        if not self.undo_stack:
            return None

        action = self.undo_stack.pop()

        # Get handler for this action type
        handler = self.action_handlers.get(action.action_type)
        if handler:
            try:
                handler(action, is_undo=True)
                # Add to redo stack
                self.redo_stack.append(action)
                return action.description
            except Exception as e:
                print(f"Error undoing action {action.description}: {e}")
                # Put action back on undo stack
                self.undo_stack.append(action)
                return None

        return None

    def redo(self) -> Optional[str]:
        """Perform redo operation."""
        if not self.redo_stack:
            return None

        action = self.redo_stack.pop()

        # Get handler for this action type
        handler = self.action_handlers.get(action.action_type)
        if handler:
            try:
                handler(action, is_undo=False)
                # Add to undo stack
                self.undo_stack.append(action)
                return action.description
            except Exception as e:
                print(f"Error redoing action {action.description}: {e}")
                # Put action back on redo stack
                self.redo_stack.append(action)
                return None

        return None

    def can_undo(self) -> bool:
        """Check if undo is possible."""
        return len(self.undo_stack) > 0

    def can_redo(self) -> bool:
        """Check if redo is possible."""
        return len(self.redo_stack) > 0

    def get_undo_description(self) -> Optional[str]:
        """Get description of next undo action."""
        if self.undo_stack:
            return self.undo_stack[-1].description
        return None

    def get_redo_description(self) -> Optional[str]:
        """Get description of next redo action."""
        if self.redo_stack:
            return self.redo_stack[-1].description
        return None

    def clear_history(self) -> None:
        """Clear all undo/redo history."""
        self.undo_stack.clear()
        self.redo_stack.clear()

    def get_history(self, max_items: int = 20) -> List[Dict[str, str]]:
        """Get recent history for display."""
        history = []

        # Recent undo actions (in reverse order)
        for action in reversed(self.undo_stack[-max_items // 2 :]):
            history.append(
                {
                    "type": "undo",
                    "description": action.description,
                    "timestamp": action.timestamp.strftime("%H:%M:%S"),
                    "action_type": action.action_type,
                }
            )

        # Recent redo actions
        for action in self.redo_stack[-max_items // 2 :]:
            history.append(
                {
                    "type": "redo",
                    "description": action.description,
                    "timestamp": action.timestamp.strftime("%H:%M:%S"),
                    "action_type": action.action_type,
                }
            )

        return history

    def track_parameter_change(
        self,
        widget,
        param_name: str,
        old_value: Any,
        new_value: Any,
    ) -> None:
        """Track a parameter change."""
        data = {
            "widget_id": str(id(widget)),
            "param_name": param_name,
            "old_value": old_value,
            "new_value": new_value,
        }

        description = f"Changed {param_name} from {old_value} to {new_value}"
        self.add_action("parameter_change", description, data, widget)

    def track_text_edit(self, widget, old_text: str, new_text: str) -> None:
        """Track a text edit."""
        data = {
            "widget_id": str(id(widget)),
            "old_text": old_text,
            "new_text": new_text,
        }

        description = f"Text edit in {widget.winfo_class()}"
        self.add_action("text_edit", description, data, widget)

    def track_widget_state(self, widget, state_changes: Dict[str, Any]) -> None:
        """Track widget state changes."""
        data = {"widget_id": str(id(widget)), "state_changes": state_changes}

        description = f"State change in {widget.winfo_class()}"
        self.add_action("widget_state", description, data, widget)

    def _handle_parameter_change(self, action: UndoRedoAction, is_undo: bool) -> None:
        """Handle parameter change undo/redo."""
        data = action.data
        widget_id = data["widget_id"]

        # Find the widget (this is a simplified approach)
        # In practice, you'd want to maintain a widget registry
        widget = self._find_widget_by_id(widget_id)
        if widget:
            if is_undo:
                value = data["old_value"]
            else:
                value = data["new_value"]

            # Restore the value
            if hasattr(widget, "set"):
                widget.set(value)
            elif hasattr(widget, "config"):
                widget.config(textvariable=tk.StringVar(value=value))
            elif hasattr(widget, "delete") and hasattr(widget, "insert"):
                widget.delete(0, tk.END)
                widget.insert(0, str(value))

    def _handle_text_edit(self, action: UndoRedoAction, is_undo: bool) -> None:
        """Handle text edit undo/redo."""
        data = action.data
        widget_id = data["widget_id"]

        widget = self._find_widget_by_id(widget_id)
        if widget and hasattr(widget, "delete") and hasattr(widget, "insert"):
            if is_undo:
                text = data["old_text"]
            else:
                text = data["new_text"]

            widget.delete(1.0, tk.END)
            widget.insert(1.0, text)

    def _handle_config_change(self, action: UndoRedoAction, is_undo: bool) -> None:
        """Handle configuration change undo/redo."""
        data = action.data

        if is_undo:
            config_data = data.get("old_config", {})
        else:
            config_data = data.get("new_config", {})

        # This would need to be implemented based on your config system
        # For now, just print what would happen
        print(f"Would restore config: {config_data}")

    def _handle_widget_state(self, action: UndoRedoAction, is_undo: bool) -> None:
        """Handle widget state undo/redo."""
        data = action.data
        widget_id = data["widget_id"]

        widget = self._find_widget_by_id(widget_id)
        if widget:
            state_changes = data["state_changes"]

            for property_name, value in state_changes.items():
                if is_undo:
                    # Restore old state (you'd need to store old state in data)
                    pass
                else:
                    # Apply new state
                    if hasattr(widget, property_name):
                        setattr(widget, property_name, value)

    def _handle_custom_action(self, action: UndoRedoAction, is_undo: bool) -> None:
        """Handle custom action undo/redo."""
        data = action.data

        if "undo_handler" in data and is_undo:
            data["undo_handler"]()
        elif "redo_handler" in data and not is_undo:
            data["redo_handler"]()

    def _find_widget_by_id(self, widget_id: str) -> Optional[Any]:
        """Find widget by ID (simplified implementation)."""
        # This is a simplified approach - in practice, you'd want to maintain
        # a registry of tracked widgets
        return None

    def save_history(self, filepath: str) -> None:
        """Save undo/redo history to file."""
        history_data = {
            "undo_stack": [action.to_dict() for action in self.undo_stack],
            "redo_stack": [action.to_dict() for action in self.redo_stack],
        }

        with open(filepath, "w") as f:
            json.dump(history_data, f, indent=2)

    def load_history(self, filepath: str) -> None:
        """Load undo/redo history from file."""
        try:
            with open(filepath, "r") as f:
                history_data = json.load(f)

            self.undo_stack = [
                UndoRedoAction.from_dict(action_data)
                for action_data in history_data.get("undo_stack", [])
            ]
            self.redo_stack = [
                UndoRedoAction.from_dict(action_data)
                for action_data in history_data.get("redo_stack", [])
            ]
        except Exception as e:
            print(f"Error loading history from {filepath}: {e}")


class WidgetTracker:
    """Helper class to track widget changes for undo/redo."""

    def __init__(self, undo_manager: UndoRedoManager):
        self.undo_manager = undo_manager
        self.tracked_widgets = {}
        self.original_values = {}

    def track_widget(self, widget, widget_type: str = "parameter") -> None:
        """Start tracking a widget for changes."""
        widget_id = str(id(widget))
        self.tracked_widgets[widget_id] = {"widget": widget, "type": widget_type}

        # Store original value
        if widget_type == "parameter":
            if hasattr(widget, "get"):
                self.original_values[widget_id] = widget.get()
            elif hasattr(widget, "cget"):
                self.original_values[widget_id] = widget.cget("text")

        # Bind change events based on widget type
        if isinstance(widget, (tk.Entry, ttk.Entry, ctk.CTkEntry)):
            widget.bind("<FocusOut>", lambda e: self._on_parameter_change(widget))
        elif isinstance(widget, (tk.Spinbox, ttk.Spinbox)):
            widget.bind("<FocusOut>", lambda e: self._on_parameter_change(widget))
        elif isinstance(widget, (tk.Text, ctk.CTkTextbox)):
            widget.bind("<FocusOut>", lambda e: self._on_text_change(widget))

    def _on_parameter_change(self, widget) -> None:
        """Handle parameter change event."""
        widget_id = str(id(widget))

        if widget_id in self.tracked_widgets:
            old_value = self.original_values.get(widget_id, "")

            if hasattr(widget, "get"):
                new_value = widget.get()
            elif hasattr(widget, "cget"):
                new_value = widget.cget("text")
            else:
                new_value = ""

            if old_value != new_value:
                param_name = self.tracked_widgets[widget_id].get(
                    "param_name", "parameter"
                )
                self.undo_manager.track_parameter_change(
                    widget, param_name, old_value, new_value
                )
                self.original_values[widget_id] = new_value

    def _on_text_change(self, widget) -> None:
        """Handle text change event."""
        widget_id = str(id(widget))

        if widget_id in self.tracked_widgets:
            old_text = self.original_values.get(widget_id, "")

            if hasattr(widget, "get"):
                new_text = widget.get(1.0, tk.END).strip()
            else:
                new_text = ""

            if old_text != new_text:
                self.undo_manager.track_text_edit(widget, old_text, new_text)
                self.original_values[widget_id] = new_text


def create_undo_redo_menu(menu_bar: tk.Menu, undo_manager: UndoRedoManager) -> None:
    """Create undo/redo menu items."""
    edit_menu = tk.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="Edit", menu=edit_menu)

    # Add undo/redo items
    edit_menu.add_command(label="Undo", command=undo_manager.undo, accelerator="Ctrl+Z")
    edit_menu.add_command(label="Redo", command=undo_manager.redo, accelerator="Ctrl+Y")
    edit_menu.add_separator()

    # Add clear history
    edit_menu.add_command(label="Clear History", command=undo_manager.clear_history)
