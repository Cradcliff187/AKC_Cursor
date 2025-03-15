"""
Customer management routes for the AKC CRM application.
"""

from fastapi import APIRouter, Request, Depends, Form, HTTPException, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from dependencies import get_session, check_auth, templates, get_supabase_client
from routes.auth import require_auth
from mock_data import MOCK_CUSTOMERS
import traceback
from typing import Optional, List
from datetime import datetime
import json

router = APIRouter()

# Mock customer data for when Supabase is unavailable
MOCK_CUSTOMERS = [
    {
        "id": "1",
        "name": "ABC Corporation",
        "contact_name": "John Smith",
        "email": "john@abccorp.com",
        "phone": "555-123-4567",
        "address": "123 Main St, Anytown, USA",
        "type": "Commercial",
        "status": "Active",
        "created_at": "2024-01-15T08:00:00",
        "notes": "Large commercial client with multiple properties"
    },
    {
        "id": "2",
        "name": "XYZ Enterprises",
        "contact_name": "Jane Doe",
        "email": "jane@xyzent.com",
        "phone": "555-987-6543",
        "address": "456 Oak Ave, Business Park, USA",
        "type": "Industrial",
        "status": "Active",
        "created_at": "2024-02-10T10:15:00",
        "notes": "Industrial client with specialized requirements"
    },
    {
        "id": "3",
        "name": "Sunrise Residential",
        "contact_name": "Robert Johnson",
        "email": "robert@sunriseresidential.com",
        "phone": "555-456-7890",
        "address": "789 Elm St, Hometown, USA",
        "type": "Residential",
        "status": "Inactive",
        "created_at": "2024-03-05T14:30:00",
        "notes": "Residential development project"
    }
]

@router.get("/customers", response_class=HTMLResponse)
async def list_customers(
    request: Request,
    session: dict = Depends(require_auth),
    search: Optional[str] = None,
    status: Optional[str] = None,
    type: Optional[str] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100)
):
    """List all customers with optional filtering and pagination."""
    try:
        supabase = get_supabase_client()
        offset = (page - 1) * per_page
        
        # Use mock data if Supabase client is unavailable
        if supabase is None:
            filtered_customers = MOCK_CUSTOMERS.copy()
            
            # Apply filters to mock data
            if search:
                search = search.lower()
                filtered_customers = [c for c in filtered_customers if 
                                     search in c["name"].lower() or 
                                     search in c["contact_name"].lower() or
                                     search in c["email"].lower()]
            
            if status:
                filtered_customers = [c for c in filtered_customers if c["status"] == status]
                
            if type:
                filtered_customers = [c for c in filtered_customers if c["type"] == type]
            
            # Get total count for pagination
            total_count = len(filtered_customers)
            
            # Apply pagination
            customers = filtered_customers[offset:offset+per_page]
            
            # Get available statuses and types for filters
            available_statuses = list(set(c["status"] for c in MOCK_CUSTOMERS))
            available_types = list(set(c["type"] for c in MOCK_CUSTOMERS))
        else:
            # Use Supabase for data retrieval
            query = supabase.table("customers").select("*")
            
            if search:
                query = query.or_(f"name.ilike.%{search}%,contact_name.ilike.%{search}%,email.ilike.%{search}%")
            
            if status:
                query = query.eq("status", status)
                
            if type:
                query = query.eq("type", type)
            
            # First get the total count for pagination
            count_response = query.execute()
            if not count_response.data:
                count_response.data = []
            total_count = len(count_response.data)
            
            # Then get the paginated results
            query = query.range(offset, offset + per_page - 1).order("name")
            response = query.execute()
            customers = response.data if response.data else []
            
            # Get available statuses and types for filters
            status_response = supabase.table("customers").select("status").execute()
            status_data = status_response.data if status_response.data else []
            available_statuses = list(set(item["status"] for item in status_data if item.get("status")))
            
            type_response = supabase.table("customers").select("type").execute()
            type_data = type_response.data if type_response.data else []
            available_types = list(set(item["type"] for item in type_data if item.get("type")))
        
        # Calculate pagination info
        total_pages = (total_count + per_page - 1) // per_page
        has_next = page < total_pages
        has_prev = page > 1
        
        return templates.TemplateResponse(
            "customers.html",
            {
                "request": request,
                "session": session,
                "customers": customers,
                "search": search,
                "status": status,
                "type": type,
                "available_statuses": available_statuses,
                "available_types": available_types,
                "page": page,
                "per_page": per_page,
                "total_count": total_count,
                "total_pages": total_pages,
                "has_next": has_next,
                "has_prev": has_prev,
                "active_page": "customers"
            }
        )
    except Exception as e:
        # Log the error and return a user-friendly error page
        print(f"Error listing customers: {str(e)}")
        traceback.print_exc()
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "session": session,
                "error_code": 500,
                "error_message": "Could not retrieve customer data. Please try again later."
            }
        )

@router.get("/customers/new", response_class=HTMLResponse)
async def new_customer_form(
    request: Request,
    session: dict = Depends(require_auth)
):
    """Display form to create a new customer."""
    try:
        return templates.TemplateResponse(
            "customer_form.html",
            {
                "request": request,
                "session": session,
                "customer": {},
                "is_new": True
            }
        )
    except Exception as e:
        print(f"Error loading customer form: {str(e)}")
        traceback.print_exc()
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "session": session,
                "error_code": 500,
                "error_message": "Error loading customer form"
            }
        )

@router.post("/customers/new", response_class=RedirectResponse)
async def create_customer(
    request: Request,
    session: dict = Depends(require_auth),
    name: str = Form(...),
    company: str = Form(...),
    email: str = Form(None),
    phone: str = Form(None),
    address: str = Form(None),
    notes: str = Form(None)
):
    """Create a new customer."""
    try:
        # In real implementation, would insert into Supabase
        # For now, just redirect to customers list
        return RedirectResponse(url="/customers", status_code=303)
    except Exception as e:
        print(f"Error creating customer: {str(e)}")
        traceback.print_exc()
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "session": session,
                "error_code": 500,
                "error_message": "Error creating customer"
            }
        )

@router.get("/customers/{customer_id}", response_class=HTMLResponse)
async def customer_detail(
    request: Request,
    customer_id: int,
    session: dict = Depends(require_auth)
):
    """View customer details."""
    try:
        # Get customer with specified ID from mock data or Supabase
        customer = next((c for c in MOCK_CUSTOMERS if c["id"] == str(customer_id)), None)
        
        if not customer:
            return templates.TemplateResponse(
                "error.html",
                {
                    "request": request,
                    "session": session,
                    "error_code": 404,
                    "error_message": f"Customer with ID {customer_id} not found"
                }
            )
        
        # Get related projects for this customer
        from mock_data import MOCK_PROJECTS
        related_projects = [p for p in MOCK_PROJECTS if p.get("client_id") == customer_id]
        
        # Get related invoices for this customer
        related_invoices = []  # Would be fetched from database
        
        return templates.TemplateResponse(
            "customer_detail.html",
            {
                "request": request,
                "session": session,
                "customer": customer,
                "projects": related_projects,
                "invoices": related_invoices
            }
        )
    except Exception as e:
        print(f"Error loading customer {customer_id}: {str(e)}")
        traceback.print_exc()
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "session": session,
                "error_code": 500,
                "error_message": f"Error loading customer {customer_id}"
            }
        )

@router.get("/customers/{customer_id}/edit", response_class=HTMLResponse)
async def edit_customer_form(
    request: Request,
    customer_id: int,
    session: dict = Depends(require_auth)
):
    """Display form to edit a customer."""
    try:
        # Get customer with specified ID from mock data or Supabase
        customer = next((c for c in MOCK_CUSTOMERS if c["id"] == str(customer_id)), None)
        
        if not customer:
            return templates.TemplateResponse(
                "error.html",
                {
                    "request": request,
                    "session": session,
                    "error_code": 404,
                    "error_message": f"Customer with ID {customer_id} not found"
                }
            )
        
        return templates.TemplateResponse(
            "customer_form.html",
            {
                "request": request,
                "session": session,
                "customer": customer,
                "is_new": False
            }
        )
    except Exception as e:
        print(f"Error loading customer {customer_id} for editing: {str(e)}")
        traceback.print_exc()
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "session": session,
                "error_code": 500,
                "error_message": f"Error loading customer {customer_id} for editing"
            }
        )

@router.post("/customers/{customer_id}/edit", response_class=RedirectResponse)
async def update_customer(
    request: Request,
    customer_id: int,
    session: dict = Depends(require_auth),
    name: str = Form(...),
    company: str = Form(...),
    email: str = Form(None),
    phone: str = Form(None),
    address: str = Form(None),
    notes: str = Form(None)
):
    """Update an existing customer."""
    try:
        # In real implementation, would update in Supabase
        # For now, just redirect to customer detail
        return RedirectResponse(url=f"/customers/{customer_id}", status_code=303)
    except Exception as e:
        print(f"Error updating customer {customer_id}: {str(e)}")
        traceback.print_exc()
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "session": session,
                "error_code": 500,
                "error_message": f"Error updating customer {customer_id}"
            }
        )

@router.post("/customers/{customer_id}/delete", response_class=RedirectResponse)
async def delete_customer(
    request: Request,
    customer_id: int,
    session: dict = Depends(require_auth)
):
    """Delete a customer."""
    try:
        # In real implementation, would delete from Supabase
        # For now, just redirect to customers list
        return RedirectResponse(url="/customers", status_code=303)
    except Exception as e:
        print(f"Error deleting customer {customer_id}: {str(e)}")
        traceback.print_exc()
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "session": session,
                "error_code": 500,
                "error_message": f"Error deleting customer {customer_id}"
            }
        ) 