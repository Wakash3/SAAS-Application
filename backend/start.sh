#!/bin/bash

# Print Python version for debugging
echo "========================================="
echo "Starting Msingi Backend Service"
echo "========================================="
echo "Python version:"
python --version

# Print installed packages for debugging
echo ""
echo "Installed packages (JWT related):"
pip list | grep -i jwt

# Test JWT import
echo ""
echo "Testing JWT import..."
python -c "import jwt; print(f'✅ JWT version: {jwt.__version__}')"

# Test other critical imports
echo ""
echo "Testing critical imports..."
python -c "import fastapi; print(f'✅ FastAPI version: {fastapi.__version__}')"
python -c "import uvicorn; print(f'✅ Uvicorn available')"
python -c "import sqlalchemy; print(f'✅ SQLAlchemy version: {sqlalchemy.__version__}')"

# Set default port if not provided
export PORT=${PORT:-8080}
echo ""
echo "Using port: $PORT"

# Print environment info (without sensitive data)
echo ""
echo "Environment variables set:"
echo "PORT: $PORT"
echo "DATABASE_URL: ${DATABASE_URL:0:50}..." 
echo ""

# Run the application
echo "========================================="
echo "Starting FastAPI application..."
echo "========================================="

# Run with uvicorn
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT