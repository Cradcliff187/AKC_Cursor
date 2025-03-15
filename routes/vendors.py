"""
Vendor management routes for the AKC CRM application.
"""

from fastapi import APIRouter, Request, Depends, Form, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from dependencies import get_session, check_auth, templates, get_supabase_client
from routes.auth import require_auth
from typing import List, Optional
import os
import traceback
from datetime import datetime
from pathlib import Path

router = APIRouter()

# Mock data for vendors
from mock_data import MOCK_VENDORS, VENDOR_CATEGORIES, VENDOR_STATUSES

# Ensure uploads directory exists for vendor documents
VENDOR_DOCS_DIR = Path("static/uploads/vendor_documents")
VENDOR_DOCS_DIR.mkdir(parents=True, exist_ok=True)

@router.get("/vendors", response_class=HTMLResponse)
async def list_vendors(
    request: Request,
    session: dict = Depends(require_auth),
    search: str = "",
    category: str = "",
    status: str = "",
    page: int = 1
):
    """Display a list of vendors with filtering and pagination."""
    try:
        # Get Supabase client
        supabase_client = get_supabase_client()
        
        if supabase_client:
            # Build query
            query = supabase_client.table("vendors").select("*")
            
            # Apply filters
            if search:
                query = query.or_(f"name.ilike.%{search}%,description.ilike.%{search}%")
            if category:
                query = query.eq("category", category)
            if status:
                query = query.eq("status", status)
                
            # Execute query
            response = query.execute()
            
            if hasattr(response, 'data'):
                vendors = response.data
            else:
                vendors = []
        else:
            # Use mock data when Supabase client is not available
            vendors = MOCK_VENDORS
            
            # Apply filters to mock data
            filtered_vendors = []
            for vendor in vendors:
                if search and not (
                    search.lower() in vendor["name"].lower() or
                    (vendor.get("description") and search.lower() in vendor["description"].lower())
                ):
                    continue
                if category and vendor["category"] != category:
                    continue
                if status and vendor["status"] != status:
                    continue
                filtered_vendors.append(vendor)
            
            vendors = filtered_vendors
        
        # Pagination
        items_per_page = 10
        total_items = len(vendors)
        total_pages = (total_items + items_per_page - 1) // items_per_page
        
        # Ensure page is within valid range
        if page < 1:
            page = 1
        elif page > total_pages and total_pages > 0:
            page = total_pages
            
        # Calculate pagination indices
        start_idx = (page - 1) * items_per_page
        end_idx = min(start_idx + items_per_page, total_items)
        
        # Get vendors for current page
        paginated_vendors = vendors[start_idx:end_idx]
        
        return templates.TemplateResponse(
            "vendors.html",
            {
                "request": request,
                "session": session,
                "vendors": paginated_vendors,
                "categories": VENDOR_CATEGORIES,
                "statuses": VENDOR_STATUSES,
                "search": search,
                "category": category,
                "status": status,
                "page": page,
                "total_pages": total_pages,
                "total_items": total_items,
                "page_title": "Vendors"
            }
        )
    except Exception as e:
        print(f"Error listing vendors: {str(e)}")
        traceback.print_exc()
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "session": session,
                "error_code": 500,
                "error_message": "Error loading vendors"
            }
        )

@router.get("/vendors/{vendor_id}", response_class=HTMLResponse)
async def vendor_detail(
    request: Request,
    vendor_id: int,
    session: dict = Depends(require_auth)
):
    """Display vendor details."""
    try:
        # Get vendor data
        supabase_client = get_supabase_client()
        
        if supabase_client:
            # Get vendor from Supabase
            response = supabase_client.table("vendors").select("*").eq("id", vendor_id).execute()
            
            if hasattr(response, 'data') and len(response.data) > 0:
                vendor = response.data[0]
            else:
                raise HTTPException(status_code=404, detail=f"Vendor with ID {vendor_id} not found")
        else:
            # Use mock data
            vendor = next((v for v in MOCK_VENDORS if v["id"] == vendor_id), None)
            
            if not vendor:
                return templates.TemplateResponse(
                    "error.html",
                    {
                        "request": request,
                        "session": session,
                        "error_code": 404,
                        "error_message": f"Vendor with ID {vendor_id} not found"
                    }
                )
                
        # Get vendor documents (would fetch from Supabase in real implementation)
        documents = []
        # Mock documents
        if vendor["name"] == "ABC Supply":
            documents = [
                {
                    "id": 1,
                    "name": "Contract 2025",
                    "description": "Annual contract for materials supply",
                    "file_path": "/static/uploads/vendor_documents/contract_abc_2025.pdf",
                    "upload_date": "2025-01-15T10:30:00Z",
                    "file_type": "application/pdf",
                    "file_size": 1254000
                },
                {
                    "id": 2,
                    "name": "Insurance Certificate",
                    "description": "Liability insurance certificate",
                    "file_path": "/static/uploads/vendor_documents/insurance_abc.pdf",
                    "upload_date": "2025-01-10T09:15:00Z",
                    "file_type": "application/pdf",
                    "file_size": 852000
                }
            ]
            
        return templates.TemplateResponse(
            "vendor_detail.html",
            {
                "request": request,
                "session": session,
                "vendor": vendor,
                "documents": documents,
                "categories": VENDOR_CATEGORIES,
                "statuses": VENDOR_STATUSES
            }
        )
    except HTTPException as e:
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "session": session,
                "error_code": e.status_code,
                "error_message": e.detail
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
                "error_code": 500,
                "error_message": f"Error loading vendor {vendor_id}"
            }
        )

@router.get("/vendors/new", response_class=HTMLResponse)
async def new_vendor_form(
    request: Request,
    session: dict = Depends(require_auth)
):
    """Display form to create a new vendor."""
    try:
        return templates.TemplateResponse(
            "vendor_form.html",
            {
                "request": request,
                "session": session,
                "vendor": {},
                "categories": VENDOR_CATEGORIES,
                "statuses": VENDOR_STATUSES,
                "is_new": True
            }
        )
    except Exception as e:
        print(f"Error loading vendor form: {str(e)}")
        traceback.print_exc()
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "session": session,
                "error_code": 500,
                "error_message": "Error loading vendor form"
            }
        )

@router.post("/vendors/new", response_class=RedirectResponse)
async def create_vendor(
    request: Request,
    session: dict = Depends(require_auth),
    name: str = Form(...),
    category: str = Form(...),
    status: str = Form(...),
    contact_name: str = Form(None),
    contact_email: str = Form(None),
    contact_phone: str = Form(None),
    website: str = Form(None),
    address: str = Form(None),
    city: str = Form(None),
    state: str = Form(None),
    zip_code: str = Form(None),
    description: str = Form(None),
    notes: str = Form(None),
    document: UploadFile = File(None)
):
    """Create a new vendor."""
    try:
        # Handle document upload if provided
        document_path = None
        if document and document.filename:
            # Generate a unique filename to prevent collisions
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            filename = f"{timestamp}_{document.filename}"
            file_path = VENDOR_DOCS_DIR / filename
            
            # Save the file
            with open(file_path, "wb") as buffer:
                file_content = await document.read()
                buffer.write(file_content)
            
            document_path = f"/static/uploads/vendor_documents/{filename}"
        
        # Get Supabase client
        supabase_client = get_supabase_client()
        
        if supabase_client:
            # Insert vendor into Supabase
            data = {
                "name": name,
                "category": category,
                "status": status,
                "contact_name": contact_name,
                "contact_email": contact_email,
                "contact_phone": contact_phone,
                "website": website,
                "address": address,
                "city": city,
                "state": state,
                "zip_code": zip_code,
                "description": description,
                "notes": notes
            }
            
            response = supabase_client.table("vendors").insert(data).execute()
            
            if hasattr(response, 'data') and len(response.data) > 0:
                vendor_id = response.data[0]["id"]
                
                # If we have a document, save it as well
                if document_path:
                    doc_data = {
                        "vendor_id": vendor_id,
                        "name": document.filename,
                        "file_path": document_path,
                        "file_type": document.content_type,
                        "upload_date": datetime.now().isoformat()
                    }
                    supabase_client.table("vendor_documents").insert(doc_data).execute()
                
                return RedirectResponse(url=f"/vendors/{vendor_id}", status_code=303)
            else:
                # Fall back to redirecting to vendors list
                return RedirectResponse(url="/vendors", status_code=303)
        else:
            # In mock implementation, just redirect to vendors list
            return RedirectResponse(url="/vendors", status_code=303)
    except Exception as e:
        print(f"Error creating vendor: {str(e)}")
        traceback.print_exc()
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "session": session,
                "error_code": 500,
                "error_message": "Error creating vendor"
            }
        )

@router.get("/vendors/{vendor_id}/edit", response_class=HTMLResponse)
async def edit_vendor_form(
    request: Request,
    vendor_id: int,
    session: dict = Depends(require_auth)
):
    """Display form to edit a vendor."""
    try:
        # Get vendor data
        supabase_client = get_supabase_client()
        
        if supabase_client:
            # Get vendor from Supabase
            response = supabase_client.table("vendors").select("*").eq("id", vendor_id).execute()
            
            if hasattr(response, 'data') and len(response.data) > 0:
                vendor = response.data[0]
            else:
                return templates.TemplateResponse(
                    "error.html",
                    {
                        "request": request,
                        "session": session,
                        "error_code": 404,
                        "error_message": f"Vendor with ID {vendor_id} not found"
                    }
                )
        else:
            # Use mock data
            vendor = next((v for v in MOCK_VENDORS if v["id"] == vendor_id), None)
            
            if not vendor:
                return templates.TemplateResponse(
                    "error.html",
                    {
                        "request": request,
                        "session": session,
                        "error_code": 404,
                        "error_message": f"Vendor with ID {vendor_id} not found"
                    }
                )
                
        return templates.TemplateResponse(
            "vendor_form.html",
            {
                "request": request,
                "session": session,
                "vendor": vendor,
                "categories": VENDOR_CATEGORIES,
                "statuses": VENDOR_STATUSES,
                "is_new": False
            }
        )
    except Exception as e:
        print(f"Error loading vendor {vendor_id} for editing: {str(e)}")
        traceback.print_exc()
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "session": session,
                "error_code": 500,
                "error_message": f"Error loading vendor {vendor_id} for editing"
            }
        )

@router.post("/vendors/{vendor_id}/edit", response_class=RedirectResponse)
async def update_vendor(
    request: Request,
    vendor_id: int,
    session: dict = Depends(require_auth),
    name: str = Form(...),
    category: str = Form(...),
    status: str = Form(...),
    contact_name: str = Form(None),
    contact_email: str = Form(None),
    contact_phone: str = Form(None),
    website: str = Form(None),
    address: str = Form(None),
    city: str = Form(None),
    state: str = Form(None),
    zip_code: str = Form(None),
    description: str = Form(None),
    notes: str = Form(None),
    document: UploadFile = File(None)
):
    """Update an existing vendor."""
    try:
        # Handle document upload if provided
        document_path = None
        if document and document.filename:
            # Generate a unique filename to prevent collisions
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            filename = f"{timestamp}_{document.filename}"
            file_path = VENDOR_DOCS_DIR / filename
            
            # Save the file
            with open(file_path, "wb") as buffer:
                file_content = await document.read()
                buffer.write(file_content)
            
            document_path = f"/static/uploads/vendor_documents/{filename}"
        
        # Get Supabase client
        supabase_client = get_supabase_client()
        
        if supabase_client:
            # Update vendor in Supabase
            data = {
                "name": name,
                "category": category,
                "status": status,
                "contact_name": contact_name,
                "contact_email": contact_email,
                "contact_phone": contact_phone,
                "website": website,
                "address": address,
                "city": city,
                "state": state,
                "zip_code": zip_code,
                "description": description,
                "notes": notes,
                "updated_at": datetime.now().isoformat()
            }
            
            response = supabase_client.table("vendors").update(data).eq("id", vendor_id).execute()
            
            # If we have a document, save it as well
            if document_path:
                doc_data = {
                    "vendor_id": vendor_id,
                    "name": document.filename,
                    "file_path": document_path,
                    "file_type": document.content_type,
                    "upload_date": datetime.now().isoformat()
                }
                supabase_client.table("vendor_documents").insert(doc_data).execute()
            
            return RedirectResponse(url=f"/vendors/{vendor_id}", status_code=303)
        else:
            # In mock implementation, just redirect to vendor detail
            return RedirectResponse(url=f"/vendors/{vendor_id}", status_code=303)
    except Exception as e:
        print(f"Error updating vendor {vendor_id}: {str(e)}")
        traceback.print_exc()
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "session": session,
                "error_code": 500,
                "error_message": f"Error updating vendor {vendor_id}"
            }
        )

@router.post("/vendors/{vendor_id}/delete", response_class=RedirectResponse)
async def delete_vendor(
    request: Request,
    vendor_id: int,
    session: dict = Depends(require_auth)
):
    """Delete a vendor."""
    try:
        # Get Supabase client
        supabase_client = get_supabase_client()
        
        if supabase_client:
            # Delete vendor in Supabase
            response = supabase_client.table("vendors").delete().eq("id", vendor_id).execute()
            
            # Also delete related vendor documents
            supabase_client.table("vendor_documents").delete().eq("vendor_id", vendor_id).execute()
            
        # Redirect to vendors list
        return RedirectResponse(url="/vendors", status_code=303)
    except Exception as e:
        print(f"Error deleting vendor {vendor_id}: {str(e)}")
        traceback.print_exc()
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "session": session,
                "error_code": 500,
                "error_message": f"Error deleting vendor {vendor_id}"
            }
        ) 