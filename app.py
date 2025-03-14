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
    """Get or create a Supabase client instance. Returns None if Supabase is not configured or unavailable."""
    try:
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            print("Supabase configuration missing - falling back to mock data")
            return None
        
        client = create_client(supabase_url, supabase_key)
        # Test the connection
        client.table("vendors").select("*").limit(1).execute()
        return client
    except Exception as e:
        print(f"Error connecting to Supabase - falling back to mock data: {str(e)}")
        return None

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
        
        # Customers
        "customers": "/customers",
        "new_customer": "/customers/new",
        "customer_detail": "/customers/{}",
        "edit_customer": "/customers/{}/edit",
        "delete_customer": "/customers/{}/delete",
        
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
    sort: str = None
):
    if not check_auth(session):
        return RedirectResponse(url="/login")
    
    # Mock data for projects
    projects = [
        {
            "id": 1,
            "name": "Website Redesign",
            "client_id": 1,
            "client_name": "Acme Corporation",
            "status": "In Progress",
            "status_color": "primary",
            "start_date": "2023-02-01",
            "end_date": "2023-06-30",
            "budget": 25000,
            "description": "Complete overhaul of corporate website with new branding",
            "manager": "Jane Doe",
            "team": ["John Smith", "Emily Johnson", "Michael Brown"],
            "progress": 45
        },
        {
            "id": 2,
            "name": "Mobile App Development",
            "client_id": 1,
            "client_name": "Acme Corporation",
            "status": "Planning",
            "status_color": "info",
            "start_date": "2023-07-15",
            "end_date": "2023-12-31",
            "budget": 50000,
            "description": "Development of iOS and Android mobile applications",
            "manager": "Mike Johnson",
            "team": ["Sarah Williams", "David Lee", "Jessica Taylor"],
            "progress": 10
        },
        {
            "id": 3,
            "name": "CRM Implementation",
            "client_id": 2,
            "client_name": "TechSolutions Inc",
            "status": "Completed",
            "status_color": "success",
            "start_date": "2023-01-10",
            "end_date": "2023-04-30",
            "budget": 35000,
            "description": "Implementation of custom CRM solution with integration to existing systems",
            "manager": "Robert Wilson",
            "team": ["Jennifer Davis", "Christopher Martinez", "Amanda Thompson"],
            "progress": 100
        },
        {
            "id": 4,
            "name": "Digital Marketing Campaign",
            "client_id": 4,
            "client_name": "Healthcare Partners",
            "status": "On Hold",
            "status_color": "warning",
            "start_date": "2023-03-15",
            "end_date": "2023-09-15",
            "budget": 15000,
            "description": "Comprehensive digital marketing campaign across multiple channels",
            "manager": "Lisa Anderson",
            "team": ["Daniel White", "Michelle Garcia"],
            "progress": 30
        },
        {
            "id": 5,
            "name": "IT Infrastructure Upgrade",
            "client_id": 3,
            "client_name": "Global Retail Group",
            "status": "Cancelled",
            "status_color": "danger",
            "start_date": "2023-02-20",
            "end_date": "2023-05-20",
            "budget": 40000,
            "description": "Upgrade of network infrastructure and server hardware",
            "manager": "Thomas Robinson",
            "team": ["Kevin Lewis", "Stephanie Hall", "Brian Young"],
            "progress": 15
        }
    ]
    
    # Filter projects by search query
    if search:
        search = search.lower()
        projects = [p for p in projects if search in p["name"].lower() or search in p["client_name"].lower()]
    
    # Filter projects by status
    if status:
        projects = [p for p in projects if p["status"] == status]
    
    # Sort projects
    if sort:
        if sort == "name_asc":
            projects = sorted(projects, key=lambda p: p["name"])
        elif sort == "name_desc":
            projects = sorted(projects, key=lambda p: p["name"], reverse=True)
        elif sort == "date_asc":
            projects = sorted(projects, key=lambda p: p["start_date"])
        elif sort == "date_desc":
            projects = sorted(projects, key=lambda p: p["start_date"], reverse=True)
        elif sort == "budget_asc":
            projects = sorted(projects, key=lambda p: p["budget"])
        elif sort == "budget_desc":
            projects = sorted(projects, key=lambda p: p["budget"], reverse=True)
    
    # Available statuses for filtering
    statuses = ["Planning", "In Progress", "On Hold", "Completed", "Cancelled"]
    
    # Prepare context with projects data
    context = {
        "request": request, 
        "session": request.session,
        "projects": projects,
        "statuses": statuses,
        "search_query": search or "",
        "current_status": status or "All"
    }
    
    return templates.TemplateResponse("projects.html", context)

@app.get("/projects/{project_id}", response_class=HTMLResponse)
async def project_detail(project_id: int, request: Request, session: dict = Depends(get_session)):
    if not check_auth(session):
        return RedirectResponse(url="/login")
    
    # Mock data for projects (reusing the same data from projects)
    projects = [
        {
            "id": 1,
            "name": "Website Redesign",
            "client_id": 1,
            "client_name": "Acme Corporation",
            "status": "In Progress",
            "status_color": "primary",
            "start_date": "2023-02-01",
            "end_date": "2023-06-30",
            "budget": 25000,
            "description": "Complete overhaul of corporate website with new branding",
            "manager": "Jane Doe",
            "team": ["John Smith", "Emily Johnson", "Michael Brown"],
            "progress": 45
        },
        {
            "id": 2,
            "name": "Mobile App Development",
            "client_id": 1,
            "client_name": "Acme Corporation",
            "status": "Planning",
            "status_color": "info",
            "start_date": "2023-07-15",
            "end_date": "2023-12-31",
            "budget": 50000,
            "description": "Development of iOS and Android mobile applications",
            "manager": "Mike Johnson",
            "team": ["Sarah Williams", "David Lee", "Jessica Taylor"],
            "progress": 10
        },
        {
            "id": 3,
            "name": "CRM Implementation",
            "client_id": 2,
            "client_name": "TechSolutions Inc",
            "status": "Completed",
            "status_color": "success",
            "start_date": "2023-01-10",
            "end_date": "2023-04-30",
            "budget": 35000,
            "description": "Implementation of custom CRM solution with integration to existing systems",
            "manager": "Robert Wilson",
            "team": ["Jennifer Davis", "Christopher Martinez", "Amanda Thompson"],
            "progress": 100
        },
        {
            "id": 4,
            "name": "Digital Marketing Campaign",
            "client_id": 4,
            "client_name": "Healthcare Partners",
            "status": "On Hold",
            "status_color": "warning",
            "start_date": "2023-03-15",
            "end_date": "2023-09-15",
            "budget": 15000,
            "description": "Comprehensive digital marketing campaign across multiple channels",
            "manager": "Lisa Anderson",
            "team": ["Daniel White", "Michelle Garcia"],
            "progress": 30
        },
        {
            "id": 5,
            "name": "IT Infrastructure Upgrade",
            "client_id": 3,
            "client_name": "Global Retail Group",
            "status": "Cancelled",
            "status_color": "danger",
            "start_date": "2023-02-20",
            "end_date": "2023-05-20",
            "budget": 40000,
            "description": "Upgrade of network infrastructure and server hardware",
            "manager": "Thomas Robinson",
            "team": ["Kevin Lewis", "Stephanie Hall", "Brian Young"],
            "progress": 15
        }
    ]
    
    # Find the project with the matching ID
    project = next((p for p in projects if p["id"] == project_id), None)
    
    # If project not found, return 404
    if not project:
        return templates.TemplateResponse(
            "error.html", 
            {"request": request, "session": request.session, "status_code": 404, "detail": f"Project with ID {project_id} not found"}
        )
    
    # Mock tasks for this project
    tasks = [
        {
            "id": 101,
            "name": "Requirements Gathering",
            "status": "Completed",
            "status_color": "success",
            "due_date": "2023-02-15",
            "assigned_to": "John Smith",
            "priority": "High",
            "description": "Gather and document all requirements for the project"
        },
        {
            "id": 102,
            "name": "Design Mockups",
            "status": "Completed",
            "status_color": "success",
            "due_date": "2023-03-01",
            "assigned_to": "Emily Johnson",
            "priority": "Medium",
            "description": "Create design mockups for all pages"
        },
        {
            "id": 103,
            "name": "Frontend Development",
            "status": "In Progress",
            "status_color": "primary",
            "due_date": "2023-04-15",
            "assigned_to": "Michael Brown",
            "priority": "High",
            "description": "Implement frontend components based on approved designs"
        },
        {
            "id": 104,
            "name": "Backend Development",
            "status": "In Progress",
            "status_color": "primary",
            "due_date": "2023-05-01",
            "assigned_to": "John Smith",
            "priority": "High",
            "description": "Implement backend APIs and database integration"
        },
        {
            "id": 105,
            "name": "Testing",
            "status": "Not Started",
            "status_color": "secondary",
            "due_date": "2023-05-15",
            "assigned_to": "Emily Johnson",
            "priority": "Medium",
            "description": "Perform comprehensive testing of all features"
        },
        {
            "id": 106,
            "name": "Deployment",
            "status": "Not Started",
            "status_color": "secondary",
            "due_date": "2023-06-15",
            "assigned_to": "Michael Brown",
            "priority": "High",
            "description": "Deploy the application to production environment"
        }
    ] if project_id == 1 else []
    
    # Mock milestones for this project
    milestones = [
        {
            "id": 201,
            "name": "Project Kickoff",
            "date": "2023-02-01",
            "status": "Completed",
            "status_color": "success",
            "description": "Initial project kickoff meeting with all stakeholders"
        },
        {
            "id": 202,
            "name": "Design Approval",
            "date": "2023-03-15",
            "status": "Completed",
            "status_color": "success",
            "description": "Approval of all design mockups by client"
        },
        {
            "id": 203,
            "name": "Alpha Release",
            "date": "2023-04-30",
            "status": "In Progress",
            "status_color": "primary",
            "description": "Initial alpha release for internal testing"
        },
        {
            "id": 204,
            "name": "Beta Release",
            "date": "2023-05-30",
            "status": "Not Started",
            "status_color": "secondary",
            "description": "Beta release for client testing"
        },
        {
            "id": 205,
            "name": "Final Delivery",
            "date": "2023-06-30",
            "status": "Not Started",
            "status_color": "secondary",
            "description": "Final delivery of the project"
        }
    ] if project_id == 1 else []
    
    # Mock expenses for this project
    expenses = [
        {
            "id": 301,
            "description": "Software Licenses",
            "date": "2023-02-10",
            "amount": 1200,
            "category": "Software",
            "submitted_by": "Jane Doe"
        },
        {
            "id": 302,
            "description": "Design Tools Subscription",
            "date": "2023-02-15",
            "amount": 500,
            "category": "Software",
            "submitted_by": "Emily Johnson"
        },
        {
            "id": 303,
            "description": "Client Meeting Lunch",
            "date": "2023-03-05",
            "amount": 150,
            "category": "Meals",
            "submitted_by": "Jane Doe"
        },
        {
            "id": 304,
            "description": "Stock Photos",
            "date": "2023-03-20",
            "amount": 300,
            "category": "Content",
            "submitted_by": "Emily Johnson"
        }
    ] if project_id == 1 else []
    
    # Mock time entries for this project
    time_entries = [
        {
            "id": 401,
            "task": "Requirements Gathering",
            "date": "2023-02-05",
            "hours": 8,
            "user": "John Smith",
            "notes": "Initial requirements gathering session with client"
        },
        {
            "id": 402,
            "task": "Requirements Documentation",
            "date": "2023-02-06",
            "hours": 6,
            "user": "John Smith",
            "notes": "Documenting requirements from client meeting"
        },
        {
            "id": 403,
            "task": "Design Research",
            "date": "2023-02-10",
            "hours": 4,
            "user": "Emily Johnson",
            "notes": "Research on design trends and competitor websites"
        },
        {
            "id": 404,
            "task": "Initial Mockups",
            "date": "2023-02-15",
            "hours": 8,
            "user": "Emily Johnson",
            "notes": "Creating initial mockups for homepage and key pages"
        },
        {
            "id": 405,
            "task": "Client Review Meeting",
            "date": "2023-02-20",
            "hours": 2,
            "user": "Jane Doe",
            "notes": "Meeting with client to review initial mockups"
        }
    ] if project_id == 1 else []
    
    # Prepare context with project and related data
    context = {
        "request": request, 
        "session": request.session,
        "project": project,
        "tasks": tasks,
        "milestones": milestones,
        "expenses": expenses,
        "time_entries": time_entries
    }
    
    return templates.TemplateResponse("project_detail.html", context)

@app.get("/projects/new", response_class=HTMLResponse)
async def new_project(request: Request, session: dict = Depends(get_session), customer_id: int = None):
    if not check_auth(session):
        return RedirectResponse(url="/login")
    
    # Mock data for contacts/clients
    contacts = [
        {"id": 1, "name": "Acme Corporation"},
        {"id": 2, "name": "TechSolutions Inc"},
        {"id": 3, "name": "Global Retail Group"},
        {"id": 4, "name": "Healthcare Partners"},
        {"id": 5, "name": "EduLearn Academy"}
    ]
    
    # Create an empty project object for the form
    project = None
    
    # If customer_id is provided, pre-select that customer
    selected_client_id = customer_id
    
    # Prepare context with project data and contacts
    context = {
        "request": request, 
        "session": request.session,
        "project": project,
        "contacts": contacts,
        "selected_client_id": selected_client_id
    }
    
    return templates.TemplateResponse("project_form.html", context)

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
async def edit_project(project_id: int, request: Request, session: dict = Depends(get_session)):
    if not check_auth(session):
        return RedirectResponse(url="/login")
    
    # Mock data for projects (reusing the same data from projects)
    projects = [
        {
            "id": 1,
            "name": "Website Redesign",
            "client_id": 1,
            "client_name": "Acme Corporation",
            "status": "In Progress",
            "status_color": "primary",
            "start_date": "2023-02-01",
            "end_date": "2023-06-30",
            "budget": 25000,
            "description": "Complete overhaul of corporate website with new branding",
            "manager": "Jane Doe",
            "team": ["John Smith", "Emily Johnson", "Michael Brown"],
            "progress": 45
        },
        {
            "id": 2,
            "name": "Mobile App Development",
            "client_id": 1,
            "client_name": "Acme Corporation",
            "status": "Planning",
            "status_color": "info",
            "start_date": "2023-07-15",
            "end_date": "2023-12-31",
            "budget": 50000,
            "description": "Development of iOS and Android mobile applications",
            "manager": "Mike Johnson",
            "team": ["Sarah Williams", "David Lee", "Jessica Taylor"],
            "progress": 10
        },
        {
            "id": 3,
            "name": "CRM Implementation",
            "client_id": 2,
            "client_name": "TechSolutions Inc",
            "status": "Completed",
            "status_color": "success",
            "start_date": "2023-01-10",
            "end_date": "2023-04-30",
            "budget": 35000,
            "description": "Implementation of custom CRM solution with integration to existing systems",
            "manager": "Robert Wilson",
            "team": ["Jennifer Davis", "Christopher Martinez", "Amanda Thompson"],
            "progress": 100
        },
        {
            "id": 4,
            "name": "Digital Marketing Campaign",
            "client_id": 4,
            "client_name": "Healthcare Partners",
            "status": "On Hold",
            "status_color": "warning",
            "start_date": "2023-03-15",
            "end_date": "2023-09-15",
            "budget": 15000,
            "description": "Comprehensive digital marketing campaign across multiple channels",
            "manager": "Lisa Anderson",
            "team": ["Daniel White", "Michelle Garcia"],
            "progress": 30
        },
        {
            "id": 5,
            "name": "IT Infrastructure Upgrade",
            "client_id": 3,
            "client_name": "Global Retail Group",
            "status": "Cancelled",
            "status_color": "danger",
            "start_date": "2023-02-20",
            "end_date": "2023-05-20",
            "budget": 40000,
            "description": "Upgrade of network infrastructure and server hardware",
            "manager": "Thomas Robinson",
            "team": ["Kevin Lewis", "Stephanie Hall", "Brian Young"],
            "progress": 15
        }
    ]
    
    # Find the project with the matching ID
    project = next((p for p in projects if p["id"] == project_id), None)
    
    # If project not found, return 404
    if not project:
        return templates.TemplateResponse(
            "error.html", 
            {"request": request, "session": request.session, "status_code": 404, "detail": f"Project with ID {project_id} not found"}
        )
    
    # Mock data for contacts/clients
    contacts = [
        {"id": 1, "name": "Acme Corporation"},
        {"id": 2, "name": "TechSolutions Inc"},
        {"id": 3, "name": "Global Retail Group"},
        {"id": 4, "name": "Healthcare Partners"},
        {"id": 5, "name": "EduLearn Academy"}
    ]
    
    # Prepare context with project data and contacts
    context = {
        "request": request, 
        "session": request.session,
        "project": project,
        "contacts": contacts
    }
    
    return templates.TemplateResponse("project_form.html", context)

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
async def time_logs(request: Request, session: dict = Depends(get_session), page: int = 1, search_query: str = None, status_filter: str = None, project_filter: str = None):
    if not check_auth(session):
        return RedirectResponse(url="/login")
    
    # Mock data for time logs
    mock_time_logs = [
        {"id": 1, "date": "2025-03-01", "project": "Office Renovation", "task": "Electrical Work", "user": "Admin", "hours": 4.5, "description": "Installed new lighting fixtures", "billable": True, "status": "Approved", "status_color": "success"},
        {"id": 2, "date": "2025-03-02", "project": "Warehouse Expansion", "task": "Planning", "user": "Admin", "hours": 2.0, "description": "Meeting with architects", "billable": True, "status": "Approved", "status_color": "success"},
        {"id": 3, "date": "2025-03-03", "project": "Office Renovation", "task": "Plumbing", "user": "Admin", "hours": 6.0, "description": "Bathroom fixtures installation", "billable": True, "status": "Pending", "status_color": "warning"},
        {"id": 4, "date": "2025-03-04", "project": "Retail Store Remodel", "task": "Demolition", "user": "Admin", "hours": 8.0, "description": "Removed old fixtures and walls", "billable": True, "status": "Pending", "status_color": "warning"},
        {"id": 5, "date": "2025-03-05", "project": "Office Renovation", "task": "Painting", "user": "Admin", "hours": 7.5, "description": "Painted main office area", "billable": True, "status": "Pending", "status_color": "warning"},
        {"id": 6, "date": "2025-03-06", "project": "Warehouse Expansion", "task": "Foundation", "user": "Admin", "hours": 8.0, "description": "Supervised foundation pouring", "billable": True, "status": "Pending", "status_color": "warning"},
        {"id": 7, "date": "2025-03-07", "project": "Retail Store Remodel", "task": "Electrical Work", "user": "Admin", "hours": 5.0, "description": "Rewired sales floor", "billable": True, "status": "Draft", "status_color": "secondary"},
    ]
    
    # Pagination variables
    items_per_page = 10
    total_items = len(mock_time_logs)
    total_pages = (total_items + items_per_page - 1) // items_per_page  # Ceiling division
    
    # Ensure page is within valid range
    if page < 1:
        page = 1
    elif page > total_pages and total_pages > 0:
        page = total_pages
    
    # Calculate pagination indices
    start_idx = (page - 1) * items_per_page
    end_idx = min(start_idx + items_per_page, total_items)
    
    # Get time logs for current page
    paginated_time_logs = mock_time_logs[start_idx:end_idx]
    
    # Mock projects for filter
    projects = ["Office Renovation", "Warehouse Expansion", "Retail Store Remodel"]
    
    # Mock statuses for filter
    statuses = ["Draft", "Pending", "Approved", "Rejected"]
    
    # Prepare context with pagination data
    context = {
        "request": request, 
        "session": request.session,
        "time_logs": paginated_time_logs,
        "page": page,
        "total_pages": total_pages,
        "search_query": search_query or "",
        "status_filter": status_filter or "",
        "project_filter": project_filter or "",
        "projects": projects,
        "statuses": statuses,
        "total_hours": sum(log["hours"] for log in mock_time_logs),
        "billable_hours": sum(log["hours"] for log in mock_time_logs if log["billable"]),
        "pending_hours": sum(log["hours"] for log in mock_time_logs if log["status"] == "Pending")
    }
    
    return templates.TemplateResponse("time_logs.html", context)

@app.get("/time-logs/new", response_class=HTMLResponse)
async def new_time_log(request: Request, session: dict = Depends(get_session), project_id: int = None):
    if not check_auth(session):
        return RedirectResponse(url="/login")
    
    # Mock projects for selection
    projects = [
        (1, "Office Renovation"),
        (2, "Warehouse Expansion"),
        (3, "Retail Store Remodel")
    ]
    
    # Mock tasks for the selected project
    project_tasks = []
    selected_project = None
    
    if project_id:
        # In a real app, we would fetch tasks for the selected project from the database
        if project_id == 1:
            project_tasks = [(1, "Electrical Work"), (2, "Plumbing"), (3, "Painting")]
            selected_project = {"id": 1, "name": "Office Renovation"}
        elif project_id == 2:
            project_tasks = [(4, "Planning"), (5, "Foundation"), (6, "Framing")]
            selected_project = {"id": 2, "name": "Warehouse Expansion"}
        elif project_id == 3:
            project_tasks = [(7, "Demolition"), (8, "Electrical Work"), (9, "Fixtures")]
            selected_project = {"id": 3, "name": "Retail Store Remodel"}
    
    return templates.TemplateResponse("time_log_form.html", {
        "request": request, 
        "session": request.session,
        "projects": projects,
        "project_tasks": project_tasks,
        "selected_project": selected_project,
        "time_log": None
    })

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
    
    # Mock time log data
    # In a real app, we would fetch this from the database
    mock_time_logs = {
        1: {"id": 1, "date": "2025-03-01", "project_id": 1, "project_name": "Office Renovation", 
            "task_id": 1, "task_name": "Electrical Work", "user_id": 1, "user_name": "Admin", 
            "hours": 4.5, "description": "Installed new lighting fixtures", "billable": True, "status": "Approved"},
        2: {"id": 2, "date": "2025-03-02", "project_id": 2, "project_name": "Warehouse Expansion", 
            "task_id": 4, "task_name": "Planning", "user_id": 1, "user_name": "Admin", 
            "hours": 2.0, "description": "Meeting with architects", "billable": True, "status": "Approved"},
        3: {"id": 3, "date": "2025-03-03", "project_id": 1, "project_name": "Office Renovation", 
            "task_id": 2, "task_name": "Plumbing", "user_id": 1, "user_name": "Admin", 
            "hours": 6.0, "description": "Bathroom fixtures installation", "billable": True, "status": "Pending"}
    }
    
    # Get the time log or return 404
    time_log = mock_time_logs.get(log_id)
    if not time_log:
        return templates.TemplateResponse("404.html", {"request": request, "session": request.session}, status_code=404)
    
    # Mock projects for selection
    projects = [
        (1, "Office Renovation"),
        (2, "Warehouse Expansion"),
        (3, "Retail Store Remodel")
    ]
    
    # Use project_id from query param if provided, otherwise use the time log's project_id
    project_id = project_id if project_id else time_log["project_id"]
    
    # Mock tasks for the selected project
    project_tasks = []
    selected_project = None
    
    if project_id:
        # In a real app, we would fetch tasks for the selected project from the database
        if project_id == 1:
            project_tasks = [(1, "Electrical Work"), (2, "Plumbing"), (3, "Painting")]
            selected_project = {"id": 1, "name": "Office Renovation"}
        elif project_id == 2:
            project_tasks = [(4, "Planning"), (5, "Foundation"), (6, "Framing")]
            selected_project = {"id": 2, "name": "Warehouse Expansion"}
        elif project_id == 3:
            project_tasks = [(7, "Demolition"), (8, "Electrical Work"), (9, "Fixtures")]
            selected_project = {"id": 3, "name": "Retail Store Remodel"}
    
    return templates.TemplateResponse("time_log_form.html", {
        "request": request, 
        "session": request.session,
        "time_log": time_log,
        "projects": projects,
        "project_tasks": project_tasks,
        "selected_project": selected_project
    })

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
async def project_time_logs(request: Request, project_id: int, session: dict = Depends(get_session)):
    if not check_auth(session):
        return RedirectResponse(url="/login")
    
    # Mock project data
    # In a real app, we would fetch this from the database
    mock_projects = {
        1: {"id": 1, "name": "Office Renovation", "customer_name": "Acme Corporation"},
        2: {"id": 2, "name": "Mobile App Development", "customer_name": "Acme Corporation"},
        3: {"id": 3, "name": "CRM Implementation", "customer_name": "TechSolutions Inc"},
        4: {"id": 4, "name": "Digital Marketing Campaign", "customer_name": "Healthcare Partners"}
    }
    
    # Get the project or return 404
    project = mock_projects.get(project_id)
    if not project:
        return templates.TemplateResponse(
            "error.html", 
            {"request": request, "session": request.session, "status_code": 404, "detail": f"Project with ID {project_id} not found"}
        )
    
    # Mock data for time logs filtered by project
    mock_time_logs = [
        {"id": 1, "date": "2025-03-01", "project_id": 1, "project_name": "Office Renovation", 
         "task_name": "Electrical Work", "user_name": "Admin", "hours": 4.5, 
         "description": "Installed new lighting fixtures", "billable": True, "status": "Approved", "status_color": "success"},
        {"id": 3, "date": "2025-03-03", "project_id": 1, "project_name": "Office Renovation", 
         "task_name": "Plumbing", "user_name": "Admin", "hours": 6.0, 
         "description": "Bathroom fixtures installation", "billable": True, "status": "Pending", "status_color": "warning"},
        {"id": 5, "date": "2025-03-05", "project_id": 1, "project_name": "Office Renovation", 
         "task_name": "Painting", "user_name": "Admin", "hours": 7.5, 
         "description": "Painted main office area", "billable": True, "status": "Pending", "status_color": "warning"}
    ]
    
    # Filter time logs by project
    project_time_logs = [log for log in mock_time_logs if log["project_id"] == project_id]
    
    # Mock statuses for filter
    statuses = ["Draft", "Pending", "Approved", "Rejected"]
    
    # Prepare context
    context = {
        "request": request, 
        "session": request.session,
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
    page: int = 1
):
    if not check_auth(session):
        return RedirectResponse(url="/login")
    
    # Mock data for expenses
    mock_expenses = [
        {
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
            "receipt": True,
            "submitted_by": "John Doe"
        },
        {
            "id": 2,
            "date": "2023-03-05",
            "category": "Equipment Rental",
            "vendor_id": 5,
            "vendor_name": "Equipment Rental Co",
            "project_id": 1,
            "project_name": "Office Renovation",
            "amount": 450.00,
            "description": "Concrete mixer rental (3 days)",
            "status": "Approved",
            "status_color": "success",
            "receipt": True,
            "submitted_by": "John Doe"
        },
        {
            "id": 3,
            "date": "2023-03-10",
            "category": "Subcontractor",
            "vendor_id": 1,
            "vendor_name": "Elite Electrical Services",
            "project_id": 1,
            "project_name": "Office Renovation",
            "amount": 2800.00,
            "description": "Electrical work - Phase 1",
            "status": "Approved",
            "status_color": "success",
            "receipt": True,
            "submitted_by": "John Doe"
        },
        {
            "id": 4,
            "date": "2023-03-15",
            "category": "Permits",
            "vendor_id": None,
            "vendor_name": "City Building Department",
            "project_id": 1,
            "project_name": "Office Renovation",
            "amount": 350.00,
            "description": "Building permit fees",
            "status": "Pending",
            "status_color": "warning",
            "receipt": True,
            "submitted_by": "Jane Smith"
        },
        {
            "id": 5,
            "date": "2023-03-20",
            "category": "Materials",
            "vendor_id": 3,
            "vendor_name": "Quality Construction Materials",
            "project_id": 1,
            "project_name": "Office Renovation",
            "amount": 875.00,
            "description": "Paint and finishing materials",
            "status": "Pending",
            "status_color": "warning",
            "receipt": False,
            "submitted_by": "Jane Smith"
        }
    ]
    
    # Filter by search query
    if search:
        search = search.lower()
        mock_expenses = [e for e in mock_expenses if search in e["description"].lower() or 
                         search in e["vendor_name"].lower() or 
                         search in e["project_name"].lower() or
                         search in e["category"].lower()]
    
    # Filter by category
    if category:
        mock_expenses = [e for e in mock_expenses if e["category"] == category]
    
    # Filter by project
    if project_id:
        mock_expenses = [e for e in mock_expenses if e["project_id"] == project_id]
    
    # Filter by date range
    if date_from:
        mock_expenses = [e for e in mock_expenses if e["date"] >= date_from]
    
    if date_to:
        mock_expenses = [e for e in mock_expenses if e["date"] <= date_to]
    
    # Pagination variables
    items_per_page = 10
    total_items = len(mock_expenses)
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
    paginated_expenses = mock_expenses[start_idx:end_idx]
    
    # Expense categories for filtering
    expense_categories = ["Materials", "Equipment Rental", "Subcontractor", "Permits", "Labor", "Travel", "Office", "Other"]
    
    # Mock projects for filtering
    projects = [
        {"id": 1, "name": "Office Renovation"},
        {"id": 2, "name": "Mobile App Development"},
        {"id": 3, "name": "CRM Implementation"},
        {"id": 4, "name": "Digital Marketing Campaign"}
    ]
    
    # Calculate summary statistics
    total_amount = sum(e["amount"] for e in mock_expenses)
    approved_amount = sum(e["amount"] for e in mock_expenses if e["status"] == "Approved")
    pending_amount = sum(e["amount"] for e in mock_expenses if e["status"] == "Pending")
    
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
        "date_from": date_from or "",
        "date_to": date_to or "",
        "categories": expense_categories,
        "projects": projects,
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
        
        return templates.TemplateResponse(
            "vendors.html",
            {
                "request": request,
                "session": request.session,
                "vendors": vendors,
                "material_categories": MATERIAL_CATEGORIES
            }
        )
    except Exception as e:
        print(f"Error listing vendors: {str(e)}")
        # Fall back to mock data on error
        vendors = MOCK_VENDORS
        if material_category:
            vendors = [v for v in vendors if material_category in v.get('material_categories', [])]
        if preferred_only:
            vendors = [v for v in vendors if v.get('is_preferred')]
        if status:
            vendors = [v for v in vendors if v.get('status') == status]
            
        return templates.TemplateResponse(
            "vendors.html",
            {
                "request": request,
                "session": request.session,
                "vendors": vendors,
                "material_categories": MATERIAL_CATEGORIES
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
                    "insurance_status": "Valid" if vendor.get("insurance_expiry") and datetime.fromisoformat(vendor["insurance_expiry"]) > datetime.now() else "Expired"
                }
        else:
            # Use mock data
            vendor = next((v for v in MOCK_VENDORS if v['id'] == vendor_id), None)
            if vendor:
                metrics = {
                    "total_purchases": len([p for p in MOCK_MATERIALS if p['vendor_id'] == vendor_id]),
                    "active_projects": 2,  # Mock value
                    "insurance_status": "Valid" if vendor.get("insurance_expiry") and datetime.fromisoformat(vendor["insurance_expiry"]) > datetime.now() else "Expired"
                }
        
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
            "insurance_status": "Valid" if vendor.get("insurance_expiry") and datetime.fromisoformat(vendor["insurance_expiry"]) > datetime.now() else "Expired"
        }
        
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
            "insurance_expiry": insurance_expiry,
            "certifications": certifications.split('\n') if certifications else [],
            "notes": notes,
            "updated_at": datetime.utcnow()
        }
        
        # Handle insurance document upload if provided
        if insurance_document:
            document_url = await save_uploaded_file(
                insurance_document, 
                f"vendors/{vendor_id}/insurance",
                metadata={
                    "type": "insurance",
                    "policy_number": insurance_policy,
                    "expiry_date": insurance_expiry
                }
            )
            vendor_data["insurance_document_url"] = document_url
        
        # Update vendor in database
        if supabase:
            response = supabase.from_("vendors").update(vendor_data).eq("id", vendor_id).execute()
            result = response.data[0] if response.data else None
        else:
            # Update mock data
            for i, vendor in enumerate(MOCK_VENDORS):
                if vendor['id'] == vendor_id:
                    MOCK_VENDORS[i].update(vendor_data)
                    result = MOCK_VENDORS[i]
                    break
            else:
                result = None
        
        if not result:
            raise HTTPException(status_code=404, detail="Vendor not found")
        
        return RedirectResponse(
            url=f"/vendors/{vendor_id}",
            status_code=303
        )
    except Exception as e:
        print(f"Error updating vendor: {e}")
        raise HTTPException(status_code=500, detail=str(e))

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
    notes: str = Form(None)
):
    """Handle customer creation form submission."""
    if not check_auth(session):
        return RedirectResponse(url="/login")
    
    try:
        # Create new customer data
        new_customer = {
            "id": len(MOCK_CUSTOMERS) + 1,  # Simple ID generation for mock data
            "name": name,
            "contact_name": contact_name,
            "email": email,
            "phone": phone,
            "address": address or "",
            "city": city or "",
            "state": state or "",
            "zip": zip or "",
            "status": status,
            "customer_since": customer_since or datetime.now().strftime("%Y-%m-%d"),
            "payment_terms": payment_terms,
            "credit_limit": credit_limit,
            "notes": notes or "",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # Try to save to Supabase if available
        supabase_client = get_supabase_client()
        if supabase_client:
            result = supabase_client.table("customers").insert(new_customer).execute()
            if result.data:
                new_customer = result.data[0]
        else:
            # Just add to mock data
            MOCK_CUSTOMERS.append(new_customer)
        
        # Redirect to customer detail page
        return RedirectResponse(url=f"/customers/{new_customer['id']}", status_code=303)
    
    except Exception as e:
        print(f"Error creating customer: {str(e)}")
        
        # Return the form with error
        statuses = ["Active", "Inactive", "Pending", "VIP"]
        payment_terms = ["Net 15", "Net 30", "Net 45", "Net 60", "Due on Receipt"]
        
        return templates.TemplateResponse(
            "customer_form.html", 
            {
                "request": request, 
                "session": request.session, 
                "customer": {
                    "id": None,
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
                    "notes": notes
                },
                "statuses": statuses,
                "payment_terms": payment_terms,
                "error": str(e)
            },
            status_code=400
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
                    "session": request.session,
                    "status_code": 404,
                    "detail": f"Customer with ID {customer_id} not found"
                },
                status_code=404
            )
        
        # Get related projects for this customer (mock data for now)
        projects = [
            {
                "id": 1,
                "name": "Office Renovation",
                "status": "In Progress",
                "start_date": "2025-01-15",
                "end_date": "2025-04-30",
                "budget": 75000.00,
                "progress": 40
            },
            {
                "id": 2,
                "name": "Warehouse Expansion",
                "status": "Planning",
                "start_date": "2025-05-01",
                "end_date": "2025-08-31",
                "budget": 150000.00,
                "progress": 10
            }
        ] if customer_id == 1 else []
        
        # Return the customer detail template
        return templates.TemplateResponse(
            "customer_detail.html", 
            {
                "request": request, 
                "session": request.session,
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
                "session": request.session,
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
    notes: str = Form(None)
):
    """Handle customer update form submission."""
    if not check_auth(session):
        return RedirectResponse(url="/login")
    
    try:
        # Prepare updated customer data
        updated_customer = {
            "name": name,
            "contact_name": contact_name,
            "email": email,
            "phone": phone,
            "address": address or "",
            "city": city or "",
            "state": state or "",
            "zip": zip or "",
            "status": status,
            "customer_since": customer_since or datetime.now().strftime("%Y-%m-%d"),
            "payment_terms": payment_terms,
            "credit_limit": credit_limit,
            "notes": notes or "",
            "updated_at": datetime.now().isoformat()
        }
        
        # Try to update in Supabase if available
        supabase_client = get_supabase_client()
        if supabase_client:
            result = supabase_client.table("customers").update(updated_customer).eq("id", customer_id).execute()
            if result.data:
                updated_customer = result.data[0]
        else:
            # Update in mock data
            for i, customer in enumerate(MOCK_CUSTOMERS):
                if customer["id"] == customer_id:
                    # Preserve id and created_at
                    updated_customer["id"] = customer_id
                    updated_customer["created_at"] = customer["created_at"]
                    MOCK_CUSTOMERS[i] = updated_customer
                    break
        
        # Redirect to customer detail page
        return RedirectResponse(url=f"/customers/{customer_id}", status_code=303)
    
    except Exception as e:
        print(f"Error updating customer {customer_id}: {str(e)}")
        
        # Return the form with error
        statuses = ["Active", "Inactive", "Pending", "VIP"]
        payment_terms = ["Net 15", "Net 30", "Net 45", "Net 60", "Due on Receipt"]
        
        return templates.TemplateResponse(
            "customer_form.html", 
            {
                "request": request, 
                "session": request.session, 
                "customer": {
                    "id": customer_id,
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
                    "notes": notes
                },
                "statuses": statuses,
                "payment_terms": payment_terms,
                "error": str(e)
            },
            status_code=400
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