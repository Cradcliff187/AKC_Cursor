# Use Python 3.9 slim image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and constraints files
COPY requirements.txt constraints.txt ./

# Install dependencies in stages to avoid complex dependency resolution
# Stage 1: Install core Flask and database dependencies
RUN pip install --no-cache-dir \
    Flask==2.0.1 \
    Flask-SQLAlchemy==2.5.1 \
    psycopg2-binary==2.9.10 \
    python-dotenv==0.19.0 \
    requests==2.26.0 \
    SQLAlchemy==1.4.23 \
    Werkzeug==2.0.1 \
    Flask-Login==0.6.2 \
    gunicorn==20.1.0

# Stage 2: Install problematic dependencies with explicit versions
RUN pip install --no-cache-dir \
    httpx==0.26.0 \
    httpcore==1.0.7 \
    pydantic==2.10.6 \
    requests-oauthlib==1.3.1

# Stage 3: Install the rest of the requirements with constraints
RUN pip install --no-cache-dir -r requirements.txt -c constraints.txt

# Copy application code
COPY . .

# Create instance and uploads directories
RUN mkdir -p /app/instance/uploads && \
    chmod -R 777 /app/instance

# Set environment variables
ENV PORT=8080
ENV FLASK_APP=run.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8080

# Run the application
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 run:app 