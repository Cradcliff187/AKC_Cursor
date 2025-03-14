# Use Python 3.9 slim image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy app.py and requirements-minimal.txt
COPY app.py .
COPY requirements-minimal.txt ./requirements.txt
COPY static/ ./static/
COPY templates/ ./templates/

# Install dependencies
RUN pip install -r requirements.txt

# Set environment variables
ENV PORT=8080
ENV PYTHONUNBUFFERED=1
ENV FASTAPI_ENV=production

# Expose port
EXPOSE 8080

# Run the application
CMD ["python", "app.py"] 