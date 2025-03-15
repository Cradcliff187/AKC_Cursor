"""
Vendor routes for the AKC CRM application.
"""

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from datetime import datetime
from typing import Optional
import traceback

from dependencies import get_session, check_auth, templates, get_supabase_client
from mock_data import MOCK_VENDORS, MOCK_EXPENSES, VENDOR_CATEGORIES, VENDOR_STATUSES

router = APIRouter()

@router.get("/vendors", response_class=HTMLResponse)
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

@router.get("/vendors/{vendor_id}", response_class=HTMLResponse)
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

@router.get("/vendors/new", response_class=HTMLResponse)
async def new_vendor_form(
    request: Request,
    session: dict = Depends(get_session)
):
    """Display form for creating a new vendor."""
    if not check_auth(session):
        return RedirectResponse(url="/login")
        
    try:
        return templates.TemplateResponse(
            "vendors/form.html",
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
                "status_code": 500,
                "detail": "Error loading vendor form"
            }
        )

@router.post("/vendors/new", response_class=RedirectResponse)
async def create_vendor(
    request: Request,
    session: dict = Depends(get_session),
    name: str = Form(...),
    contact_name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    address: str = Form(...),
    material_category: str = Form(...),
    preferred: bool = Form(False),
    rating: int = Form(0),
    status: str = Form("active")
):
    """Create a new vendor."""
    if not check_auth(session):
        return RedirectResponse(url="/login")
        
    try:
        # Get Supabase client
        supabase_client = get_supabase_client()
        
        # Prepare vendor data
        vendor_data = {
            "name": name,
            "contact_name": contact_name,
            "email": email,
            "phone": phone,
            "address": address,
            "material_category": material_category,
            "preferred": preferred,
            "rating": rating,
            "status": status,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        if supabase_client:
            # Create vendor in Supabase
            result = supabase_client.table("vendors").insert(vendor_data).execute()
            vendor_id = result.data[0]["id"]
        else:
            # Use mock data
            vendor_id = max(v["id"] for v in MOCK_VENDORS) + 1
            vendor_data["id"] = vendor_id
            MOCK_VENDORS.append(vendor_data)
            
        return RedirectResponse(url=f"/vendors/{vendor_id}", status_code=303)
        
    except Exception as e:
        print(f"Error creating vendor: {str(e)}")
        traceback.print_exc()
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "session": session,
                "status_code": 500,
                "detail": "Error creating vendor"
            }
        )

@router.get("/vendors/{vendor_id}/edit", response_class=HTMLResponse)
async def edit_vendor_form(
    request: Request,
    vendor_id: int,
    session: dict = Depends(get_session)
):
    """Display form for editing a vendor."""
    if not check_auth(session):
        return RedirectResponse(url="/login")
        
    try:
        # Get Supabase client
        supabase_client = get_supabase_client()
        
        # Get vendor
        if supabase_client:
            result = supabase_client.table("vendors").select("*").eq("id", vendor_id).execute()
            vendor = result.data[0] if result.data else None
        else:
            vendor = next((v for v in MOCK_VENDORS if v["id"] == vendor_id), None)
            
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
            "vendors/form.html",
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
        print(f"Error loading vendor form: {str(e)}")
        traceback.print_exc()
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "session": session,
                "status_code": 500,
                "detail": "Error loading vendor form"
            }
        )

@router.post("/vendors/{vendor_id}/edit", response_class=RedirectResponse)
async def update_vendor(
    request: Request,
    vendor_id: int,
    session: dict = Depends(get_session),
    name: str = Form(...),
    contact_name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    address: str = Form(...),
    material_category: str = Form(...),
    preferred: bool = Form(False),
    rating: int = Form(0),
    status: str = Form("active")
):
    """Update an existing vendor."""
    if not check_auth(session):
        return RedirectResponse(url="/login")
        
    try:
        # Get Supabase client
        supabase_client = get_supabase_client()
        
        # Prepare update data
        update_data = {
            "name": name,
            "contact_name": contact_name,
            "email": email,
            "phone": phone,
            "address": address,
            "material_category": material_category,
            "preferred": preferred,
            "rating": rating,
            "status": status,
            "updated_at": datetime.now().isoformat()
        }
        
        if supabase_client:
            # Update vendor in Supabase
            result = supabase_client.table("vendors").update(update_data).eq("id", vendor_id).execute()
        else:
            # Update mock data
            vendor_idx = next((i for i, v in enumerate(MOCK_VENDORS) if v["id"] == vendor_id), None)
            if vendor_idx is not None:
                MOCK_VENDORS[vendor_idx].update(update_data)
            
        return RedirectResponse(url=f"/vendors/{vendor_id}", status_code=303)
        
    except Exception as e:
        print(f"Error updating vendor: {str(e)}")
        traceback.print_exc()
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "session": session,
                "status_code": 500,
                "detail": "Error updating vendor"
            }
        )

@router.post("/vendors/{vendor_id}/delete", response_class=RedirectResponse)
async def delete_vendor(
    request: Request,
    vendor_id: int,
    session: dict = Depends(get_session)
):
    """Delete a vendor."""
    if not check_auth(session):
        return RedirectResponse(url="/login")
        
    try:
        # Get Supabase client
        supabase_client = get_supabase_client()
        
        if supabase_client:
            # Delete vendor from Supabase
            result = supabase_client.table("vendors").delete().eq("id", vendor_id).execute()
        else:
            # Delete from mock data
            global MOCK_VENDORS
            MOCK_VENDORS = [v for v in MOCK_VENDORS if v["id"] != vendor_id]
            
        return RedirectResponse(url="/vendors", status_code=303)
        
    except Exception as e:
        print(f"Error deleting vendor: {str(e)}")
        traceback.print_exc()
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "session": session,
                "status_code": 500,
                "detail": "Error deleting vendor"
            }
        ) 