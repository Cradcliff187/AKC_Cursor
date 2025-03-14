# Use Python 3.9 slim image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy only what we need
COPY supabase_api.py .
COPY run_supabase_api.py .
COPY requirements-updated.txt ./requirements.txt
COPY static/ ./static/
COPY templates/ ./templates/
COPY .env .

# Install dependencies
RUN pip install -r requirements.txt

# Set environment variables
ENV PORT=8080
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8080

# Run the application
CMD ["python", "run_supabase_api.py"] 