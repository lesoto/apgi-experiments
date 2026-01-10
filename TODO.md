# APGI Framework TODO

## Issues 

#### ISSUE-001: Inconsistent Logging
- Some legacy modules may still use different formats
- Priority: Low - cosmetic issue

#### ISSUE-002: Hard-coded Parameters
⚠️ **Some Hard-coded Values Persist**
- Found in examples, GUI components, and test files
- Thresholds and constants still embedded in code
- Priority: Low - technical debt

### LAUNCHER-001: Missing Dependencies
⚠️ **Flask Dependencies Missing**
- **Interactive Dashboard**: Requires `flask-socketio` (added to requirements.txt)
- **APGI Framework App**: Has relative import issues when run directly
- **Impact**: Some GUI applications fail to launch
- **Status**: Dependencies added, import fixes needed

### GUI-001: Configuration Interface Issues
⚠️ **Parameter Configuration Problems**
- **ConfigManager API**: Missing required arguments in some calls
- **GUI Integration**: Some parameter panels failing to load configurations
- **Impact**: Manual configuration required for some features
