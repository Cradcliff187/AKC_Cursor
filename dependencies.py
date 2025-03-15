"""
Shared dependencies for the AKC CRM application.
"""

import os
from fastapi import Request, Depends, HTTPException, status
from fastapi.templating import Jinja2Templates
from supabase import create_client, Client
from typing import Optional
from datetime import datetime
from starlette.datastructures import URL
from starlette.responses import RedirectResponse

# Initialize templates
templates = Jinja2Templates(directory="templates")

# Add the current date to all templates
templates.env.globals["now"] = datetime.now()

# Replace the simple URL generator with the one matching app.py
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
        "customers": "/customers",
        "invoices": "/invoices",
        
        # Authentication routes
        "login": "/login",
        "logout": "/logout",
        "register": "/register",
        "reset_password": "/reset-password",
    }
    
    # Get the base URL pattern
    url_pattern = url_map.get(name)
    if not url_pattern:
        # Fallback for undefined paths - simply use the name
        return f"/{name}"
    
    # Replace URL parameters with their values
    try:
        for key, value in kwargs.items():
            if value is not None:
                url_pattern = url_pattern.replace(f"{{{key}}}", str(value))
        
        return url_pattern
        
    except Exception as e:
        print(f"Error generating URL for {name}: {str(e)}")
        return "#"  # Return a safe fallback

# Make the url_for function available to all templates
templates.env.globals["url_for"] = url_for

def get_session(request: Request) -> dict:
    """Get session data from request."""
    return request.session

def check_auth(session: dict) -> bool:
    """Check if user is authenticated."""
    return session.get("user_id") is not None

def get_supabase_client() -> Optional[Client]:
    """Initialize Supabase client with proper error handling."""
    try:
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            print("Warning: Supabase environment variables not found, using mock data")
            return None
            
        return create_client(supabase_url, supabase_key)
    except Exception as e:
        print(f"Error initializing Supabase client: {e}")
        return None 

async def require_auth(request: Request) -> dict:
    """
    Dependency function to require authentication.
    Will return the session if authenticated, or raise an exception if not.
    """
    session = get_session(request)
    if not check_auth(session):
        if request.url.path.startswith("/api/"):
            # For API routes, return a proper HTTP 401 error
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
                headers={"WWW-Authenticate": "Bearer"},
            )
        else:
            # For UI routes, redirect to login page
            return RedirectResponse(url="/login?next=" + str(request.url.path), status_code=303)
    return session 