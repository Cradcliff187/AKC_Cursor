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

from dependencies import get_session, check_auth, templates, get_supabase_client
from mock_data import (
    MOCK_ACTIVITY, MOCK_VENDORS, MOCK_EXPENSES, MOCK_PROJECTS,
    MOCK_METRICS, MOCK_CUSTOMERS,
    VENDOR_CATEGORIES, VENDOR_STATUSES,
    EXPENSE_CATEGORIES, EXPENSE_STATUSES
)
from routes.vendors import router as vendors_router
from routes.projects import router as projects_router
from routes.auth import auth_router

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

# Add session middleware with a secure secret key
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET_KEY", os.urandom(24).hex())
)

# Custom URL generator function for templates
def url_for(name, filename=None, **kwargs):
    """Custom URL generator function for templates."""
    # Handle static files
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
        
        # Auth routes
        "login": "/login",
        "logout": "/logout",
        "index": "/"
    }
    
    if name in url_map:
        url_pattern = url_map[name]
        
        # Handle URL patterns with format placeholders
        if "{}" in url_pattern and kwargs:
            # For routes with a single parameter (like customer_id)
            if len(kwargs) == 1:
                param_value = list(kwargs.values())[0]
                return url_pattern.format(param_value)
            # For routes with multiple parameters
            elif len(kwargs) > 1:
                url_parts = url_pattern.split('{}')
                if len(url_parts) == len(kwargs) + 1:
                    result = url_parts[0]
                    for i, key in enumerate(kwargs):
                        result += str(kwargs[key]) + url_parts[i+1]
                    return result
        
        return url_pattern
    
    # Special case for direct paths
    if name.startswith('/'):
        return name
    
    # If the name contains a slash, treat it as a direct path
    if '/' in name:
        return f"/{name}"
    
    return f"/{name}"

# Add template globals
from dependencies import templates
templates.env.globals["url_for"] = url_for
templates.env.globals["get_flashed_messages"] = lambda with_categories=False: []
templates.env.globals["google_maps_api_key"] = os.getenv("GOOGLE_MAPS_API_KEY", "")

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

# Include routers - include auth_router first
app.include_router(auth_router)
app.include_router(vendors_router)
app.include_router(projects_router)

# Google Maps API configuration
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")

# Mock data for when Supabase is unavailable
MOCK_METRICS = {
    "total_projects": 5,
    "active_vendors": 12,
    "pending_approvals": 3
}

# Mock customer data
MOCK_CUSTOMERS = [
    {
        "id": 1,
        "name": "Acme Corporation",
        "contact_name": "John Smith",
        "email": "john.smith@acme.com",
        "phone": "(555) 123-4567",
        "address": "123 Main Street",
        "city": "Springfield",
        "state": "IL",
        "zip": "62701",
        "status": "Active",
        "customer_since": "2023-01-15",
        "payment_terms": "Net 30",
        "credit_limit": 25000.00,
        "notes": "Key client for commercial projects. Prefers email communication.",
        "created_at": "2023-01-15T10:00:00Z",
        "updated_at": "2025-02-20T14:30:00Z"
    },
    {
        "id": 2,
        "name": "TechSolutions Inc",
        "contact_name": "Sarah Johnson",
        "email": "sarah@techsolutions.com",
        "phone": "(555) 987-6543",
        "address": "456 Tech Boulevard",
        "city": "San Francisco",
        "state": "CA",
        "zip": "94105",
        "status": "Active",
        "customer_since": "2023-03-10",
        "payment_terms": "Net 15",
        "credit_limit": 50000.00,
        "notes": "Tech company requiring regular office renovations. Quick payment history.",
        "created_at": "2023-03-10T09:15:00Z",
        "updated_at": "2025-01-15T11:20:00Z"
    },
    {
        "id": 3,
        "name": "Global Retail Group",
        "contact_name": "Michael Williams",
        "email": "m.williams@globalretail.com",
        "phone": "(555) 456-7890",
        "address": "789 Shopping Lane",
        "city": "Chicago",
        "state": "IL",
        "zip": "60601",
        "status": "Active",
        "customer_since": "2023-05-22",
        "payment_terms": "Net 45",
        "credit_limit": 100000.00,
        "notes": "Multiple retail locations requiring consistent buildouts and maintenance.",
        "created_at": "2023-05-22T13:45:00Z",
        "updated_at": "2024-12-10T16:30:00Z"
    },
    {
        "id": 4,
        "name": "Healthcare Partners",
        "contact_name": "Dr. Emily Chen",
        "email": "dr.chen@healthcarepartners.org",
        "phone": "(555) 234-5678",
        "address": "321 Medical Center Drive",
        "city": "Boston",
        "state": "MA",
        "zip": "02115",
        "status": "Inactive",
        "customer_since": "2023-08-05",
        "payment_terms": "Net 30",
        "credit_limit": 75000.00,
        "notes": "Healthcare facility specializing in clinic renovations. Currently on hold due to budget constraints.",
        "created_at": "2023-08-05T08:20:00Z",
        "updated_at": "2025-01-30T10:15:00Z"
    },
    {
        "id": 5,
        "name": "EduLearn Academy",
        "contact_name": "Robert Taylor",
        "email": "r.taylor@edulearn.edu",
        "phone": "(555) 876-5432",
        "address": "555 Campus Circle",
        "city": "Austin",
        "state": "TX",
        "zip": "78712",
        "status": "Active",
        "customer_since": "2023-11-15",
        "payment_terms": "Net 60",
        "credit_limit": 40000.00,
        "notes": "Educational institution with regular summer renovation projects. Requires detailed planning and scheduling around academic calendar.",
        "created_at": "2023-11-15T11:30:00Z",
        "updated_at": "2025-02-28T09:45:00Z"
    }
]

# Mock projects data
MOCK_PROJECTS = [
    {
        "id": 1,
        "name": "Office Renovation",
        "client_id": 1,
        "client_name": "Acme Corporation",
        "status": "In Progress",
        "status_color": "primary",
        "start_date": "2025-01-15",
        "end_date": "2025-04-30",
        "budget": 75000.00,
        "spent": 30000.00,
        "remaining": 45000.00,
        "description": "Complete renovation of the main office space including new flooring, lighting, and workstations",
        "manager": "Jane Doe",
        "team": ["John Smith", "Emily Johnson", "Michael Brown"],
        "progress": 40,
        "created_at": "2024-12-10T09:00:00Z",
        "updated_at": "2025-02-15T14:30:00Z",
        "tasks": [
            {"id": 101, "name": "Demolition", "status": "Completed", "due_date": "2025-01-25"},
            {"id": 102, "name": "Electrical Work", "status": "In Progress", "due_date": "2025-02-20"},
            {"id": 103, "name": "Flooring Installation", "status": "Pending", "due_date": "2025-03-10"},
            {"id": 104, "name": "Furniture Assembly", "status": "Pending", "due_date": "2025-04-15"}
        ]
    },
    {
        "id": 2,
        "name": "Website Redesign",
        "client_id": 1,
        "client_name": "Acme Corporation",
        "status": "Planning",
        "status_color": "info",
        "start_date": "2025-03-01",
        "end_date": "2025-05-31",
        "budget": 25000.00,
        "spent": 5000.00,
        "remaining": 20000.00,
        "description": "Complete overhaul of corporate website with responsive design and modern branding",
        "manager": "David Chen",
        "team": ["Sarah Williams", "Alex Rodriguez"],
        "progress": 20,
        "created_at": "2025-01-15T11:30:00Z",
        "updated_at": "2025-02-20T16:45:00Z",
        "tasks": [
            {"id": 201, "name": "Requirements Gathering", "status": "Completed", "due_date": "2025-03-10"},
            {"id": 202, "name": "Wireframing", "status": "In Progress", "due_date": "2025-03-25"},
            {"id": 203, "name": "UI Design", "status": "Pending", "due_date": "2025-04-15"},
            {"id": 204, "name": "Development", "status": "Pending", "due_date": "2025-05-15"}
        ]
    },
    {
        "id": 3,
        "name": "Mobile App Development",
        "client_id": 2,
        "client_name": "TechSolutions Inc",
        "status": "In Progress",
        "status_color": "primary",
        "start_date": "2024-11-01",
        "end_date": "2025-06-30",
        "budget": 120000.00,
        "spent": 65000.00,
        "remaining": 55000.00,
        "description": "Development of cross-platform mobile application for inventory management",
        "manager": "Mike Johnson",
        "team": ["Jennifer Lee", "Raj Patel", "Chris Thompson", "Ana Garcia"],
        "progress": 55,
        "created_at": "2024-10-05T13:45:00Z",
        "updated_at": "2025-02-26T10:15:00Z",
        "tasks": [
            {"id": 301, "name": "Requirements Analysis", "status": "Completed", "due_date": "2024-11-15"},
            {"id": 302, "name": "UI/UX Design", "status": "Completed", "due_date": "2024-12-20"},
            {"id": 303, "name": "Frontend Development", "status": "In Progress", "due_date": "2025-03-15"},
            {"id": 304, "name": "Backend Integration", "status": "In Progress", "due_date": "2025-04-30"},
            {"id": 305, "name": "Testing & QA", "status": "Pending", "due_date": "2025-06-01"}
        ]
    },
    {
        "id": 4,
        "name": "Warehouse Expansion",
        "client_id": 3,
        "client_name": "Global Retail Group",
        "status": "Planning",
        "status_color": "info",
        "start_date": "2025-04-15",
        "end_date": "2025-12-31",
        "budget": 500000.00,
        "spent": 25000.00,
        "remaining": 475000.00,
        "description": "Construction of additional 50,000 sq ft warehouse space with modern logistics systems",
        "manager": "Robert Jackson",
        "team": ["Lisa Chen", "Mark Davis", "Samantha Perez"],
        "progress": 5,
        "created_at": "2025-01-10T09:30:00Z",
        "updated_at": "2025-02-28T15:20:00Z",
        "tasks": [
            {"id": 401, "name": "Site Survey", "status": "Completed", "due_date": "2025-02-15"},
            {"id": 402, "name": "Permit Acquisition", "status": "In Progress", "due_date": "2025-04-01"},
            {"id": 403, "name": "Foundation Work", "status": "Pending", "due_date": "2025-06-15"},
            {"id": 404, "name": "Structure Construction", "status": "Pending", "due_date": "2025-09-30"},
            {"id": 405, "name": "Interior Finishing", "status": "Pending", "due_date": "2025-11-30"}
        ]
    },
    {
        "id": 5,
        "name": "Clinic Renovation",
        "client_id": 4,
        "client_name": "Healthcare Partners",
        "status": "On Hold",
        "status_color": "warning",
        "start_date": "2025-03-01",
        "end_date": "2025-07-31",
        "budget": 250000.00,
        "spent": 0.00,
        "remaining": 250000.00,
        "description": "Renovation of outpatient clinic with updated medical facilities and patient waiting areas",
        "manager": "Patricia Wilson",
        "team": ["James Miller", "Nancy Thompson"],
        "progress": 0,
        "created_at": "2024-12-15T14:20:00Z",
        "updated_at": "2025-02-10T11:45:00Z",
        "tasks": [
            {"id": 501, "name": "Initial Planning", "status": "Completed", "due_date": "2025-01-15"},
            {"id": 502, "name": "Budget Approval", "status": "On Hold", "due_date": "2025-02-28"},
            {"id": 503, "name": "Construction Start", "status": "Pending", "due_date": "2025-03-15"},
            {"id": 504, "name": "Equipment Installation", "status": "Pending", "due_date": "2025-06-15"}
        ]
    },
    {
        "id": 6,
        "name": "Campus Library Modernization",
        "client_id": 5,
        "client_name": "EduLearn Academy",
        "status": "Completed",
        "status_color": "success",
        "start_date": "2024-06-01",
        "end_date": "2024-12-15",
        "budget": 180000.00,
        "spent": 172500.00,
        "remaining": 7500.00,
        "description": "Renovation of the main campus library with digital learning spaces and modernized study areas",
        "manager": "Thomas Wright",
        "team": ["Elizabeth Young", "Daniel Martinez", "Olivia Johnson"],
        "progress": 100,
        "created_at": "2024-05-10T10:00:00Z",
        "updated_at": "2024-12-20T16:30:00Z",
        "tasks": [
            {"id": 601, "name": "Design Phase", "status": "Completed", "due_date": "2024-06-30"},
            {"id": 602, "name": "Demolition", "status": "Completed", "due_date": "2024-07-31"},
            {"id": 603, "name": "Construction", "status": "Completed", "due_date": "2024-10-31"},
            {"id": 604, "name": "Furnishing", "status": "Completed", "due_date": "2024-11-30"},
            {"id": 605, "name": "Final Inspection", "status": "Completed", "due_date": "2024-12-15"}
        ]
    }
]

# Mock time logs data
MOCK_TIME_LOGS = [
    {"id": 1, "date": "2025-03-01", "project_id": 1, "project_name": "Office Renovation", "task_name": "Electrical Work", "user_name": "Admin", "hours": 4.5, "description": "Installed new lighting fixtures", "billable": True, "status": "Approved", "status_color": "success"},
    {"id": 2, "date": "2025-03-02", "project_id": 4, "project_name": "Warehouse Expansion", "task_name": "Planning", "user_name": "Admin", "hours": 2.0, "description": "Meeting with architects", "billable": True, "status": "Approved", "status_color": "success"},
    {"id": 3, "date": "2025-03-03", "project_id": 1, "project_name": "Office Renovation", "task_name": "Plumbing", "user_name": "Admin", "hours": 6.0, "description": "Bathroom fixtures installation", "billable": True, "status": "Pending", "status_color": "warning"},
    {"id": 4, "date": "2025-03-04", "project_id": 3, "project_name": "Mobile App Development", "task_name": "Frontend Development", "user_name": "Admin", "hours": 8.0, "description": "Implemented UI components", "billable": True, "status": "Pending", "status_color": "warning"},
    {"id": 5, "date": "2025-03-05", "project_id": 1, "project_name": "Office Renovation", "task_name": "Painting", "user_name": "Admin", "hours": 7.5, "description": "Painted main office area", "billable": True, "status": "Pending", "status_color": "warning"},
    {"id": 6, "date": "2025-03-06", "project_id": 4, "project_name": "Warehouse Expansion", "task_name": "Foundation", "user_name": "Admin", "hours": 8.0, "description": "Supervised foundation pouring", "billable": True, "status": "Pending", "status_color": "warning"},
    {"id": 7, "date": "2025-03-07", "project_id": 3, "project_name": "Mobile App Development", "task_name": "Backend Integration", "user_name": "Admin", "hours": 5.0, "description": "API integration work", "billable": True, "status": "Draft", "status_color": "secondary"},
]

# Mock data for expenses
MOCK_EXPENSES = [
    {
        "id": 1,
        "date": "2025-03-14",
        "vendor_id": 1,
        "vendor_name": "ABC Supply",
        "project_id": 1,
        "project_name": "Office Renovation",
        "category": "Materials",
        "description": "Lumber and building materials",
        "amount": 1500.00,
        "status": "approved",
        "receipt_url": "/static/mock/receipts/receipt1.pdf",
        "created_at": "2025-03-14T10:00:00Z",
        "updated_at": "2025-03-14T11:00:00Z"
    },
    {
        "id": 2,
        "date": "2025-03-14",
        "vendor_id": 2,
        "vendor_name": "XYZ Tools",
        "project_id": 1,
        "project_name": "Office Renovation",
        "category": "Equipment",
        "description": "Power tools rental",
        "amount": 750.00,
        "status": "pending",
        "receipt_url": "/static/mock/receipts/receipt2.pdf",
        "created_at": "2025-03-14T09:00:00Z",
        "updated_at": "2025-03-14T09:00:00Z"
    }
]

# Expense categories and statuses
EXPENSE_CATEGORIES = [
    "Materials",
    "Equipment",
    "Labor",
    "Transportation",
    "Permits",
    "Insurance",
    "Office Supplies",
    "Utilities",
    "Maintenance",
    "Other"
]

EXPENSE_STATUSES = [
    "pending",
    "approved",
    "rejected",
    "reimbursed"
]

# Mock data for vendors
MOCK_VENDORS = [
    {
        "id": 1,
        "name": "ABC Supply",
        "contact_name": "John Smith",
        "email": "john@abcsupply.com",
        "phone": "555-0100",
        "address": "123 Main St, Anytown, USA",
        "material_category": "Building Materials",
        "preferred": True,
        "rating": 5,
        "status": "active",
        "created_at": "2025-03-01T10:00:00Z",
        "updated_at": "2025-03-14T11:00:00Z"
    },
    {
        "id": 2,
        "name": "XYZ Tools",
        "contact_name": "Jane Doe",
        "email": "jane@xyztools.com",
        "phone": "555-0200",
        "address": "456 Oak St, Anytown, USA",
        "material_category": "Tools & Equipment",
        "preferred": False,
        "rating": 4,
        "status": "active",
        "created_at": "2025-03-02T10:00:00Z",
        "updated_at": "2025-03-14T09:00:00Z"
    }
]

# Vendor categories and statuses
VENDOR_CATEGORIES = [
    "Building Materials",
    "Tools & Equipment",
    "Electrical",
    "Plumbing",
    "HVAC",
    "Landscaping",
    "Safety Equipment",
    "Office Supplies",
    "Cleaning Supplies",
    "Other"
]

VENDOR_STATUSES = [
    "active",
    "inactive",
    "pending",
    "blacklisted"
]

# Dashboard page (placeholder)
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Dashboard endpoint with proper Supabase handling and mock data fallback."""
    try:
        supabase = get_supabase_client()
        recent_activity = []
        metrics = {}
        
        if supabase:
            try:
                # Try to get data from Supabase
                activity_result = supabase.table("activity_log").select("*").order("created_at", desc=True).limit(5).execute()
                recent_activity = activity_result.data if activity_result else []
                
                # Get key metrics
                metrics = {
                    "total_projects": len(supabase.table("projects").select("id").execute().data),
                    "active_vendors": len(supabase.table("vendors").select("id").eq("status", "active").execute().data),
                    "pending_approvals": len(supabase.table("purchases").select("id").eq("status", "pending").execute().data)
                }
            except Exception as e:
                print(f"Error fetching data from Supabase: {str(e)}")
                recent_activity = MOCK_ACTIVITY
                metrics = MOCK_METRICS
        else:
            # Use mock data when Supabase is not available
            recent_activity = MOCK_ACTIVITY
            metrics = MOCK_METRICS
        
        return templates.TemplateResponse(
            "dashboard.html",
            {
                "request": request,
                "session": request.session,
                "recent_activity": recent_activity,
                "metrics": metrics
            }
        )
    except Exception as e:
        print(f"Dashboard Error: {str(e)}")
        print(f"Stack Trace: {traceback.format_exc()}")
        
        # Return error response with mock data as fallback
        return templates.TemplateResponse(
            "dashboard.html",
            {
                "request": request,
                "session": request.session,
                "recent_activity": MOCK_ACTIVITY,
                "metrics": MOCK_METRICS,
                "error": "Error loading live data - showing mock data"
            }
        )

# Define other route handlers as needed
@app.get("/contacts", response_class=HTMLResponse)
async def contacts(
    request: Request,
    session: dict = Depends(get_session),
    search: str = None,
    type: str = None,
    sort: str = None,
    page: int = 1
):
    """List all contacts with filtering, sorting, and pagination."""
    if not check_auth(session):
        return RedirectResponse(url="/login")
    
    try:
        # Get contacts from Supabase or mock data
        supabase_client = get_supabase_client()
        contacts_data = []
        
        try:
            if supabase_client:
                # Build query with filters
                query = supabase_client.table("contacts").select("*")
                
                if type and type != "All":
                    query = query.eq("type", type)
                    
                if search:
                    query = query.or_(f"name.ilike.%{search}%,company.ilike.%{search}%,email.ilike.%{search}%")
                    
                if sort:
                    # Example: sort=name.asc or sort=company.desc
                    field, direction = sort.split('.')
                    query = query.order(field, ascending=(direction == 'asc'))
                else:
                    # Default sort by name ascending
                    query = query.order("name", ascending=True)
                
                result = query.execute()
                contacts_data = result.data
            else:
                # Use mock data with filtering in Python
                contacts_data = [
                    {"id": 1, "name": "John Smith", "company": "ABC Corp", "email": "john.smith@abccorp.com", "phone": "(555) 123-4567", "type": "Client", "type_color": "primary"},
                    {"id": 2, "name": "Jane Doe", "company": "XYZ Industries", "email": "jane.doe@xyzindustries.com", "phone": "(555) 987-6543", "type": "Client", "type_color": "primary"},
                    {"id": 3, "name": "Bob Johnson", "company": "123 Retail", "email": "bob.johnson@123retail.com", "phone": "(555) 456-7890", "type": "Client", "type_color": "primary"},
                    {"id": 4, "name": "Alice Williams", "company": "DEF Corp", "email": "alice.williams@defcorp.com", "phone": "(555) 234-5678", "type": "Client", "type_color": "primary"},
                    {"id": 5, "name": "Charlie Brown", "company": "Gourmet Foods", "email": "charlie.brown@gourmetfoods.com", "phone": "(555) 876-5432", "type": "Client", "type_color": "primary"},
                    {"id": 6, "name": "David Miller", "company": "Electrical Services", "email": "david.miller@electrical.com", "phone": "(555) 345-6789", "type": "Vendor", "type_color": "success"},
                    {"id": 7, "name": "Eva Garcia", "company": "Plumbing Co", "email": "eva.garcia@plumbing.com", "phone": "(555) 654-3210", "type": "Vendor", "type_color": "success"},
                    {"id": 8, "name": "Frank Wilson", "company": "HVAC Solutions", "email": "frank.wilson@hvac.com", "phone": "(555) 765-4321", "type": "Vendor", "type_color": "success"},
                ]
                
                # Apply filters
                if type and type != "All":
                    contacts_data = [c for c in contacts_data if c["type"].lower() == type.lower()]
                    
                if search:
                    search = search.lower()
                    contacts_data = [c for c in contacts_data if 
                                   search in c["name"].lower() or
                                   search in c["company"].lower() or
                                   search in c["email"].lower()]
                
                # Apply sorting
                if sort:
                    field, direction = sort.split('.')
                    reverse = direction == 'desc'
                    contacts_data.sort(key=lambda x: x.get(field, ''), reverse=reverse)
                else:
                    # Default sort by name ascending
                    contacts_data.sort(key=lambda x: x.get("name", ''))
        
        except Exception as e:
            print(f"Error fetching contacts: {str(e)}")
            # Fallback to empty list
            contacts_data = []
        
        # Pagination
        items_per_page = 10
        total_items = len(contacts_data)
        total_pages = (total_items + items_per_page - 1) // items_per_page
        
        # Ensure page is within valid range
        if page < 1:
            page = 1
        elif page > total_pages and total_pages > 0:
            page = total_pages
        
        # Calculate pagination indices
        start_idx = (page - 1) * items_per_page
        end_idx = min(start_idx + items_per_page, total_items)
        
        # Get contacts for current page
        paginated_contacts = contacts_data[start_idx:end_idx]
        
        # Get contact statistics
        total_contacts = len(contacts_data)
        client_contacts = len([c for c in contacts_data if c["type"] == "Client"])
        vendor_contacts = len([c for c in contacts_data if c["type"] == "Vendor"])
        recent_contacts = len([c for c in contacts_data if c.get("last_contact", "") >= (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")])
        
        # Prepare filter options
        contact_types = ["All", "Client", "Vendor", "Subcontractor", "Employee"]
        sort_options = [
            {"value": "name.asc", "label": "Name (A-Z)"},
            {"value": "name.desc", "label": "Name (Z-A)"},
            {"value": "company.asc", "label": "Company (A-Z)"},
            {"value": "company.desc", "label": "Company (Z-A)"},
            {"value": "type.asc", "label": "Type (A-Z)"},
            {"value": "type.desc", "label": "Type (Z-A)"}
        ]
        
        return templates.TemplateResponse(
            "contacts.html",
            {
                "request": request,
                "session": session,
                "contacts": paginated_contacts,
                "page": page,
                "total_pages": total_pages,
                "total_items": total_items,
                "search": search or "",
                "type": type or "All",
                "sort": sort or "name.asc",
                "contact_types": contact_types,
                "sort_options": sort_options,
                "stats": {
                    "total": total_contacts,
                    "clients": client_contacts,
                    "vendors": vendor_contacts,
                    "recent": recent_contacts
                }
            }
        )
        
    except Exception as e:
        print(f"Error in contacts route: {str(e)}")
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "session": session,
                "status_code": 500,
                "detail": f"Error loading contacts: {str(e)}"
            },
            status_code=500
        )

@app.get("/contacts/new", response_class=HTMLResponse)
async def new_contact(
    request: Request,
    session: dict = Depends(get_session)
):
    """Display form for creating a new contact."""
    if not check_auth(session):
        return RedirectResponse(url="/login")
    
    try:
        # Prepare form options
        contact_types = ["Client", "Vendor", "Subcontractor", "Employee"]
        
        return templates.TemplateResponse(
            "contact_form.html",
            {
                "request": request,
                "session": session,
                "contact": None,  # No contact data for new form
                "contact_types": contact_types,
                "mode": "create"
            }
        )
    except Exception as e:
        print(f"Error in new contact form route: {str(e)}")
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "session": session,
                "status_code": 500,
                "detail": f"Error loading contact form: {str(e)}"
            },
            status_code=500
        )

@app.post("/contacts/new", response_class=RedirectResponse)
async def create_contact(
    request: Request,
    session: dict = Depends(get_session)
):
    """Handle creation of a new contact."""
    if not check_auth(session):
        return RedirectResponse(url="/login")
    
    try:
        form = await request.form()
        
        # Prepare contact data
        contact_data = {
            "name": form.get("name"),
            "company": form.get("company"),
            "email": form.get("email"),
            "phone": form.get("phone"),
            "type": form.get("type"),
            "address": form.get("address"),
            "notes": form.get("notes"),
            "created_at": datetime.now().strftime("%Y-%m-%d"),
            "last_contact": datetime.now().strftime("%Y-%m-%d")
        }
        
        # Validate required fields
        required_fields = ["name", "email", "type"]
        for field in required_fields:
            if not contact_data[field]:
                return templates.TemplateResponse(
                    "contact_form.html",
                    {
                        "request": request,
                        "session": session,
                        "contact": contact_data,
                        "contact_types": ["Client", "Vendor", "Subcontractor", "Employee"],
                        "mode": "create",
                        "error": f"{field.title()} is required"
                    }
                )
        
        # Create contact in Supabase or mock data
        supabase_client = get_supabase_client()
        if supabase_client:
            result = supabase_client.table("contacts").insert(contact_data).execute()
            contact_id = result.data[0]["id"]
        else:
            # Mock creation (just redirect)
            contact_id = 1
        
        return RedirectResponse(url=f"/contacts/{contact_id}", status_code=303)
        
    except Exception as e:
        print(f"Error creating contact: {str(e)}")
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "session": session,
                "status_code": 500,
                "detail": f"Error creating contact: {str(e)}"
            },
            status_code=500
        )

@app.get("/contacts/{contact_id}/edit", response_class=HTMLResponse)
async def edit_contact_form(
    request: Request,
    contact_id: int,
    session: dict = Depends(get_session)
):
    """Display form for editing an existing contact."""
    if not check_auth(session):
        return RedirectResponse(url="/login")
    
    try:
        # Get contact from Supabase or mock data
        supabase_client = get_supabase_client()
        contact = None
        
        try:
            if supabase_client:
                result = supabase_client.table("contacts").select("*").eq("id", contact_id).execute()
                if result.data:
                    contact = result.data[0]
            else:
                # Mock contact data
                mock_contacts = [
                    {"id": 1, "name": "John Smith", "company": "ABC Corp", "email": "john.smith@abccorp.com", "phone": "(555) 123-4567", "type": "Client", "address": "123 Main St, Anytown, USA", "notes": "Key decision maker for office renovation project", "created_at": "2025-01-15", "last_contact": "2025-03-01"},
                ]
                contact = next((c for c in mock_contacts if c["id"] == contact_id), None)
        
        except Exception as e:
            print(f"Error fetching contact: {str(e)}")
            contact = None
        
        if not contact:
            return templates.TemplateResponse(
                "error.html",
                {
                    "request": request,
                    "session": session,
                    "status_code": 404,
                    "detail": f"Contact with ID {contact_id} not found"
                },
                status_code=404
            )
        
        # Prepare form options
        contact_types = ["Client", "Vendor", "Subcontractor", "Employee"]
        
        return templates.TemplateResponse(
            "contact_form.html",
            {
                "request": request,
                "session": session,
                "contact": contact,
                "contact_types": contact_types,
                "mode": "edit"
            }
        )
        
    except Exception as e:
        print(f"Error in edit contact form route: {str(e)}")
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "session": session,
                "status_code": 500,
                "detail": f"Error loading contact form: {str(e)}"
            },
            status_code=500
        )

@app.post("/contacts/{contact_id}/edit", response_class=RedirectResponse)
async def update_contact(
    request: Request,
    contact_id: int,
    session: dict = Depends(get_session)
):
    """Handle updating an existing contact."""
    if not check_auth(session):
        return RedirectResponse(url="/login")
    
    try:
        form = await request.form()
        
        # Prepare contact data
        contact_data = {
            "name": form.get("name"),
            "company": form.get("company"),
            "email": form.get("email"),
            "phone": form.get("phone"),
            "type": form.get("type"),
            "address": form.get("address"),
            "notes": form.get("notes"),
            "last_contact": datetime.now().strftime("%Y-%m-%d")
        }
        
        # Validate required fields
        required_fields = ["name", "email", "type"]
        for field in required_fields:
            if not contact_data[field]:
                return templates.TemplateResponse(
                    "contact_form.html",
                    {
                        "request": request,
                        "session": session,
                        "contact": {**contact_data, "id": contact_id},
                        "contact_types": ["Client", "Vendor", "Subcontractor", "Employee"],
                        "mode": "edit",
                        "error": f"{field.title()} is required"
                    }
                )
        
        # Update contact in Supabase or mock data
        supabase_client = get_supabase_client()
        if supabase_client:
            result = supabase_client.table("contacts").update(contact_data).eq("id", contact_id).execute()
            if not result.data:
                raise Exception("Contact not found")
        
        return RedirectResponse(url=f"/contacts/{contact_id}", status_code=303)
        
    except Exception as e:
        print(f"Error updating contact: {str(e)}")
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "session": session,
                "status_code": 500,
                "detail": f"Error updating contact: {str(e)}"
            },
            status_code=500
        )

@app.post("/contacts/{contact_id}/delete", response_class=RedirectResponse)
async def delete_contact(
    request: Request,
    contact_id: int,
    session: dict = Depends(get_session)
):
    """Handle deletion of a contact."""
    if not check_auth(session):
        return RedirectResponse(url="/login")
    
    try:
        # Delete contact from Supabase or mock data
        supabase_client = get_supabase_client()
        if supabase_client:
            result = supabase_client.table("contacts").delete().eq("id", contact_id).execute()
            if not result.data:
                raise Exception("Contact not found")
        
        return RedirectResponse(url="/contacts", status_code=303)
        
    except Exception as e:
        print(f"Error deleting contact: {str(e)}")
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "session": session,
                "status_code": 500,
                "detail": f"Error deleting contact: {str(e)}"
            },
            status_code=500
        )

@app.get("/time-logs", response_class=HTMLResponse)
async def time_logs(
    request: Request,
    session: dict = Depends(get_session),
    search: str = None,
    project_id: int = None,
    user_id: int = None,
    status: str = None,
    date_from: str = None,
    date_to: str = None,
    sort: str = None,
    page: int = 1
):
    """List all time logs with filtering, sorting, and pagination."""
    if not check_auth(session):
        return RedirectResponse(url="/login")
    
    try:
        # Get time logs from Supabase or mock data
        supabase_client = get_supabase_client()
        time_logs_data = []
        
        try:
            if supabase_client:
                # Build query with filters
                query = supabase_client.table("time_logs").select("*")
                
                if status:
                    query = query.eq("status", status)
                
                if project_id:
                    query = query.eq("project_id", project_id)
                
                if user_id:
                    query = query.eq("user_id", user_id)
                
                if date_from:
                    query = query.gte("date", date_from)
                
                if date_to:
                    query = query.lte("date", date_to)
                
                if search:
                    query = query.or_(f"description.ilike.%{search}%,task.ilike.%{search}%")
                
                if sort:
                    # Example: sort=date.desc or sort=hours.asc
                    field, direction = sort.split('.')
                    query = query.order(field, ascending=(direction == 'asc'))
                else:
                    # Default sort by date descending
                    query = query.order("date", ascending=False)
                
                result = query.execute()
                time_logs_data = result.data
            else:
                # Use mock data
                time_logs_data = [
                    {
                        "id": 1,
                        "project_id": 1,
                        "project_name": "Office Renovation",
                        "user_id": 1,
                        "user_name": "John Smith",
                        "date": "2025-03-15",
                        "hours": 8.5,
                        "task": "Electrical Work",
                        "description": "Installed new lighting fixtures in main office area",
                        "billable": True,
                        "status": "Approved",
                        "created_at": "2025-03-15T17:00:00Z"
                    },
                    {
                        "id": 2,
                        "project_id": 1,
                        "project_name": "Office Renovation",
                        "user_id": 2,
                        "user_name": "Emily Johnson",
                        "date": "2025-03-15",
                        "hours": 6.0,
                        "task": "Flooring",
                        "description": "Prepared subfloor for new tile installation",
                        "billable": True,
                        "status": "Pending",
                        "created_at": "2025-03-15T15:30:00Z"
                    },
                    {
                        "id": 3,
                        "project_id": 2,
                        "project_name": "Website Redesign",
                        "user_id": 3,
                        "user_name": "Sarah Williams",
                        "date": "2025-03-15",
                        "hours": 4.5,
                        "task": "UI Design",
                        "description": "Created wireframes for homepage and product pages",
                        "billable": True,
                        "status": "Approved",
                        "created_at": "2025-03-15T14:00:00Z"
                    }
                ]
                
                # Apply filters to mock data
                if status:
                    time_logs_data = [t for t in time_logs_data if t["status"].lower() == status.lower()]
                
                if project_id:
                    time_logs_data = [t for t in time_logs_data if t["project_id"] == project_id]
                
                if user_id:
                    time_logs_data = [t for t in time_logs_data if t["user_id"] == user_id]
                
                if date_from:
                    time_logs_data = [t for t in time_logs_data if t["date"] >= date_from]
                
                if date_to:
                    time_logs_data = [t for t in time_logs_data if t["date"] <= date_to]
                
                if search:
                    search = search.lower()
                    time_logs_data = [t for t in time_logs_data if 
                                    search in t["description"].lower() or
                                    search in t["task"].lower()]
                
                # Apply sorting
                if sort:
                    field, direction = sort.split('.')
                    reverse = direction == 'desc'
                    time_logs_data.sort(key=lambda x: x.get(field, ''), reverse=reverse)
                else:
                    # Default sort by date descending
                    time_logs_data.sort(key=lambda x: x["date"], reverse=True)
        
        except Exception as e:
            print(f"Error fetching time logs: {str(e)}")
            time_logs_data = []
        
        # Pagination
        items_per_page = 10
        total_items = len(time_logs_data)
        total_pages = (total_items + items_per_page - 1) // items_per_page
        
        # Ensure page is within valid range
        if page < 1:
            page = 1
        elif page > total_pages and total_pages > 0:
            page = total_pages
        
        # Calculate pagination indices
        start_idx = (page - 1) * items_per_page
        end_idx = min(start_idx + items_per_page, total_items)
        
        # Get time logs for current page
        paginated_time_logs = time_logs_data[start_idx:end_idx]
        
        # Get time log statistics
        total_hours = sum(t["hours"] for t in time_logs_data)
        billable_hours = sum(t["hours"] for t in time_logs_data if t["billable"])
        pending_hours = sum(t["hours"] for t in time_logs_data if t["status"] == "Pending")
        today_hours = sum(t["hours"] for t in time_logs_data if t["date"] == datetime.now().strftime("%Y-%m-%d"))
        
        # Prepare filter options
        statuses = ["All", "Pending", "Approved", "Rejected"]
        sort_options = [
            {"value": "date.desc", "label": "Date (Newest)"},
            {"value": "date.asc", "label": "Date (Oldest)"},
            {"value": "hours.desc", "label": "Hours (Highest)"},
            {"value": "hours.asc", "label": "Hours (Lowest)"},
            {"value": "project_name.asc", "label": "Project (A-Z)"},
            {"value": "project_name.desc", "label": "Project (Z-A)"}
        ]
        
        # Get projects for filter dropdown
        projects = []
        try:
            if supabase_client:
                result = supabase_client.table("projects").select("id,name").execute()
                projects = result.data
            else:
                projects = [{"id": p["id"], "name": p["name"]} for p in MOCK_PROJECTS]
        except Exception as e:
            print(f"Error fetching projects: {str(e)}")
        
        return templates.TemplateResponse(
            "time_logs.html",
            {
                "request": request,
                "session": session,
                "time_logs": paginated_time_logs,
                "page": page,
                "total_pages": total_pages,
                "total_items": total_items,
                "search": search or "",
                "project_id": project_id,
                "user_id": user_id,
                "status": status or "All",
                "date_from": date_from or "",
                "date_to": date_to or "",
                "sort": sort or "date.desc",
                "projects": projects,
                "statuses": statuses,
                "sort_options": sort_options,
                "stats": {
                    "total_hours": total_hours,
                    "billable_hours": billable_hours,
                    "pending_hours": pending_hours,
                    "today_hours": today_hours
                }
            }
        )
        
    except Exception as e:
        print(f"Error in time logs route: {str(e)}")
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "session": session,
                "status_code": 500,
                "detail": f"Error loading time logs: {str(e)}"
            },
            status_code=500
        )

@app.get("/time-logs/{time_log_id}", response_class=HTMLResponse)
async def time_log_detail(
    request: Request,
    time_log_id: int,
    session: dict = Depends(get_session)
):
    """Get detailed information about a specific time log entry."""
    if not check_auth(session):
        return RedirectResponse(url="/login")
    
    try:
        # Get time log from Supabase or mock data
        supabase_client = get_supabase_client()
        time_log = None
        
        try:
            if supabase_client:
                result = supabase_client.table("time_logs").select("*").eq("id", time_log_id).execute()
                if result.data:
                    time_log = result.data[0]
            else:
                # Mock time log data
                mock_time_logs = [
                    {
                        "id": 1,
                        "project_id": 1,
                        "project_name": "Office Renovation",
                        "user_id": 1,
                        "user_name": "John Smith",
                        "date": "2025-03-15",
                        "hours": 8.5,
                        "task": "Electrical Work",
                        "description": "Installed new lighting fixtures in main office area",
                        "billable": True,
                        "status": "Approved",
                        "created_at": "2025-03-15T17:00:00Z",
                        "updated_at": "2025-03-15T17:30:00Z",
                        "approved_by": "Jane Doe",
                        "approved_at": "2025-03-15T18:00:00Z",
                        "notes": "Completed on schedule, all fixtures tested and working",
                        "location": "Main Office - Floor 2",
                        "overtime": False,
                        "break_time": 1.0
                    }
                ]
                time_log = next((t for t in mock_time_logs if t["id"] == time_log_id), None)
        
        except Exception as e:
            print(f"Error fetching time log: {str(e)}")
            time_log = None
        
        if not time_log:
            return templates.TemplateResponse(
                "error.html",
                {
                    "request": request,
                    "session": session,
                    "status_code": 404,
                    "detail": f"Time log with ID {time_log_id} not found"
                },
                status_code=404
            )
        
        # Get related project details
        project = None
        try:
            if supabase_client:
                result = supabase_client.table("projects").select("*").eq("id", time_log["project_id"]).execute()
                if result.data:
                    project = result.data[0]
            else:
                project = next((p for p in MOCK_PROJECTS if p["id"] == time_log["project_id"]), None)
        except Exception as e:
            print(f"Error fetching project details: {str(e)}")
        
        # Get user details
        user = None
        try:
            if supabase_client:
                result = supabase_client.table("users").select("*").eq("id", time_log["user_id"]).execute()
                if result.data:
                    user = result.data[0]
            else:
                # Mock user data
                user = {
                    "id": time_log["user_id"],
                    "name": time_log["user_name"],
                    "email": "john.smith@example.com",
                    "role": "Technician",
                    "department": "Field Operations"
                }
        except Exception as e:
            print(f"Error fetching user details: {str(e)}")
        
        # Get related time logs (same project, same day)
        related_time_logs = []
        try:
            if supabase_client:
                result = supabase_client.table("time_logs").select("*").eq("project_id", time_log["project_id"]).eq("date", time_log["date"]).neq("id", time_log_id).execute()
                related_time_logs = result.data
            else:
                # Mock related time logs
                related_time_logs = [
                    {
                        "id": 2,
                        "project_id": 1,
                        "project_name": "Office Renovation",
                        "user_id": 2,
                        "user_name": "Emily Johnson",
                        "date": "2025-03-15",
                        "hours": 6.0,
                        "task": "Flooring",
                        "description": "Prepared subfloor for new tile installation",
                        "billable": True,
                        "status": "Pending"
                    }
                ]
        except Exception as e:
            print(f"Error fetching related time logs: {str(e)}")
        
        return templates.TemplateResponse(
            "time_log_detail.html",
            {
                "request": request,
                "session": session,
                "time_log": time_log,
                "project": project,
                "user": user,
                "related_time_logs": related_time_logs
            }
        )
        
    except Exception as e:
        print(f"Error in time log detail route: {str(e)}")
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "session": session,
                "status_code": 500,
                "detail": f"Error loading time log details: {str(e)}"
            },
            status_code=500
        )

@app.get("/time-logs/new", response_class=HTMLResponse)
async def new_time_log(
    request: Request,
    session: dict = Depends(get_session),
    project_id: int = None
):
    """Display form for creating a new time log entry."""
    if not check_auth(session):
        return RedirectResponse(url="/login")
    
    try:
        # Get projects for dropdown
        projects = []
        try:
            supabase_client = get_supabase_client()
            if supabase_client:
                result = supabase_client.table("projects").select("*").eq("status", "Active").execute()
                projects = result.data
            else:
                projects = [p for p in MOCK_PROJECTS if p["status"] == "Active"]
        except Exception as e:
            print(f"Error fetching projects: {str(e)}")
            projects = []
        
        # Get selected project if project_id is provided
        selected_project = None
        if project_id:
            selected_project = next((p for p in projects if p["id"] == project_id), None)
        
        return templates.TemplateResponse(
            "time_log_form.html",
            {
                "request": request,
                "session": session,
                "time_log": {
                    "id": None,
                    "project_id": project_id,
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "hours": 0,
                    "task": "",
                    "description": "",
                    "billable": True,
                    "status": "Pending"
                },
                "projects": projects,
                "selected_project": selected_project,
                "mode": "create"
            }
        )
    except Exception as e:
        print(f"Error in new time log form route: {str(e)}")
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "session": session,
                "status_code": 500,
                "detail": f"Error loading time log form: {str(e)}"
            },
            status_code=500
        )

@app.post("/time-logs/new", response_class=RedirectResponse)
async def create_time_log(
    request: Request,
    session: dict = Depends(get_session)
):
    """Handle creation of a new time log entry."""
    if not check_auth(session):
        return RedirectResponse(url="/login")
    
    try:
        form = await request.form()
        
        # Prepare time log data
        time_log_data = {
            "project_id": int(form.get("project_id")),
            "user_id": session.get("user_id"),
            "date": form.get("date"),
            "hours": float(form.get("hours")),
            "task": form.get("task"),
            "description": form.get("description"),
            "billable": form.get("billable") == "true",
            "status": "Pending",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "location": form.get("location", ""),
            "overtime": form.get("overtime") == "true",
            "break_time": float(form.get("break_time", 0))
        }
        
        # Validate required fields
        required_fields = ["project_id", "date", "hours", "task"]
        for field in required_fields:
            if not time_log_data.get(field):
                return templates.TemplateResponse(
                    "time_log_form.html",
                    {
                        "request": request,
                        "session": session,
                        "time_log": time_log_data,
                        "projects": MOCK_PROJECTS,
                        "mode": "create",
                        "error": f"{field.replace('_', ' ').title()} is required"
                    }
                )
        
        # Create time log in Supabase or mock data
        supabase_client = get_supabase_client()
        if supabase_client:
            result = supabase_client.table("time_logs").insert(time_log_data).execute()
            time_log_id = result.data[0]["id"]
        else:
            # Mock creation (just redirect)
            time_log_id = 1
        
        return RedirectResponse(url=f"/time-logs/{time_log_id}", status_code=303)
        
    except Exception as e:
        print(f"Error creating time log: {str(e)}")
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "session": session,
                "status_code": 500,
                "detail": f"Error creating time log: {str(e)}"
            },
            status_code=500
        )

@app.get("/time-logs/{time_log_id}/edit", response_class=HTMLResponse)
async def edit_time_log_form(
    request: Request,
    time_log_id: int,
    session: dict = Depends(get_session)
):
    """Display form for editing an existing time log entry."""
    if not check_auth(session):
        return RedirectResponse(url="/login")
    
    try:
        # Get time log from Supabase or mock data
        supabase_client = get_supabase_client()
        time_log = None
        
        try:
            if supabase_client:
                result = supabase_client.table("time_logs").select("*").eq("id", time_log_id).execute()
                if result.data:
                    time_log = result.data[0]
            else:
                # Mock time log data
                time_log = {
                    "id": time_log_id,
                    "project_id": 1,
                    "user_id": 1,
                    "date": "2025-03-15",
                    "hours": 8.5,
                    "task": "Electrical Work",
                    "description": "Installed new lighting fixtures in main office area",
                    "billable": True,
                    "status": "Pending",
                    "location": "Main Office - Floor 2",
                    "overtime": False,
                    "break_time": 1.0
                }
        
        except Exception as e:
            print(f"Error fetching time log: {str(e)}")
            time_log = None
        
        if not time_log:
            return templates.TemplateResponse(
                "error.html",
                {
                    "request": request,
                    "session": session,
                    "status_code": 404,
                    "detail": f"Time log with ID {time_log_id} not found"
                },
                status_code=404
            )
        
        # Get projects for dropdown
        projects = []
        try:
            if supabase_client:
                result = supabase_client.table("projects").select("*").execute()
                projects = result.data
            else:
                projects = MOCK_PROJECTS
        except Exception as e:
            print(f"Error fetching projects: {str(e)}")
            projects = []
        
        return templates.TemplateResponse(
            "time_log_form.html",
            {
                "request": request,
                "session": session,
                "time_log": time_log,
                "projects": projects,
                "selected_project": next((p for p in projects if p["id"] == time_log["project_id"]), None),
                "mode": "edit"
            }
        )
        
    except Exception as e:
        print(f"Error in edit time log form route: {str(e)}")
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "session": session,
                "status_code": 500,
                "detail": f"Error loading time log form: {str(e)}"
            },
            status_code=500
        )

@app.post("/time-logs/{time_log_id}/edit", response_class=RedirectResponse)
async def update_time_log(
    request: Request,
    time_log_id: int,
    session: dict = Depends(get_session)
):
    """Handle updating an existing time log entry."""
    if not check_auth(session):
        return RedirectResponse(url="/login")
    
    try:
        form = await request.form()
        
        # Prepare update data
        update_data = {
            "project_id": int(form.get("project_id")),
            "date": form.get("date"),
            "hours": float(form.get("hours")),
            "task": form.get("task"),
            "description": form.get("description"),
            "billable": form.get("billable") == "true",
            "location": form.get("location", ""),
            "overtime": form.get("overtime") == "true",
            "break_time": float(form.get("break_time", 0)),
            "updated_at": datetime.now().isoformat(),
            "updated_by": session.get("user_id")
        }
        
        # Validate required fields
        required_fields = ["project_id", "date", "hours", "task"]
        for field in required_fields:
            if not update_data.get(field):
                return templates.TemplateResponse(
                    "time_log_form.html",
                    {
                        "request": request,
                        "session": session,
                        "time_log": {**update_data, "id": time_log_id},
                        "projects": MOCK_PROJECTS,
                        "mode": "edit",
                        "error": f"{field.replace('_', ' ').title()} is required"
                    }
                )
        
        # Update time log in Supabase or mock data
        supabase_client = get_supabase_client()
        if supabase_client:
            result = supabase_client.table("time_logs").update(update_data).eq("id", time_log_id).execute()
            if not result.data:
                raise Exception("Time log not found")
        
        return RedirectResponse(url=f"/time-logs/{time_log_id}", status_code=303)
        
    except Exception as e:
        print(f"Error updating time log: {str(e)}")
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "session": session,
                "status_code": 500,
                "detail": f"Error updating time log: {str(e)}"
            },
            status_code=500
        )

@app.post("/time-logs/{time_log_id}/delete", response_class=RedirectResponse)
async def delete_time_log(
    request: Request,
    time_log_id: int,
    session: dict = Depends(get_session)
):
    """Handle deletion of a time log entry."""
    if not check_auth(session):
        return RedirectResponse(url="/login")
    
    try:
        # Delete time log from Supabase or mock data
        supabase_client = get_supabase_client()
        if supabase_client:
            result = supabase_client.table("time_logs").delete().eq("id", time_log_id).execute()
            if not result.data:
                raise Exception("Time log not found")
        
        return RedirectResponse(url="/time-logs", status_code=303)
        
    except Exception as e:
        print(f"Error deleting time log: {str(e)}")
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "session": session,
                "status_code": 500,
                "detail": f"Error deleting time log: {str(e)}"
            },
            status_code=500
        )

@app.get("/expenses", response_class=HTMLResponse)
async def list_expenses(
    request: Request,
    session: dict = Depends(get_session),
    search: str = "",
    category: str = "",
    project_id: int = None,
    vendor_id: int = None,
    status: str = "",
    date_from: str = None,
    date_to: str = None,
    sort: str = "-date",
    page: int = 1
):
    """List expenses with filtering, sorting, and pagination."""
    if not check_auth(session):
        return RedirectResponse(url="/login")
        
    try:
        # Get Supabase client
        supabase_client = get_supabase_client()
        
        if supabase_client:
            # Build query
            query = supabase_client.table("expenses").select("*")
            
            # Apply filters
            if search:
                query = query.or_(f"description.ilike.%{search}%,vendor_name.ilike.%{search}%")
            if category:
                query = query.eq("category", category)
            if project_id:
                query = query.eq("project_id", project_id)
            if vendor_id:
                query = query.eq("vendor_id", vendor_id)
            if status:
                query = query.eq("status", status)
            if date_from:
                query = query.gte("date", date_from)
            if date_to:
                query = query.lte("date", date_to)
                
            # Apply sorting
            sort_column = sort[1:] if sort.startswith("-") else sort
            sort_order = "desc" if sort.startswith("-") else "asc"
            query = query.order(sort_column, desc=(sort_order == "desc"))
            
            # Execute query
            result = query.execute()
            expenses = result.data
        else:
            # Use mock data
            expenses = MOCK_EXPENSES
            
            # Apply filters to mock data
            if search:
                search = search.lower()
                expenses = [e for e in expenses if search in e["description"].lower() or search in e["vendor_name"].lower()]
            if category:
                expenses = [e for e in expenses if e["category"] == category]
            if project_id:
                expenses = [e for e in expenses if e["project_id"] == project_id]
            if vendor_id:
                expenses = [e for e in expenses if e["vendor_id"] == vendor_id]
            if status:
                expenses = [e for e in expenses if e["status"] == status]
            if date_from:
                expenses = [e for e in expenses if e["date"] >= date_from]
            if date_to:
                expenses = [e for e in expenses if e["date"] <= date_to]
                
            # Apply sorting to mock data
            reverse = sort.startswith("-")
            sort_key = sort[1:] if reverse else sort
            expenses = sorted(expenses, key=lambda x: x[sort_key], reverse=reverse)
        
        # Calculate pagination
        items_per_page = 10
        total_items = len(expenses)
        total_pages = (total_items + items_per_page - 1) // items_per_page
        
        # Ensure page is within valid range
        if page < 1:
            page = 1
        elif page > total_pages and total_pages > 0:
            page = total_pages
            
        # Get expenses for current page
        start_idx = (page - 1) * items_per_page
        end_idx = min(start_idx + items_per_page, total_items)
        paginated_expenses = expenses[start_idx:end_idx]
        
        # Calculate statistics
        total_amount = sum(e["amount"] for e in expenses)
        pending_amount = sum(e["amount"] for e in expenses if e["status"] == "pending")
        current_month = datetime.now().strftime("%Y-%m")
        month_amount = sum(e["amount"] for e in expenses if e["date"].startswith(current_month))
        
        # Get projects for filter dropdown
        if supabase_client:
            projects_result = supabase_client.table("projects").select("id,name").execute()
            projects = projects_result.data
        else:
            projects = MOCK_PROJECTS
            
        # Get vendors for filter dropdown
        if supabase_client:
            vendors_result = supabase_client.table("vendors").select("id,name").execute()
            vendors = vendors_result.data
        else:
            vendors = MOCK_VENDORS
            
        return templates.TemplateResponse(
            "expenses/list.html",
            {
                "request": request,
                "session": session,
                "expenses": paginated_expenses,
                "page": page,
                "total_pages": total_pages,
                "total_items": total_items,
                "search": search,
                "category": category,
                "project_id": project_id,
                "vendor_id": vendor_id,
                "status": status,
                "date_from": date_from,
                "date_to": date_to,
                "sort": sort,
                "categories": EXPENSE_CATEGORIES,
                "statuses": EXPENSE_STATUSES,
                "projects": projects,
                "vendors": vendors,
                "total_amount": total_amount,
                "pending_amount": pending_amount,
                "month_amount": month_amount
            }
        )
        
    except Exception as e:
        print(f"Error loading expenses: {str(e)}")
        traceback.print_exc()
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "session": session,
                "status_code": 500,
                "detail": "Error loading expenses"
            }
        )

@app.get("/expenses/{expense_id}", response_class=HTMLResponse)
async def expense_detail(
    request: Request,
    expense_id: int,
    session: dict = Depends(get_session)
):
    """View expense details."""
    if not check_auth(session):
        return RedirectResponse(url="/login")
        
    try:
        # Get Supabase client
        supabase_client = get_supabase_client()
        
        if supabase_client:
            # Get expense
            result = supabase_client.table("expenses").select("*").eq("id", expense_id).execute()
            expense = result.data[0] if result.data else None
        else:
            # Use mock data
            expense = next((e for e in MOCK_EXPENSES if e["id"] == expense_id), None)
            
        if not expense:
            return templates.TemplateResponse(
                "error.html",
                {
                    "request": request,
                    "session": session,
                    "status_code": 404,
                    "detail": f"Expense {expense_id} not found"
                }
            )
            
        return templates.TemplateResponse(
            "expenses/detail.html",
            {
                "request": request,
                "session": session,
                "expense": expense
            }
        )
        
    except Exception as e:
        print(f"Error loading expense {expense_id}: {str(e)}")
        traceback.print_exc()
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "session": session,
                "status_code": 500,
                "detail": f"Error loading expense {expense_id}"
            }
        )

@app.get("/expenses/new", response_class=HTMLResponse)
async def new_expense_form(
    request: Request,
    session: dict = Depends(get_session),
    project_id: int = None
):
    """Display form for creating a new expense."""
    if not check_auth(session):
        return RedirectResponse(url="/login")
        
    try:
        # Get Supabase client
        supabase_client = get_supabase_client()
        
        # Get projects for dropdown
        if supabase_client:
            projects_result = supabase_client.table("projects").select("id,name").execute()
            projects = projects_result.data
        else:
            projects = MOCK_PROJECTS
            
        # Get vendors for dropdown
        if supabase_client:
            vendors_result = supabase_client.table("vendors").select("id,name").execute()
            vendors = vendors_result.data
        else:
            vendors = MOCK_VENDORS
            
        return templates.TemplateResponse(
            "expenses/form.html",
            {
                "request": request,
                "session": session,
                "expense": {"project_id": project_id} if project_id else {},
                "projects": projects,
                "vendors": vendors,
                "categories": EXPENSE_CATEGORIES,
                "is_new": True
            }
        )
        
    except Exception as e:
        print(f"Error loading expense form: {str(e)}")
        traceback.print_exc()
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "session": session,
                "status_code": 500,
                "detail": "Error loading expense form"
            }
        )

@app.post("/expenses/new", response_class=RedirectResponse)
async def create_expense(
    request: Request,
    session: dict = Depends(get_session),
    date: str = Form(...),
    vendor_id: int = Form(...),
    project_id: int = Form(...),
    category: str = Form(...),
    description: str = Form(...),
    amount: float = Form(...),
    receipt: UploadFile = File(None)
):
    """Create a new expense."""
    if not check_auth(session):
        return RedirectResponse(url="/login")
        
    try:
        # Get Supabase client
        supabase_client = get_supabase_client()
        
        # Prepare expense data
        expense_data = {
            "date": date,
            "vendor_id": vendor_id,
            "project_id": project_id,
            "category": category,
            "description": description,
            "amount": amount,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        if receipt:
            # TODO: Implement file upload to storage
            expense_data["receipt_url"] = f"/static/uploads/receipts/{receipt.filename}"
            
        if supabase_client:
            # Create expense in Supabase
            result = supabase_client.table("expenses").insert(expense_data).execute()
            expense_id = result.data[0]["id"]
        else:
            # Use mock data
            expense_id = max(e["id"] for e in MOCK_EXPENSES) + 1
            expense_data["id"] = expense_id
            MOCK_EXPENSES.append(expense_data)
            
        return RedirectResponse(url=f"/expenses/{expense_id}", status_code=303)
        
    except Exception as e:
        print(f"Error creating expense: {str(e)}")
        traceback.print_exc()
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "session": session,
                "status_code": 500,
                "detail": "Error creating expense"
            }
        )

@app.get("/expenses/{expense_id}/edit", response_class=HTMLResponse)
async def edit_expense_form(
    request: Request,
    expense_id: int,
    session: dict = Depends(get_session)
):
    """Display form for editing an expense."""
    if not check_auth(session):
        return RedirectResponse(url="/login")
        
    try:
        # Get Supabase client
        supabase_client = get_supabase_client()
        
        # Get expense
        if supabase_client:
            result = supabase_client.table("expenses").select("*").eq("id", expense_id).execute()
            expense = result.data[0] if result.data else None
        else:
            expense = next((e for e in MOCK_EXPENSES if e["id"] == expense_id), None)
            
        if not expense:
            return templates.TemplateResponse(
                "error.html",
                {
                    "request": request,
                    "session": session,
                    "status_code": 404,
                    "detail": f"Expense {expense_id} not found"
                }
            )
            
        # Get projects for dropdown
        if supabase_client:
            projects_result = supabase_client.table("projects").select("id,name").execute()
            projects = projects_result.data
        else:
            projects = MOCK_PROJECTS
            
        # Get vendors for dropdown
        if supabase_client:
            vendors_result = supabase_client.table("vendors").select("id,name").execute()
            vendors = vendors_result.data
        else:
            vendors = MOCK_VENDORS
            
        return templates.TemplateResponse(
            "expenses/form.html",
            {
                "request": request,
                "session": session,
                "expense": expense,
                "projects": projects,
                "vendors": vendors,
                "categories": EXPENSE_CATEGORIES,
                "is_new": False
            }
        )
        
    except Exception as e:
        print(f"Error loading expense form: {str(e)}")
        traceback.print_exc()
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "session": session,
                "status_code": 500,
                "detail": "Error loading expense form"
            }
        )

@app.post("/expenses/{expense_id}/edit", response_class=RedirectResponse)
async def update_expense(
    request: Request,
    expense_id: int,
    session: dict = Depends(get_session),
    date: str = Form(...),
    vendor_id: int = Form(...),
    project_id: int = Form(...),
    category: str = Form(...),
    description: str = Form(...),
    amount: float = Form(...),
    status: str = Form(...),
    receipt: UploadFile = File(None)
):
    """Update an existing expense."""
    if not check_auth(session):
        return RedirectResponse(url="/login")
        
    try:
        # Get Supabase client
        supabase_client = get_supabase_client()
        
        # Prepare update data
        update_data = {
            "date": date,
            "vendor_id": vendor_id,
            "project_id": project_id,
            "category": category,
            "description": description,
            "amount": amount,
            "status": status,
            "updated_at": datetime.now().isoformat()
        }
        
        if receipt:
            # TODO: Implement file upload to storage
            update_data["receipt_url"] = f"/static/uploads/receipts/{receipt.filename}"
            
        if supabase_client:
            # Update expense in Supabase
            result = supabase_client.table("expenses").update(update_data).eq("id", expense_id).execute()
        else:
            # Update mock data
            expense_idx = next((i for i, e in enumerate(MOCK_EXPENSES) if e["id"] == expense_id), None)
            if expense_idx is not None:
                MOCK_EXPENSES[expense_idx].update(update_data)
            
        return RedirectResponse(url=f"/expenses/{expense_id}", status_code=303)
        
    except Exception as e:
        print(f"Error updating expense: {str(e)}")
        traceback.print_exc()
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "session": session,
                "status_code": 500,
                "detail": "Error updating expense"
            }
        )

@app.post("/expenses/{expense_id}/delete", response_class=RedirectResponse)
async def delete_expense(
    request: Request,
    expense_id: int,
    session: dict = Depends(get_session)
):
    """Delete an expense."""
    if not check_auth(session):
        return RedirectResponse(url="/login")
        
    try:
        # Get Supabase client
        supabase_client = get_supabase_client()
        
        if supabase_client:
            # Delete expense from Supabase
            result = supabase_client.table("expenses").delete().eq("id", expense_id).execute()
        else:
            # Delete from mock data
            global MOCK_EXPENSES
            MOCK_EXPENSES = [e for e in MOCK_EXPENSES if e["id"] != expense_id]
            
        return RedirectResponse(url="/expenses", status_code=303)
        
    except Exception as e:
        print(f"Error deleting expense: {str(e)}")
        traceback.print_exc()
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "session": session,
                "status_code": 500,
                "detail": "Error deleting expense"
            }
        )

# Vendors routes
@app.get("/vendors", response_class=HTMLResponse)
async def list_vendors(
    request: Request,
    session: dict = Depends(get_session),
    search: str = "",
    material_category: str = "",
    status: str = "",
    preferred_only: bool = False,
    sort: str = "name",
    page: int = 1
):
    """List vendors with filtering, sorting, and pagination."""
    if not check_auth(session):
        return RedirectResponse(url="/login")
        
    try:
        # Get Supabase client
        supabase_client = get_supabase_client()
        
        if supabase_client:
            # Build query
            query = supabase_client.table("vendors").select("*")
            
            # Apply filters
            if search:
                query = query.or_(f"name.ilike.%{search}%,contact_name.ilike.%{search}%,email.ilike.%{search}%")
            if material_category:
                query = query.eq("material_category", material_category)
            if status:
                query = query.eq("status", status)
            if preferred_only:
                query = query.eq("preferred", True)
                
            # Apply sorting
            sort_column = sort[1:] if sort.startswith("-") else sort
            sort_order = "desc" if sort.startswith("-") else "asc"
            query = query.order(sort_column, desc=(sort_order == "desc"))
            
            # Execute query
            result = query.execute()
            vendors = result.data
        else:
            # Use mock data
            vendors = MOCK_VENDORS
            
            # Apply filters to mock data
            if search:
                search = search.lower()
                vendors = [v for v in vendors if 
                    search in v["name"].lower() or 
                    search in v["contact_name"].lower() or 
                    search in v["email"].lower()]
            if material_category:
                vendors = [v for v in vendors if v["material_category"] == material_category]
            if status:
                vendors = [v for v in vendors if v["status"] == status]
            if preferred_only:
                vendors = [v for v in vendors if v["preferred"]]
                
            # Apply sorting to mock data
            reverse = sort.startswith("-")
            sort_key = sort[1:] if reverse else sort
            vendors = sorted(vendors, key=lambda x: x[sort_key], reverse=reverse)
        
        # Calculate pagination
        items_per_page = 10
        total_items = len(vendors)
        total_pages = (total_items + items_per_page - 1) // items_per_page
        
        # Ensure page is within valid range
        if page < 1:
            page = 1
        elif page > total_pages and total_pages > 0:
            page = total_pages
            
        # Get vendors for current page
        start_idx = (page - 1) * items_per_page
        end_idx = min(start_idx + items_per_page, total_items)
        paginated_vendors = vendors[start_idx:end_idx]
        
        # Calculate statistics
        total_vendors = len(vendors)
        active_vendors = len([v for v in vendors if v["status"] == "active"])
        preferred_vendors = len([v for v in vendors if v["preferred"]])
        high_rated_vendors = len([v for v in vendors if v["rating"] >= 4])
        
        return templates.TemplateResponse(
            "vendors/list.html",
            {
                "request": request,
                "session": session,
                "vendors": paginated_vendors,
                "page": page,
                "total_pages": total_pages,
                "total_items": total_items,
                "search": search,
                "material_category": material_category,
                "status": status,
                "preferred_only": preferred_only,
                "sort": sort,
                "categories": VENDOR_CATEGORIES,
                "statuses": VENDOR_STATUSES,
                "total_vendors": total_vendors,
                "active_vendors": active_vendors,
                "preferred_vendors": preferred_vendors,
                "high_rated_vendors": high_rated_vendors
            }
        )
        
    except Exception as e:
        print(f"Error loading vendors: {str(e)}")
        traceback.print_exc()
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "session": session,
                "status_code": 500,
                "detail": "Error loading vendors"
            }
        )

@app.get("/vendors/{vendor_id}", response_class=HTMLResponse)
async def vendor_detail(
    request: Request,
    vendor_id: int,
    session: dict = Depends(get_session)
):
    """View vendor details."""
    if not check_auth(session):
        return RedirectResponse(url="/login")
        
    try:
        # Get Supabase client
        supabase_client = get_supabase_client()
        
        if supabase_client:
            # Get vendor
            result = supabase_client.table("vendors").select("*").eq("id", vendor_id).execute()
            vendor = result.data[0] if result.data else None
            
            # Get recent expenses for this vendor
            expenses_result = supabase_client.table("expenses").select("*").eq("vendor_id", vendor_id).order("date", desc=True).limit(5).execute()
            recent_expenses = expenses_result.data
        else:
            # Use mock data
            vendor = next((v for v in MOCK_VENDORS if v["id"] == vendor_id), None)
            recent_expenses = [e for e in MOCK_EXPENSES if e["vendor_id"] == vendor_id][:5]
            
        if not vendor:
            return templates.TemplateResponse(
                "error.html",
                {
                    "request": request,
                    "session": session,
                    "status_code": 404,
                    "detail": f"Vendor {vendor_id} not found"
                }
            )
            
        return templates.TemplateResponse(
            "vendors/detail.html",
            {
                "request": request,
                "session": session,
                "vendor": vendor,
                "recent_expenses": recent_expenses
            }
        )
        
    except Exception as e:
        print(f"Error loading vendor {vendor_id}: {str(e)}")
        traceback.print_exc()
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "session": session,
                "status_code": 500,
                "detail": f"Error loading vendor {vendor_id}"
            }
        )