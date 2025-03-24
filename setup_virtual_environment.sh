#!/bin/bash

# Variables
VENV_NAME="venv"
REQUIREMENTS_FILE="requirements.txt"

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_NAME" ]; then
    python3 -m venv "$VENV_NAME"
    echo "Virtual environment '${VENV_NAME}' created."
else
    echo "Virtual environment '${VENV_NAME}' already exists."
fi

# Activate virtual environment
source "$VENV_NAME/bin/activate"
echo "Virtual environment activated."

# Install dependencies if requirements.txt exists
if [ -f "$REQUIREMENTS_FILE" ]; then
    pip install -r "$REQUIREMENTS_FILE"
    echo "Dependencies installed from '${REQUIREMENTS_FILE}'."
else
    echo "No '${REQUIREMENTS_FILE}' found. Skipping dependency installation."
fi

echo "Setup complete. To activate the virtual environment later, run: source ${VENV_NAME}/bin/activate"