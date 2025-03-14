#!/bin/bash

# AKC LLC Construction CRM Installation Script

echo "Starting AKC LLC Construction CRM installation..."

# Check if Python is installed
if command -v python3 &>/dev/null; then
    PYTHON=python3
elif command -v python &>/dev/null; then
    PYTHON=python
else
    echo "Error: Python not found. Please install Python 3.8 or newer."
    exit 1
fi

# Check Python version
$PYTHON -c "import sys; sys.exit(0) if sys.version_info >= (3, 8) else sys.exit(1)" || {
    echo "Error: Python 3.8 or newer is required."
    exit 1
}

echo "Python version check passed."

# Create virtual environment
echo "Creating virtual environment..."
$PYTHON -m venv venv || {
    echo "Error: Failed to create virtual environment."
    exit 1
}

# Activate virtual environment
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows
    source venv/Scripts/activate || {
        echo "Error: Failed to activate virtual environment."
        exit 1
    }
else
    # Unix/Linux/MacOS
    source venv/bin/activate || {
        echo "Error: Failed to activate virtual environment."
        exit 1
    }
fi

echo "Virtual environment activated."

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt || {
    echo "Error: Failed to install dependencies."
    exit 1
}

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env || {
        echo "Error: Failed to create .env file."
        exit 1
    }
    echo "Please edit the .env file with your Supabase credentials."
else
    echo ".env file already exists. Skipping creation."
fi

echo "Installation complete!"
echo ""
echo "To start the application:"
echo "1. Activate the virtual environment (if not already activated):"
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    echo "   venv\\Scripts\\activate"
else
    echo "   source venv/bin/activate"
fi
echo "2. Start the application with: flask run"
echo ""
echo "Default admin credentials:"
echo "Username: admin"
echo "Password: admin123"
echo ""
echo "IMPORTANT: Make sure to set up your Supabase database using the init_db.sql script."
echo "Refer to README.md for detailed instructions." 