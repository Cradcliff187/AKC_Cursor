"""
Shared dependencies for the AKC CRM application.
"""

import os
from fastapi import Request
from fastapi.templating import Jinja2Templates
from supabase import create_client, Client
from typing import Optional

# Initialize templates
templates = Jinja2Templates(directory="templates")

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