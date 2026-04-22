#!/bin/bash

echo "Starting Msingi Backend..."

# Verify JWT is available
python -c "import jwt; print('✅ JWT version:', jwt.__version__)"

# Set port
export PORT=${PORT:-8080}

# Run the application
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT