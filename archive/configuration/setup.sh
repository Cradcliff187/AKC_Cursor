#!/bin/bash

# Exit on error
set -e

# Function to check if running on Windows
is_windows() {
    case "$(uname -s)" in
        CYGWIN*|MINGW*|MSYS*)
            return 0
            ;;
        *)
            return 1
            ;;
    esac
}

# Function to check if Python is installed
check_python() {
    if ! command -v python3 &> /dev/null; then
        echo "Error: Python 3 is not installed. Please install it first."
        echo "Visit: https://www.python.org/downloads/"
        exit 1
    fi
}

# Function to check if pip is installed
check_pip() {
    if ! command -v pip3 &> /dev/null; then
        echo "Error: pip3 is not installed. Please install it first."
        exit 1
    fi
}

# Function to check if virtualenv is installed
check_virtualenv() {
    if ! command -v virtualenv &> /dev/null; then
        echo "Installing virtualenv..."
        pip3 install virtualenv
    fi
}

# Function to check if gcloud is installed
check_gcloud() {
    if ! command -v gcloud &> /dev/null; then
        echo "Error: gcloud CLI is not installed. Please install it first."
        echo "Visit: https://cloud.google.com/sdk/docs/install"
        exit 1
    fi
}

# Function to create and activate virtual environment
setup_venv() {
    echo "Setting up virtual environment..."
    
    if [ -d "venv" ]; then
        echo "Virtual environment already exists. Removing it..."
        rm -rf venv
    fi
    
    virtualenv venv
    
    if is_windows; then
        source venv/Scripts/activate
    else
        source venv/bin/activate
    fi
}

# Function to install dependencies
install_dependencies() {
    echo "Installing dependencies..."
    pip install -r requirements.txt
}

# Function to check environment variables
check_env() {
    echo "Checking environment variables..."
    
    if [ ! -f ".env" ]; then
        echo "Error: .env file not found. Please create one with the following variables:"
        echo "SUPABASE_URL=your_supabase_url"
        echo "SUPABASE_KEY=your_supabase_anon_key"
        echo "SUPABASE_SERVICE_KEY=your_supabase_service_key"
        echo "SUPABASE_DB_PASSWORD=your_db_password"
        echo "FLASK_SECRET_KEY=your_secret_key"
        exit 1
    fi
    
    source .env
    
    # Check if all required variables are set
    required_vars=("SUPABASE_URL" "SUPABASE_KEY" "SUPABASE_SERVICE_KEY" "SUPABASE_DB_PASSWORD" "FLASK_SECRET_KEY")
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            echo "Error: $var is not set in .env file"
            exit 1
        fi
    done
}

# Main setup function
setup() {
    echo "Starting setup process..."
    
    # Check prerequisites
    check_python
    check_pip
    check_virtualenv
    check_gcloud
    
    # Setup virtual environment
    setup_venv
    
    # Install dependencies
    install_dependencies
    
    # Check environment variables
    check_env
    
    echo "Setup completed successfully!"
    echo "To activate the virtual environment:"
    if is_windows; then
        echo "    .\\venv\\Scripts\\activate"
    else
        echo "    source venv/bin/activate"
    fi
}

# Run setup
setup 