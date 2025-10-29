#!/bin/bash

# Setup development environment script

set -e

echo "Setting up development environment..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3.11 or higher."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.11"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "Python $REQUIRED_VERSION or higher is required. Current version: $PYTHON_VERSION"
    exit 1
fi

echo "Python version: $PYTHON_VERSION ✓"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Install pre-commit hooks
echo "Installing pre-commit hooks..."
pre-commit install

# Copy environment file
if [ ! -f ".env" ]; then
    echo "Copying .env.sample to .env..."
    cp .env.sample .env
    echo "Please update .env with your configuration."
fi

# Run database migrations (if alembic is configured)
if [ -d "alembic" ]; then
    echo "Running database migrations..."
    alembic upgrade head
fi

echo ""
echo "Development environment setup complete! 🎉"
echo ""
echo "Next steps:"
echo "1. Update .env with your configuration"
echo "2. Run 'python src/main.py' to start the application"
echo "3. Visit http://localhost:8000/docs for API documentation"
echo ""
echo "To activate the virtual environment in future sessions:"
echo "source venv/bin/activate"
