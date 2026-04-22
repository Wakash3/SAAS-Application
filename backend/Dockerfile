FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y gcc libpq-dev curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first
COPY requirements.txt .

# Force install all dependencies including PyJWT
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir PyJWT==2.8.0 && \
    pip install --no-cache-dir -r requirements.txt

# Verify JWT is installed
RUN python -c "import jwt; print(f'✅ JWT {jwt.__version__} installed successfully')"

# Copy application code
COPY . .

# Make start script executable
RUN chmod +x start.sh

EXPOSE 8080

CMD ["./start.sh"]