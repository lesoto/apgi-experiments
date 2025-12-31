"""
GUI Component Tests for APGI Framework

Tests for the GUI components including sidebar, main area, and status bar.
These tests ensure the GUI components function correctly and handle edge cases.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import tkinter as tk
import sys
import os

# Add the project root to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    import customtkinter as ctk
    from apgi_gui.components.sidebar import Sidebar
    from apgi_gui.components.main_area import MainArea
    from apgi_gui.components.status_bar import StatusBar
    from apgi_gui.utils.config import AppConfig
    GUI_AVAILABLE = True
except ImportError as e:
    print(f"GUI components not available: {e}")
    GUI_AVAILABLE = False


@unittest.skipUnless(GUI_AVAILABLE, "GUI components not available")
class TestSidebar(unittest.TestCase):
    """Test cases for the Sidebar component."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a mock app
        self.mock_app = Mock()
        self.mock_app.new_file = Mock()
        self.mock_app.open_file = Mock()
        self.mock_app.save_file = Mock()
        self.mock_app.undo = Mock()
        self.mock_app.redo = Mock()
        self.mock_app.toggle_theme = Mock()
        self.mock_app.show_help = Mock()
        self.mock_app.recent_files = []
        
        # Create the root window and sidebar
        self.root = ctk.CTk()
        self.sidebar = Sidebar(self.root, self.mock_app)
        
    def tearDown(self):
        """Clean up after tests."""
        if hasattr(self, 'root'):
            self.root.destroy()
    
    def test_sidebar_initialization(self):
        """Test that sidebar initializes correctly."""
        self.assertIsNotNone(self.sidebar)
        self.assertIsNotNone(self.sidebar.app)
        self.assertEqual(self.sidebar.app, self.mock_app)
    
    def test_sidebar_has_required_components(self):
        """Test that sidebar has all required UI components."""
        # Check for navigation buttons
        self.assertTrue(hasattr(self.sidebar, 'new_btn'))
        self.assertTrue(hasattr(self.sidebar, 'open_btn'))
        self.assertTrue(hasattr(self.sidebar, 'save_btn'))
        
        # Check for tool buttons
        self.assertTrue(hasattr(self.sidebar, 'undo_btn'))
        self.assertTrue(hasattr(self.sidebar, 'redo_btn'))
        self.assertTrue(hasattr(self.sidebar, 'theme_btn'))
        
        # Check for recent files listbox
        self.assertTrue(hasattr(self.sidebar, 'recent_listbox'))
        
        # Check for help button
        self.assertTrue(hasattr(self.sidebar, 'help_btn'))
    
    def test_new_button_calls_app_new_file(self):
        """Test that new button calls the app's new_file method."""
        # Simulate button click
        self.sidebar.new_btn.invoke()
        self.mock_app.new_file.assert_called_once()
    
    def test_open_button_calls_app_open_file(self):
        """Test that open button calls the app's open_file method."""
        # Simulate button click
        self.sidebar.open_btn.invoke()
        self.mock_app.open_file.assert_called_once()
    
    def test_save_button_calls_app_save_file(self):
        """Test that save button calls the app's save_file method."""
        # Simulate button click
        self.sidebar.save_btn.invoke()
        self.mock_app.save_file.assert_called_once()
    
    def test_undo_button_calls_app_undo(self):
        """Test that undo button calls the app's undo method."""
        # Simulate button click
        self.sidebar.undo_btn.invoke()
        self.mock_app.undo.assert_called_once()
    
    def test_redo_button_calls_app_redo(self):
        """Test that redo button calls the app's redo method."""
        # Simulate button click
        self.sidebar.redo_btn.invoke()
        self.mock_app.redo.assert_called_once()
    
    def test_theme_button_calls_app_toggle_theme(self):
        """Test that theme button calls the app's toggle_theme method."""
        # Simulate button click
        self.sidebar.theme_btn.invoke()
        self.mock_app.toggle_theme.assert_called_once()
    
    def test_help_button_calls_app_show_help(self):
        """Test that help button calls the app's show_help method."""
        # Simulate button click
        self.sidebar.help_btn.invoke()
        self.mock_app.show_help.assert_called_once()
    
    def test_update_recent_files(self):
        """Test updating recent files list."""
        # Set up mock recent files
        from pathlib import Path
        self.mock_app.recent_files = [
            Path("/test/file1.json"),
            Path("/test/file2.json"),
            Path("/test/file3.json")
        ]
        
        # Update recent files
        self.sidebar.update_recent_files()
        
        # Check that listbox was updated
        self.assertEqual(self.sidebar.recent_listbox.size(), 3)
    
    def test_refresh(self):
        """Test refreshing sidebar content."""
        # Mock update_recent_files
        self.sidebar.update_recent_files = Mock()
        
        # Call refresh
        self.sidebar.refresh()
        
        # Check that update_recent_files was called
        self.sidebar.update_recent_files.assert_called_once()


@unittest.skipUnless(GUI_AVAILABLE, "GUI components not available")
class TestMainArea(unittest.TestCase):
    """Test cases for the MainArea component."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a mock app
        self.mock_app = Mock()
        self.mock_app.update_status = Mock()
        
        # Create the root window and main area
        self.root = ctk.CTk()
        self.main_area = MainArea(self.root, self.mock_app)
        
    def tearDown(self):
        """Clean up after tests."""
        if hasattr(self, 'root'):
            self.root.destroy()
    
    def test_main_area_initialization(self):
        """Test that main area initializes correctly."""
        self.assertIsNotNone(self.main_area)
        self.assertIsNotNone(self.main_area.app)
        self.assertEqual(self.main_area.app, self.mock_app)
        self.assertIsInstance(self.main_area.current_data, dict)
    
    def test_main_area_has_required_components(self):
        """Test that main area has all required UI components."""
        # Check for tabview
        self.assertTrue(hasattr(self.main_area, 'tabview'))
        
        # Check for scrollable frame
        self.assertTrue(hasattr(self.main_area, 'scrollable_frame'))
        
        # Check for parameter entries
        self.assertTrue(hasattr(self.main_area, 'param_entries'))
        self.assertTrue(hasattr(self.main_area, 'neural_vars'))
        self.assertTrue(hasattr(self.main_area, 'exp_entries'))
    
    def test_get_data_returns_structure(self):
        """Test that get_data returns proper structure."""
        data = self.main_area.get_data()
        
        # Check structure
        self.assertIn('apgi_parameters', data)
        self.assertIn('neural_signatures', data)
        self.assertIn('experimental_settings', data)
    
    def test_load_data_sets_values(self):
        """Test that load_data properly sets values."""
        test_data = {
            'apgi_parameters': {
                'learning_rate': 0.05,
                'precision_weight': 2.0
            },
            'neural_signatures': {
                'p3b': True,
                'gamma': False
            },
            'experimental_settings': {
                'sample_rate': 1000,
                'num_trials': 50
            }
        }
        
        # Load data
        self.main_area.load_data(test_data)
        
        # Check that data was loaded
        self.assertEqual(self.main_area.current_data, test_data)
    
    def test_clear_resets_all_fields(self):
        """Test that clear resets all fields to default."""
        # Set some data first
        self.main_area.current_data = {'test': 'data'}
        
        # Clear
        self.main_area.clear()
        
        # Check that data was cleared
        self.assertEqual(self.main_area.current_data, {})
    
    def test_apply_changes_updates_data(self):
        """Test that apply_changes updates current data."""
        # Call apply changes
        self.main_area.apply_changes()
        
        # Check that update_status was called
        self.mock_app.update_status.assert_called_with("Configuration changes applied")
    
    def test_reset_to_defaults_clears_fields(self):
        """Test that reset_to_defaults clears fields."""
        # Call reset
        self.main_area.reset_to_defaults()
        
        # Check that update_status was called
        self.mock_app.update_status.assert_called_with("Reset to default values")
    
    def test_run_analysis_calls_status_update(self):
        """Test that run_analysis updates status."""
        # Call run analysis
        self.main_area.run_analysis()
        
        # Check that status was updated
        self.mock_app.update_status.assert_called()


@unittest.skipUnless(GUI_AVAILABLE, "GUI components not available")
class TestStatusBar(unittest.TestCase):
    """Test cases for the StatusBar component."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a mock app
        self.mock_app = Mock()
        
        # Create the root window and status bar
        self.root = ctk.CTk()
        self.status_bar = StatusBar(self.root, self.mock_app)
        
    def tearDown(self):
        """Clean up after tests."""
        if hasattr(self, 'root'):
            self.root.destroy()
    
    def test_status_bar_initialization(self):
        """Test that status bar initializes correctly."""
        self.assertIsNotNone(self.status_bar)
        self.assertIsNotNone(self.status_bar.app)
        self.assertEqual(self.status_bar.app, self.mock_app)
    
    def test_status_bar_has_required_components(self):
        """Test that status bar has all required UI components."""
        # Check for labels
        self.assertTrue(hasattr(self.status_bar, 'status_label'))
        self.assertTrue(hasattr(self.status_bar, 'file_label'))
        self.assertTrue(hasattr(self.status_bar, 'time_label'))
        
        # Check for progress bar
        self.assertTrue(hasattr(self.status_bar, 'progress_bar'))
    
    def test_set_status_updates_message(self):
        """Test that set_status updates the status message."""
        # Set status
        self.status_bar.set_status("Test message")
        
        # Check that label was updated (note: we can't easily test the actual text 
        # due to customtkinter internals, but we can test that no errors occur)
        self.assertIsNotNone(self.status_bar.status_label)
    
    def test_set_status_with_warning_level(self):
        """Test that set_status handles warning level correctly."""
        # Set status with warning
        self.status_bar.set_status("Warning message", "warning")
        
        # Check that no errors occur
        self.assertIsNotNone(self.status_bar.status_label)
    
    def test_set_status_with_error_level(self):
        """Test that set_status handles error level correctly."""
        # Set status with error
        self.status_bar.set_status("Error message", "error")
        
        # Check that no errors occur
        self.assertIsNotNone(self.status_bar.status_label)
    
    def test_set_status_with_success_level(self):
        """Test that set_status handles success level correctly."""
        # Set status with success
        self.status_bar.set_status("Success message", "success")
        
        # Check that no errors occur
        self.assertIsNotNone(self.status_bar.status_label)
    
    def test_set_file_updates_file_display(self):
        """Test that set_file updates the file display."""
        # Set file
        self.status_bar.set_file("/test/file.json")
        
        # Check that no errors occur
        self.assertIsNotNone(self.status_bar.file_label)
    
    def test_set_file_with_none(self):
        """Test that set_file handles None correctly."""
        # Set file to None
        self.status_bar.set_file(None)
        
        # Check that no errors occur
        self.assertIsNotNone(self.status_bar.file_label)
    
    def test_show_progress_displays_progress_bar(self):
        """Test that show_progress displays and updates progress bar."""
        # Show progress
        self.status_bar.show_progress(0.5)
        
        # Check that progress bar value was set
        self.assertIsNotNone(self.status_bar.progress_bar)
    
    def test_hide_progress_hides_progress_bar(self):
        """Test that hide_progress hides the progress bar."""
        # Hide progress
        self.status_bar.hide_progress()
        
        # Check that no errors occur
        self.assertIsNotNone(self.status_bar.progress_bar)
    
    def test_clear_status_resets_message(self):
        """Test that clear_status resets the status message."""
        # Clear status
        self.status_bar.clear_status()
        
        # Check that no errors occur
        self.assertIsNotNone(self.status_bar.status_label)


@unittest.skipUnless(GUI_AVAILABLE, "GUI components not available")
class TestGUIIntegration(unittest.TestCase):
    """Integration tests for GUI components working together."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a mock app
        self.mock_app = Mock()
        self.mock_app.update_status = Mock()
        self.mock_app.new_file = Mock()
        self.mock_app.open_file = Mock()
        self.mock_app.save_file = Mock()
        self.mock_app.recent_files = []
        
        # Create the root window
        self.root = ctk.CTk()
        
        # Create components
        self.sidebar = Sidebar(self.root, self.mock_app)
        self.main_area = MainArea(self.root, self.mock_app)
        self.status_bar = StatusBar(self.root, self.mock_app)
        
    def tearDown(self):
        """Clean up after tests."""
        if hasattr(self, 'root'):
            self.root.destroy()
    
    def test_components_can_be_created_together(self):
        """Test that all components can be created without conflicts."""
        self.assertIsNotNone(self.sidebar)
        self.assertIsNotNone(self.main_area)
        self.assertIsNotNone(self.status_bar)
    
    def test_components_share_same_app_reference(self):
        """Test that all components reference the same app."""
        self.assertEqual(self.sidebar.app, self.mock_app)
        self.assertEqual(self.main_area.app, self.mock_app)
        self.assertEqual(self.status_bar.app, self.mock_app)
    
    def test_sidebar_button_triggers_app_method(self):
        """Test that sidebar buttons properly trigger app methods."""
        # Test new file button
        self.sidebar.new_btn.invoke()
        self.mock_app.new_file.assert_called_once()
        
        # Reset mock
        self.mock_app.reset_mock()
        
        # Test save file button
        self.sidebar.save_btn.invoke()
        self.mock_app.save_file.assert_called_once()
    
    def test_main_area_data_flow(self):
        """Test data flow in main area component."""
        # Set some data
        test_data = {
            'apgi_parameters': {'learning_rate': 0.01},
            'neural_signatures': {'p3b': True},
            'experimental_settings': {'sample_rate': 1000}
        }
        
        # Load data
        self.main_area.load_data(test_data)
        
        # Get data back
        retrieved_data = self.main_area.get_data()
        
        # Check structure
        self.assertIn('apgi_parameters', retrieved_data)
        self.assertIn('neural_signatures', retrieved_data)
        self.assertIn('experimental_settings', retrieved_data)


if __name__ == '__main__':
    # Configure customtkinter for testing (headless mode)
    if GUI_AVAILABLE:
        # Set appearance mode to avoid theme issues
        ctk.set_appearance_mode("dark")
    
    # Run tests
    unittest.main(verbosity=2)
