#!/bin/bash
# Test runner script for the Mergington High School Activities API

echo "🧪 Running FastAPI Tests"
echo "========================="

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

echo "Running tests with coverage..."
python -m pytest tests/ --cov=src --cov-report=term-missing --cov-report=html -v

echo ""
echo "✅ Test run complete!"
echo ""
echo "📊 Coverage report available in htmlcov/index.html"
echo "🏃 To run tests again: python -m pytest tests/ -v"
echo "🔍 To run specific test: python -m pytest tests/test_api.py::TestSignupEndpoint::test_signup_success -v"