"""
APGI Framework Reporting Module

This module provides comprehensive reporting capabilities including:
- PDF report generation with ReportLab
- Flexible template system with Jinja2
- Custom report layouts and styling
- Statistical report formatting
"""

# Import components with graceful fallback for missing dependencies
try:
    pass

    PDF_GENERATOR_AVAILABLE = True
except ImportError:
    PDF_GENERATOR_AVAILABLE = False

try:
    pass

    TEMPLATE_SYSTEM_AVAILABLE = True
except ImportError:
    TEMPLATE_SYSTEM_AVAILABLE = False


# Convenience functions
def get_available_features():
    """Get list of available reporting features."""
    features = []

    if PDF_GENERATOR_AVAILABLE:
        features.append("pdf_generation")

    if TEMPLATE_SYSTEM_AVAILABLE:
        features.append("template_system")

    return features


def is_feature_available(feature_name: str) -> bool:
    """Check if a specific reporting feature is available."""
    availability_map = {
        "pdf_generation": PDF_GENERATOR_AVAILABLE,
        "template_system": TEMPLATE_SYSTEM_AVAILABLE,
    }

    return availability_map.get(feature_name, False)


def get_missing_dependencies():
    """Get list of missing dependencies for reporting features."""
    missing = []

    if not PDF_GENERATOR_AVAILABLE:
        missing.append("reportlab>=3.6.0 (for PDF generation)")

    if not TEMPLATE_SYSTEM_AVAILABLE:
        missing.append("jinja2>=3.1.0 (for template system)")

    return missing


# Export availability flags and main classes
__all__ = [
    # Availability flags
    "PDF_GENERATOR_AVAILABLE",
    "TEMPLATE_SYSTEM_AVAILABLE",
    # Utility functions
    "get_available_features",
    "is_feature_available",
    "get_missing_dependencies",
]

# Conditionally add imports to __all__ if available
if PDF_GENERATOR_AVAILABLE:
    __all__.extend(
        [
            "PDFReportGenerator",
            "ReportConfig",
            "ReportSection",
            "APGIReportTemplate",
            "create_pdf_generator",
            "generate_experiment_report",
        ]
    )

if TEMPLATE_SYSTEM_AVAILABLE:
    __all__.extend(
        [
            "TemplateManager",
            "TemplateBuilder",
            "ReportTemplate",
            "TemplateSection",
            "TemplateVariable",
            "TemplateFormat",
            "create_template_manager",
            "create_template_builder",
        ]
    )
