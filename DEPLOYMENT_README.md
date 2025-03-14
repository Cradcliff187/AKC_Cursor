# ⚠️ DO NOT DELETE THIS FILE ⚠️

# AKC CRM Deployment Documentation

## IMPORTANT: This file contains critical deployment information
This document outlines the exact approach used for successfully deploying the AKC CRM application to Google Cloud Run. **DO NOT DELETE OR MODIFY** this file as it contains the only verified working deployment configuration.

## Project Structure

The deployment uses a simplified approach with these key files:

1. **app.py** - Main application entry point
2. **requirements.txt** - Minimal dependencies
3. **Dockerfile** - Container configuration
4. **static/** - Static files directory
5. **templates/** - HTML templates directory

## Key Files

### 1. app.py

This is a simplified FastAPI application that serves as the entry point:

```python
"""
Simple FastAPI Application with Supabase Integration

This is a simple FastAPI application that integrates with Supabase.
"""

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Request

# Create FastAPI app
app = FastAPI(
    title="AKC CRM",
    description="AKC Construction CRM",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Root endpoint
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Root endpoint for the API."""
    return templates.TemplateResponse("index.html", {"request": request})

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
```

### 2. requirements.txt

This file contains only the essential dependencies needed for the application:

```
# Minimal requirements for running the FastAPI application with Supabase
fastapi==0.95.1
uvicorn==0.22.0
supabase==1.0.3
postgrest-py==0.10.6
python-dotenv==1.0.0
psycopg2-binary==2.9.7
pydantic==1.10.7
httpx>=0.23.0,<0.24.0
```

### 3. Dockerfile

The Dockerfile is configured to build a lightweight container:

```dockerfile
# Use Python 3.9 slim image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy app.py and requirements.txt
COPY app.py .
COPY requirements.txt ./requirements.txt
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
```

## ⚠️ CRITICAL WARNINGS ⚠️

1. **DO NOT** include the `.env` file in the Dockerfile's COPY commands. The `.dockerignore` file excludes it.

2. **DO NOT** use `load_dotenv()` in the app.py file. Environment variables should be set in the Dockerfile or through Cloud Run's environment variables/secrets.

3. **DO NOT** use the full `requirements.txt` file. Use only the minimal requirements.

4. **DO NOT** use `supabase_api.py` and `run_supabase_api.py`. Use the simplified `app.py` approach.

5. **ALWAYS** use `psycopg2-binary` instead of `psycopg2` to avoid build issues.

6. **ALWAYS** use specific versions for dependencies to ensure reproducible builds.

## Deployment Steps

1. **Ensure the correct files are in place:**
   - app.py
   - requirements.txt
   - Dockerfile
   - static/ directory
   - templates/ directory

2. **Deploy directly to Cloud Run:**

   ```bash
   gcloud run deploy akc-crm --source . --platform managed --region us-east4 --allow-unauthenticated
   ```

3. **For setting secrets (if needed):**

   ```bash
   gcloud run deploy akc-crm --source . --platform managed --region us-east4 --allow-unauthenticated --set-secrets=SUPABASE_URL=SUPABASE_URL:latest,SUPABASE_KEY=SUPABASE_ANON_KEY:latest,SUPABASE_SERVICE_ROLE_KEY=SUPABASE_SERVICE_ROLE_KEY:latest,SUPABASE_DB_PASSWORD=SUPABASE_DB_PASSWORD:latest,FLASK_SECRET_KEY=FLASK_SECRET_KEY:latest
   ```

4. **Verify deployment:**

   ```bash
   gcloud run services describe akc-crm --platform managed --region us-east4
   ```

5. **Test the health endpoint:**

   ```bash
   curl -s https://akc-crm-988587667075.us-east4.run.app/health
   ```

## Troubleshooting

1. **Build Failures:**
   - Check the build logs: `gcloud builds log BUILD_ID`
   - Ensure all dependencies in requirements.txt are available on PyPI
   - Verify that the Dockerfile doesn't try to copy files excluded by .dockerignore

2. **Runtime Errors:**
   - Check Cloud Run logs: `gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=akc-crm"`
   - Verify environment variables are correctly set

3. **Dependency Issues:**
   - If you encounter issues with a specific package, check its compatibility with Python 3.9
   - Always use binary packages when available (e.g., psycopg2-binary instead of psycopg2)

4. **Internal Server Error (500):**
   - If you encounter a 500 Internal Server Error when accessing the application, check the following:
     - Ensure the app.py file includes all necessary route handlers for pages referenced in templates
     - Make sure the Jinja2 template functions like `url_for` and `get_flashed_messages` are properly defined
     - Add the SessionMiddleware to handle session data
     - Include `starlette` and `itsdangerous` in the requirements.txt file
     - Check that all template files are properly formatted and extend the correct base template
     - Verify that the index.html file doesn't reference missing images or resources
   - The fixed app.py should include:
     ```python
     # Add session middleware
     app.add_middleware(SessionMiddleware, secret_key="your-secret-key")
     
     # Add custom template functions
     def url_for(name, filename=None):
         if filename:
             return f"/{name}/{filename}"
         return f"/{name}"
     
     # Add template globals
     templates.env.globals["url_for"] = url_for
     templates.env.globals["get_flashed_messages"] = lambda with_categories=False: []
     ```
   - The requirements.txt should include:
     ```
     starlette==0.27.0
     itsdangerous==2.1.2
     ```
   - If you're still experiencing issues, try the following:
     - Check the Cloud Run logs for specific error messages
     - Verify that all route handlers referenced in the templates are defined in app.py
     - Test the application locally before deploying to Cloud Run
     - Make sure the static files are properly mounted and accessible

## Manual Fix Steps

If you're experiencing an internal server error, follow these steps to fix it:

1. **Update app.py** to include the necessary route handlers and template functions:
   ```python
   from fastapi import FastAPI, HTTPException, Request, Depends
   from fastapi.middleware.cors import CORSMiddleware
   from fastapi.staticfiles import StaticFiles
   from fastapi.templating import Jinja2Templates
   from fastapi.responses import HTMLResponse, RedirectResponse
   from starlette.middleware.sessions import SessionMiddleware
   
   # Add session middleware
   app.add_middleware(SessionMiddleware, secret_key="your-secret-key")
   
   # Add custom template functions
   def url_for(name, filename=None):
       if filename:
           return f"/{name}/{filename}"
       return f"/{name}"
   
   # Add template globals
   templates.env.globals["url_for"] = url_for
   templates.env.globals["get_flashed_messages"] = lambda with_categories=False: []
   ```

2. **Update requirements.txt** to include the necessary dependencies:
   ```
   fastapi==0.95.1
   uvicorn==0.22.0
   supabase==1.0.3
   postgrest-py==0.10.6
   python-dotenv==1.0.0
   psycopg2-binary==2.9.7
   pydantic==1.10.7
   httpx>=0.23.0,<0.24.0
   jinja2==3.1.2
   starlette==0.27.0
   itsdangerous==2.1.2
   ```

3. **Update the Dockerfile** to use the correct requirements file:
   ```dockerfile
   # Copy app.py and requirements.txt
   COPY app.py .
   COPY requirements.txt ./requirements.txt
   COPY static/ ./static/
   COPY templates/ ./templates/
   ```

4. **Update templates/index.html** to handle missing images:
   ```html
   <div class="col-lg-6 d-none d-lg-block">
       <img src="https://via.placeholder.com/600x400?text=AKC+CRM+Dashboard" alt="Dashboard Preview" class="img-fluid rounded shadow-lg">
   </div>
   ```

5. **Deploy the application** with the updated files:
   ```bash
   gcloud run deploy akc-crm --source . --platform managed --region us-east4 --allow-unauthenticated
   ```

## Last Successful Deployment

- **Date:** March 14, 2025
- **URL:** https://akc-crm-988587667075.us-east4.run.app
- **Deployment Command:** `gcloud run deploy akc-crm --source . --platform managed --region us-east4 --allow-unauthenticated --set-secrets=SUPABASE_URL=SUPABASE_URL:latest,SUPABASE_KEY=SUPABASE_ANON_KEY:latest,SUPABASE_SERVICE_ROLE_KEY=SUPABASE_SERVICE_ROLE_KEY:latest,SUPABASE_DB_PASSWORD=SUPABASE_DB_PASSWORD:latest,FLASK_SECRET_KEY=FLASK_SECRET_KEY:latest --set-env-vars="FASTAPI_ENV=production"`

## ⚠️ FINAL WARNING ⚠️

**DO NOT DELETE THIS FILE OR MODIFY THE DEPLOYMENT APPROACH**. This configuration is the only verified working deployment method for this application. Any changes to this approach may result in deployment failures and service outages. 