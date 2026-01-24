"""
Navigation history system for APGI Framework GUI applications.

Provides comprehensive navigation tracking, breadcrumb navigation,
back/forward functionality, and navigation state management.
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
import json
from pathlib import Path
import logging
from enum import Enum

logger = logging.getLogger(__name__)


class NavigationAction(Enum):
    """Types of navigation actions."""

    NAVIGATE = "navigate"
    OPEN_FILE = "open_file"
    OPEN_TAB = "open_tab"
    CLOSE_TAB = "close_tab"
    SWITCH_VIEW = "switch_view"
    FILTER = "filter"
    SEARCH = "search"
    SETTINGS = "settings"
    HELP = "help"


@dataclass
class NavigationState:
    """Represents a navigation state."""

    id: str
    action: NavigationAction
    title: str
    description: str
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    parent_id: Optional[str] = None
    can_navigate_back: bool = True
    can_navigate_forward: bool = True
    is_bookmarkable: bool = True
    icon: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "action": self.action.value,
            "title": self.title,
            "description": self.description,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
            "parent_id": self.parent_id,
            "can_navigate_back": self.can_navigate_back,
            "can_navigate_forward": self.can_navigate_forward,
            "is_bookmarkable": self.is_bookmarkable,
            "icon": self.icon,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "NavigationState":
        """Create from dictionary."""
        data["action"] = NavigationAction(data["action"])
        data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        return cls(**data)


class NavigationHistory:
    """
    Navigation history manager.

    Tracks navigation actions, provides back/forward functionality,
    and maintains navigation state.
    """

    def __init__(self, max_history: int = 100):
        self.max_history = max_history
        self.history: List[NavigationState] = []
        self.current_index: int = -1
        self.bookmarks: List[NavigationState] = []
        self.navigation_callbacks: List[Callable] = []
        self.id_counter = 0

        logger.info("Navigation history initialized")

    def _generate_id(self) -> str:
        """Generate a unique navigation ID."""
        self.id_counter += 1
        return f"nav_{self.id_counter}_{int(datetime.now().timestamp())}"

    def add_navigation(
        self,
        action: NavigationAction,
        title: str,
        description: str = "",
        data: Optional[Dict[str, Any]] = None,
        parent_id: Optional[str] = None,
        can_navigate_back: bool = True,
        can_navigate_forward: bool = True,
        is_bookmarkable: bool = True,
        icon: Optional[str] = None,
    ) -> str:
        """
        Add a navigation state to history.

        Args:
            action: Type of navigation action
            title: Navigation title
            description: Navigation description
            data: Additional navigation data
            parent_id: Parent navigation ID
            can_navigate_back: Whether can navigate back from this state
            can_navigate_forward: Whether can navigate forward from this state
            is_bookmarkable: Whether this state can be bookmarked
            icon: Icon for this navigation state

        Returns:
            Navigation state ID
        """
        # Create navigation state
        nav_state = NavigationState(
            id=self._generate_id(),
            action=action,
            title=title,
            description=description,
            data=data or {},
            parent_id=parent_id,
            can_navigate_back=can_navigate_back,
            can_navigate_forward=can_navigate_forward,
            is_bookmarkable=is_bookmarkable,
            icon=icon,
        )

        # Add to history
        self._add_to_history(nav_state)

        logger.debug(f"Added navigation: {title} ({action.value})")
        return nav_state.id

    def _add_to_history(self, nav_state: NavigationState):
        """Add navigation state to history."""
        # Remove any forward history
        if self.current_index < len(self.history) - 1:
            self.history = self.history[: self.current_index + 1]

        # Add new state
        self.history.append(nav_state)
        self.current_index = len(self.history) - 1

        # Limit history size
        if len(self.history) > self.max_history:
            self.history.pop(0)
            self.current_index -= 1

        # Notify callbacks
        for callback in self.navigation_callbacks:
            try:
                callback("navigation_added", nav_state)
            except Exception as e:
                logger.error(f"Navigation callback error: {e}")

    def can_go_back(self) -> bool:
        """Check if can navigate back."""
        if self.current_index <= 0:
            return False

        current_state = self.history[self.current_index]
        return current_state.can_navigate_back

    def can_go_forward(self) -> bool:
        """Check if can navigate forward."""
        if self.current_index >= len(self.history) - 1:
            return False

        current_state = self.history[self.current_index]
        return current_state.can_navigate_forward

    def go_back(self) -> Optional[NavigationState]:
        """Navigate back in history."""
        if not self.can_go_back():
            return None

        self.current_index -= 1
        nav_state = self.history[self.current_index]

        # Notify callbacks
        for callback in self.navigation_callbacks:
            try:
                callback("navigation_back", nav_state)
            except Exception as e:
                logger.error(f"Navigation callback error: {e}")

        logger.debug(f"Navigated back to: {nav_state.title}")
        return nav_state

    def go_forward(self) -> Optional[NavigationState]:
        """Navigate forward in history."""
        if not self.can_go_forward():
            return None

        self.current_index += 1
        nav_state = self.history[self.current_index]

        # Notify callbacks
        for callback in self.navigation_callbacks:
            try:
                callback("navigation_forward", nav_state)
            except Exception as e:
                logger.error(f"Navigation callback error: {e}")

        logger.debug(f"Navigated forward to: {nav_state.title}")
        return nav_state

    def get_current_state(self) -> Optional[NavigationState]:
        """Get current navigation state."""
        if 0 <= self.current_index < len(self.history):
            return self.history[self.current_index]
        return None

    def get_back_history(self, count: int = 10) -> List[NavigationState]:
        """Get navigation history for back button."""
        if self.current_index <= 0:
            return []

        start_index = max(0, self.current_index - count)
        return list(reversed(self.history[start_index : self.current_index]))

    def get_forward_history(self, count: int = 10) -> List[NavigationState]:
        """Get navigation history for forward button."""
        if self.current_index >= len(self.history) - 1:
            return []

        end_index = min(len(self.history), self.current_index + count + 1)
        return self.history[self.current_index + 1 : end_index]

    def get_breadcrumb_trail(self) -> List[NavigationState]:
        """Get breadcrumb trail for current navigation."""
        if not self.history:
            return []

        current = self.get_current_state()
        if not current:
            return []

        # Build breadcrumb trail by following parent relationships
        trail = []
        visited = set()

        state = current
        while state and state.id not in visited:
            trail.append(state)
            visited.add(state.id)

            # Find parent
            if state.parent_id:
                state = next((s for s in self.history if s.id == state.parent_id), None)
            else:
                break

        return list(reversed(trail))

    def add_bookmark(self, nav_state_id: str) -> bool:
        """Add a navigation state to bookmarks."""
        nav_state = next((s for s in self.history if s.id == nav_state_id), None)

        if not nav_state or not nav_state.is_bookmarkable:
            return False

        # Check if already bookmarked
        if any(s.id == nav_state_id for s in self.bookmarks):
            return False

        self.bookmarks.append(nav_state)
        logger.info(f"Added bookmark: {nav_state.title}")
        return True

    def remove_bookmark(self, nav_state_id: str) -> bool:
        """Remove a navigation state from bookmarks."""
        self.bookmarks = [s for s in self.bookmarks if s.id != nav_state_id]
        logger.info(f"Removed bookmark: {nav_state_id}")
        return True

    def get_bookmarks(self) -> List[NavigationState]:
        """Get all bookmarks."""
        return self.bookmarks.copy()

    def search_history(self, query: str) -> List[NavigationState]:
        """Search navigation history."""
        query_lower = query.lower()
        results = []

        for state in self.history:
            if (
                query_lower in state.title.lower()
                or query_lower in state.description.lower()
            ):
                results.append(state)

        return results

    def clear_history(self):
        """Clear navigation history."""
        self.history.clear()
        self.current_index = -1
        logger.info("Navigation history cleared")

    def export_history(self, file_path: Path) -> bool:
        """Export navigation history to file."""
        try:
            export_data = {
                "export_timestamp": datetime.now().isoformat(),
                "current_index": self.current_index,
                "history": [state.to_dict() for state in self.history],
                "bookmarks": [state.to_dict() for state in self.bookmarks],
            }

            with open(file_path, "w") as f:
                json.dump(export_data, f, indent=2)

            logger.info(f"Navigation history exported to {file_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to export navigation history: {e}")
            return False

    def import_history(self, file_path: Path) -> bool:
        """Import navigation history from file."""
        try:
            with open(file_path, "r") as f:
                import_data = json.load(f)

            # Import history
            self.history = [
                NavigationState.from_dict(data) for data in import_data["history"]
            ]
            self.current_index = import_data.get("current_index", len(self.history) - 1)

            # Import bookmarks
            if "bookmarks" in import_data:
                self.bookmarks = [
                    NavigationState.from_dict(data) for data in import_data["bookmarks"]
                ]

            logger.info(f"Navigation history imported from {file_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to import navigation history: {e}")
            return False

    def add_navigation_callback(self, callback: Callable):
        """Add a navigation callback."""
        self.navigation_callbacks.append(callback)

    def remove_navigation_callback(self, callback: Callable):
        """Remove a navigation callback."""
        if callback in self.navigation_callbacks:
            self.navigation_callbacks.remove(callback)


class NavigationWidget:
    """
    Navigation widget with back/forward buttons and breadcrumbs.

    Provides a complete navigation interface for GUI applications.
    """

    def __init__(self, parent: tk.Widget, navigation_history: NavigationHistory):
        self.parent = parent
        self.nav_history = navigation_history
        self.navigation_callback: Optional[Callable] = None

        # Create UI
        self._create_ui()

        # Register navigation callbacks
        self.nav_history.add_navigation_callback(self._on_navigation_event)

        # Update initial state
        self._update_navigation_state()

        logger.info("Navigation widget created")

    def _create_ui(self):
        """Create the navigation UI."""
        # Main frame
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill=tk.X, padx=5, pady=5)

        # Navigation buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(side=tk.LEFT, padx=(0, 10))

        # Back button
        self.back_btn = ttk.Button(
            button_frame, text="← Back", command=self._go_back, state=tk.DISABLED
        )
        self.back_btn.pack(side=tk.LEFT, padx=(0, 2))

        # Forward button
        self.forward_btn = ttk.Button(
            button_frame, text="Forward →", command=self._go_forward, state=tk.DISABLED
        )
        self.forward_btn.pack(side=tk.LEFT, padx=(0, 2))

        # Home button
        self.home_btn = ttk.Button(button_frame, text="🏠 Home", command=self._go_home)
        self.home_btn.pack(side=tk.LEFT, padx=(0, 2))

        # Separator
        ttk.Separator(button_frame, orient=tk.VERTICAL).pack(
            side=tk.LEFT, padx=5, fill=tk.Y
        )

        # Bookmark button
        self.bookmark_btn = ttk.Button(
            button_frame, text="⭐ Bookmark", command=self._toggle_bookmark
        )
        self.bookmark_btn.pack(side=tk.LEFT, padx=(0, 2))

        # Breadcrumbs frame
        self.breadcrumb_frame = ttk.Frame(main_frame)
        self.breadcrumb_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Create breadcrumb labels
        self.breadcrumb_labels: List[tk.Label] = []

    def _on_navigation_event(self, event_type: str, nav_state: NavigationState):
        """Handle navigation events."""
        self._update_navigation_state()
        self._update_breadcrumbs()

        # Call custom callback if set
        if self.navigation_callback:
            try:
                self.navigation_callback(event_type, nav_state)
            except Exception as e:
                logger.error(f"Navigation callback error: {e}")

    def _update_navigation_state(self):
        """Update navigation button states."""
        # Update back button
        if self.nav_history.can_go_back():
            self.back_btn.config(state=tk.NORMAL)
        else:
            self.back_btn.config(state=tk.DISABLED)

        # Update forward button
        if self.nav_history.can_go_forward():
            self.forward_btn.config(state=tk.NORMAL)
        else:
            self.forward_btn.config(state=tk.DISABLED)

        # Update bookmark button
        current = self.nav_history.get_current_state()
        if current and current.is_bookmarkable:
            bookmarks = self.nav_history.get_bookmarks()
            is_bookmarked = any(b.id == current.id for b in bookmarks)

            if is_bookmarked:
                self.bookmark_btn.config(text="⭐ Bookmarked")
            else:
                self.bookmark_btn.config(text="☆ Bookmark")
        else:
            self.bookmark_btn.config(state=tk.DISABLED)

    def _update_breadcrumbs(self):
        """Update breadcrumb trail."""
        # Clear existing breadcrumbs
        for label in self.breadcrumb_labels:
            label.destroy()
        self.breadcrumb_labels.clear()

        # Get breadcrumb trail
        trail = self.nav_history.get_breadcrumb_trail()

        if not trail:
            return

        # Create breadcrumb labels
        for i, state in enumerate(trail):
            # Add separator
            if i > 0:
                separator = tk.Label(
                    self.breadcrumb_frame, text=" › ", font=("Arial", 10)
                )
                separator.pack(side=tk.LEFT)
                self.breadcrumb_labels.append(separator)

            # Create breadcrumb label
            if i == len(trail) - 1:
                # Current state - bold
                label = tk.Label(
                    self.breadcrumb_frame,
                    text=state.title,
                    font=("Arial", 10, "bold"),
                    fg="blue",
                )
            else:
                # Clickable breadcrumb
                label = tk.Label(
                    self.breadcrumb_frame,
                    text=state.title,
                    font=("Arial", 10),
                    fg="blue",
                    cursor="hand2",
                )
                label.bind("<Button-1>", lambda e, s=state: self._navigate_to_state(s))

            label.pack(side=tk.LEFT)
            self.breadcrumb_labels.append(label)

    def _go_back(self):
        """Navigate back."""
        state = self.nav_history.go_back()
        if state:
            logger.info(f"Navigated back to: {state.title}")

    def _go_forward(self):
        """Navigate forward."""
        state = self.nav_history.go_forward()
        if state:
            logger.info(f"Navigated forward to: {state.title}")

    def _go_home(self):
        """Navigate to home."""
        # Add home navigation
        self.nav_history.add_navigation(
            NavigationAction.NAVIGATE, "Home", "Return to main screen", {"view": "home"}
        )

    def _toggle_bookmark(self):
        """Toggle bookmark for current state."""
        current = self.nav_history.get_current_state()
        if not current:
            return

        bookmarks = self.nav_history.get_bookmarks()
        is_bookmarked = any(b.id == current.id for b in bookmarks)

        if is_bookmarked:
            self.nav_history.remove_bookmark(current.id)
        else:
            self.nav_history.add_bookmark(current.id)

    def _navigate_to_state(self, state: NavigationState):
        """Navigate to a specific state."""
        # Find the state in history and navigate to it
        for i, history_state in enumerate(self.nav_history.history):
            if history_state.id == state.id:
                self.nav_history.current_index = i

                # Notify callbacks
                for callback in self.nav_history.navigation_callbacks:
                    try:
                        callback("navigation_jump", state)
                    except Exception as e:
                        logger.error(f"Navigation callback error: {e}")

                self._update_navigation_state()
                self._update_breadcrumbs()
                break

    def set_navigation_callback(self, callback: Callable):
        """Set custom navigation callback."""
        self.navigation_callback = callback

    def show_history_dialog(self):
        """Show navigation history dialog."""
        dialog = tk.Toplevel(self.parent)
        dialog.title("Navigation History")
        dialog.geometry("600x400")

        # Create treeview for history
        columns = ("Time", "Action", "Title", "Description")
        tree = ttk.Treeview(dialog, columns=columns, show="tree headings")

        tree.heading("#0", text="")
        tree.heading("Time", text="Time")
        tree.heading("Action", text="Action")
        tree.heading("Title", text="Title")
        tree.heading("Description", text="Description")

        tree.column("#0", width=0, stretch=False)
        tree.column("Time", width=120)
        tree.column("Action", width=100)
        tree.column("Title", width=150)
        tree.column("Description", width=200)

        # Add history items
        for state in self.nav_history.history:
            tree.insert(
                "",
                tk.END,
                values=(
                    state.timestamp.strftime("%H:%M:%S"),
                    state.action.value,
                    state.title,
                    (
                        state.description[:50] + "..."
                        if len(state.description) > 50
                        else state.description
                    ),
                ),
                tags=(state.id,),
            )

        # Bind double-click to navigate
        def on_double_click(event):
            selection = tree.selection()
            if selection:
                item = tree.item(selection[0])
                state_id = item["tags"][0]
                state = next(
                    (s for s in self.nav_history.history if s.id == state_id), None
                )
                if state:
                    self._navigate_to_state(state)
                    dialog.destroy()

        tree.bind("<Double-1>", on_double_click)

        # Pack tree with scrollbar
        scrollbar = ttk.Scrollbar(dialog, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)

        # Close button
        close_btn = ttk.Button(dialog, text="Close", command=dialog.destroy)
        close_btn.pack(pady=10)


def create_navigation_widget(
    parent: tk.Widget, navigation_history: NavigationHistory
) -> NavigationWidget:
    """
    Convenience function to create a navigation widget.

    Args:
        parent: Parent widget
        navigation_history: NavigationHistory instance

    Returns:
        NavigationWidget instance
    """
    return NavigationWidget(parent, navigation_history)
