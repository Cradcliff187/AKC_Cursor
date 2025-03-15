"""
Contact management routes for the AKC CRM application.
"""

from fastapi import APIRouter, Request, Depends, Form, HTTPException, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from dependencies import get_session, check_auth, templates, get_supabase_client
from routes.auth import require_auth
from typing import Optional, List
import logging
import traceback
from datetime import datetime

router = APIRouter(prefix="/contacts", tags=["contacts"])

# Mock contact data for when Supabase is unavailable
MOCK_CONTACTS = [
    {
        "id": "1",
        "first_name": "John",
        "last_name": "Smith",
        "company": "ABC Corporation",
        "position": "Project Manager",
        "email": "john.smith@abccorp.com",
        "phone": "555-123-4567",
        "address": "123 Main St, Anytown, USA",
        "relationship": "Client",
        "status": "Active",
        "created_at": "2024-01-15T08:00:00",
        "notes": "Primary contact for ABC Corp projects"
    },
    {
        "id": "2",
        "first_name": "Jane",
        "last_name": "Doe",
        "company": "XYZ Industries",
        "position": "CEO",
        "email": "jane.doe@xyzind.com",
        "phone": "555-987-6543",
        "address": "456 Oak Ave, Somewhere, USA",
        "relationship": "Vendor",
        "status": "Active",
        "created_at": "2024-01-20T10:30:00",
        "notes": "Key decision maker at XYZ Industries"
    },
    {
        "id": "3",
        "first_name": "Robert",
        "last_name": "Johnson",
        "company": "City Building Department",
        "position": "Inspector",
        "email": "rjohnson@citygov.org",
        "phone": "555-555-1212",
        "address": "789 Government Blvd, Cityville, USA",
        "relationship": "Government",
        "status": "Active",
        "created_at": "2024-02-01T09:15:00",
        "notes": "Handles residential property maintenance requests"
    }
]

@router.get("/", response_class=HTMLResponse)
async def list_contacts(
    request: Request,
    session: dict = Depends(require_auth),
    search: Optional[str] = None,
    relationship: Optional[str] = None,
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100)
):
    """List all contacts with optional filtering and pagination."""
    try:
        offset = (page - 1) * per_page
        
        # Get Supabase client
        supabase = get_supabase_client()
        
        # Use mock data if Supabase client is unavailable
        if supabase is None:
            filtered_contacts = MOCK_CONTACTS.copy()
            
            # Apply filters to mock data
            if search:
                search = search.lower()
                filtered_contacts = [c for c in filtered_contacts if 
                                    search in c["first_name"].lower() or 
                                    search in c["last_name"].lower() or
                                    search in c["company"].lower() or
                                    search in c["email"].lower()]
            
            if relationship:
                filtered_contacts = [c for c in filtered_contacts if c["relationship"] == relationship]
                
            if status:
                filtered_contacts = [c for c in filtered_contacts if c["status"] == status]
            
            # Get total count for pagination
            total_count = len(filtered_contacts)
            
            # Apply pagination
            contacts = filtered_contacts[offset:offset+per_page]
            
            # Get available relationships and statuses for filters
            available_relationships = list(set(c["relationship"] for c in MOCK_CONTACTS))
            available_statuses = list(set(c["status"] for c in MOCK_CONTACTS))
        else:
            # Use Supabase for data retrieval
            query = supabase.table("contacts").select("*")
            
            if search:
                query = query.or_(f"first_name.ilike.%{search}%,last_name.ilike.%{search}%,company.ilike.%{search}%,email.ilike.%{search}%")
            
            if relationship:
                query = query.eq("relationship", relationship)
                
            if status:
                query = query.eq("status", status)
            
            # First get the total count for pagination
            count_response = query.execute()
            if not count_response.data:
                count_response.data = []
            total_count = len(count_response.data)
            
            # Then get the paginated results
            query = query.range(offset, offset + per_page - 1).order("last_name")
            response = query.execute()
            contacts = response.data if response.data else []
            
            # Get available relationships and statuses for filters
            relationship_response = supabase.table("contacts").select("relationship").execute()
            relationship_data = relationship_response.data if relationship_response.data else []
            available_relationships = list(set(item["relationship"] for item in relationship_data if item.get("relationship")))
            
            status_response = supabase.table("contacts").select("status").execute()
            status_data = status_response.data if status_response.data else []
            available_statuses = list(set(item["status"] for item in status_data if item.get("status")))
        
        # Calculate pagination info
        total_pages = (total_count + per_page - 1) // per_page
        has_next = page < total_pages
        has_prev = page > 1
        
        return templates.TemplateResponse(
            "contacts.html",
            {
                "request": request,
                "session": session,
                "contacts": contacts,
                "search": search,
                "relationship": relationship,
                "status": status,
                "available_relationships": available_relationships,
                "available_statuses": available_statuses,
                "page": page,
                "per_page": per_page,
                "total_count": total_count,
                "total_pages": total_pages,
                "has_next": has_next,
                "has_prev": has_prev
            }
        )
    except Exception as e:
        logging.error(f"Error listing contacts: {str(e)}")
        logging.error(traceback.format_exc())
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "session": session,
                "error_code": 500,
                "error_message": "Error retrieving contacts list"
            }
        )

@router.get("/new", response_class=HTMLResponse)
async def new_contact_form(request: Request, session: dict = Depends(require_auth)):
    """Show form to create a new contact."""
    try:
        # Get available relationships and statuses for dropdowns
        relationships = ["Client", "Vendor", "Subcontractor", "Government", "Other"]
        statuses = ["Active", "Inactive", "Lead", "Former"]
        
        return templates.TemplateResponse(
            "contact_form.html",
            {
                "request": request,
                "session": session,
                "contact": {},
                "relationships": relationships,
                "statuses": statuses,
                "is_new": True
            }
        )
    except Exception as e:
        logging.error(f"Error showing new contact form: {str(e)}")
        logging.error(traceback.format_exc())
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "session": session,
                "error_code": 500,
                "error_message": "Error loading contact form"
            }
        )

@router.post("/create", response_class=HTMLResponse)
async def create_contact(
    request: Request,
    session: dict = Depends(require_auth),
    first_name: str = Form(...),
    last_name: str = Form(...),
    company: str = Form(None),
    position: str = Form(None),
    email: str = Form(None),
    phone: str = Form(None),
    address: str = Form(None),
    relationship: str = Form(...),
    status: str = Form(...),
    notes: str = Form(None)
):
    """Create a new contact."""
    try:
        # Validate inputs
        if not first_name or not last_name:
            raise ValueError("First name and last name are required")
        
        # Get Supabase client
        supabase = get_supabase_client()
        
        if supabase:
            # Create contact in Supabase
            contact_data = {
                "first_name": first_name,
                "last_name": last_name,
                "company": company,
                "position": position,
                "email": email,
                "phone": phone,
                "address": address,
                "relationship": relationship,
                "status": status,
                "notes": notes,
                "created_by": session.get("user_id"),
                "created_at": datetime.now().isoformat()
            }
            
            result = supabase.table("contacts").insert(contact_data).execute()
            
            if hasattr(result, 'data') and len(result.data) > 0:
                contact_id = result.data[0].get("id")
                return RedirectResponse(url=f"/contacts/{contact_id}", status_code=303)
        
        # If Supabase is not available or insert failed, just redirect to contacts list
        return RedirectResponse(url="/contacts", status_code=303)
    except ValueError as e:
        # Return to form with error message
        relationships = ["Client", "Vendor", "Subcontractor", "Government", "Other"]
        statuses = ["Active", "Inactive", "Lead", "Former"]
        
        return templates.TemplateResponse(
            "contact_form.html",
            {
                "request": request,
                "session": session,
                "contact": {
                    "first_name": first_name,
                    "last_name": last_name,
                    "company": company,
                    "position": position,
                    "email": email,
                    "phone": phone,
                    "address": address,
                    "relationship": relationship,
                    "status": status,
                    "notes": notes
                },
                "relationships": relationships,
                "statuses": statuses,
                "is_new": True,
                "error_message": str(e)
            }
        )
    except Exception as e:
        logging.error(f"Error creating contact: {str(e)}")
        logging.error(traceback.format_exc())
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "session": session,
                "error_code": 500,
                "error_message": "Error creating contact"
            }
        )

@router.get("/{contact_id}", response_class=HTMLResponse)
async def contact_detail(
    request: Request,
    contact_id: str,
    session: dict = Depends(require_auth)
):
    """Show contact details."""
    try:
        # Get Supabase client
        supabase = get_supabase_client()
        
        if supabase:
            # Get contact from Supabase
            result = supabase.table("contacts").select("*").eq("id", contact_id).execute()
            
            if hasattr(result, 'data') and len(result.data) > 0:
                contact = result.data[0]
            else:
                return templates.TemplateResponse(
                    "error.html",
                    {
                        "request": request,
                        "session": session,
                        "error_code": 404,
                        "error_message": f"Contact with ID {contact_id} not found"
                    }
                )
        else:
            # Use mock data
            contact = next((c for c in MOCK_CONTACTS if c["id"] == contact_id), None)
            
            if not contact:
                return templates.TemplateResponse(
                    "error.html",
                    {
                        "request": request,
                        "session": session,
                        "error_code": 404,
                        "error_message": f"Contact with ID {contact_id} not found"
                    }
                )
        
        return templates.TemplateResponse(
            "contact_detail.html",
            {
                "request": request,
                "session": session,
                "contact": contact
            }
        )
    except Exception as e:
        logging.error(f"Error showing contact detail: {str(e)}")
        logging.error(traceback.format_exc())
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "session": session,
                "error_code": 500,
                "error_message": "Error loading contact details"
            }
        )

@router.get("/{contact_id}/edit", response_class=HTMLResponse)
async def edit_contact_form(
    request: Request,
    contact_id: str,
    session: dict = Depends(require_auth)
):
    """Show form to edit a contact."""
    try:
        # Get Supabase client
        supabase = get_supabase_client()
        
        if supabase:
            # Get contact from Supabase
            result = supabase.table("contacts").select("*").eq("id", contact_id).execute()
            
            if hasattr(result, 'data') and len(result.data) > 0:
                contact = result.data[0]
            else:
                return templates.TemplateResponse(
                    "error.html",
                    {
                        "request": request,
                        "session": session,
                        "error_code": 404,
                        "error_message": f"Contact with ID {contact_id} not found"
                    }
                )
        else:
            # Use mock data
            contact = next((c for c in MOCK_CONTACTS if c["id"] == contact_id), None)
            
            if not contact:
                return templates.TemplateResponse(
                    "error.html",
                    {
                        "request": request,
                        "session": session,
                        "error_code": 404,
                        "error_message": f"Contact with ID {contact_id} not found"
                    }
                )
        
        # Get available relationships and statuses for dropdowns
        relationships = ["Client", "Vendor", "Subcontractor", "Government", "Other"]
        statuses = ["Active", "Inactive", "Lead", "Former"]
        
        return templates.TemplateResponse(
            "contact_form.html",
            {
                "request": request,
                "session": session,
                "contact": contact,
                "relationships": relationships,
                "statuses": statuses,
                "is_new": False
            }
        )
    except Exception as e:
        logging.error(f"Error showing edit contact form: {str(e)}")
        logging.error(traceback.format_exc())
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "session": session,
                "error_code": 500,
                "error_message": "Error loading edit form"
            }
        )

@router.post("/{contact_id}/update", response_class=HTMLResponse)
async def update_contact(
    request: Request,
    contact_id: str,
    session: dict = Depends(require_auth),
    first_name: str = Form(...),
    last_name: str = Form(...),
    company: str = Form(None),
    position: str = Form(None),
    email: str = Form(None),
    phone: str = Form(None),
    address: str = Form(None),
    relationship: str = Form(...),
    status: str = Form(...),
    notes: str = Form(None)
):
    """Update an existing contact."""
    try:
        # Validate inputs
        if not first_name or not last_name:
            raise ValueError("First name and last name are required")
        
        # Get Supabase client
        supabase = get_supabase_client()
        
        if supabase:
            # Update contact in Supabase
            contact_data = {
                "first_name": first_name,
                "last_name": last_name,
                "company": company,
                "position": position,
                "email": email,
                "phone": phone,
                "address": address,
                "relationship": relationship,
                "status": status,
                "notes": notes,
                "updated_by": session.get("user_id"),
                "updated_at": datetime.now().isoformat()
            }
            
            supabase.table("contacts").update(contact_data).eq("id", contact_id).execute()
        
        return RedirectResponse(url=f"/contacts/{contact_id}", status_code=303)
    except ValueError as e:
        # Return to form with error message
        relationships = ["Client", "Vendor", "Subcontractor", "Government", "Other"]
        statuses = ["Active", "Inactive", "Lead", "Former"]
        
        return templates.TemplateResponse(
            "contact_form.html",
            {
                "request": request,
                "session": session,
                "contact": {
                    "id": contact_id,
                    "first_name": first_name,
                    "last_name": last_name,
                    "company": company,
                    "position": position,
                    "email": email,
                    "phone": phone,
                    "address": address,
                    "relationship": relationship,
                    "status": status,
                    "notes": notes
                },
                "relationships": relationships,
                "statuses": statuses,
                "is_new": False,
                "error_message": str(e)
            }
        )
    except Exception as e:
        logging.error(f"Error updating contact: {str(e)}")
        logging.error(traceback.format_exc())
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "session": session,
                "error_code": 500,
                "error_message": "Error updating contact"
            }
        )

@router.get("/{contact_id}/delete", response_class=HTMLResponse)
async def delete_contact(
    request: Request,
    contact_id: str,
    session: dict = Depends(require_auth)
):
    """Delete a contact."""
    try:
        # Get Supabase client
        supabase = get_supabase_client()
        
        if supabase:
            # Delete contact from Supabase
            supabase.table("contacts").delete().eq("id", contact_id).execute()
        
        return RedirectResponse(url="/contacts", status_code=303)
    except Exception as e:
        logging.error(f"Error deleting contact: {str(e)}")
        logging.error(traceback.format_exc())
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "session": session,
                "error_code": 500,
                "error_message": "Error deleting contact"
            }
        ) 