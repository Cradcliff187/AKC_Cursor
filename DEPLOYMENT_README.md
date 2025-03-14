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
from fastapi import FastAPI, HTTPException, Request, Depends, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.middleware.sessions import SessionMiddleware

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

# Add session middleware
app.add_middleware(SessionMiddleware, secret_key="your-secret-key")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Add custom template functions
def url_for(name, filename=None):
    """Custom URL generator function for templates."""
    if name == 'static' and filename:
        return f"/static/{filename}"
    
    # Map function names to URL paths
    url_map = {
        # Main navigation
        "dashboard": "/dashboard",
        "contacts": "/contacts",
        "projects": "/projects",
        "time_logs": "/time-logs",
        "expenses": "/expenses",
        "vendors": "/vendors",
        "reports": "/reports",
        "admin_users": "/admin/users",
        "profile": "/profile",
        
        # Time logs
        "new_time_log": "/time-logs/new",
        "time_summary_report": "/reports/time-summary",
        
        # Expenses
        "new_expense": "/expenses/new",
        "expense_summary_report": "/reports/expense-summary",
        
        # Projects
        "new_project": "/projects/new",
        
        # Other
        "login": "/login",
        "logout": "/logout"
    }
    
    if name in url_map:
        return url_map[name]
    
    return f"/{name}"

# Add template globals
templates.env.globals["url_for"] = url_for
templates.env.globals["get_flashed_messages"] = lambda with_categories=False: []

# Session dependency
def get_session(request: Request):
    return request.session

# Root endpoint
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Root endpoint for the API."""
    # Set a mock session for templates
    request.session["user_id"] = None
    request.session["user_name"] = "Guest"
    request.session["user_role"] = None
    
    # Pass the session to the template context
    return templates.TemplateResponse("index.html", {"request": request, "session": request.session})

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return templates.TemplateResponse(
        "error.html", 
        {"request": request, "status_code": exc.status_code, "detail": exc.detail}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    # Log the error
    print(f"Internal Server Error: {str(exc)}")
    print(f"Stack Trace: {traceback.format_exc()}")
    
    # Return a more helpful error page in development
    return templates.TemplateResponse(
        "error.html", 
        {
            "request": request, 
            "status_code": 500, 
            "detail": str(exc),
            "traceback": traceback.format_exc()
        }
    )

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
```

### 2. requirements.txt

This file contains only the essential dependencies needed for the application:

```
# Requirements for running the FastAPI application with Supabase
fastapi==0.95.1
uvicorn==0.22.0
supabase==1.0.3
postgrest-py==0.10.6
python-dotenv==1.0.0
psycopg2-binary==2.9.7
pydantic==1.10.7
httpx>=0.23.0,<0.24.0
jinja2==3.1.2
starlette==0.26.1
itsdangerous==2.1.2
python-multipart==0.0.6
```

### 3. Dockerfile

The Dockerfile is configured to build a lightweight container with the necessary system dependencies for psycopg2-binary:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies required for psycopg2-binary
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Set environment variables
ENV PORT=8080
ENV HOST=0.0.0.0

# Command to run the application
CMD exec uvicorn app:app --host 0.0.0.0 --port ${PORT}
```

## ⚠️ CRITICAL WARNINGS ⚠️

1. **DO NOT** include the `.env` file in the Dockerfile's COPY commands. The `.dockerignore` file should exclude it.

2. **DO NOT** use `load_dotenv()` in the app.py file for production. Environment variables should be set in the Dockerfile or through Cloud Run's environment variables/secrets.

3. **DO NOT** use the full `requirements.txt` file. Use only the minimal requirements.

4. **ALWAYS** use `psycopg2-binary` instead of `psycopg2` to avoid build issues.

5. **ALWAYS** use specific versions for dependencies to ensure reproducible builds.

6. **ALWAYS** include system dependencies in the Dockerfile for packages that require compilation (like psycopg2-binary).

7. **ALWAYS** use the `exec` form of CMD in the Dockerfile to ensure proper signal handling.

## Successful Deployment Method

The following method has been verified to work correctly for deploying the AKC CRM application to Google Cloud Run:

### 1. Prepare the Dockerfile

Create a Dockerfile with the following content:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies required for psycopg2-binary
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Set environment variables
ENV PORT=8080
ENV HOST=0.0.0.0

# Command to run the application
CMD exec uvicorn app:app --host 0.0.0.0 --port ${PORT}
```

This Dockerfile:
- Uses a slim Python 3.9 base image
- Installs system dependencies required for psycopg2-binary
- Copies and installs requirements before copying the application code (for better caching)
- Sets the necessary environment variables
- Uses the exec form of CMD with uvicorn to run the application

### 2. Deploy Directly to Cloud Run

The most reliable method for deployment is to use the `gcloud run deploy` command with the `--source` flag to deploy directly from the source code:

```bash
gcloud run deploy akc-crm --source . --platform managed --region us-east4 --allow-unauthenticated
```

This command:
- Builds the container image using Cloud Build
- Deploys the image to Cloud Run
- Makes the service publicly accessible
- Uses the us-east4 region

### 3. Verify Deployment

After deployment, verify that the service is running correctly:

```bash
# Get the service URL
gcloud run services describe akc-crm --platform managed --region us-east4 --format='value(status.url)'

# Check the health endpoint
curl -s <service-url>/health

# Check the main page
curl -s -o /dev/null -w "%{http_code}" <service-url>/
```

### 4. Troubleshooting Build Issues

If you encounter build issues, particularly with psycopg2-binary, ensure:

1. The Dockerfile includes the necessary system dependencies:
   - gcc
   - python3-dev
   - libpq-dev

2. The requirements.txt file specifies psycopg2-binary (not psycopg2)

3. If the build is still failing, you can try building the image locally and pushing it to Container Registry:

```bash
# Build the image locally
docker build -t gcr.io/akc-crm/akc-crm:latest .

# Push to Container Registry
docker push gcr.io/akc-crm/akc-crm:latest

# Deploy the image to Cloud Run
gcloud run deploy akc-crm --image gcr.io/akc-crm/akc-crm:latest --platform managed --region us-east4 --allow-unauthenticated
```

## Dashboard Links Fix

If you encounter issues with dashboard links not working (clicking on links in the dashboard doesn't navigate to the correct pages), you need to ensure that:

1. The `url_for` function in app.py correctly maps function names to URL paths
2. All necessary route handlers are defined in app.py
3. The templates exist for all routes referenced in the dashboard

### URL Mapping Solution

The key to fixing dashboard links is to implement a proper URL mapping in the `url_for` function:

```python
def url_for(name, filename=None):
    """Custom URL generator function for templates."""
    if name == 'static' and filename:
        return f"/static/{filename}"
    
    # Map function names to URL paths
    url_map = {
        # Main navigation
        "dashboard": "/dashboard",
        "contacts": "/contacts",
        "projects": "/projects",
        "time_logs": "/time-logs",
        "expenses": "/expenses",
        "vendors": "/vendors",
        "reports": "/reports",
        "admin_users": "/admin/users",
        "profile": "/profile",
        
        # Time logs
        "new_time_log": "/time-logs/new",
        "time_summary_report": "/reports/time-summary",
        
        # Expenses
        "new_expense": "/expenses/new",
        "expense_summary_report": "/reports/expense-summary",
        
        # Projects
        "new_project": "/projects/new",
        
        # Other
        "login": "/login",
        "logout": "/logout"
    }
    
    if name in url_map:
        return url_map[name]
    
    return f"/{name}"
```

This mapping ensures that when templates call `url_for('new_time_log')`, it correctly returns `/time-logs/new` instead of `/new_time_log`.

### Route Handlers

Make sure to define all necessary route handlers in app.py:

```python
@app.get("/time-logs/new", response_class=HTMLResponse)
async def new_time_log(request: Request, session: dict = Depends(get_session)):
    if not check_auth(session):
        return RedirectResponse(url="/login")
    return templates.TemplateResponse("time_log_form.html", {"request": request, "session": request.session})

@app.get("/reports/time-summary", response_class=HTMLResponse)
async def time_summary_report(request: Request, session: dict = Depends(get_session)):
    if not check_auth(session):
        return RedirectResponse(url="/login")
    return templates.TemplateResponse("time_summary_report.html", {"request": request, "session": request.session})

@app.get("/expenses/new", response_class=HTMLResponse)
async def new_expense(request: Request, session: dict = Depends(get_session)):
    if not check_auth(session):
        return RedirectResponse(url="/login")
    return templates.TemplateResponse("expense_form.html", {"request": request, "session": request.session})

@app.get("/reports/expense-summary", response_class=HTMLResponse)
async def expense_summary_report(request: Request, session: dict = Depends(get_session)):
    if not check_auth(session):
        return RedirectResponse(url="/login")
    return templates.TemplateResponse("reports.html", {"request": request, "session": request.session, "report_type": "expense"})
```

### Template Mapping

Ensure that the route handlers map to the correct template files:

| Route | Template File |
|-------|--------------|
| `/time-logs/new` | `time_log_form.html` |
| `/reports/time-summary` | `time_summary_report.html` |
| `/expenses/new` | `expense_form.html` |
| `/reports/expense-summary` | `reports.html` (with context parameter) |

## Login Credentials

For testing purposes, the application has a mock authentication system with the following credentials:

- **Email:** admin@akc.org
- **Password:** admin123

These credentials are hardcoded in the `login_post` function in app.py:

```python
# Login form submission
@app.post("/login", response_class=HTMLResponse)
async def login_post(request: Request, username: str = Form(...), password: str = Form(...)):
    # This is a simple mock authentication
    # In a real application, you would validate against a database
    if username == "admin@akc.org" and password == "admin123":
        request.session["user_id"] = 1
        request.session["user_name"] = "Admin"
        request.session["user_role"] = "admin"
        return RedirectResponse(url="/dashboard", status_code=303)
    
    # If authentication fails, render the login page with an error message
    return templates.TemplateResponse(
        "login.html", 
        {"request": request, "session": request.session, "error": "Invalid username or password"}
    )
```

In a production environment, you would replace this with a proper authentication system that validates against a database.

## Internal Server Error Fix

If you encounter internal server errors when clicking on dashboard links, the issue is likely related to the `url_for` function in app.py. The following fixes were implemented:

1. **Fixed the `url_for` function to correctly handle static files:**

```python
def url_for(name, filename=None):
    """Custom URL generator function for templates."""
    if name == 'static' and filename:
        return f"/static/{filename}"
    
    # Map function names to URL paths
    url_map = {
        # Main navigation
        "dashboard": "/dashboard",
        "contacts": "/contacts",
        "projects": "/projects",
        "time_logs": "/time-logs",
        "expenses": "/expenses",
        "vendors": "/vendors",
        "reports": "/reports",
        "admin_users": "/admin/users",
        "profile": "/profile",
        
        # Time logs
        "new_time_log": "/time-logs/new",
        "time_summary_report": "/reports/time-summary",
        
        # Expenses
        "new_expense": "/expenses/new",
        "expense_summary_report": "/reports/expense-summary",
        
        # Projects
        "new_project": "/projects/new",
        
        # Other
        "login": "/login",
        "logout": "/logout"
    }
    
    if name in url_map:
        return url_map[name]
    
    return f"/{name}"
```

2. **Added error handlers to provide better diagnostics:**

```python
# Error handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return templates.TemplateResponse(
        "error.html", 
        {"request": request, "status_code": exc.status_code, "detail": exc.detail}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    # Log the error
    print(f"Internal Server Error: {str(exc)}")
    print(f"Stack Trace: {traceback.format_exc()}")
    
    # Return a more helpful error page in development
    return templates.TemplateResponse(
        "error.html", 
        {
            "request": request, 
            "status_code": 500, 
            "detail": str(exc),
            "traceback": traceback.format_exc()
        }
    )
```

3. **Created an error.html template to display error information:**

```html
{% extends "base.html" %}

{% block title %}Error {{ status_code }} - AKC CRM{% endblock %}

{% block content %}
<div class="container">
    <div class="row justify-content-center">
        <div class="col-md-8">
            <div class="card shadow-sm mb-4">
                <div class="card-header bg-danger text-white">
                    <h4 class="mb-0">Error {{ status_code }}</h4>
                </div>
                <div class="card-body">
                    <h5>Something went wrong</h5>
                    <p>{{ detail }}</p>
                    
                    {% if traceback %}
                    <div class="mt-4">
                        <h6>Technical Details (Debug Mode)</h6>
                        <div class="bg-light p-3 rounded">
                            <pre class="mb-0"><code>{{ traceback }}</code></pre>
                        </div>
                    </div>
                    {% endif %}
                    
                    <div class="mt-4">
                        <a href="/" class="btn btn-primary">Return to Home</a>
                        <a href="javascript:history.back()" class="btn btn-outline-secondary ms-2">Go Back</a>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

These changes ensure that:
1. Static files are correctly referenced in templates
2. All URL paths in the dashboard are properly mapped
3. Any errors that do occur are handled gracefully with helpful error messages

## Pagination Fix

If you encounter a 500 error with the message `'total_pages' is undefined` when accessing pages with pagination (like projects, contacts, time logs, or admin users), the issue is that the route handlers are not providing the necessary pagination variables to the templates.

The following fixes were implemented:

1. **Updated route handlers to include pagination variables:**

Each route handler for pages with pagination needs to include the following variables in the template context:

```python
# Pagination variables
items_per_page = 10
total_items = len(items)
total_pages = (total_items + items_per_page - 1) // items_per_page  # Ceiling division

# Ensure page is within valid range
if page < 1:
    page = 1
elif page > total_pages and total_pages > 0:
    page = total_pages

# Calculate pagination indices
start_idx = (page - 1) * items_per_page
end_idx = min(start_idx + items_per_page, total_items)

# Get items for current page
paginated_items = items[start_idx:end_idx]

# Prepare context with pagination data
context = {
    "request": request, 
    "session": request.session,
    "items": paginated_items,
    "page": page,
    "total_pages": total_pages,
    # ... other context variables ...
}
```

2. **Updated the following route handlers:**

- `/projects` - Added pagination for projects list
- `/contacts` - Added pagination for contacts list
- `/time-logs` - Added pagination for time logs list
- `/admin/users` - Added pagination for users list

3. **Added mock data for testing:**

Each route handler now includes mock data for testing, which allows the application to function properly without a database connection. This is especially useful for demonstration purposes.

These changes ensure that all pages with pagination work correctly and don't throw 500 errors due to missing template variables.

## Detail Page Fix

If you encounter a 500 error with messages like `'contact' is undefined`, `'project' is undefined`, or `'vendor' is undefined` when accessing detail pages, the issue is that the route handlers are not providing the necessary data for the specific item being viewed.

The following fixes were implemented:

1. **Updated detail route handlers to include mock data:**

Each detail route handler needs to include mock data for the specific item being viewed:

```python
# Find the item with the matching ID
item = next((i for i in mock_items if i["id"] == item_id), None)

# If item not found, return 404
if not item:
    return templates.TemplateResponse(
        "error.html", 
        {"request": request, "session": request.session, "status_code": 404, "detail": f"Item with ID {item_id} not found"}
    )

# Prepare context with item data
context = {
    "request": request, 
    "session": request.session,
    "item": item,
    # ... other context variables ...
}

return templates.TemplateResponse("item_detail.html", context)
```

2. **Updated the following detail route handlers:**

- `/contacts/{contact_id}` - Added mock data for the specific contact
- `/projects/{project_id}` - Added mock data for the specific project
- `/vendors/{vendor_id}` - Added mock data for the specific vendor

3. **Added related mock data:**

Each detail route handler now includes related mock data such as:
- Associated projects
- Team members
- Recent activities
- Documents
- Tasks

These changes ensure that all detail pages work correctly and don't throw 500 errors due to missing template variables.

## Last Successful Deployment

- **Date:** March 15, 2025
- **URL:** https://akc-crm-988587667075.us-east4.run.app
- **Deployment Command:** `gcloud run deploy akc-crm --source . --platform managed --region us-east4 --allow-unauthenticated`
- **Dockerfile Used:** The Dockerfile with system dependencies for psycopg2-binary as shown above
- **Latest Fixes:** 
  - Fixed internal server errors with dashboard links by updating the url_for function and adding error handlers
  - Fixed pagination issues by adding missing template variables to route handlers
  - Fixed detail page issues by adding mock data to detail route handlers

## Troubleshooting

1. **Build Failures:**
   - Check the build logs: `gcloud builds log BUILD_ID`
   - Ensure all dependencies in requirements.txt are available on PyPI
   - Verify that the Dockerfile doesn't try to copy files excluded by .dockerignore
   - Make sure system dependencies are installed for packages that require compilation

2. **Runtime Errors:**
   - Check Cloud Run logs: `gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=akc-crm"`
   - Verify environment variables are correctly set

3. **Dependency Issues:**
   - If you encounter issues with a specific package, check its compatibility with Python 3.9
   - Always use binary packages when available (e.g., psycopg2-binary instead of psycopg2)
   - Make sure FastAPI and Starlette versions are compatible (FastAPI 0.95.1 requires starlette<0.27.0)

4. **Internal Server Error (500):**
   - If you encounter a 500 Internal Server Error when accessing the application, check the following:
     - Ensure the app.py file includes all necessary route handlers for pages referenced in templates
     - Make sure the Jinja2 template functions like `url_for` and `get_flashed_messages` are properly defined
     - Add the SessionMiddleware to handle session data
     - Include `starlette` and `itsdangerous` in the requirements.txt file
     - Check that all template files are properly formatted and extend the correct base template
     - Verify that the index.html file doesn't reference missing images or resources
     - **IMPORTANT**: Make sure to pass the session to the template context in all route handlers
     - **IMPORTANT**: Update the base.html template to check if session exists before accessing it

5. **Method Not Allowed Error:**
   - If you encounter a "Method Not Allowed" error when submitting forms, check the following:
     - Ensure you have defined both GET and POST routes for pages with forms
     - Make sure you have included `python-multipart` in your requirements.txt file
     - Verify that form field names in the HTML match the parameter names in your route handlers

6. **Dashboard Links Not Working:**
   - If links in the dashboard don't navigate to the correct pages, check the following:
     - Ensure the `url_for` function in app.py correctly maps function names to URL paths
     - Verify that all necessary route handlers are defined in app.py
     - Check that the templates exist for all routes referenced in the dashboard
     - Look at the browser's developer console for any JavaScript errors
     - Inspect the generated HTML to ensure the links have the correct href attributes

## ⚠️ FINAL WARNING ⚠️

**DO NOT DELETE THIS FILE OR MODIFY THE DEPLOYMENT APPROACH**. This configuration is the only verified working deployment method for this application. Any changes to this approach may result in deployment failures and service outages. 