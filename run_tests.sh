#!/bin/bash

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Install requirements
pip install -r requirements.txt
pip install -r requirements-test.txt

# Run tests with coverage
python -m pytest tests/ --cov=app --cov-report=term-missing

# Deactivate virtual environment if it was activated
if [ -n "$VIRTUAL_ENV" ]; then
    deactivate
fi 