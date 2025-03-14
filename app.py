"""
Simple FastAPI Application with Supabase Integration

This is a simple FastAPI application that integrates with Supabase.
"""

import os
import traceback
from fastapi import FastAPI, HTTPException, Request, Depends, Form, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from starlette.middleware.sessions import SessionMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from datetime import datetime, timedelta
from supabase import create_client, Client
from typing import Optional, List

# Initialize Supabase client
def get_supabase_client() -> Optional[Client]:
    """Get Supabase client initialized with environment variables.
    Returns None if environment variables are not set or initialization fails.
    """
    try:
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            print("Warning: Supabase environment variables not found, using mock data")
            return None
            
        return create_client(supabase_url, supabase_key)
    except Exception as e:
        print(f"Error initializing Supabase client: {e}")
        traceback.print_exc()
        return None

# Google Maps API configuration
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")

# Mock data for when Supabase is unavailable
MOCK_ACTIVITY = [
    {"id": 1, "type": "vendor_added", "description": "New vendor 'ABC Supply' added", "created_at": "2025-03-14T10:00:00Z"},
    {"id": 2, "type": "project_updated", "description": "Project 'Office Renovation' status updated to 'In Progress'", "created_at": "2025-03-14T09:30:00Z"},
    {"id": 3, "type": "expense_approved", "description": "Expense #1234 approved for $1,500", "created_at": "2025-03-14T09:00:00Z"},
    {"id": 4, "type": "time_log_added", "description": "8 hours logged for 'Electrical Work'", "created_at": "2025-03-14T08:30:00Z"},
    {"id": 5, "type": "material_ordered", "description": "Order placed for lumber materials", "created_at": "2025-03-14T08:00:00Z"}
]

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
app.add_middleware(SessionMiddleware, secret_key=os.getenv("FLASK_SECRET_KEY", "your-secret-key"))

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Add custom template functions
def url_for(name, filename=None, **kwargs):
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
        "edit_time_log": "/time-logs/{}/edit",
        "time_summary_report": "/reports/time-summary",
        
        # Expenses
        "new_expense": "/expenses/new",
        "edit_expense": "/expenses/{}/edit",
        "expense_detail": "/expenses/{}",
        "expense_summary_report": "/reports/expense-summary",
        
        # Projects
        "new_project": "/projects/new",
        "edit_project": "/projects/{}/edit",
        "project_detail": "/projects/{}",
        
        # Contacts
        "new_contact": "/contacts/new",
        "contact_detail": "/contacts/{}",
        "edit_contact": "/contacts/{}/edit",
        
        # Customers
        "customers": "/customers",
        "new_customer": "/customers/new",
        "customer_detail": "/customers/{}",
        "edit_customer": "/customers/{}/edit",
        "delete_customer": "/customers/{}/delete",
        
        # Vendors
        "vendor_detail": "/vendors/{}",
        "edit_vendor": "/vendors/{}/edit",
        "new_vendor": "/vendors/new",
        "delete_vendor": "/vendors/{}/delete",
        
        # Invoices
        "invoices": "/invoices",
        "edit_invoice": "/invoices/{}/edit",
        "new_invoice": "/invoices/new",
        "invoice_detail": "/invoices/{}",
        "create_invoice": "/invoices/create",
        "update_invoice": "/invoices/{}/update",
        "delete_invoice": "/invoices/{}/delete",
        "send_invoice": "/invoices/{}/send",
        "record_payment": "/invoices/{}/payment",
        "cancel_invoice": "/invoices/{}/cancel",
        "project_invoices": "/projects/{}/invoices",
        
        # Other
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
templates.env.globals["url_for"] = url_for
templates.env.globals["get_flashed_messages"] = lambda with_categories=False: []
templates.env.globals["google_maps_api_key"] = GOOGLE_MAPS_API_KEY

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

# Initialize database tables if they don't exist
supabase = get_supabase_client()
if supabase:
    try:
        # Create purchases table if it doesn't exist
        supabase.table("purchases").select("*").limit(1).execute()
    except:
        supabase.table("purchases").create({
            "id": "uuid",
            "vendor_id": "uuid",
            "project_id": "uuid",
            "description": "text",
            "amount": "numeric",
            "date": "date",
            "category": "text",
            "status": "text",
            "invoice_number": "text",
            "receipt_url": "text",
            "notes": "text",
            "created_at": "timestamp with time zone",
            "updated_at": "timestamp with time zone",
            "created_by": "uuid",
            "updated_by": "uuid"
        }).execute()

# Authentication check middleware
def check_auth(session: dict):
    if not session.get("user_id"):
        return False
    return True

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
async def contacts(request: Request, session: dict = Depends(get_session), page: int = 1, search_query: str = None):
    if not check_auth(session):
        return RedirectResponse(url="/login")
    
    # Mock data for contacts
    mock_contacts = [
        {"id": 1, "name": "John Smith", "company": "ABC Corp", "email": "john.smith@abccorp.com", "phone": "(555) 123-4567", "type": "Client", "type_color": "primary"},
        {"id": 2, "name": "Jane Doe", "company": "XYZ Industries", "email": "jane.doe@xyzindustries.com", "phone": "(555) 987-6543", "type": "Client", "type_color": "primary"},
        {"id": 3, "name": "Bob Johnson", "company": "123 Retail", "email": "bob.johnson@123retail.com", "phone": "(555) 456-7890", "type": "Client", "type_color": "primary"},
        {"id": 4, "name": "Alice Williams", "company": "DEF Corp", "email": "alice.williams@defcorp.com", "phone": "(555) 234-5678", "type": "Client", "type_color": "primary"},
        {"id": 5, "name": "Charlie Brown", "company": "Gourmet Foods", "email": "charlie.brown@gourmetfoods.com", "phone": "(555) 876-5432", "type": "Client", "type_color": "primary"},
        {"id": 6, "name": "David Miller", "company": "Electrical Services", "email": "david.miller@electrical.com", "phone": "(555) 345-6789", "type": "Vendor", "type_color": "success"},
        {"id": 7, "name": "Eva Garcia", "company": "Plumbing Co", "email": "eva.garcia@plumbing.com", "phone": "(555) 654-3210", "type": "Vendor", "type_color": "success"},
        {"id": 8, "name": "Frank Wilson", "company": "HVAC Solutions", "email": "frank.wilson@hvac.com", "phone": "(555) 765-4321", "type": "Vendor", "type_color": "success"},
    ]
    
    # Pagination variables
    items_per_page = 10
    total_items = len(mock_contacts)
    total_pages = (total_items + items_per_page - 1) // items_per_page  # Ceiling division
    
    # Ensure page is within valid range
    if page < 1:
        page = 1
    elif page > total_pages and total_pages > 0:
        page = total_pages
    
    # Calculate pagination indices
    start_idx = (page - 1) * items_per_page
    end_idx = min(start_idx + items_per_page, total_items)
    
    # Get contacts for current page
    paginated_contacts = mock_contacts[start_idx:end_idx]
    
    # Prepare context with pagination data
    context = {
        "request": request, 
        "session": request.session,
        "contacts": paginated_contacts,
        "page": page,
        "total_pages": total_pages,
        "search_query": search_query or "",
        "contact_types": ["All", "Client", "Vendor", "Subcontractor", "Employee"]
    }
    
    return templates.TemplateResponse("contacts.html", context)

@app.get("/contacts/new", response_class=HTMLResponse)
async def new_contact(request: Request, session: dict = Depends(get_session)):
    if not check_auth(session):
        return RedirectResponse(url="/login")
    return templates.TemplateResponse("contact_form.html", {"request": request, "session": request.session})

@app.get("/contacts/{contact_id}", response_class=HTMLResponse)
async def contact_detail(contact_id: int, request: Request, session: dict = Depends(get_session)):
    if not check_auth(session):
        return RedirectResponse(url="/login")
    
    # Mock data for contacts
    mock_contacts = [
        {"id": 1, "name": "John Smith", "company": "ABC Corp", "email": "john.smith@abccorp.com", "phone": "(555) 123-4567", "type": "Client", "type_color": "primary", "address": "123 Main St, Anytown, USA", "notes": "Key decision maker for office renovation project", "created_at": "2025-01-15", "last_contact": "2025-03-01"},
        {"id": 2, "name": "Jane Doe", "company": "XYZ Industries", "email": "jane.doe@xyzindustries.com", "phone": "(555) 987-6543", "type": "Client", "type_color": "primary", "address": "456 Oak Ave, Somewhere, USA", "notes": "Prefers email communication", "created_at": "2025-01-20", "last_contact": "2025-02-28"},
        {"id": 3, "name": "Bob Johnson", "company": "123 Retail", "email": "bob.johnson@123retail.com", "phone": "(555) 456-7890", "type": "Client", "type_color": "primary", "address": "789 Pine Rd, Elsewhere, USA", "notes": "Interested in retail store remodeling", "created_at": "2025-02-01", "last_contact": "2025-03-05"},
        {"id": 4, "name": "Alice Williams", "company": "DEF Corp", "email": "alice.williams@defcorp.com", "phone": "(555) 234-5678", "type": "Client", "type_color": "primary", "address": "321 Elm St, Nowhere, USA", "notes": "Referred by John Smith", "created_at": "2025-02-10", "last_contact": "2025-03-02"},
        {"id": 5, "name": "Charlie Brown", "company": "Gourmet Foods", "email": "charlie.brown@gourmetfoods.com", "phone": "(555) 876-5432", "type": "Client", "type_color": "primary", "address": "654 Maple Dr, Anywhere, USA", "notes": "Restaurant renovation project", "created_at": "2025-02-15", "last_contact": "2025-03-10"},
    ]
    
    # Find the contact with the matching ID
    contact = next((c for c in mock_contacts if c["id"] == contact_id), None)
    
    # If contact not found, return 404
    if not contact:
        return templates.TemplateResponse(
            "error.html", 
            {"request": request, "session": request.session, "status_code": 404, "detail": f"Contact with ID {contact_id} not found"}
        )
    
    # Mock projects associated with this contact
    associated_projects = [
        {"id": 1, "name": "Office Renovation", "status": "In Progress", "status_color": "success", "start_date": "2025-01-15", "end_date": "2025-03-30", "budget": 75000.00, "spent": 45000.00}
    ] if contact_id == 1 else []
    
    # Mock recent activities
    recent_activities = [
        {"date": "2025-03-01", "type": "Call", "description": "Discussed project timeline", "user": "Admin"},
        {"date": "2025-02-15", "type": "Email", "description": "Sent proposal", "user": "Admin"},
        {"date": "2025-02-01", "type": "Meeting", "description": "Initial consultation", "user": "Admin"}
    ] if contact_id <= 3 else [
        {"date": "2025-03-02", "type": "Email", "description": "Introduction", "user": "Admin"},
        {"date": "2025-02-20", "type": "Call", "description": "Discussed needs", "user": "Admin"}
    ]
    
    # Prepare context with contact data
    context = {
        "request": request, 
        "session": request.session,
        "contact": contact,
        "associated_projects": associated_projects,
        "recent_activities": recent_activities
    }
    
    return templates.TemplateResponse("contact_detail.html", context)

@app.get("/projects", response_class=HTMLResponse)
async def projects(
    request: Request, 
    session: dict = Depends(get_session),
    search: str = None,
    status: str = None,
    sort: str = None,
    page: int = 1
):
    if not check_auth(session):
        return RedirectResponse(url="/login")
    
    # Use global MOCK_PROJECTS data instead of inline mock data
    projects_data = MOCK_PROJECTS.copy()
    
    # Apply filters
    if search:
        projects_data = [p for p in projects_data if search.lower() in p["name"].lower() or search.lower() in p["client_name"].lower()]
    
    if status:
        projects_data = [p for p in projects_data if p["status"].lower() == status.lower()]
    
    # Apply sorting
    if sort:
        reverse = False
        if sort.startswith('-'):
            sort = sort[1:]
            reverse = True
        
        if sort == 'name':
            projects_data = sorted(projects_data, key=lambda p: p["name"], reverse=reverse)
        elif sort == 'client':
            projects_data = sorted(projects_data, key=lambda p: p["client_name"], reverse=reverse)
        elif sort == 'date':
            projects_data = sorted(projects_data, key=lambda p: p["start_date"], reverse=reverse)
        elif sort == 'budget':
            projects_data = sorted(projects_data, key=lambda p: p["budget"], reverse=reverse)
        elif sort == 'progress':
            projects_data = sorted(projects_data, key=lambda p: p["progress"], reverse=reverse)
    
    # Pagination variables
    items_per_page = 10
    total_items = len(projects_data)
    total_pages = (total_items + items_per_page - 1) // items_per_page  # Ceiling division
    
    # Ensure page is within valid range
    if page < 1:
        page = 1
    elif page > total_pages and total_pages > 0:
        page = total_pages
    
    # Calculate pagination indices
    start_idx = (page - 1) * items_per_page
    end_idx = min(start_idx + items_per_page, total_items)
    
    # Get paginated projects
    paginated_projects = projects_data[start_idx:end_idx]
    
    # Get available statuses for filter dropdown
    statuses = ["Planning", "In Progress", "On Hold", "Completed", "Cancelled"]
    
    return templates.TemplateResponse(
        "projects.html",
        {
            "request": request, 
            "projects": paginated_projects,
            "page": page,
            "total_pages": total_pages,
            "total_items": total_items,
            "search_query": search or "",
            "current_status": status or "All",
            "statuses": statuses
        }
    )

@app.get("/projects/{project_id}", response_class=HTMLResponse)
async def project_detail(
    request: Request, 
    project_id: int,
    session: dict = Depends(get_session)
):
    if not check_auth(session):
        return RedirectResponse(url="/login")
    
    # Use global MOCK_PROJECTS data
    # Find the project with the matching ID
    project = next((p for p in MOCK_PROJECTS if p["id"] == project_id), None)
    
    # If project not found, return 404
    if not project:
        return templates.TemplateResponse(
            "error.html", 
            {"request": request, "status_code": 404, "detail": f"Project with ID {project_id} not found"}
        )
    
    # Prepare context with project data
    context = {
        "request": request,
        "project": project,
    }
    
    return templates.TemplateResponse("project_detail.html", context)

@app.get("/projects/new", response_class=HTMLResponse)
async def new_project(
    request: Request, 
    session: dict = Depends(get_session), 
    customer_id: int = None
):
    if not check_auth(session):
        return RedirectResponse(url="/login")
    
    # Get all customers for the dropdown
    customers = MOCK_CUSTOMERS
    
    # Create an empty project object for the form
    project = {
        "id": None,
        "name": "",
        "client_id": customer_id,
        "client_name": "",
        "status": "Planning",
        "status_color": "info",
        "start_date": "",
        "end_date": "",
        "budget": 0.0,
        "spent": 0.0,
        "remaining": 0.0,
        "description": "",
        "manager": "",
        "team": [],
        "progress": 0
    }
    
    # If customer_id is provided, pre-select that customer and set client_name
    if customer_id:
        customer = next((c for c in customers if c["id"] == customer_id), None)
        if customer:
            project["client_name"] = customer["name"]
    
    return templates.TemplateResponse(
        "project_form.html", 
        {"request": request, "project": project, "customers": customers, "mode": "new"}
    )

@app.post("/projects/new", response_class=HTMLResponse)
async def new_project_post(
    request: Request,
    session: dict = Depends(get_session),
    project_name: str = Form(...),
    client_id: int = Form(...),
    status: str = Form(...),
    budget: float = Form(...),
    start_date: str = Form(...),
    end_date: str = Form(...),
    description: str = Form(None),
    manager: str = Form(None)
):
    if not check_auth(session):
        return RedirectResponse(url="/login")
    
    # In a real application, you would save the project to the database
    # For this mock application, we'll just redirect to the projects list
    
    # Redirect to projects page with success message
    return RedirectResponse(url="/projects", status_code=303)

@app.get("/projects/{project_id}/edit", response_class=HTMLResponse)
async def edit_project(
    request: Request, 
    project_id: int,
    session: dict = Depends(get_session)
):
    if not check_auth(session):
        return RedirectResponse(url="/login")
    
    # Use global MOCK_PROJECTS data
    # Find the project with the matching ID
    project = next((p for p in MOCK_PROJECTS if p["id"] == project_id), None)
    
    # If project not found, return 404
    if not project:
        return templates.TemplateResponse(
            "error.html", 
            {"request": request, "status_code": 404, "detail": f"Project with ID {project_id} not found"}
        )
    
    # Get all customers for the dropdown
    customers = MOCK_CUSTOMERS
    
    return templates.TemplateResponse(
        "project_form.html", 
        {"request": request, "project": project, "customers": customers, "mode": "edit"}
    )

@app.post("/projects/{project_id}/edit", response_class=HTMLResponse)
async def edit_project_post(
    project_id: int,
    request: Request,
    session: dict = Depends(get_session),
    project_name: str = Form(...),
    client_id: int = Form(...),
    status: str = Form(...),
    budget: float = Form(...),
    start_date: str = Form(...),
    end_date: str = Form(...),
    description: str = Form(None),
    manager: str = Form(None)
):
    if not check_auth(session):
        return RedirectResponse(url="/login")
    
    # In a real application, you would update the project in the database
    # For this mock application, we'll just redirect to the project detail page
    
    # Redirect to project detail page with success message
    return RedirectResponse(url=f"/projects/{project_id}", status_code=303)

@app.get("/time-logs", response_class=HTMLResponse)
async def time_logs(
    request: Request, 
    session: dict = Depends(get_session), 
    page: int = 1, 
    search_query: str = None, 
    status_filter: str = None, 
    project_filter: int = None
):
    if not check_auth(session):
        return RedirectResponse(url="/login")
    
    # Use global MOCK_TIME_LOGS data
    time_logs_data = MOCK_TIME_LOGS.copy()
    
    # Apply filters
    if search_query:
        time_logs_data = [log for log in time_logs_data if 
                         search_query.lower() in log["project_name"].lower() or 
                         search_query.lower() in log["task_name"].lower() or 
                         search_query.lower() in log["description"].lower()]
    
    if status_filter:
        time_logs_data = [log for log in time_logs_data if log["status"].lower() == status_filter.lower()]
    
    if project_filter:
        time_logs_data = [log for log in time_logs_data if log["project_id"] == project_filter]
    
    # Pagination variables
    items_per_page = 10
    total_items = len(time_logs_data)
    total_pages = (total_items + items_per_page - 1) // items_per_page  # Ceiling division
    
    # Ensure page is within valid range
    if page < 1:
        page = 1
    elif page > total_pages and total_pages > 0:
        page = total_pages
    
    # Calculate pagination indices
    start_idx = (page - 1) * items_per_page
    end_idx = min(start_idx + items_per_page, total_items)
    
    # Get paginated time logs
    paginated_time_logs = time_logs_data[start_idx:end_idx]
    
    # Get projects for filter dropdown
    projects = [(p["id"], p["name"]) for p in MOCK_PROJECTS]
    
    # Get statuses for filter dropdown
    statuses = ["Approved", "Pending", "Draft", "Rejected"]
    
    # Calculate summary statistics
    total_hours = sum(log["hours"] for log in time_logs_data)
    billable_hours = sum(log["hours"] for log in time_logs_data if log["billable"])
    pending_hours = sum(log["hours"] for log in time_logs_data if log["status"] == "Pending")
    
    return templates.TemplateResponse(
        "time_logs.html", 
        {
            "request": request,
            "time_logs": paginated_time_logs,
            "page": page,
            "total_pages": total_pages,
            "total_items": total_items,
            "search_query": search_query or "",
            "status_filter": status_filter or "",
            "project_filter": project_filter or "",
            "projects": projects,
            "statuses": statuses,
            "total_hours": total_hours,
            "billable_hours": billable_hours,
            "pending_hours": pending_hours
        }
    )

@app.get("/time-logs/new", response_class=HTMLResponse)
async def new_time_log(
    request: Request, 
    session: dict = Depends(get_session), 
    project_id: int = None
):
    if not check_auth(session):
        return RedirectResponse(url="/login")
    
    # Get projects from MOCK_PROJECTS for selection
    projects = [(p["id"], p["name"]) for p in MOCK_PROJECTS]
    
    # Mock tasks for the selected project
    project_tasks = []
    selected_project = None
    
    if project_id:
        # Find the selected project from MOCK_PROJECTS
        selected_project = next((p for p in MOCK_PROJECTS if p["id"] == project_id), None)
        
        if selected_project:
            # In a real app, we would fetch tasks for the selected project from the database
            # For now, use mock tasks based on the project's tasks array if available
            if "tasks" in selected_project and selected_project["tasks"]:
                project_tasks = [(task["id"], task["name"]) for task in selected_project["tasks"]]
            else:
                # Fallback mock tasks
                if project_id == 1:  # Office Renovation
                    project_tasks = [(101, "Electrical Work"), (102, "Plumbing"), (103, "Painting")]
                elif project_id == 4:  # Warehouse Expansion
                    project_tasks = [(401, "Planning"), (402, "Foundation"), (403, "Framing")]
                elif project_id == 3:  # Mobile App Development
                    project_tasks = [(301, "Frontend Development"), (302, "Backend Integration"), (303, "Testing")]
    
    return templates.TemplateResponse(
        "time_log_form.html", 
        {
            "request": request,
            "projects": projects,
            "project_tasks": project_tasks,
            "selected_project": selected_project,
            "time_log": None
        }
    )

@app.post("/time-logs/new", response_class=HTMLResponse)
async def create_time_log(
    request: Request,
    session: dict = Depends(get_session),
    project_id: int = Form(...),
    task_id: int = Form(...),
    date: str = Form(...),
    hours: float = Form(...),
    description: str = Form(...),
    billable: bool = Form(False),
    status: str = Form("Pending")
):
    if not check_auth(session):
        return RedirectResponse(url="/login")
    
    # In a real app, we would save the time log to the database
    # For this demo, we'll just redirect to the time logs list
    
    # Add a success message
    request.session["flash_messages"] = [
        {"type": "success", "message": "Time log created successfully."}
    ]
    
    return RedirectResponse(url="/time-logs", status_code=303)

@app.get("/time-logs/{log_id}/edit", response_class=HTMLResponse)
async def edit_time_log(request: Request, log_id: int, session: dict = Depends(get_session), project_id: int = None):
    if not check_auth(session):
        return RedirectResponse(url="/login")
    
    # Find the time log in MOCK_TIME_LOGS
    time_log = next((log for log in MOCK_TIME_LOGS if log["id"] == log_id), None)
    
    # If time log not found, return 404
    if not time_log:
        return templates.TemplateResponse(
            "error.html", 
            {"request": request, "status_code": 404, "detail": f"Time log with ID {log_id} not found"}
        )
    
    # Get projects from MOCK_PROJECTS for selection
    projects = [(p["id"], p["name"]) for p in MOCK_PROJECTS]
    
    # Use project_id from query param if provided, otherwise use the time log's project_id
    project_id = project_id if project_id else time_log["project_id"]
    
    # Find the project for this time log
    project = next((p for p in MOCK_PROJECTS if p["id"] == project_id), None)
    
    # Get tasks for the project
    project_tasks = []
    if project and "tasks" in project and project["tasks"]:
        project_tasks = [(task["id"], task["name"]) for task in project["tasks"]]
    else:
        # Fallback mock tasks
        if project_id == 1:  # Office Renovation
            project_tasks = [(101, "Electrical Work"), (102, "Plumbing"), (103, "Painting")]
        elif project_id == 4:  # Warehouse Expansion
            project_tasks = [(401, "Planning"), (402, "Foundation"), (403, "Framing")]
        elif project_id == 3:  # Mobile App Development
            project_tasks = [(301, "Frontend Development"), (302, "Backend Integration"), (303, "Testing")]
    
    return templates.TemplateResponse(
        "time_log_form.html", 
        {
            "request": request,
            "time_log": time_log,
            "projects": projects,
            "project_tasks": project_tasks,
            "selected_project": project
        }
    )

@app.post("/time-logs/{log_id}/edit", response_class=HTMLResponse)
async def update_time_log(
    request: Request, 
    log_id: int, 
    session: dict = Depends(get_session), 
    project_id: int = Form(...),
    task_id: int = Form(...),
    date: str = Form(...),
    hours: float = Form(...),
    description: str = Form(...),
    billable: bool = Form(False),
    status: str = Form("Pending")
):
    if not check_auth(session):
        return RedirectResponse(url="/login")
    
    # In a real app, we would update the time log in the database
    # For this demo, we'll just redirect to the time logs list
    
    # Add a success message
    request.session["flash_messages"] = [
        {"type": "success", "message": f"Time log #{log_id} updated successfully."}
    ]
    
    return RedirectResponse(url="/time-logs", status_code=303)

@app.get("/projects/{project_id}/time-logs", response_class=HTMLResponse)
async def project_time_logs(
    request: Request, 
    project_id: int, 
    session: dict = Depends(get_session)
):
    if not check_auth(session):
        return RedirectResponse(url="/login")
    
    # Use global MOCK_PROJECTS data
    # Find the project with the matching ID
    project = next((p for p in MOCK_PROJECTS if p["id"] == project_id), None)
    
    # If project not found, return 404
    if not project:
        return templates.TemplateResponse(
            "error.html", 
            {"request": request, "status_code": 404, "detail": f"Project with ID {project_id} not found"}
        )
    
    # Filter time logs by project
    project_time_logs = [log for log in MOCK_TIME_LOGS if log["project_id"] == project_id]
    
    # Available statuses for filtering
    statuses = ["Pending", "Approved", "Rejected"]
    
    # Prepare context
    context = {
        "request": request,
        "project": project,
        "time_logs": project_time_logs,
        "statuses": statuses,
        "total_hours": sum(log["hours"] for log in project_time_logs),
        "billable_hours": sum(log["hours"] for log in project_time_logs if log["billable"]),
        "pending_hours": sum(log["hours"] for log in project_time_logs if log["status"] == "Pending")
    }
    
    return templates.TemplateResponse("time_logs.html", context)

@app.get("/reports/time-summary", response_class=HTMLResponse)
async def time_summary_report(
    request: Request, 
    session: dict = Depends(get_session),
    date_from: str = None,
    date_to: str = None,
    project_id: int = None,
    group_by: str = "project"
):
    if not check_auth(session):
        return RedirectResponse(url="/login")
    
    # Mock projects for filter
    projects = [
        (1, "Office Renovation"),
        (2, "Warehouse Expansion"),
        (3, "Retail Store Remodel")
    ]
    
    # Mock time log data for report
    mock_time_logs = [
        {"id": 1, "date": "2025-03-01", "project_id": 1, "project_name": "Office Renovation", 
         "task_id": 1, "task_name": "Electrical Work", "user_id": 1, "user_name": "Admin", 
         "hours": 4.5, "billable": True, "status": "Approved"},
        {"id": 2, "date": "2025-03-02", "project_id": 2, "project_name": "Warehouse Expansion", 
         "task_id": 4, "task_name": "Planning", "user_id": 1, "user_name": "Admin", 
         "hours": 2.0, "billable": True, "status": "Approved"},
        {"id": 3, "date": "2025-03-03", "project_id": 1, "project_name": "Office Renovation", 
         "task_id": 2, "task_name": "Plumbing", "user_id": 1, "user_name": "Admin", 
         "hours": 6.0, "billable": True, "status": "Pending"},
        {"id": 4, "date": "2025-03-04", "project_id": 3, "project_name": "Retail Store Remodel", 
         "task_id": 7, "task_name": "Demolition", "user_id": 2, "user_name": "Jane Smith", 
         "hours": 8.0, "billable": True, "status": "Pending"},
        {"id": 5, "date": "2025-03-05", "project_id": 1, "project_name": "Office Renovation", 
         "task_id": 3, "task_name": "Painting", "user_id": 2, "user_name": "Jane Smith", 
         "hours": 7.5, "billable": True, "status": "Pending"},
        {"id": 6, "date": "2025-03-06", "project_id": 2, "project_name": "Warehouse Expansion", 
         "task_id": 5, "task_name": "Foundation", "user_id": 3, "user_name": "Bob Johnson", 
         "hours": 8.0, "billable": True, "status": "Pending"},
        {"id": 7, "date": "2025-03-07", "project_id": 3, "project_name": "Retail Store Remodel", 
         "task_id": 8, "task_name": "Electrical Work", "user_id": 3, "user_name": "Bob Johnson", 
         "hours": 5.0, "billable": False, "status": "Draft"},
    ]
    
    # Filter by project if specified
    if project_id:
        mock_time_logs = [log for log in mock_time_logs if log["project_id"] == int(project_id)]
    
    # Calculate summary based on group_by parameter
    summary = []
    if group_by == "project":
        # Group by project
        project_data = {}
        for log in mock_time_logs:
            project_id = log["project_id"]
            if project_id not in project_data:
                project_data[project_id] = {
                    "name": log["project_name"],
                    "total_hours": 0,
                    "billable_hours": 0,
                    "non_billable_hours": 0
                }
            project_data[project_id]["total_hours"] += log["hours"]
            if log["billable"]:
                project_data[project_id]["billable_hours"] += log["hours"]
            else:
                project_data[project_id]["non_billable_hours"] += log["hours"]
        
        summary = list(project_data.values())
    
    elif group_by == "user":
        # Group by user
        user_data = {}
        for log in mock_time_logs:
            user_id = log["user_id"]
            if user_id not in user_data:
                user_data[user_id] = {
                    "name": log["user_name"],
                    "total_hours": 0,
                    "billable_hours": 0,
                    "non_billable_hours": 0
                }
            user_data[user_id]["total_hours"] += log["hours"]
            if log["billable"]:
                user_data[user_id]["billable_hours"] += log["hours"]
            else:
                user_data[user_id]["non_billable_hours"] += log["hours"]
        
        summary = list(user_data.values())
    
    elif group_by == "task":
        # Group by task
        task_data = {}
        for log in mock_time_logs:
            task_id = log["task_id"]
            if task_id not in task_data:
                task_data[task_id] = {
                    "name": log["task_name"],
                    "total_hours": 0,
                    "billable_hours": 0,
                    "non_billable_hours": 0
                }
            task_data[task_id]["total_hours"] += log["hours"]
            if log["billable"]:
                task_data[task_id]["billable_hours"] += log["hours"]
            else:
                task_data[task_id]["non_billable_hours"] += log["hours"]
        
        summary = list(task_data.values())
    
    # Calculate totals
    total_hours = sum(item["total_hours"] for item in summary)
    billable_hours = sum(item["billable_hours"] for item in summary)
    non_billable_hours = sum(item["non_billable_hours"] for item in summary)
    
    return templates.TemplateResponse("time_summary_report.html", {
        "request": request, 
        "session": request.session,
        "date_from": date_from,
        "date_to": date_to,
        "project_id": project_id,
        "group_by": group_by,
        "projects": projects,
        "summary": summary,
        "total_hours": total_hours,
        "billable_hours": billable_hours,
        "non_billable_hours": non_billable_hours
    })

@app.get("/reports", response_class=HTMLResponse)
async def reports(request: Request, session: dict = Depends(get_session)):
    if not check_auth(session):
        return RedirectResponse(url="/login")
    return templates.TemplateResponse("reports.html", {"request": request, "session": request.session})

@app.get("/expenses", response_class=HTMLResponse)
async def expenses(
    request: Request, 
    session: dict = Depends(get_session),
    search: str = None,
    category: str = None,
    project_id: int = None,
    date_from: str = None,
    date_to: str = None,
    page: int = 1,
    status: str = None
):
    if not check_auth(session):
        return RedirectResponse(url="/login")
    
    # Use our comprehensive MOCK_EXPENSES for data
    expenses_data = MOCK_EXPENSES.copy()
    
    # Filter by search query
    if search:
        search = search.lower()
        expenses_data = [e for e in expenses_data if 
                        (e["description"] and search in e["description"].lower()) or 
                        (e["vendor_name"] and search in e["vendor_name"].lower()) or 
                        (e["project_name"] and search in e["project_name"].lower()) or
                        (e["category"] and search in e["category"].lower()) or
                        (e["submitted_by"] and search in e["submitted_by"].lower())]
    
    # Filter by category
    if category and category != "All":
        expenses_data = [e for e in expenses_data if e["category"] == category]
    
    # Filter by project
    if project_id:
        expenses_data = [e for e in expenses_data if e["project_id"] == project_id]
    
    # Filter by status
    if status and status != "All":
        expenses_data = [e for e in expenses_data if e["status"] == status]
    
    # Filter by date range
    if date_from:
        expenses_data = [e for e in expenses_data if e["date"] >= date_from]
    
    if date_to:
        expenses_data = [e for e in expenses_data if e["date"] <= date_to]
    
    # Pagination variables
    items_per_page = 10
    total_items = len(expenses_data)
    total_pages = (total_items + items_per_page - 1) // items_per_page  # Ceiling division
    
    # Ensure page is within valid range
    if page < 1:
        page = 1
    elif page > total_pages and total_pages > 0:
        page = total_pages
    
    # Calculate pagination indices
    start_idx = (page - 1) * items_per_page
    end_idx = min(start_idx + items_per_page, total_items)
    
    # Get expenses for current page
    paginated_expenses = expenses_data[start_idx:end_idx]
    
    # Process expense status for display
    for expense in paginated_expenses:
        if expense["status"] == "Approved" or expense["status"] == "Reimbursed" or expense["status"] == "Reconciled":
            expense["status_color"] = "success"
        elif expense["status"] == "Pending Review":
            expense["status_color"] = "warning"
        elif expense["status"] == "Rejected":
            expense["status_color"] = "danger"
        else:
            expense["status_color"] = "primary"
        
        # Check if receipt exists
        expense["receipt"] = True if expense.get("receipt_url") else False
    
    # Calculate summary statistics
    total_amount = sum(e["amount"] for e in expenses_data)
    approved_amount = sum(e["amount"] for e in expenses_data if e["status"] in ["Approved", "Reimbursed", "Reconciled"])
    pending_amount = sum(e["amount"] for e in expenses_data if e["status"] == "Pending Review")
    
    # Prepare context
    context = {
        "request": request, 
        "session": request.session,
        "expenses": paginated_expenses,
        "page": page,
        "total_pages": total_pages,
        "search_query": search or "",
        "category_filter": category or "All",
        "project_filter": project_id,
        "status_filter": status or "All",
        "date_from": date_from or "",
        "date_to": date_to or "",
        "categories": EXPENSE_CATEGORIES,
        "statuses": EXPENSE_STATUSES,
        "projects": MOCK_PROJECTS,
        "total_expenses": total_items,
        "total_amount": total_amount,
        "approved_amount": approved_amount,
        "pending_amount": pending_amount
    }
    
    return templates.TemplateResponse("expenses.html", context)

@app.get("/expenses/new", response_class=HTMLResponse)
async def new_expense(request: Request, session: dict = Depends(get_session), project_id: int = None):
    if not check_auth(session):
        return RedirectResponse(url="/login")
    
    # Mock data for projects
    projects = [
        {"id": 1, "name": "Office Renovation"},
        {"id": 2, "name": "Mobile App Development"},
        {"id": 3, "name": "CRM Implementation"},
        {"id": 4, "name": "Digital Marketing Campaign"}
    ]
    
    # Mock data for vendors
    vendors = [
        {"id": 1, "name": "Elite Electrical Services"},
        {"id": 2, "name": "Premium Plumbing Co"},
        {"id": 3, "name": "Quality Construction Materials"},
        {"id": 4, "name": "Professional Painting Services"},
        {"id": 5, "name": "Equipment Rental Co"}
    ]
    
    # Expense categories
    expense_categories = ["Materials", "Equipment Rental", "Subcontractor", "Permits", "Labor", "Travel", "Office", "Other"]
    
    # Pre-select project if provided
    selected_project = next((p for p in projects if p["id"] == project_id), None) if project_id else None
    
    # Prepare context
    context = {
        "request": request, 
        "session": request.session,
        "projects": projects,
        "vendors": vendors,
        "categories": expense_categories,
        "selected_project": selected_project,
        "expense": None
    }
    
    return templates.TemplateResponse("expense_form.html", context)

@app.post("/expenses/new", response_class=HTMLResponse)
async def create_expense(
    request: Request,
    session: dict = Depends(get_session),
    date: str = Form(...),
    category: str = Form(...),
    vendor_id: int = Form(None),
    vendor_name: str = Form(...),
    project_id: int = Form(...),
    amount: float = Form(...),
    description: str = Form(...)
    # receipt: UploadFile = File(None)  # Commented out for mock implementation
):
    if not check_auth(session):
        return RedirectResponse(url="/login")
    
    # In a real app, we would save the expense to the database and handle the receipt upload
    # For this demo, we'll just redirect to the expenses list
    
    # Add a success message
    request.session["flash_messages"] = [
        {"type": "success", "message": "Expense submitted successfully."}
    ]
    
    return RedirectResponse(url="/expenses", status_code=303)

@app.get("/expenses/{expense_id}", response_class=HTMLResponse)
async def expense_detail(expense_id: int, request: Request, session: dict = Depends(get_session)):
    if not check_auth(session):
        return RedirectResponse(url="/login")
    
    # Mock data for expenses
    mock_expenses = {
        1: {
            "id": 1,
            "date": "2023-03-01",
            "category": "Materials",
            "vendor_id": 3,
            "vendor_name": "Quality Construction Materials",
            "project_id": 1,
            "project_name": "Office Renovation",
            "amount": 1250.00,
            "description": "Lumber and drywall materials",
            "status": "Approved",
            "status_color": "success",
            "receipt_url": "/uploads/receipts/receipt_1.pdf",
            "submitted_by": "John Doe",
            "submitted_at": "2023-03-01 14:30:00",
            "approved_by": "Admin",
            "approved_at": "2023-03-02 09:15:00",
            "notes": "Materials for office renovation project"
        },
        2: {
            "id": 2,
            "receipt": True,
            "submitted_by": "John Doe"
        },
    }
    
    # Get the expense or return 404
    expense = mock_expenses.get(expense_id)
    if not expense:
        return templates.TemplateResponse("404.html", {"request": request, "session": request.session}, status_code=404)
    
    return templates.TemplateResponse("expense_detail.html", {"request": request, "session": request.session, "expense": expense})

# Construction material categories
MATERIAL_CATEGORIES = [
    "Concrete & Masonry",
    "Lumber & Wood Products",
    "Steel & Metal",
    "Electrical",
    "Plumbing",
    "HVAC",
    "Roofing",
    "Flooring",
    "Paint & Coatings",
    "Windows & Doors",
    "Hardware & Fasteners",
    "Insulation",
    "Drywall & Accessories",
    "Site Materials",
    "Safety Equipment"
]

# Mock data for testing
MOCK_MATERIALS = [
    {
        'id': '1',
        'vendor_id': '1',
        'name': 'Portland Cement',
        'category': 'Concrete & Masonry',
        'unit_price': 12.99,
        'unit': 'bag',
        'min_order_quantity': 10,
        'lead_time_days': 3,
        'quantity': 50,
        'status': 'in_stock',
        'quality_rating': 4,
        'delivery_status': 'on_time',
        'updated_at': datetime.now().isoformat()
    }
]

MOCK_VENDORS = [
    {
        'id': '1',
        'name': 'ABC Building Supply',
        'vendor_type': 'Material',
        'contact_name': 'John Doe',
        'email': 'john@abcsupply.com',
        'phone': '555-0123',
        'address': {'street': '123 Main St', 'city': 'Springfield', 'state': 'IL', 'zip': '62701'},
        'material_categories': ['Concrete & Masonry', 'Lumber & Wood Products'],
        'lead_time_days': 3,
        'payment_terms': 'Net 30',
        'is_preferred': True,
        'has_volume_discount': True,
        'quality_rating': 4,
        'insurance_policy': 'INS-12345',
        'insurance_expiry': (datetime.now() + timedelta(days=60)).isoformat(),
        'certifications': ['ISO 9001', 'Green Building Certified'],
        'status': 'active',
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat()
    }
]

# Vendor routes
@app.get("/vendors", response_class=HTMLResponse)
async def list_vendors(
    request: Request,
    material_category: Optional[str] = None,
    preferred_only: bool = False,
    status: Optional[str] = None
):
    """List all vendors with optional filtering."""
    try:
        # Get the current date for insurance expiry comparisons
        current_date = datetime.now().date()
        
        supabase = get_supabase_client()
        vendors = []
        
        if supabase:
            # Try to get vendors from Supabase
            query = supabase.table("vendors").select("*")
            
            # Apply filters
            if material_category:
                query = query.contains("material_categories", [material_category])
            if preferred_only:
                query = query.eq("is_preferred", True)
            if status:
                query = query.eq("status", status)
                
            # Execute query
            result = query.execute()
            vendors = result.data if result else []
        else:
            # Use mock data
            vendors = MOCK_VENDORS
            
            # Apply filters to mock data
            if material_category:
                vendors = [v for v in vendors if material_category in v.get('material_categories', [])]
            if preferred_only:
                vendors = [v for v in vendors if v.get('is_preferred')]
            if status:
                vendors = [v for v in vendors if v.get('status') == status]
        
        # Process vendor dates for comparison
        for vendor in vendors:
            if vendor.get('insurance_expiry'):
                # Parse the ISO-formatted date string to a datetime object
                try:
                    insurance_date = datetime.fromisoformat(vendor['insurance_expiry'].replace('Z', '+00:00'))
                    vendor['insurance_expiry'] = insurance_date.date()
                except (ValueError, AttributeError):
                    # If parsing fails, set to None to avoid comparison errors
                    vendor['insurance_expiry'] = None
        
        return templates.TemplateResponse(
            "vendors.html",
            {
                "request": request,
                "session": request.session,
                "vendors": vendors,
                "material_categories": MATERIAL_CATEGORIES,
                "now": current_date  # Add the current date to the template context
            }
        )
    except Exception as e:
        print(f"Error listing vendors: {str(e)}")
        # Fall back to mock data on error
        current_date = datetime.now().date()  # Also add in the error case
        vendors = MOCK_VENDORS
        if material_category:
            vendors = [v for v in vendors if material_category in v.get('material_categories', [])]
        if preferred_only:
            vendors = [v for v in vendors if v.get('is_preferred')]
        if status:
            vendors = [v for v in vendors if v.get('status') == status]
        
        # Process vendor dates for comparison
        for vendor in vendors:
            if vendor.get('insurance_expiry'):
                # Parse the ISO-formatted date string to a datetime object
                try:
                    insurance_date = datetime.fromisoformat(vendor['insurance_expiry'].replace('Z', '+00:00'))
                    vendor['insurance_expiry'] = insurance_date.date()
                except (ValueError, AttributeError):
                    # If parsing fails, set to None to avoid comparison errors
                    vendor['insurance_expiry'] = None
            
        return templates.TemplateResponse(
            "vendors.html",
            {
                "request": request,
                "session": request.session,
                "vendors": vendors,
                "material_categories": MATERIAL_CATEGORIES,
                "now": current_date  # Add the current date to the template context
            }
        )

@app.get("/vendors/new", response_class=HTMLResponse)
async def new_vendor(request: Request):
    """Display form for creating a new vendor."""
    return templates.TemplateResponse(
        "vendor_form.html",
        {
            "request": request,
            "session": request.session,
            "material_categories": MATERIAL_CATEGORIES,
            "vendor": None  # No vendor data for new form
        }
    )

@app.post("/vendors", response_class=HTMLResponse)
async def create_vendor_route(
    request: Request,
    name: str = Form(...),
    contact_name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    material_categories: List[str] = Form(...),
    address: str = Form(...),
    tax_id: str = Form(...),
    insurance_doc: UploadFile = File(...),
    notes: Optional[str] = Form(None)
):
    """Create a new vendor."""
    try:
        supabase = get_supabase_client()
        
        # Upload insurance document
        file_path = f"vendor_docs/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{insurance_doc.filename}"
        result = supabase.storage.from_("vendor_documents").upload(
            file_path,
            insurance_doc.file.read()
        )
        
        # Create vendor record
        vendor_data = {
            "name": name,
            "contact_name": contact_name,
            "email": email,
            "phone": phone,
            "material_categories": material_categories,
            "address": address,
            "tax_id": tax_id,
            "insurance_doc_url": file_path if result else None,
            "notes": notes,
            "status": "pending",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        result = supabase.table("vendors").insert(vendor_data).execute()
        
        if result and result.data:
            return RedirectResponse(url="/vendors", status_code=303)
        else:
            raise HTTPException(status_code=500, detail="Failed to create vendor")
            
    except Exception as e:
        print(f"Error creating vendor: {str(e)}")
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "status_code": 500,
                "detail": "Error creating vendor"
            }
        )

@app.get("/vendors/{vendor_id}", response_class=HTMLResponse)
async def view_vendor(request: Request, vendor_id: str):
    """View details of a specific vendor."""
    try:
        supabase = get_supabase_client()
        vendor = None
        metrics = None
        
        if supabase:
            # Try to get vendor from Supabase
            result = supabase.table("vendors").select("*").eq("id", vendor_id).single().execute()
            if result and result.data:
                vendor = result.data
                # Get vendor's performance metrics
                metrics = {
                    "total_purchases": len(supabase.table("purchases").select("id").eq("vendor_id", vendor_id).execute().data),
                    "active_projects": len(supabase.table("project_vendors").select("project_id").eq("vendor_id", vendor_id).eq("status", "active").execute().data),
                    "insurance_status": "Valid" 
                }
                
                # Handle insurance expiry date
                if vendor.get("insurance_expiry"):
                    try:
                        insurance_date = datetime.fromisoformat(vendor["insurance_expiry"].replace('Z', '+00:00')).date()
                        vendor["insurance_expiry"] = insurance_date
                        metrics["insurance_status"] = "Valid" if insurance_date > datetime.now().date() else "Expired"
                    except (ValueError, TypeError):
                        vendor["insurance_expiry"] = None
                        metrics["insurance_status"] = "Unknown"
        else:
            # Use mock data
            vendor = next((v for v in MOCK_VENDORS if v['id'] == vendor_id), None)
            if vendor:
                metrics = {
                    "total_purchases": len([p for p in MOCK_MATERIALS if p['vendor_id'] == vendor_id]),
                    "active_projects": 2,  # Mock value
                    "insurance_status": "Unknown"
                }
                
                # Handle insurance expiry date
                if vendor.get("insurance_expiry"):
                    try:
                        insurance_date = datetime.fromisoformat(vendor["insurance_expiry"].replace('Z', '+00:00')).date()
                        vendor["insurance_expiry"] = insurance_date
                        metrics["insurance_status"] = "Valid" if insurance_date > datetime.now().date() else "Expired"
                    except (ValueError, TypeError):
                        vendor["insurance_expiry"] = None
        
        if not vendor:
            raise HTTPException(status_code=404, detail="Vendor not found")
            
        return templates.TemplateResponse(
            "vendor_details.html",
            {
                "request": request,
                "session": request.session,
                "vendor": vendor,
                "metrics": metrics
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error viewing vendor: {str(e)}")
        # Fall back to mock data on error
        vendor = next((v for v in MOCK_VENDORS if v['id'] == vendor_id), None)
        if not vendor:
            raise HTTPException(status_code=404, detail="Vendor not found")
            
        metrics = {
            "total_purchases": len([p for p in MOCK_MATERIALS if p['vendor_id'] == vendor_id]),
            "active_projects": 2,  # Mock value
            "insurance_status": "Unknown"
        }
        
        # Handle insurance expiry date
        if vendor.get("insurance_expiry"):
            try:
                insurance_date = datetime.fromisoformat(vendor["insurance_expiry"].replace('Z', '+00:00')).date()
                vendor["insurance_expiry"] = insurance_date
                metrics["insurance_status"] = "Valid" if insurance_date > datetime.now().date() else "Expired"
            except (ValueError, TypeError):
                vendor["insurance_expiry"] = None
                metrics["insurance_status"] = "Unknown"
        
        return templates.TemplateResponse(
            "vendor_details.html",
            {
                "request": request,
                "session": request.session,
                "vendor": vendor,
                "metrics": metrics
            }
        )

@app.get("/vendors/{vendor_id}/edit", response_class=HTMLResponse)
async def edit_vendor(
    vendor_id: str,
    request: Request,
    session: dict = Depends(get_session)
):
    """Display edit vendor form"""
    if not check_auth(session):
        return RedirectResponse(url="/login")
        
    try:
        # Get vendor from database
        if supabase:
            response = supabase.from_("vendors").select("*").eq("id", vendor_id).execute()
            vendor = response.data[0] if response.data else None
        else:
            # Use mock data
            vendor = next((v for v in MOCK_VENDORS if v['id'] == vendor_id), None)
            
        if not vendor:
            raise HTTPException(status_code=404, detail="Vendor not found")
        
        return templates.TemplateResponse("vendor_form.html", {
            "request": request,
            "vendor": vendor,
            "material_categories": MATERIAL_CATEGORIES,
            "session": session
        })
    except Exception as e:
        print(f"Error editing vendor: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/vendors/{vendor_id}/edit")
async def update_vendor_route(
    vendor_id: str,
    request: Request,
    session: dict = Depends(get_session),
    name: str = Form(...),
    vendor_type: str = Form(...),
    contact_name: str = Form(None),
    email: str = Form(None),
    phone: str = Form(None),
    address: str = Form(None),
    city: str = Form(None),
    state: str = Form(None),
    zip_code: str = Form(None),
    material_categories: List[str] = Form([]),
    lead_time_days: int = Form(0),
    payment_terms: str = Form(None),
    is_preferred: bool = Form(False),
    quality_rating: int = Form(3),
    tax_id: str = Form(None),
    insurance_policy: str = Form(None),
    insurance_expiry: str = Form(None),
    certifications: str = Form(None),
    notes: str = Form(None),
    insurance_document: Optional[UploadFile] = File(None)
):
    """Update a vendor"""
    if not check_auth(session):
        return RedirectResponse(url="/login")
        
    try:
        vendor_data = {
            "name": name,
            "vendor_type": vendor_type,
            "contact_name": contact_name,
            "email": email,
            "phone": phone,
            "address": {
                "street": address,
                "city": city,
                "state": state,
                "zip": zip_code
            },
            "material_categories": material_categories,
            "lead_time_days": lead_time_days,
            "payment_terms": payment_terms,
            "is_preferred": is_preferred,
            "quality_rating": quality_rating,
            "tax_id": tax_id,
            "insurance_policy": insurance_policy,
            "insurance_expiry": insurance_expiry,  # This is a string from the form
            "certifications": certifications.split('\n') if certifications else [],
            "notes": notes,
            "updated_at": datetime.utcnow().isoformat() + "Z"  # Store as ISO format string with Z
        }
        
        # Handle insurance document upload if provided
        if insurance_document and insurance_document.filename:
            file_path = f"vendor_docs/{datetime.now().strftime('%Y%m%d_%H%M%S')}_{insurance_document.filename}"
            result = supabase.storage.from_("vendor_documents").upload(
                file_path,
                insurance_document.file.read()
            )
            if result:
                vendor_data["insurance_doc_url"] = file_path
        
        # Update vendor in database
        if supabase:
            result = supabase.table("vendors").update(vendor_data).eq("id", vendor_id).execute()
            if not result or not result.data:
                raise HTTPException(status_code=500, detail="Failed to update vendor")
        
        return RedirectResponse(url=f"/vendors/{vendor_id}", status_code=303)
    except Exception as e:
        print(f"Error updating vendor: {str(e)}")
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "status_code": 500,
                "detail": f"Error updating vendor: {str(e)}"
            }
        )

@app.post("/vendors/{vendor_id}/delete")
async def delete_vendor_route(
    vendor_id: str,
    request: Request,
    session: dict = Depends(get_session)
):
    """Delete a vendor"""
    if not check_auth(session):
        return RedirectResponse(url="/login")
        
    try:
        # Delete vendor from database
        if supabase:
            response = supabase.from_("vendors").delete().eq("id", vendor_id).execute()
        else:
            # Remove from mock data
            global MOCK_VENDORS
            MOCK_VENDORS = [v for v in MOCK_VENDORS if v['id'] != vendor_id]
        
        return RedirectResponse(
            url="/vendors",
            status_code=303
        )
    except Exception as e:
        print(f"Error deleting vendor: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/vendors/{vendor_id}/materials", response_class=HTMLResponse)
async def view_vendor_materials(
    vendor_id: str,
    request: Request,
    session: dict = Depends(get_session)
):
    """View vendor's materials"""
    if not check_auth(session):
        return RedirectResponse(url="/login")
        
    try:
        # Get vendor from database
        if supabase:
            response = supabase.from_("vendors").select("*").eq("id", vendor_id).execute()
            vendor = response.data[0] if response.data else None
        else:
            # Use mock data
            vendor = next((v for v in MOCK_VENDORS if v['id'] == vendor_id), None)
            
        if not vendor:
            raise HTTPException(status_code=404, detail="Vendor not found")
        
        # Get vendor materials
        materials = []
        if supabase:
            response = supabase.from_("materials").select("*").eq("vendor_id", vendor_id).execute()
            materials = response.data if response.data else []
        else:
            materials = [m for m in MOCK_MATERIALS if m['vendor_id'] == vendor_id]
        
        return templates.TemplateResponse("vendor_materials.html", {
            "request": request,
            "vendor": vendor,
            "materials": materials,
            "material_categories": MATERIAL_CATEGORIES,
            "session": session
        })
    except Exception as e:
        print(f"Error viewing vendor materials: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/vendors/{vendor_id}/materials/{material_id}/stock")
async def update_material_stock_route(
    vendor_id: str,
    material_id: str,
    quantity: int = Form(...),
    status: str = Form(...),
    session: dict = Depends(get_session)
):
    """Update material stock level"""
    if not check_auth(session):
        return RedirectResponse(url="/login")
        
    try:
        update_data = {
            "quantity": quantity,
            "status": status,
            "updated_at": datetime.utcnow()
        }
        
        # Update material in database
        if supabase:
            response = supabase.from_("materials").update(update_data).eq("id", material_id).eq("vendor_id", vendor_id).execute()
            result = response.data[0] if response.data else None
        else:
            # Update mock data
            for i, material in enumerate(MOCK_MATERIALS):
                if material['id'] == material_id and material['vendor_id'] == vendor_id:
                    MOCK_MATERIALS[i].update(update_data)
                    result = MOCK_MATERIALS[i]
                    break
            else:
                result = None
        
        if not result:
            raise HTTPException(status_code=404, detail="Material not found")
        
        return RedirectResponse(
            url=f"/vendors/{vendor_id}/materials",
            status_code=303
        )
    except Exception as e:
        print(f"Error updating material stock: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Login page
@app.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "session": request.session})

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

# If this file is run directly, use Uvicorn to serve the app
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)

# Customer routes
@app.get("/customers", response_class=HTMLResponse)
async def customers(
    request: Request, 
    session: dict = Depends(get_session),
    search: str = None,
    status: str = None
):
    """List all customers with optional filtering."""
    if not check_auth(session):
        return RedirectResponse(url="/login")
    
    # Try to get customer data from Supabase
    supabase_client = get_supabase_client()
    customers_data = []
    
    try:
        if supabase_client:
            # Fetch data from Supabase with optional filters
            query = supabase_client.table("customers").select("*")
            
            if status:
                query = query.eq("status", status)
                
            if search:
                query = query.or_(f"name.ilike.%{search}%,contact_name.ilike.%{search}%,email.ilike.%{search}%")
            
            result = query.execute()
            customers_data = result.data
        else:
            # Use mock data with filtering in Python
            customers_data = MOCK_CUSTOMERS
            
            # Apply filters
            if status:
                customers_data = [c for c in customers_data if c["status"].lower() == status.lower()]
                
            if search:
                search = search.lower()
                customers_data = [c for c in customers_data if 
                                 search in c["name"].lower() or
                                 search in c["contact_name"].lower() or
                                 search in c["email"].lower()]
    except Exception as e:
        print(f"Error fetching customers: {str(e)}")
        # Fallback to mock data
        customers_data = MOCK_CUSTOMERS
    
    # Get unique statuses for the status filter dropdown
    statuses = sorted(list(set(c["status"] for c in MOCK_CUSTOMERS)))
    
    return templates.TemplateResponse(
        "customers.html", 
        {
            "request": request, 
            "session": request.session, 
            "customers": customers_data,
            "statuses": statuses
        }
    )

@app.get("/customers/new", response_class=HTMLResponse)
async def new_customer(request: Request, session: dict = Depends(get_session)):
    """Create a new customer form."""
    if not check_auth(session):
        return RedirectResponse(url="/login")
    
    # Empty customer object for the form
    customer = {
        "id": None,
        "name": "",
        "contact_name": "",
        "email": "",
        "phone": "",
        "address": "",
        "city": "",
        "state": "",
        "zip": "",
        "status": "Active",
        "customer_since": datetime.now().strftime("%Y-%m-%d"),
        "payment_terms": "Net 30",
        "credit_limit": 0.00,
        "notes": ""
    }
    
    # Statuses and payment terms for form dropdowns
    statuses = ["Active", "Inactive", "Pending", "VIP"]
    payment_terms = ["Net 15", "Net 30", "Net 45", "Net 60", "Due on Receipt"]
    
    return templates.TemplateResponse(
        "customer_form.html", 
        {
            "request": request, 
            "session": request.session, 
            "customer": customer,
            "statuses": statuses,
            "payment_terms": payment_terms
        }
    )

@app.post("/customers/new", response_class=HTMLResponse)
async def create_customer(
    request: Request,
    session: dict = Depends(get_session),
    name: str = Form(...),
    contact_name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    address: str = Form(None),
    city: str = Form(None),
    state: str = Form(None),
    zip: str = Form(None),
    status: str = Form("Active"),
    customer_since: str = Form(None),
    payment_terms: str = Form("Net 30"),
    credit_limit: float = Form(0.00),
    notes: str = Form(None),
    latitude: float = Form(None),
    longitude: float = Form(None),
    formatted_address: str = Form(None)
):
    """Create a new customer."""
    if not check_auth(session):
        return RedirectResponse(url="/login")
    
    supabase_client = get_supabase_client()
    
    try:
        # Prepare the customer data
        customer_data = {
            "name": name,
            "contact_name": contact_name,
            "email": email,
            "phone": phone,
            "address": address,
            "city": city,
            "state": state,
            "zip": zip,
            "status": status,
            "customer_since": customer_since or datetime.now().strftime("%Y-%m-%d"),
            "payment_terms": payment_terms,
            "credit_limit": credit_limit,
            "notes": notes,
            "latitude": latitude,
            "longitude": longitude,
            "formatted_address": formatted_address,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        # Try to insert into Supabase
        customer_id = None
        if supabase_client:
            try:
                result = supabase_client.table("customers").insert(customer_data).execute()
                if result.data:
                    customer_id = result.data[0].get('id')
            except Exception as supabase_error:
                print(f"Supabase error creating customer: {str(supabase_error)}")
        
        # If we couldn't insert into Supabase, use a mock ID
        if not customer_id:
            # In a mock scenario, generate a new ID
            customer_id = max([c["id"] for c in MOCK_CUSTOMERS]) + 1
            
            # Add to mock data for this session
            customer_data["id"] = customer_id
            MOCK_CUSTOMERS.append(customer_data)
        
        # Redirect to the new customer's detail page
        return RedirectResponse(url=f"/customers/{customer_id}", status_code=303)
    
    except Exception as e:
        print(f"Error creating customer: {str(e)}")
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "session": request.session,
                "status_code": 500,
                "detail": f"Error creating customer: {str(e)}"
            },
            status_code=500
        )

@app.get("/customers/{customer_id}", response_class=HTMLResponse)
async def customer_detail(customer_id: int, request: Request, session: dict = Depends(get_session)):
    """Display customer details."""
    if not check_auth(session):
        return RedirectResponse(url="/login")
    
    # Try to get the customer from Supabase
    supabase_client = get_supabase_client()
    customer = None
    
    try:
        if supabase_client:
            result = supabase_client.table("customers").select("*").eq("id", customer_id).execute()
            if result.data:
                customer = result.data[0]
        
        # If not found or Supabase not available, check mock data
        if not customer:
            customer = next((c for c in MOCK_CUSTOMERS if c["id"] == customer_id), None)
        
        if not customer:
            # Customer not found
            return templates.TemplateResponse(
                "error.html", 
                {
                    "request": request, 
                    "status_code": 404,
                    "detail": f"Customer with ID {customer_id} not found"
                },
                status_code=404
            )
        
        # Get related projects for this customer from MOCK_PROJECTS
        projects = [p for p in MOCK_PROJECTS if p["client_id"] == customer_id]
        
        # Return the customer detail template
        return templates.TemplateResponse(
            "customer_detail.html", 
            {
                "request": request, 
                "customer": customer,
                "projects": projects
            }
        )
    
    except Exception as e:
        print(f"Error retrieving customer {customer_id}: {str(e)}")
        return templates.TemplateResponse(
            "error.html", 
            {
                "request": request, 
                "status_code": 500,
                "detail": f"Error retrieving customer: {str(e)}"
            },
            status_code=500
        )

@app.get("/customers/{customer_id}/edit", response_class=HTMLResponse)
async def edit_customer(customer_id: int, request: Request, session: dict = Depends(get_session)):
    """Edit customer form."""
    if not check_auth(session):
        return RedirectResponse(url="/login")
    
    # Try to get the customer from Supabase
    supabase_client = get_supabase_client()
    customer = None
    
    try:
        if supabase_client:
            result = supabase_client.table("customers").select("*").eq("id", customer_id).execute()
            if result.data:
                customer = result.data[0]
        
        # If not found or Supabase not available, check mock data
        if not customer:
            customer = next((c for c in MOCK_CUSTOMERS if c["id"] == customer_id), None)
        
        if not customer:
            # Customer not found
            return templates.TemplateResponse(
                "error.html", 
                {
                    "request": request, 
                    "session": request.session,
                    "status_code": 404,
                    "detail": f"Customer with ID {customer_id} not found"
                },
                status_code=404
            )
        
        # Statuses and payment terms for form dropdowns
        statuses = ["Active", "Inactive", "Pending", "VIP"]
        payment_terms = ["Net 15", "Net 30", "Net 45", "Net 60", "Due on Receipt"]
        
        # Return the customer edit form
        return templates.TemplateResponse(
            "customer_form.html", 
            {
                "request": request, 
                "session": request.session,
                "customer": customer,
                "statuses": statuses,
                "payment_terms": payment_terms
            }
        )
    
    except Exception as e:
        print(f"Error retrieving customer {customer_id} for edit: {str(e)}")
        return templates.TemplateResponse(
            "error.html", 
            {
                "request": request, 
                "session": request.session,
                "status_code": 500,
                "detail": f"Error retrieving customer: {str(e)}"
            },
            status_code=500
        )

@app.post("/customers/{customer_id}/edit", response_class=HTMLResponse)
async def update_customer(
    customer_id: int,
    request: Request,
    session: dict = Depends(get_session),
    name: str = Form(...),
    contact_name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    address: str = Form(None),
    city: str = Form(None),
    state: str = Form(None),
    zip: str = Form(None),
    status: str = Form("Active"),
    customer_since: str = Form(None),
    payment_terms: str = Form("Net 30"),
    credit_limit: float = Form(0.00),
    notes: str = Form(None),
    latitude: float = Form(None),
    longitude: float = Form(None),
    formatted_address: str = Form(None)
):
    """Update customer information."""
    if not check_auth(session):
        return RedirectResponse(url="/login")
    
    supabase_client = get_supabase_client()
    
    try:
        customer_data = {
            "name": name,
            "contact_name": contact_name,
            "email": email,
            "phone": phone,
            "address": address,
            "city": city,
            "state": state,
            "zip": zip,
            "status": status,
            "customer_since": customer_since,
            "payment_terms": payment_terms,
            "credit_limit": credit_limit,
            "notes": notes,
            "latitude": latitude,
            "longitude": longitude,
            "formatted_address": formatted_address,
            "updated_at": datetime.utcnow().isoformat()
        }
        
        if supabase_client:
            try:
                result = supabase_client.table("customers").update(customer_data).eq("id", customer_id).execute()
                
                if not result.data:
                    print(f"No data returned when updating customer {customer_id}")
            except Exception as supabase_error:
                print(f"Supabase error updating customer: {str(supabase_error)}")
        
        # In a real app, you would update the customer in the database
        # Here we're just redirecting back to the customer detail page
        
        return RedirectResponse(url=f"/customers/{customer_id}", status_code=303)
    
    except Exception as e:
        print(f"Error updating customer {customer_id}: {str(e)}")
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "session": request.session,
                "status_code": 500,
                "detail": f"Error updating customer: {str(e)}"
            },
            status_code=500
        )

@app.post("/customers/{customer_id}/delete", response_class=HTMLResponse)
async def delete_customer(customer_id: int, request: Request, session: dict = Depends(get_session)):
    """Delete a customer."""
    if not check_auth(session):
        return RedirectResponse(url="/login")
    
    try:
        # Try to delete from Supabase if available
        supabase_client = get_supabase_client()
        if supabase_client:
            supabase_client.table("customers").delete().eq("id", customer_id).execute()
        
        # Also remove from mock data
        global MOCK_CUSTOMERS
        MOCK_CUSTOMERS = [c for c in MOCK_CUSTOMERS if c["id"] != customer_id]
        
        # Redirect to customer list
        return RedirectResponse(url="/customers", status_code=303)
    
    except Exception as e:
        print(f"Error deleting customer {customer_id}: {str(e)}")
        return templates.TemplateResponse(
            "error.html", 
            {
                "request": request, 
                "session": request.session,
                "status_code": 500,
                "detail": f"Error deleting customer: {str(e)}"
            },
            status_code=500
        )

# Expense categories
EXPENSE_CATEGORIES = [
    "Materials",
    "Labor",
    "Equipment Rental",
    "Permits & Fees",
    "Subcontractor",
    "Transportation",
    "Accommodation",
    "Meals",
    "Office Supplies",
    "Software & Subscriptions",
    "Insurance",
    "Professional Services",
    "Marketing & Advertising",
    "Utilities",
    "Maintenance & Repairs",
    "Miscellaneous"
]

# Define expense statuses
EXPENSE_STATUSES = [
    "Pending Review",
    "Approved",
    "Rejected",
    "Reimbursed",
    "Reconciled"
]

# Comprehensive mock expenses data
MOCK_EXPENSES = [
    {
        "id": 1,
        "date": "2025-02-15",
        "category": "Materials",
        "vendor_id": "1",
        "vendor_name": "ABC Building Supply",
        "project_id": 1,
        "project_name": "Office Renovation",
        "description": "Lumber for framing",
        "amount": 2500.00,
        "receipt_url": "https://storage.googleapis.com/receipt-images/receipt-001.pdf",
        "status": "Approved",
        "payment_method": "Company Credit Card",
        "submitted_by": "John Smith",
        "billable": True,
        "notes": "Bulk purchase for main office area",
        "invoice_id": 1,
        "created_at": "2025-02-15T10:30:00Z",
        "updated_at": "2025-02-16T14:15:00Z"
    },
    {
        "id": 2,
        "date": "2025-02-18",
        "category": "Equipment Rental",
        "vendor_id": "3",
        "vendor_name": "Acme Plumbing",
        "project_id": 1,
        "project_name": "Office Renovation",
        "description": "Pipe bender rental (3 days)",
        "amount": 350.00,
        "receipt_url": "https://storage.googleapis.com/receipt-images/receipt-002.pdf",
        "status": "Approved",
        "payment_method": "Company Credit Card",
        "submitted_by": "Emily Johnson",
        "billable": True,
        "notes": "Needed for bathroom plumbing modifications",
        "invoice_id": 1,
        "created_at": "2025-02-18T09:20:00Z",
        "updated_at": "2025-02-19T11:30:00Z"
    },
    {
        "id": 3,
        "date": "2025-02-20",
        "category": "Permits & Fees",
        "vendor_id": "",
        "vendor_name": "City Planning Department",
        "project_id": 1,
        "project_name": "Office Renovation",
        "description": "Building permit application fee",
        "amount": 750.00,
        "receipt_url": "https://storage.googleapis.com/receipt-images/receipt-003.pdf",
        "status": "Reimbursed",
        "payment_method": "Personal Funds",
        "submitted_by": "Michael Brown",
        "billable": True,
        "notes": "Required for structural modifications",
        "invoice_id": None,
        "created_at": "2025-02-20T14:45:00Z",
        "updated_at": "2025-02-22T10:10:00Z"
    },
    {
        "id": 4,
        "date": "2025-02-22",
        "category": "Subcontractor",
        "vendor_id": "2",
        "vendor_name": "XYZ Electrical",
        "project_id": 1,
        "project_name": "Office Renovation",
        "description": "Electrical wiring installation",
        "amount": 3800.00,
        "receipt_url": "https://storage.googleapis.com/receipt-images/receipt-004.pdf",
        "status": "Approved",
        "payment_method": "Company Check",
        "submitted_by": "Jane Doe",
        "billable": True,
        "notes": "Completed per electrical plans",
        "invoice_id": 2,
        "created_at": "2025-02-22T16:30:00Z",
        "updated_at": "2025-02-23T09:45:00Z"
    },
    {
        "id": 5,
        "date": "2025-02-25",
        "category": "Materials",
        "vendor_id": "1",
        "vendor_name": "ABC Building Supply",
        "project_id": 1,
        "project_name": "Office Renovation",
        "description": "Drywall and finishing materials",
        "amount": 1850.00,
        "receipt_url": "https://storage.googleapis.com/receipt-images/receipt-005.pdf",
        "status": "Approved",
        "payment_method": "Company Credit Card",
        "submitted_by": "John Smith",
        "billable": True,
        "notes": "For office dividing walls",
        "invoice_id": 2,
        "created_at": "2025-02-25T13:20:00Z",
        "updated_at": "2025-02-26T15:15:00Z"
    },
    {
        "id": 6,
        "date": "2025-02-10",
        "category": "Transportation",
        "vendor_id": "",
        "vendor_name": "Uber",
        "project_id": 2,
        "project_name": "Mobile App Development",
        "description": "Client meeting transportation",
        "amount": 45.00,
        "receipt_url": "https://storage.googleapis.com/receipt-images/receipt-006.pdf",
        "status": "Reimbursed",
        "payment_method": "Personal Funds",
        "submitted_by": "Sarah Williams",
        "billable": False,
        "notes": "Traveled to client headquarters for project kickoff",
        "invoice_id": None,
        "created_at": "2025-02-10T18:10:00Z",
        "updated_at": "2025-02-12T09:30:00Z"
    },
    {
        "id": 7,
        "date": "2025-02-12",
        "category": "Meals",
        "vendor_id": "",
        "vendor_name": "City Grill Restaurant",
        "project_id": 2,
        "project_name": "Mobile App Development",
        "description": "Client lunch meeting",
        "amount": 120.00,
        "receipt_url": "https://storage.googleapis.com/receipt-images/receipt-007.pdf",
        "status": "Approved",
        "payment_method": "Company Credit Card",
        "submitted_by": "Sarah Williams",
        "billable": True,
        "notes": "Discussion of app requirements with client stakeholders",
        "invoice_id": 3,
        "created_at": "2025-02-12T14:40:00Z",
        "updated_at": "2025-02-13T10:20:00Z"
    },
    {
        "id": 8,
        "date": "2025-02-18",
        "category": "Software & Subscriptions",
        "vendor_id": "",
        "vendor_name": "Adobe",
        "project_id": 2,
        "project_name": "Mobile App Development",
        "description": "Adobe Creative Cloud (1 month)",
        "amount": 79.99,
        "receipt_url": "https://storage.googleapis.com/receipt-images/receipt-008.pdf",
        "status": "Approved",
        "payment_method": "Company Credit Card",
        "submitted_by": "Alex Thompson",
        "billable": True,
        "notes": "For app UI design",
        "invoice_id": 3,
        "created_at": "2025-02-18T11:25:00Z",
        "updated_at": "2025-02-19T16:40:00Z"
    },
    {
        "id": 9,
        "date": "2025-02-05",
        "category": "Labor",
        "vendor_id": "",
        "vendor_name": "Freelance Developer Group",
        "project_id": 3,
        "project_name": "CRM Implementation",
        "description": "Contract developer assistance (40 hours)",
        "amount": 4000.00,
        "receipt_url": "https://storage.googleapis.com/receipt-images/receipt-009.pdf",
        "status": "Approved",
        "payment_method": "Bank Transfer",
        "submitted_by": "David Chen",
        "billable": True,
        "notes": "Additional developer resources for data migration component",
        "invoice_id": None,
        "created_at": "2025-02-05T09:15:00Z",
        "updated_at": "2025-02-07T14:30:00Z"
    },
    {
        "id": 10,
        "date": "2025-02-08",
        "category": "Professional Services",
        "vendor_id": "",
        "vendor_name": "Data Solutions Inc",
        "project_id": 3,
        "project_name": "CRM Implementation",
        "description": "Data cleaning and preparation",
        "amount": 2500.00,
        "receipt_url": "https://storage.googleapis.com/receipt-images/receipt-010.pdf",
        "status": "Pending Review",
        "payment_method": "Bank Transfer",
        "submitted_by": "David Chen",
        "billable": True,
        "notes": "Preparation of client data for CRM import",
        "invoice_id": None,
        "created_at": "2025-02-08T15:45:00Z",
        "updated_at": "2025-02-08T15:45:00Z"
    },
    {
        "id": 11,
        "date": "2025-03-01",
        "category": "Office Supplies",
        "vendor_id": "",
        "vendor_name": "Office Depot",
        "project_id": None,
        "project_name": None,
        "description": "General office supplies",
        "amount": 235.67,
        "receipt_url": "https://storage.googleapis.com/receipt-images/receipt-011.pdf",
        "status": "Approved",
        "payment_method": "Company Credit Card",
        "submitted_by": "Lisa Martinez",
        "billable": False,
        "notes": "Monthly office supply order",
        "invoice_id": None,
        "created_at": "2025-03-01T11:30:00Z",
        "updated_at": "2025-03-02T09:15:00Z"
    },
    {
        "id": 12,
        "date": "2025-03-05",
        "category": "Accommodation",
        "vendor_id": "",
        "vendor_name": "Hilton Hotel",
        "project_id": 2,
        "project_name": "Mobile App Development",
        "description": "Client site visit - 3 nights hotel stay",
        "amount": 780.00,
        "receipt_url": "https://storage.googleapis.com/receipt-images/receipt-012.pdf",
        "status": "Pending Review",
        "payment_method": "Company Credit Card",
        "submitted_by": "Sarah Williams",
        "billable": True,
        "notes": "On-site app testing with client team",
        "invoice_id": None,
        "created_at": "2025-03-05T19:20:00Z",
        "updated_at": "2025-03-05T19:20:00Z"
    }
]

# Comprehensive mock invoices data
MOCK_INVOICES = [
    {
        "id": 1,
        "invoice_number": "INV-2025-001",
        "client_id": 1,
        "client_name": "Acme Corporation",
        "project_id": 1,
        "project_name": "Office Renovation",
        "status": "Paid",
        "issue_date": "2025-02-20",
        "due_date": "2025-03-20",
        "subtotal": 2850.00,
        "tax_rate": 8.5,
        "tax_amount": 242.25,
        "discount_amount": 0.00,
        "total_amount": 3092.25,
        "amount_paid": 3092.25,
        "balance_due": 0.00,
        "notes": "Initial invoice for materials and equipment rental",
        "terms": "Net 30",
        "payment_instructions": "Please remit payment via bank transfer",
        "sent_date": "2025-02-20",
        "paid_date": "2025-03-15",
        "created_by": "Jane Doe",
        "created_at": "2025-02-20T10:00:00Z",
        "updated_at": "2025-03-15T14:30:00Z",
        "items": [
            {
                "id": 1,
                "invoice_id": 1,
                "description": "Lumber for framing",
                "quantity": 1,
                "unit_price": 2500.00,
                "amount": 2500.00,
                "type": "Material",
                "taxable": True
            },
            {
                "id": 2,
                "invoice_id": 1,
                "description": "Pipe bender rental (3 days)",
                "quantity": 1,
                "unit_price": 350.00,
                "amount": 350.00,
                "type": "Equipment",
                "taxable": True
            }
        ],
        "payments": [
            {
                "id": 1,
                "invoice_id": 1,
                "date": "2025-03-15",
                "amount": 3092.25,
                "method": "Bank Transfer",
                "reference": "REF45678",
                "notes": "Full payment received"
            }
        ]
    },
    {
        "id": 2,
        "invoice_number": "INV-2025-002",
        "client_id": 1,
        "client_name": "Acme Corporation",
        "project_id": 1,
        "project_name": "Office Renovation",
        "status": "Sent",
        "issue_date": "2025-03-01",
        "due_date": "2025-03-31",
        "subtotal": 5650.00,
        "tax_rate": 8.5,
        "tax_amount": 480.25,
        "discount_amount": 0.00,
        "total_amount": 6130.25,
        "amount_paid": 0.00,
        "balance_due": 6130.25,
        "notes": "Progress invoice for electrical work and materials",
        "terms": "Net 30",
        "payment_instructions": "Please remit payment via bank transfer",
        "sent_date": "2025-03-01",
        "paid_date": None,
        "created_by": "Jane Doe",
        "created_at": "2025-03-01T11:15:00Z",
        "updated_at": "2025-03-01T11:45:00Z",
        "items": [
            {
                "id": 3,
                "invoice_id": 2,
                "description": "Electrical wiring installation",
                "quantity": 1,
                "unit_price": 3800.00,
                "amount": 3800.00,
                "type": "Labor",
                "taxable": True
            },
            {
                "id": 4,
                "invoice_id": 2,
                "description": "Drywall and finishing materials",
                "quantity": 1,
                "unit_price": 1850.00,
                "amount": 1850.00,
                "type": "Material",
                "taxable": True
            }
        ],
        "payments": []
    },
    {
        "id": 3,
        "invoice_number": "INV-2025-003",
        "client_id": 2,
        "client_name": "Tech Innovations Inc",
        "project_id": 2,
        "project_name": "Mobile App Development",
        "status": "Draft",
        "issue_date": "2025-03-10",
        "due_date": "2025-04-09",
        "subtotal": 199.99,
        "tax_rate": 0.0,
        "tax_amount": 0.00,
        "discount_amount": 0.00,
        "total_amount": 199.99,
        "amount_paid": 0.00,
        "balance_due": 199.99,
        "notes": "Invoice for initial project expenses",
        "terms": "Net 30",
        "payment_instructions": "Please remit payment via credit card",
        "sent_date": None,
        "paid_date": None,
        "created_by": "Sarah Williams",
        "created_at": "2025-03-10T09:30:00Z",
        "updated_at": "2025-03-10T09:30:00Z",
        "items": [
            {
                "id": 5,
                "invoice_id": 3,
                "description": "Client lunch meeting",
                "quantity": 1,
                "unit_price": 120.00,
                "amount": 120.00,
                "type": "Expense",
                "taxable": False
            },
            {
                "id": 6,
                "invoice_id": 3,
                "description": "Adobe Creative Cloud (1 month)",
                "quantity": 1,
                "unit_price": 79.99,
                "amount": 79.99,
                "type": "Subscription",
                "taxable": False
            }
        ],
        "payments": []
    },
    {
        "id": 4,
        "invoice_number": "INV-2025-004",
        "client_id": 3,
        "client_name": "Global Logistics Co",
        "project_id": 3,
        "project_name": "CRM Implementation",
        "status": "Overdue",
        "issue_date": "2025-02-01",
        "due_date": "2025-03-01",
        "subtotal": 4000.00,
        "tax_rate": 7.0,
        "tax_amount": 280.00,
        "discount_amount": 400.00,
        "total_amount": 3880.00,
        "amount_paid": 0.00,
        "balance_due": 3880.00,
        "notes": "Invoice for contract development services",
        "terms": "Net 30",
        "payment_instructions": "Please remit payment via bank transfer",
        "sent_date": "2025-02-01",
        "paid_date": None,
        "created_by": "David Chen",
        "created_at": "2025-02-01T15:20:00Z",
        "updated_at": "2025-03-02T09:00:00Z",
        "items": [
            {
                "id": 7,
                "invoice_id": 4,
                "description": "Contract developer assistance (40 hours)",
                "quantity": 40,
                "unit_price": 100.00,
                "amount": 4000.00,
                "type": "Labor",
                "taxable": True
            },
            {
                "id": 8,
                "invoice_id": 4,
                "description": "First-time client discount",
                "quantity": 1,
                "unit_price": -400.00,
                "amount": -400.00,
                "type": "Discount",
                "taxable": False
            }
        ],
        "payments": []
    }
]

@app.get("/invoices", response_class=HTMLResponse)
async def invoices(
    request: Request, 
    session: dict = Depends(get_session),
    search: str = None,
    status: str = None,
    client_id: int = None,
    project_id: int = None,
    date_from: str = None,
    date_to: str = None,
    page: int = 1
):
    if not check_auth(session):
        return RedirectResponse(url="/login")
    
    # Use our comprehensive MOCK_INVOICES for data
    invoices_data = MOCK_INVOICES.copy()
    
    # Filter by search query
    if search:
        search = search.lower()
        invoices_data = [i for i in invoices_data if 
                        (i["invoice_number"] and search in i["invoice_number"].lower()) or 
                        (i["client_name"] and search in i["client_name"].lower()) or 
                        (i["project_name"] and search in i["project_name"].lower()) or
                        (i["notes"] and search in i["notes"].lower())]
    
    # Filter by status
    if status and status != "All":
        invoices_data = [i for i in invoices_data if i["status"] == status]
    
    # Filter by client
    if client_id:
        invoices_data = [i for i in invoices_data if i["client_id"] == client_id]
    
    # Filter by project
    if project_id:
        invoices_data = [i for i in invoices_data if i["project_id"] == project_id]
    
    # Filter by date range
    if date_from:
        invoices_data = [i for i in invoices_data if i["issue_date"] >= date_from]
    
    if date_to:
        invoices_data = [i for i in invoices_data if i["issue_date"] <= date_to]
    
    # Pagination variables
    items_per_page = 10
    total_items = len(invoices_data)
    total_pages = (total_items + items_per_page - 1) // items_per_page  # Ceiling division
    
    # Ensure page is within valid range
    if page < 1:
        page = 1
    elif page > total_pages and total_pages > 0:
        page = total_pages
    
    # Calculate pagination indices
    start_idx = (page - 1) * items_per_page
    end_idx = min(start_idx + items_per_page, total_items)
    
    # Get invoices for current page
    paginated_invoices = invoices_data[start_idx:end_idx]
    
    # Process invoice status for display
    for invoice in paginated_invoices:
        if invoice["status"] == "Paid":
            invoice["status_color"] = "success"
        elif invoice["status"] == "Sent":
            invoice["status_color"] = "primary"
        elif invoice["status"] == "Draft":
            invoice["status_color"] = "secondary"
        elif invoice["status"] == "Overdue":
            invoice["status_color"] = "danger"
        else:
            invoice["status_color"] = "info"
    
    # Define invoice statuses for filtering
    invoice_statuses = ["Draft", "Sent", "Paid", "Overdue", "Cancelled"]
    
    # Calculate summary statistics
    total_amount = sum(i["total_amount"] for i in invoices_data)
    paid_amount = sum(i["amount_paid"] for i in invoices_data)
    due_amount = sum(i["balance_due"] for i in invoices_data)
    
    # Prepare context
    context = {
        "request": request, 
        "session": request.session,
        "invoices": paginated_invoices,
        "page": page,
        "total_pages": total_pages,
        "search_query": search or "",
        "status_filter": status or "All",
        "client_filter": client_id,
        "project_filter": project_id,
        "date_from": date_from or "",
        "date_to": date_to or "",
        "statuses": invoice_statuses,
        "projects": MOCK_PROJECTS,
        "total_invoices": total_items,
        "total_amount": total_amount,
        "paid_amount": paid_amount,
        "due_amount": due_amount
    }
    
    return templates.TemplateResponse("invoices.html", context)

@app.get("/invoices/{invoice_id}", response_class=HTMLResponse)
async def invoice_detail(
    request: Request, 
    invoice_id: int,
    session: dict = Depends(get_session)
):
    if not check_auth(session):
        return RedirectResponse(url="/login")
    
    # Find the invoice by id
    invoice = next((i for i in MOCK_INVOICES if i["id"] == invoice_id), None)
    
    if not invoice:
        return templates.TemplateResponse(
            "error.html", 
            {
                "request": request, 
                "session": request.session,
                "error_title": "Invoice Not Found",
                "error_message": f"Invoice with ID {invoice_id} could not be found.",
                "status_code": 404
            },
            status_code=404
        )
    
    # Find the project if it exists
    project = None
    if invoice["project_id"]:
        project = next((p for p in MOCK_PROJECTS if p["id"] == invoice["project_id"]), None)
    
    # Find related expenses
    related_expenses = [e for e in MOCK_EXPENSES if e.get("invoice_id") == invoice_id]
    
    # Process invoice status for display
    if invoice["status"] == "Paid":
        invoice["status_color"] = "success"
    elif invoice["status"] == "Sent":
        invoice["status_color"] = "primary"
    elif invoice["status"] == "Draft":
        invoice["status_color"] = "secondary"
    elif invoice["status"] == "Overdue":
        invoice["status_color"] = "danger"
    else:
        invoice["status_color"] = "info"
    
    # Create a copy of the invoice with items renamed to line_items to avoid conflict with dict.items() method
    invoice_data = invoice.copy()
    invoice_data["line_items"] = invoice_data.pop("items")
    
    return templates.TemplateResponse(
        "invoice_detail.html", 
        {
            "request": request, 
            "session": request.session,
            "invoice": invoice_data,
            "project": project,
            "related_expenses": related_expenses
        }
    )

@app.get("/invoices/new", response_class=HTMLResponse)
async def new_invoice(
    request: Request,
    session: dict = Depends(get_session),
    project_id: int = None
):
    if not check_auth(session):
        return RedirectResponse(url="/login")
    
    # Get all projects for the dropdown
    projects = MOCK_PROJECTS
    
    # If project_id is provided, pre-select that project
    selected_project = None
    if project_id:
        selected_project = next((p for p in projects if p["id"] == project_id), None)
    
    # Get unbilled expenses
    unbilled_expenses = [e for e in MOCK_EXPENSES if e.get("invoice_id") is None and e.get("billable") is True]
    
    # Generate a new invoice number
    last_invoice_num = max([int(i["invoice_number"].split("-")[-1]) for i in MOCK_INVOICES])
    new_invoice_num = f"INV-2025-{last_invoice_num + 1:03d}"
    
    # Get invoice statuses
    invoice_statuses = ["Draft", "Sent", "Paid", "Overdue", "Cancelled"]
    
    return templates.TemplateResponse(
        "invoice_form.html", 
        {
            "request": request, 
            "session": request.session,
            "projects": projects,
            "selected_project": selected_project,
            "unbilled_expenses": unbilled_expenses,
            "new_invoice_number": new_invoice_num,
            "statuses": invoice_statuses,
            "is_new": True
        }
    )

@app.post("/invoices/create", response_class=RedirectResponse)
async def create_invoice(
    request: Request,
    session: dict = Depends(get_session)
):
    if not check_auth(session):
        return RedirectResponse(url="/login")
    
    # This would normally create an invoice in the database
    # For now, we'll just redirect back to the invoices page
    return RedirectResponse(url="/invoices", status_code=303)

@app.post("/invoices/{invoice_id}/update", response_class=RedirectResponse)
async def update_invoice(
    request: Request,
    invoice_id: int,
    session: dict = Depends(get_session)
):
    if not check_auth(session):
        return RedirectResponse(url="/login")
    
    # This would normally update an invoice in the database
    # For now, we'll just redirect back to the invoice detail page
    return RedirectResponse(url=f"/invoices/{invoice_id}", status_code=303)

@app.get("/invoices/{invoice_id}/edit", response_class=HTMLResponse)
async def edit_invoice(
    request: Request,
    invoice_id: int,
    session: dict = Depends(get_session)
):
    if not check_auth(session):
        return RedirectResponse(url="/login")
    
    # Find the invoice by id
    invoice = next((i for i in MOCK_INVOICES if i["id"] == invoice_id), None)
    
    if not invoice:
        return templates.TemplateResponse(
            "error.html", 
            {
                "request": request, 
                "session": request.session,
                "error_title": "Invoice Not Found",
                "error_message": f"Invoice with ID {invoice_id} could not be found.",
                "status_code": 404
            },
            status_code=404
        )
    
    # Get all projects for the dropdown
    projects = MOCK_PROJECTS
    
    # Get invoice statuses
    invoice_statuses = ["Draft", "Sent", "Paid", "Overdue", "Cancelled"]
    
    return templates.TemplateResponse(
        "invoice_form.html", 
        {
            "request": request, 
            "session": request.session,
            "invoice": invoice,
            "projects": projects,
            "statuses": invoice_statuses,
            "is_new": False
        }
    )

@app.post("/invoices/{invoice_id}/send", response_class=RedirectResponse)
async def send_invoice(
    request: Request,
    invoice_id: int,
    session: dict = Depends(get_session)
):
    if not check_auth(session):
        return RedirectResponse(url="/login")
    
    # This would normally send an invoice via email
    # For now, we'll just redirect back to the invoice detail page with a status update
    invoice = next((i for i in MOCK_INVOICES if i["id"] == invoice_id), None)
    if invoice and invoice["status"] == "Draft":
        invoice["status"] = "Sent"
        invoice["sent_date"] = datetime.now().strftime("%Y-%m-%d")
    
    return RedirectResponse(url=f"/invoices/{invoice_id}", status_code=303)

@app.post("/invoices/{invoice_id}/payment", response_class=RedirectResponse)
async def record_payment(
    request: Request,
    invoice_id: int,
    session: dict = Depends(get_session)
):
    if not check_auth(session):
        return RedirectResponse(url="/login")
    
    # This would normally record a payment for an invoice
    # For now, we'll just redirect back to the invoice detail page with a status update
    invoice = next((i for i in MOCK_INVOICES if i["id"] == invoice_id), None)
    
    if invoice:
        form = await request.form()
        amount = float(form.get("amount", 0))
        
        if amount >= invoice["balance_due"]:
            # Full payment
            invoice["status"] = "Paid"
            invoice["amount_paid"] = invoice["total_amount"]
            invoice["balance_due"] = 0
            invoice["paid_date"] = datetime.now().strftime("%Y-%m-%d")
        else:
            # Partial payment
            invoice["amount_paid"] += amount
            invoice["balance_due"] -= amount
    
    return RedirectResponse(url=f"/invoices/{invoice_id}", status_code=303)

@app.post("/invoices/{invoice_id}/cancel", response_class=RedirectResponse)
async def cancel_invoice(
    request: Request,
    invoice_id: int,
    session: dict = Depends(get_session)
):
    if not check_auth(session):
        return RedirectResponse(url="/login")
    
    # This would normally cancel an invoice
    # For now, we'll just redirect back to the invoice detail page with a status update
    invoice = next((i for i in MOCK_INVOICES if i["id"] == invoice_id), None)
    if invoice:
        invoice["status"] = "Cancelled"
    
    return RedirectResponse(url=f"/invoices/{invoice_id}", status_code=303)

@app.get("/projects/{project_id}/invoices", response_class=HTMLResponse)
async def project_invoices(
    request: Request,
    project_id: int,
    session: dict = Depends(get_session)
):
    if not check_auth(session):
        return RedirectResponse(url="/login")
    
    # Find the project
    project = next((p for p in MOCK_PROJECTS if p["id"] == project_id), None)
    
    if not project:
        return templates.TemplateResponse(
            "error.html", 
            {
                "request": request, 
                "session": request.session,
                "error_title": "Project Not Found",
                "error_message": f"Project with ID {project_id} could not be found.",
                "status_code": 404
            },
            status_code=404
        )
    
    # Get invoices for this project
    project_invoices = [i for i in MOCK_INVOICES if i["project_id"] == project_id]
    
    return templates.TemplateResponse(
        "project_invoices.html", 
        {
            "request": request, 
            "session": request.session,
            "project": project,
            "invoices": project_invoices
        }
    )