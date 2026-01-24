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

### 2. `GUI-Simple.py` (896 lines)
**Purpose:** Simplified GUI template for basic usage
**Features:**
- Streamlined interface
- Basic experiment configuration
- Essential functionality only
- Easier to understand and modify

**Use Case:** Quick experiments, educational purposes, or as a template for custom GUIs

### 3. `GUI-Experiment-Registry.py`
**Purpose:** Experiment registry and management interface
**Features:**
- Experiment catalog and metadata management
- Template-based experiment creation
- Experiment tracking and organization

**Use Case:** Managing large collections of experiments and templates

## Secondary Entry Points

### 4. `launch_gui.py` (1,030 lines)
**Purpose:** Centralized launcher for all GUI applications
**Features:**
- Menu-driven selection of different GUIs
- System information and requirements checking
- Easy switching between interfaces

**Use Case:** Entry point for users who need access to multiple GUI types

### 5. `apgi_gui/app.py` (1,187 lines)
**Purpose:** Modular GUI application using component architecture
**Features:**
- Component-based design (sidebar, main area, status bar)
- Modern UI with CustomTkinter
- Plugin-friendly architecture

**Use Case:** Development and customization of GUI components

## Recommended Usage

- **New Users:** Start with `GUI-Simple.py` for basic functionality
- **Researchers:** Use `GUI.py` for full-featured experiment management
- **Developers:** Use `apgi_gui/app.py` for component-based development
- **System Administrators:** Use `launch_gui.py` to provide access to all interfaces

## File Organization

The current structure has multiple entry points which can be confusing. Consider the following improvements:

1. **Consolidate entry points** into a single main launcher
2. **Standardize naming** convention (GUI_Main.py, GUI_Simple.py, etc.)
3. **Document purpose** of each entry point in code comments
4. **Create clear hierarchy** with primary vs secondary interfaces
