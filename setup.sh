#!/bin/bash

echo "Starting Nymble Setup (Linux/macOS)..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install requirements
if [ -f "backend/requirements.txt" ]; then
    echo "Installing backend dependencies..."
    pip install -r backend/requirements.txt
else
    echo "requirements.txt not found. Skipping dependency installation."
fi

echo "Setup complete! To run the backend server:"
echo "source venv/bin/activate"
echo "cd backend && uvicorn main:app --reload"
