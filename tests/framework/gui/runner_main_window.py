"""
Main Test Runner Window

This module implements the primary GUI window for the test runner with test organization,
selection, and execution controls.
"""

import sys
from typing import Dict, List, Optional, Set
from pathlib import Path

try:
    from PySide6.QtWidgets import (
        QApplication,
        QMainWindow,
        QWidget,
        QVBoxLayout,
        QHBoxLayout,
        QTreeWidget,
        QTreeWidgetItem,
        QPushButton,
        QLineEdit,
        QComboBox,
        QCheckBox,
        QGroupBox,
        QSplitter,
        QTabWidget,
        QTextEdit,
        QProgressBar,
        QLabel,
        QSpinBox,
        QDoubleSpinBox,
        QFrame,
        QScrollArea,
    )
    from PySide6.QtCore import Qt, Signal, QTimer, QThread, pyqtSignal
    from PySide6.QtGui import QIcon, QFont, QPixmap

    PYSIDE6_AVAILABLE = True
except ImportError:
    # Fallback for environments without PySide6
    PYSIDE6_AVAILABLE = False

    class QMainWindow:
        pass

    class QWidget:
        pass

    class QTreeWidget:
        pass

    class QTreeWidgetItem:
        pass

    class QPushButton:
        pass

    class QLineEdit:
        pass

    class QComboBox:
        pass

    class QCheckBox:
        pass

    class QGroupBox:
        pass

    class QSplitter:
        pass

    class QTabWidget:
        pass

    class QTextEdit:
        pass

    class QProgressBar:
        pass

    class QLabel:
        pass

    class QSpinBox:
        pass

    class QDoubleSpinBox:
        pass

    class QFrame:
        pass

    class QScrollArea:
        pass

    class QVBoxLayout:
        pass

    class QHBoxLayout:
        pass

    class Signal:
        def __init__(self, *args):
            pass

    class QTimer:
        pass

    class QThread:
        pass

    class Qt:
        Unchecked = 0
        Checked = 2
        PartiallyChecked = 1
        UserRole = 256
        Horizontal = 1
        ExtendedSelection = 3
        ItemIsTristate = 1
        ItemIsUserCheckable = 16

    pyqtSignal = Signal

from apgi_framework.utils.test_utils import (
    TestDefinition,
    TestRunCategory,
    TestRunExecution,
    TestConfiguration,
    TestResults,
)


class TestTreeWidget(QTreeWidget):
    """Custom tree widget for displaying tests with categories and modules."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHeaderLabels(["Test Name", "Category", "Module", "Status", "Time"])
        self.setSelectionMode(QTreeWidget.ExtendedSelection)
        self.itemChanged.connect(self._on_item_changed)
        self._test_items: Dict[str, QTreeWidgetItem] = {}

    def populate_tests(self, test_cases: List[TestDefinition]):
        """Populate the tree with test cases organized by category and module."""
        self.clear()
        self._test_items.clear()

        # Group tests by category and module
        category_groups: Dict[TestRunCategory, Dict[str, List[TestDefinition]]] = {}

        for test_case in test_cases:
            if test_case.category not in category_groups:
                category_groups[test_case.category] = {}

            if test_case.module not in category_groups[test_case.category]:
                category_groups[test_case.category][test_case.module] = []

            category_groups[test_case.category][test_case.module].append(test_case)

        # Create tree structure
        for category, modules in category_groups.items():
            category_item = QTreeWidgetItem(
                self, [category.value.title(), "", "", "", ""]
            )
            category_item.setFlags(
                category_item.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable
            )
            category_item.setCheckState(0, Qt.Unchecked)

            for module_name, tests in modules.items():
                module_item = QTreeWidgetItem(
                    category_item, [module_name, "", "", "", ""]
                )
                module_item.setFlags(
                    module_item.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable
                )
                module_item.setCheckState(0, Qt.Unchecked)

                for test in tests:
                    test_item = QTreeWidgetItem(
                        module_item,
                        [
                            test.name,
                            test.category.value,
                            test.module,
                            test.status.value if hasattr(test, "status") else "Not Run",
                            (
                                f"{test.execution_time:.3f}s"
                                if test.execution_time > 0
                                else ""
                            ),
                        ],
                    )
                    test_item.setFlags(test_item.flags() | Qt.ItemIsUserCheckable)
                    test_item.setCheckState(0, Qt.Unchecked)
                    test_item.setData(0, Qt.UserRole, test)
                    self._test_items[test.name] = test_item

        self.expandAll()

    def get_selected_tests(self) -> List[TestDefinition]:
        """Get all checked test cases."""
        selected_tests = []

        for test_name, item in self._test_items.items():
            if item.checkState(0) == Qt.Checked:
                test_data = item.data(0, Qt.UserRole)
                if test_data:
                    selected_tests.append(test_data)

        return selected_tests

    def update_test_status(
        self, test_name: str, status: str, execution_time: float = 0.0
    ):
        """Update the status and execution time of a test."""
        if test_name in self._test_items:
            item = self._test_items[test_name]
            item.setText(3, status)
            if execution_time > 0:
                item.setText(4, f"{execution_time:.3f}s")

    def _on_item_changed(self, item: QTreeWidgetItem, column: int):
        """Handle item check state changes."""
        if column == 0:  # Only handle check state changes
            self._update_parent_check_state(item)
            self._update_child_check_states(item)

    def _update_parent_check_state(self, item: QTreeWidgetItem):
        """Update parent item check state based on children."""
        parent = item.parent()
        if not parent:
            return

        checked_count = 0
        total_count = parent.childCount()

        for i in range(total_count):
            child = parent.child(i)
            if child.checkState(0) == Qt.Checked:
                checked_count += 1

        if checked_count == 0:
            parent.setCheckState(0, Qt.Unchecked)
        elif checked_count == total_count:
            parent.setCheckState(0, Qt.Checked)
        else:
            parent.setCheckState(0, Qt.PartiallyChecked)

        self._update_parent_check_state(parent)

    def _update_child_check_states(self, item: QTreeWidgetItem):
        """Update child item check states based on parent."""
        if item.checkState(0) != Qt.PartiallyChecked:
            check_state = item.checkState(0)
            for i in range(item.childCount()):
                child = item.child(i)
                child.setCheckState(0, check_state)
                self._update_child_check_states(child)


class TestFilterWidget(QWidget):
    """Widget for filtering tests by various criteria."""

    filter_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """Set up the filter UI."""
        layout = QVBoxLayout(self)

        # Search filter
        search_group = QGroupBox("Search")
        search_layout = QVBoxLayout(search_group)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search tests by name...")
        self.search_input.textChanged.connect(self.filter_changed.emit)
        search_layout.addWidget(self.search_input)

        layout.addWidget(search_group)

        # Category filter
        category_group = QGroupBox("Categories")
        category_layout = QVBoxLayout(category_group)

        self.category_checkboxes = {}
        for category in TestRunCategory:
            checkbox = QCheckBox(category.value.title())
            checkbox.setChecked(True)
            checkbox.stateChanged.connect(self.filter_changed.emit)
            self.category_checkboxes[category] = checkbox
            category_layout.addWidget(checkbox)

        layout.addWidget(category_group)

        # Module filter
        module_group = QGroupBox("Modules")
        module_layout = QVBoxLayout(module_group)

        self.module_combo = QComboBox()
        self.module_combo.addItem("All Modules")
        self.module_combo.currentTextChanged.connect(self.filter_changed.emit)
        module_layout.addWidget(self.module_combo)

        layout.addWidget(module_group)

        # Status filter
        status_group = QGroupBox("Status")
        status_layout = QVBoxLayout(status_group)

        self.show_passed = QCheckBox("Show Passed")
        self.show_failed = QCheckBox("Show Failed")
        self.show_skipped = QCheckBox("Show Skipped")
        self.show_not_run = QCheckBox("Show Not Run")

        for checkbox in [
            self.show_passed,
            self.show_failed,
            self.show_skipped,
            self.show_not_run,
        ]:
            checkbox.setChecked(True)
            checkbox.stateChanged.connect(self.filter_changed.emit)
            status_layout.addWidget(checkbox)

        layout.addWidget(status_group)

    def update_modules(self, modules: List[str]):
        """Update the module filter with available modules."""
        current_text = self.module_combo.currentText()
        self.module_combo.clear()
        self.module_combo.addItem("All Modules")
        self.module_combo.addItems(sorted(modules))

        # Restore previous selection if it still exists
        index = self.module_combo.findText(current_text)
        if index >= 0:
            self.module_combo.setCurrentIndex(index)

    def get_filter_criteria(self) -> Dict:
        """Get current filter criteria."""
        return {
            "search_text": self.search_input.text().lower(),
            "categories": [
                cat for cat, cb in self.category_checkboxes.items() if cb.isChecked()
            ],
            "module": (
                self.module_combo.currentText()
                if self.module_combo.currentText() != "All Modules"
                else None
            ),
            "show_passed": self.show_passed.isChecked(),
            "show_failed": self.show_failed.isChecked(),
            "show_skipped": self.show_skipped.isChecked(),
            "show_not_run": self.show_not_run.isChecked(),
        }


class TestConfigurationWidget(QWidget):
    """Widget for configuring test execution parameters."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """Set up the configuration UI."""
        layout = QVBoxLayout(self)

        # Execution settings
        exec_group = QGroupBox("Execution Settings")
        exec_layout = QVBoxLayout(exec_group)

        # Parallel execution
        parallel_layout = QHBoxLayout()
        self.parallel_checkbox = QCheckBox("Enable Parallel Execution")
        self.parallel_checkbox.setChecked(True)
        parallel_layout.addWidget(self.parallel_checkbox)

        parallel_layout.addWidget(QLabel("Max Workers:"))
        self.max_workers_spin = QSpinBox()
        self.max_workers_spin.setRange(1, 16)
        self.max_workers_spin.setValue(4)
        parallel_layout.addWidget(self.max_workers_spin)

        exec_layout.addLayout(parallel_layout)

        # Timeout
        timeout_layout = QHBoxLayout()
        timeout_layout.addWidget(QLabel("Timeout (seconds):"))
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(10, 3600)
        self.timeout_spin.setValue(300)
        timeout_layout.addWidget(self.timeout_spin)
        exec_layout.addLayout(timeout_layout)

        # Verbose output
        self.verbose_checkbox = QCheckBox("Verbose Output")
        exec_layout.addWidget(self.verbose_checkbox)

        layout.addWidget(exec_group)

        # Coverage settings
        coverage_group = QGroupBox("Coverage Settings")
        coverage_layout = QVBoxLayout(coverage_group)

        self.collect_coverage_checkbox = QCheckBox("Collect Coverage Data")
        self.collect_coverage_checkbox.setChecked(True)
        coverage_layout.addWidget(self.collect_coverage_checkbox)

        # Coverage thresholds
        threshold_layout = QHBoxLayout()
        threshold_layout.addWidget(QLabel("Line Coverage Threshold:"))
        self.line_threshold_spin = QDoubleSpinBox()
        self.line_threshold_spin.setRange(0.0, 100.0)
        self.line_threshold_spin.setValue(95.0)
        self.line_threshold_spin.setSuffix("%")
        threshold_layout.addWidget(self.line_threshold_spin)

        threshold_layout.addWidget(QLabel("Branch Coverage Threshold:"))
        self.branch_threshold_spin = QDoubleSpinBox()
        self.branch_threshold_spin.setRange(0.0, 100.0)
        self.branch_threshold_spin.setValue(90.0)
        self.branch_threshold_spin.setSuffix("%")
        threshold_layout.addWidget(self.branch_threshold_spin)

        coverage_layout.addLayout(threshold_layout)

        layout.addWidget(coverage_group)

        # Property test settings
        property_group = QGroupBox("Property Test Settings")
        property_layout = QVBoxLayout(property_group)

        iterations_layout = QHBoxLayout()
        iterations_layout.addWidget(QLabel("Iterations:"))
        self.iterations_spin = QSpinBox()
        self.iterations_spin.setRange(10, 10000)
        self.iterations_spin.setValue(100)
        iterations_layout.addWidget(self.iterations_spin)
        property_layout.addLayout(iterations_layout)

        layout.addWidget(property_group)

    def get_configuration(self) -> TestConfiguration:
        """Get the current test configuration."""
        return TestConfiguration(
            parallel_execution=self.parallel_checkbox.isChecked(),
            max_workers=self.max_workers_spin.value(),
            timeout_seconds=self.timeout_spin.value(),
            coverage_thresholds={
                "line": self.line_threshold_spin.value(),
                "branch": self.branch_threshold_spin.value(),
            },
            property_test_iterations=self.iterations_spin.value(),
            collect_coverage=self.collect_coverage_checkbox.isChecked(),
            verbose_output=self.verbose_checkbox.isChecked(),
        )

    def set_configuration(self, config: TestConfiguration):
        """Set the configuration values."""
        self.parallel_checkbox.setChecked(config.parallel_execution)
        self.max_workers_spin.setValue(config.max_workers)
        self.timeout_spin.setValue(config.timeout_seconds)
        self.line_threshold_spin.setValue(config.coverage_thresholds.get("line", 95.0))
        self.branch_threshold_spin.setValue(
            config.coverage_thresholds.get("branch", 90.0)
        )
        self.iterations_spin.setValue(config.property_test_iterations)
        self.collect_coverage_checkbox.setChecked(config.collect_coverage)
        self.verbose_checkbox.setChecked(config.verbose_output)


class MainTestWindow(QMainWindow):
    """Main window for the test runner GUI."""

    # Signals
    test_execution_requested = Signal(list, TestConfiguration)  # selected_tests, config
    test_execution_cancelled = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._test_cases: List[TestDefinition] = []
        self._filtered_tests: List[TestDefinition] = []
        self._setup_ui()
        self._setup_connections()

    def _setup_ui(self):
        """Set up the main UI."""
        self.setWindowTitle("APGI Test Runner")
        self.setMinimumSize(1200, 800)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QHBoxLayout(central_widget)

        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)

        # Left panel - Test organization and filters
        left_panel = self._create_left_panel()
        splitter.addWidget(left_panel)

        # Right panel - Configuration and controls
        right_panel = self._create_right_panel()
        splitter.addWidget(right_panel)

        # Set splitter proportions
        splitter.setSizes([800, 400])

    def _create_left_panel(self) -> QWidget:
        """Create the left panel with test tree and filters."""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # Test tree
        tree_group = QGroupBox("Test Suite")
        tree_layout = QVBoxLayout(tree_group)

        # Test selection controls
        selection_layout = QHBoxLayout()
        self.select_all_btn = QPushButton("Select All")
        self.select_none_btn = QPushButton("Select None")
        self.expand_all_btn = QPushButton("Expand All")
        self.collapse_all_btn = QPushButton("Collapse All")

        selection_layout.addWidget(self.select_all_btn)
        selection_layout.addWidget(self.select_none_btn)
        selection_layout.addWidget(self.expand_all_btn)
        selection_layout.addWidget(self.collapse_all_btn)
        selection_layout.addStretch()

        tree_layout.addLayout(selection_layout)

        # Test tree widget
        self.test_tree = TestTreeWidget()
        tree_layout.addWidget(self.test_tree)

        layout.addWidget(tree_group)

        # Filter panel
        filter_scroll = QScrollArea()
        self.filter_widget = TestFilterWidget()
        filter_scroll.setWidget(self.filter_widget)
        filter_scroll.setWidgetResizable(True)
        filter_scroll.setMaximumWidth(300)

        layout.addWidget(filter_scroll)

        return panel

    def _create_right_panel(self) -> QWidget:
        """Create the right panel with configuration and controls."""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # Configuration widget
        config_scroll = QScrollArea()
        self.config_widget = TestConfigurationWidget()
        config_scroll.setWidget(self.config_widget)
        config_scroll.setWidgetResizable(True)

        layout.addWidget(config_scroll)

        # Execution controls
        controls_group = QGroupBox("Execution Controls")
        controls_layout = QVBoxLayout(controls_group)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        controls_layout.addWidget(self.progress_bar)

        # Status label
        self.status_label = QLabel("Ready")
        controls_layout.addWidget(self.status_label)

        # Control buttons
        button_layout = QHBoxLayout()

        self.run_selected_btn = QPushButton("Run Selected Tests")
        self.run_selected_btn.setStyleSheet(
            "QPushButton { background-color: #4CAF50; color: white; font-weight: bold; }"
        )

        self.run_all_btn = QPushButton("Run All Tests")
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setEnabled(False)

        button_layout.addWidget(self.run_selected_btn)
        button_layout.addWidget(self.run_all_btn)
        button_layout.addWidget(self.cancel_btn)

        controls_layout.addLayout(button_layout)

        # Test count info
        self.test_count_label = QLabel("Tests: 0 total, 0 selected")
        controls_layout.addWidget(self.test_count_label)

        layout.addWidget(controls_group)

        return panel

    def _setup_connections(self):
        """Set up signal connections."""
        # Tree selection controls
        self.select_all_btn.clicked.connect(self._select_all_tests)
        self.select_none_btn.clicked.connect(self._select_no_tests)
        self.expand_all_btn.clicked.connect(self.test_tree.expandAll)
        self.collapse_all_btn.clicked.connect(self.test_tree.collapseAll)

        # Execution controls
        self.run_selected_btn.clicked.connect(self._run_selected_tests)
        self.run_all_btn.clicked.connect(self._run_all_tests)
        self.cancel_btn.clicked.connect(self._cancel_execution)

        # Filter changes
        self.filter_widget.filter_changed.connect(self._apply_filters)

        # Test tree changes
        self.test_tree.itemChanged.connect(self._update_test_count)

    def load_test_cases(self, test_cases: List[TestDefinition]):
        """Load test cases into the tree."""
        self._test_cases = test_cases
        self._filtered_tests = test_cases.copy()

        # Update module filter
        modules = list(set(test.module for test in test_cases))
        self.filter_widget.update_modules(modules)

        # Populate tree
        self.test_tree.populate_tests(self._filtered_tests)
        self._update_test_count()

    def _apply_filters(self):
        """Apply current filter criteria to test cases."""
        if not self._test_cases:
            return

        criteria = self.filter_widget.get_filter_criteria()
        filtered_tests = []

        for test in self._test_cases:
            # Search filter
            if (
                criteria["search_text"]
                and criteria["search_text"] not in test.name.lower()
            ):
                continue

            # Category filter
            if test.category not in criteria["categories"]:
                continue

            # Module filter
            if criteria["module"] and test.module != criteria["module"]:
                continue

            # Status filter (simplified for now)
            # In a real implementation, you'd check actual test status

            filtered_tests.append(test)

        self._filtered_tests = filtered_tests
        self.test_tree.populate_tests(self._filtered_tests)
        self._update_test_count()

    def _select_all_tests(self):
        """Select all visible tests."""
        iterator = QTreeWidgetItemIterator(self.test_tree)
        while iterator.value():
            item = iterator.value()
            if (
                item.flags() & Qt.ItemIsUserCheckable and item.parent()
            ):  # Only leaf items
                item.setCheckState(0, Qt.Checked)
            iterator += 1
        self._update_test_count()

    def _select_no_tests(self):
        """Deselect all tests."""
        iterator = QTreeWidgetItemIterator(self.test_tree)
        while iterator.value():
            item = iterator.value()
            if item.flags() & Qt.ItemIsUserCheckable:
                item.setCheckState(0, Qt.Unchecked)
            iterator += 1
        self._update_test_count()

    def _update_test_count(self):
        """Update the test count display."""
        total_tests = len(self._filtered_tests)
        selected_tests = len(self.test_tree.get_selected_tests())
        self.test_count_label.setText(
            f"Tests: {total_tests} total, {selected_tests} selected"
        )

    def _run_selected_tests(self):
        """Run the selected tests."""
        selected_tests = self.test_tree.get_selected_tests()
        if not selected_tests:
            self.status_label.setText("No tests selected")
            return

        config = self.config_widget.get_configuration()
        self._start_execution()
        self.test_execution_requested.emit(selected_tests, config)

    def _run_all_tests(self):
        """Run all filtered tests."""
        if not self._filtered_tests:
            self.status_label.setText("No tests available")
            return

        # Select all tests first
        self._select_all_tests()
        selected_tests = self.test_tree.get_selected_tests()

        config = self.config_widget.get_configuration()
        self._start_execution()
        self.test_execution_requested.emit(selected_tests, config)

    def _cancel_execution(self):
        """Cancel test execution."""
        self.test_execution_cancelled.emit()
        self._stop_execution()

    def _start_execution(self):
        """Update UI for test execution start."""
        self.run_selected_btn.setEnabled(False)
        self.run_all_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.status_label.setText("Running tests...")

    def _stop_execution(self):
        """Update UI for test execution stop."""
        self.run_selected_btn.setEnabled(True)
        self.run_all_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        self.progress_bar.setVisible(False)
        self.status_label.setText("Ready")

    def update_execution_progress(
        self, current: int, total: int, current_test: str = ""
    ):
        """Update execution progress."""
        if total > 0:
            self.progress_bar.setRange(0, total)
            self.progress_bar.setValue(current)
            status_text = f"Running tests... ({current}/{total})"
            if current_test:
                status_text += f" - {current_test}"
            self.status_label.setText(status_text)

    def update_test_result(
        self, test_name: str, status: str, execution_time: float = 0.0
    ):
        """Update a test result in the tree."""
        self.test_tree.update_test_status(test_name, status, execution_time)

    def execution_completed(self, results: TestResults):
        """Handle execution completion."""
        self._stop_execution()

        # Update status
        pass_rate = (
            (results.passed_tests / results.total_tests * 100)
            if results.total_tests > 0
            else 0
        )
        self.status_label.setText(
            f"Completed: {results.passed_tests}/{results.total_tests} passed ({pass_rate:.1f}%)"
        )


def main():
    """Main function for testing the GUI."""
    app = QApplication(sys.argv)

    # Create sample test cases
    sample_tests = [
        TestDefinition(
            name="test_core_analysis",
            module="core.analysis",
            category=TestRunCategory.UNIT,
            file_path="tests/test_core_analysis.py",
        ),
        TestDefinition(
            name="test_clinical_integration",
            module="clinical",
            category=TestRunCategory.INTEGRATION,
            file_path="tests/test_clinical.py",
        ),
        TestDefinition(
            name="test_neural_processing",
            module="neural",
            category=TestRunCategory.MODULE_SPECIFIC,
            file_path="tests/test_neural.py",
        ),
    ]

    window = MainTestWindow()
    window.load_test_cases(sample_tests)
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
