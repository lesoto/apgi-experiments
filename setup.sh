#!/bin/bash

# APGI Framework Automated Setup Script
# This script sets up the APGI Framework for development and production use

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python is installed
check_python() {
    print_status "Checking Python installation..."
    
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        print_success "Python $PYTHON_VERSION found"
        
        # Check if version is >= 3.8
        if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
            print_success "Python version is compatible (>= 3.8)"
        else
            print_error "Python version must be >= 3.8. Current version: $PYTHON_VERSION"
            exit 1
        fi
    else
        print_error "Python 3 is not installed. Please install Python 3.8 or higher."
        exit 1
    fi
}

# Check if pip is installed
check_pip() {
    print_status "Checking pip installation..."
    
    if command -v pip3 &> /dev/null; then
        print_success "pip found"
    else
        print_error "pip is not installed. Please install pip."
        exit 1
    fi
}

# Create virtual environment
create_venv() {
    print_status "Creating virtual environment..."
    
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_success "Virtual environment created"
    else
        print_warning "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    print_success "Virtual environment activated"
}

# Upgrade pip
upgrade_pip() {
    print_status "Upgrading pip..."
    pip install --upgrade pip
    print_success "pip upgraded"
}

# Install dependencies
install_dependencies() {
    print_status "Installing dependencies..."
    
    # Install requirements
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        print_success "Dependencies installed from requirements.txt"
    else
        print_error "requirements.txt not found"
        exit 1
    fi
    
    # Install package in development mode
    print_status "Installing APGI Framework in development mode..."
    pip install -e .
    print_success "APGI Framework installed"
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    directories=(
        "data"
        "results" 
        "logs"
        "figures"
        "reports"
        "session_state"
        "apgi_outputs/dashboard"
        "apgi_outputs/exports"
        "apgi_outputs/figures"
        "apgi_outputs/reports"
    )
    
    for dir in "${directories[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            print_success "Created directory: $dir"
        fi
    done
}

# Download example data (placeholder)
download_example_data() {
    print_status "Setting up example data..."
    
    # Create sample data files
    mkdir -p examples/data/eeg
    mkdir -p examples/data/pupillometry
    mkdir -p examples/data/cardiac
    
    # Create placeholder files with proper structure
    cat > examples/data/eeg/sample_eeg_data.csv << 'EOF'
timestamp,channel_Fz,channel_Cz,channel_Pz,subject_id
0.000,0.5,0.3,0.2,subject_001
0.001,0.6,0.4,0.3,subject_001
0.002,0.4,0.2,0.1,subject_001
EOF
    
    cat > examples/data/pupillometry/sample_pupil_data.csv << 'EOF'
timestamp,pupil_diameter_left,pupil_diameter_right,subject_id
0.000,3.2,3.1,subject_001
0.001,3.3,3.2,subject_001
0.002,3.1,3.0,subject_001
EOF
    
    cat > examples/data/cardiac/sample_cardiac_data.csv << 'EOF'
timestamp,heart_rate,hrv,subject_id
0.000,72.5,45.2,subject_001
0.001,73.1,44.8,subject_001
0.002,72.8,45.5,subject_001
EOF
    
    print_success "Example data created in examples/data/"
}

# Run tests to verify installation
run_tests() {
    print_status "Running tests to verify installation..."
    
    if command -v pytest &> /dev/null; then
        pytest tests/ -v --tb=short
        if [ $? -eq 0 ]; then
            print_success "All tests passed!"
        else
            print_warning "Some tests failed, but installation may still work"
        fi
    else
        print_warning "pytest not found, skipping tests"
    fi
}

# Setup configuration files
setup_config() {
    print_status "Setting up configuration files..."
    
    # Create default config if it doesn't exist
    if [ ! -f "config.json" ]; then
        cat > config.json << 'EOF'
{
    "data_directory": "./data",
    "results_directory": "./results",
    "logs_directory": "./logs",
    "default_parameters": {
        "sampling_rate": 1000,
        "window_size": 1.0,
        "overlap": 0.5
    },
    "gui": {
        "theme": "dark",
        "auto_save": true
    }
}
EOF
        print_success "Default configuration created"
    fi
}

# Print completion message
print_completion() {
    echo ""
    echo "=========================================="
    print_success "APGI Framework setup complete!"
    echo "=========================================="
    echo ""
    echo "Next steps:"
    echo "1. Activate the virtual environment:"
    echo "   source venv/bin/activate"
    echo ""
    echo "2. Run the GUI:"
    echo "   python launch_gui.py"
    echo ""
    echo "3. Run tests:"
    echo "   pytest tests/"
    echo ""
    echo "4. View documentation:"
    echo "   cat README.md"
    echo ""
    echo "For more information, visit the docs/ directory"
    echo ""
}

# Main execution
main() {
    echo "=========================================="
    echo "APGI Framework Automated Setup"
    echo "=========================================="
    echo ""
    
    check_python
    check_pip
    create_venv
    upgrade_pip
    install_dependencies
    create_directories
    download_example_data
    setup_config
    run_tests
    print_completion
}

# Run main function
main "$@"
