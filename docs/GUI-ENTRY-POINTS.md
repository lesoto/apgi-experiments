# APGI Framework GUI Entry Points

This document describes the different GUI entry points and their intended use cases.

## Primary Entry Points

### 1. `GUI.py` (5,691 lines)

**Purpose:** Main comprehensive GUI application
**Features:**

- Full-featured experiment management
- Real-time monitoring dashboard
- Advanced parameter configuration
- Data visualization and export
- Multi-threaded experiment execution

**Use Case:** Primary interface for researchers and power users

## Secondary Entry Points

### 2. `GUI-Launcher.py` (1,030 lines)

**Purpose:** Centralized launcher for all GUI applications
**Features:**

- Menu-driven selection of different GUIs
- System information and requirements checking
- Easy switching between interfaces

**Use Case:** Entry point for users who need access to multiple GUI types

- **New Users:** Start with `GUI-Launcher.py` for easy interface selection
- **Researchers:** Use `GUI.py` for full-featured experiment management
- **System Administrators:** Use `GUI-Launcher.py` to provide access to all interfaces

## File Organization

The current structure has multiple entry points which can be confusing. Consider the following improvements:

1. **Consolidate entry points** into a single main launcher
2. **Standardize naming** convention (GUI_Main.py, GUI_Simple.py, etc.)
3. **Document purpose** of each entry point in code comments
4. **Create clear hierarchy** with primary vs secondary interfaces
