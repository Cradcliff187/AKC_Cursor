"""
Simple FastAPI Application with Supabase Integration

This is a simple FastAPI application that integrates with Supabase.
"""

import os
import traceback
from fastapi import FastAPI, HTTPException, Request, Depends, Form, UploadFile, File, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from starlette.middleware.sessions import SessionMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from datetime import datetime, timedelta
from typing import Optional, List
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
# This will do nothing in production where environment variables are set via Cloud Run
try:
    load_dotenv()
except Exception as e:
    print(f"Warning: Could not load .env file: {e}")

# Verify critical environment variables are set
required_env_vars = ["SUPABASE_URL", "SUPABASE_KEY"]
missing_vars = [var for var in required_env_vars if not os.getenv(var)]
if missing_vars:
    print(f"Error: Missing required environment variables: {', '.join(missing_vars)}")
    print("This application requires Supabase configuration to function properly.")
    # We'll continue and use mock data if Supabase isn't available

from dependencies import get_session, check_auth, templates, get_supabase_client, require_auth
from mock_data import (
    MOCK_ACTIVITY, MOCK_VENDORS, MOCK_EXPENSES, MOCK_PROJECTS,
    MOCK_METRICS, MOCK_CUSTOMERS,
    VENDOR_CATEGORIES, VENDOR_STATUSES,
    EXPENSE_CATEGORIES, EXPENSE_STATUSES
)
from routes import auth, projects, vendors, reports, invoices, documents, customers, contacts, time_logs, expenses

# Create FastAPI app
app = FastAPI(
    title="AKC CRM",
    description="AKC Construction CRM",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add session middleware with a stable secret key from env or a default value
# Important: In production, always set SESSION_SECRET_KEY environment variable
SESSION_SECRET_KEY = os.getenv("SESSION_SECRET_KEY", "akc_construction_crm_default_secret_key_for_development_only")
app.add_middleware(
    SessionMiddleware,
    secret_key=SESSION_SECRET_KEY,
    max_age=3600,  # Session expires after 1 hour
)

# Custom URL generator function for templates
def url_for(name, filename=None, **kwargs):
    """Custom URL generator function for templates."""
    if name == 'static' and filename:
        return f"/static/{filename}"
    
    # Map function names to URL paths with parameter handling
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
        "customers": "/customers",  # Added missing customers route
        "invoices": "/invoices",
        
        # Project routes
        "new_project": "/projects/new",
        "edit_project": "/projects/{project_id}/edit",
        "view_project": "/projects/{project_id}",  # Alias for project_detail
        "project_detail": "/projects/{project_id}",  # Actual function name
        "delete_project": "/projects/{project_id}/delete",
        "update_project_status": "/projects/{project_id}/status",
        "add_project_task": "/projects/{project_id}/tasks",
        "view_task": "/tasks/{task_id}",
        "add_team_member": "/projects/{project_id}/team",
        "remove_team_member": "/projects/{project_id}/team/{user_id}/remove",
        
        # Document routes
        "view_document": "/documents/{document_id}",
        "upload_document": "/documents/upload",
        "delete_document": "/documents/{document_id}/delete",
        
        # Invoice routes
        "new_invoice": "/invoices/new",
        "edit_invoice": "/invoices/{invoice_id}/edit",
        "invoice_detail": "/invoices/{invoice_id}",
        "send_invoice": "/invoices/{invoice_id}/send",
        "record_payment": "/invoices/{invoice_id}/payment",
        "cancel_invoice": "/invoices/{invoice_id}/cancel",
        
        # Customer routes
        "new_customer": "/customers/new",
        "edit_customer": "/customers/{customer_id}/edit",
        "view_customer": "/customers/{customer_id}",  # Alias for customer_detail
        "customer_detail": "/customers/{customer_id}",  # Actual function name
        "delete_customer": "/customers/{customer_id}/delete",
        
        # Estimate routes
        "estimates": "/estimates",
        "new_estimate": "/estimates/new",
        "edit_estimate": "/estimates/{estimate_id}/edit",
        "estimate_detail": "/estimates/{estimate_id}",
        "send_estimate": "/estimates/{estimate_id}/send",
        "convert_to_invoice": "/estimates/{estimate_id}/convert",
        
        # Contract routes
        "contracts": "/contracts",
        "view_contract": "/contracts/{contract_id}",
        "new_contract": "/contracts/new",
        "edit_contract": "/contracts/{contract_id}/edit",
        
        # Report routes
        "reports": "/reports",
        "time_summary_report": "/reports/time",
        "expense_summary_report": "/reports/expenses",
        "project_profitability_report": "/reports/projects",
        "export_report": "/reports/export",
        
        # Time log routes
        "new_time_log": "/time-logs/new",
        "edit_time_log": "/time-logs/{log_id}/edit",
        "delete_time_log": "/time-logs/{log_id}/delete",
        "project_time_logs": "/projects/{project_id}/time-logs",
        
        # Expense routes
        "new_expense": "/expenses/new",
        "edit_expense": "/expenses/{expense_id}/edit",
        "expense_detail": "/expenses/{expense_id}",  # Added to match function name
        "delete_expense": "/expenses/{expense_id}/delete",
        "project_expenses": "/projects/{project_id}/expenses",
        
        # Vendor routes
        "new_vendor": "/vendors/new",
        "edit_vendor": "/vendors/{vendor_id}/edit",
        "view_vendor": "/vendors/{vendor_id}",  # Alias for vendor_detail
        "vendor_detail": "/vendors/{vendor_id}",  # Actual function name
        "delete_vendor": "/vendors/{vendor_id}/delete",
        "update_vendor_status": "/vendors/{vendor_id}/status",
        
        # Authentication routes
        "login": "/login",
        "logout": "/logout",
        "register": "/register",
        "reset_password": "/reset-password",
        
        # Admin routes
        "admin_dashboard": "/admin",
        "admin_users": "/admin/users",
        "admin_settings": "/admin/settings",
        "admin_logs": "/admin/logs"
    }
    
    # Get the base URL pattern
    url_pattern = url_map.get(name)
    if not url_pattern:
        raise ValueError(f"URL pattern not found for: {name}")
    
    # Replace URL parameters with their values
    try:
        for key, value in kwargs.items():
            if value is not None:
                url_pattern = url_pattern.replace(f"{{{key}}}", str(value))
        
        # Check if all parameters were replaced
        if "{" in url_pattern:
            missing_params = [p.split("}")[0] for p in url_pattern.split("{")[1:]]
            raise ValueError(f"Missing required URL parameters: {', '.join(missing_params)}")
            
        return url_pattern
        
    except Exception as e:
        print(f"Error generating URL for {name}: {str(e)}")
        return "#"  # Return a safe fallback

# Add template globals
templates.env.globals["url_for"] = url_for
templates.env.globals["get_flashed_messages"] = lambda with_categories=False: []

# Add template constants
templates.env.globals["project_status_classes"] = {
    "draft": "secondary",
    "in_progress": "primary",
    "completed": "success",
    "on_hold": "warning",
    "cancelled": "danger"
}

templates.env.globals["status_icons"] = {
    "draft": "file",
    "in_progress": "play-circle",
    "completed": "check-circle",
    "on_hold": "pause-circle",
    "cancelled": "times-circle"
}

templates.env.globals["allowed_status_transitions"] = {
    "draft": ["in_progress", "cancelled"],
    "in_progress": ["completed", "on_hold", "cancelled"],
    "completed": ["in_progress"],
    "on_hold": ["in_progress", "cancelled"],
    "cancelled": ["draft"]
}

templates.env.globals["status_messages"] = {
    "draft": "Project is in draft stage",
    "in_progress": "Project is actively being worked on",
    "completed": "Project has been completed",
    "on_hold": "Project is temporarily paused",
    "cancelled": "Project has been cancelled"
}

templates.env.globals["status_styles"] = {
    "draft": "text-secondary",
    "in_progress": "text-primary",
    "completed": "text-success",
    "on_hold": "text-warning",
    "cancelled": "text-danger"
}

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

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

# Include routers in the correct order - auth must be first!
# The order matters because FastAPI matches routes in order of declaration
app.include_router(auth.router)  # Auth routes first, so login works
app.include_router(expenses.router)  # Expense routes come earlier since these are working
app.include_router(projects.router)
app.include_router(vendors.router)
app.include_router(reports.router)
app.include_router(invoices.router)
app.include_router(documents.router)
app.include_router(customers.router)
app.include_router(contacts.router)
app.include_router(time_logs.router)

# Google Maps API configuration
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")

# Dashboard
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, session: dict = Depends(require_auth)):
    """Dashboard endpoint."""
    try:
        # Get Supabase client
        supabase_client = get_supabase_client()
        
        # In real implementation, fetch data from Supabase
        # For now, use mock data
        recent_activity = MOCK_ACTIVITY[:5]
        upcoming_tasks = []
        recent_projects = MOCK_PROJECTS[:3]
        metrics = MOCK_METRICS
        
        return templates.TemplateResponse(
            "dashboard.html",
            {
                "request": request,
                "session": session,
                "recent_activity": recent_activity,
                "upcoming_tasks": upcoming_tasks,
                "recent_projects": recent_projects,
                "metrics": metrics
            }
        )
    except Exception as e:
        print(f"Error loading dashboard: {str(e)}")
        traceback.print_exc()
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "session": session,
                "error_code": 500,
                "error_message": "Error loading dashboard"
            }
        )

# User profile
@app.get("/profile", response_class=HTMLResponse)
async def profile(request: Request, session: dict = Depends(require_auth)):
    """User profile endpoint."""
    try:
        # Get Supabase client
        supabase_client = get_supabase_client()
        
        # In real implementation, fetch user data from Supabase
        # For now, use mock data
        user = {
            "id": session.get("user_id", 1),
            "name": session.get("user_name", "John Doe"),
            "email": "john.doe@example.com",
            "phone": "555-123-4567",
            "role": session.get("user_role", "admin"),
            "created_at": "2023-01-01T00:00:00Z",
            "last_login": "2023-09-30T12:34:56Z"
        }
        
        return templates.TemplateResponse(
            "profile.html",
            {
                "request": request,
                "session": session,
                "user": user
            }
        )
    except Exception as e:
        print(f"Error loading profile: {str(e)}")
        traceback.print_exc()
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "session": session,
                "error_code": 500,
                "error_message": "Error loading profile"
            }
        )

# Add exception handlers for authentication and other errors
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions."""
    if exc.status_code == 401:
        # Authentication error - redirect to login with next parameter
        return RedirectResponse(
            url=f"/login?next={request.url.path}", 
            status_code=303
        )
    elif exc.status_code == 404:
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "session": request.session,
                "error_code": 404,
                "error_message": "Page not found"
            }
        )
    elif exc.status_code == 403:
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "session": request.session,
                "error_code": 403,
                "error_message": "You do not have permission to access this resource"
            }
        )
    
    # Default HTTP error handler
    return templates.TemplateResponse(
        "error.html",
        {
            "request": request,
            "session": request.session,
            "error_code": exc.status_code,
            "error_message": str(exc.detail)
        }
    )

# Handler for server errors
@app.exception_handler(Exception)
async def server_error_handler(request: Request, exc: Exception):
    """Handler for server errors."""
    session = request.session
    error_id = os.urandom(8).hex()
    error_details = {
        'error_id': error_id,
        'url': str(request.url),
        'method': request.method,
        'headers': dict(request.headers),
        'exception_type': type(exc).__name__,
        'exception_str': str(exc),
        'traceback': traceback.format_exc()
    }
    
    # Log the detailed error
    print(f"ERROR ID: {error_id}")
    print(f"URL: {request.url}")
    print(f"Exception: {type(exc).__name__}: {str(exc)}")
    traceback.print_exc()
    
    # Only show detailed error info to admins
    is_admin = session.get('user_role') == 'admin'
    
    return templates.TemplateResponse(
        "error.html",
        {
            "request": request,
            "session": session,
            "error_code": 500,
            "error_message": f"An unexpected error occurred. Error ID: {error_id}" if not is_admin else str(exc),
            "traceback": error_details['traceback'] if is_admin else None,
            "error_id": error_id,
            "now": datetime.now()  # Ensure now is always available
        }
    )

# Add the main entry point for running the application directly
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)