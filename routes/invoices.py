"""
Contact management routes for the AKC CRM application.
"""

from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from typing import Optional, List
from datetime import datetime, timedelta
import json
import logging
import traceback
from dependencies import get_session, check_auth, get_supabase_client, templates
from routes.auth import require_auth

router = APIRouter(prefix="/invoices", tags=["invoices"])

# Mock invoice data to use when Supabase is unavailable
MOCK_INVOICES = [
    {
        "id": 1,
        "invoice_number": "INV-2025-001",
        "project_id": 1,
        "project_name": "Office Renovation",
        "customer_id": 1,
        "customer_name": "Acme Corporation",
        "issue_date": "2025-03-01",
        "due_date": "2025-03-15",
        "total_amount": 5000.00,
        "amount_paid": 2500.00,
        "balance_due": 2500.00,
        "status": "partial",
        "discount_amount": 0,
        "discount_percent": 0,
        "tax_amount": 0,
        "tax_percent": 0,
        "notes": "Payment due upon receipt",
        "items": [
            {
                "id": 1,
                "description": "Design services",
                "quantity": 20,
                "unit_price": 150.00,
                "amount": 3000.00
            },
            {
                "id": 2,
                "description": "Materials",
                "quantity": 1,
                "unit_price": 2000.00,
                "amount": 2000.00
            }
        ],
        "payments": [
            {
                "id": 1,
                "amount": 2500.00,
                "payment_date": "2025-03-10",
                "payment_method": "check",
                "reference": "CHK#12345"
            }
        ]
    },
    {
        "id": 2,
        "invoice_number": "INV-2025-002",
        "project_id": 2,
        "project_name": "Warehouse Construction",
        "customer_id": 2,
        "customer_name": "Beta Industries",
        "issue_date": "2025-03-05",
        "due_date": "2025-04-05",
        "total_amount": 12000.00,
        "amount_paid": 0,
        "balance_due": 12000.00,
        "status": "pending",
        "discount_amount": 500.00,
        "discount_percent": 4,
        "tax_amount": 500.00,
        "tax_percent": 4,
        "notes": "Net 30 terms",
        "items": [
            {
                "id": 3,
                "description": "Site preparation",
                "quantity": 1,
                "unit_price": 5000.00,
                "amount": 5000.00
            },
            {
                "id": 4,
                "description": "Foundation work",
                "quantity": 1,
                "unit_price": 7000.00,
                "amount": 7000.00
            }
        ],
        "payments": []
    }
]

@router.get("/", response_class=HTMLResponse)
async def list_invoices(
    request: Request,
    session: dict = Depends(require_auth),
    page: int = 1,
    search: Optional[str] = None,
    status: Optional[str] = None,
    project_id: Optional[int] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None
):
    """List all invoices with filtering and pagination."""
    try:
        supabase = get_supabase_client()
        invoices = []
        
        if supabase:
            # Use Supabase if available
            query = supabase.table("invoices").select("*")
            
            # Apply filters
            if search:
                query = query.ilike("invoice_number", f"%{search}%")
            if status:
                query = query.eq("status", status)
            if project_id:
                query = query.eq("project_id", project_id)
            if date_from:
                query = query.gte("issue_date", date_from)
            if date_to:
                query = query.lte("issue_date", date_to)
                
            # Order by date and paginate
            query = query.order("issue_date", desc=True)
            
            # Get total count first
            count_result = query.execute()
            total_count = len(count_result.data) if count_result.data else 0
            
            # Then get paginated results
            per_page = 10
            offset = (page - 1) * per_page
            query = query.range(offset, offset + per_page - 1)
            
            result = query.execute()
            invoices = result.data if result.data else []
        else:
            # Use mock data
            # Apply filters to mock data
            filtered_invoices = MOCK_INVOICES
            
            if search:
                search = search.lower()
                filtered_invoices = [i for i in filtered_invoices 
                                   if search in i["invoice_number"].lower() or 
                                      search in i["customer_name"].lower()]
            
            if status:
                filtered_invoices = [i for i in filtered_invoices if i["status"] == status]
                
            if project_id:
                filtered_invoices = [i for i in filtered_invoices if i["project_id"] == project_id]
                
            if date_from:
                filtered_invoices = [i for i in filtered_invoices if i["issue_date"] >= date_from]
                
            if date_to:
                filtered_invoices = [i for i in filtered_invoices if i["issue_date"] <= date_to]
            
            # Sort by issue date (newest first)
            filtered_invoices = sorted(filtered_invoices, key=lambda x: x["issue_date"], reverse=True)
            
            # Pagination
            per_page = 10
            total_count = len(filtered_invoices)
            offset = (page - 1) * per_page
            invoices = filtered_invoices[offset:offset + per_page]
        
        # Calculate pagination info
        total_pages = (total_count + per_page - 1) // per_page
        has_next = page < total_pages
        has_prev = page > 1
        
        return templates.TemplateResponse(
            "invoices.html",
            {
                "request": request,
                "invoices": invoices,
                "search": search,
                "status": status,
                "project_id": project_id,
                "date_from": date_from,
                "date_to": date_to,
                "page": page,
                "per_page": per_page,
                "total_count": total_count,
                "total_pages": total_pages,
                "has_next": has_next,
                "has_prev": has_prev,
                "session": session
            }
        )
    except Exception as e:
        logging.error(f"Error listing invoices: {str(e)}")
        logging.error(traceback.format_exc())
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "session": session,
                "error_code": 500,
                "error_message": "Error retrieving invoice list"
            }
        )

@router.get("/new", response_class=HTMLResponse)
async def new_invoice(
    request: Request,
    session: dict = Depends(require_auth),
    project_id: Optional[int] = None,
    estimate_id: Optional[int] = None
):
    """Show form to create a new invoice."""
    try:
        supabase = get_supabase_client()
        
        # Get projects for dropdown
        projects = []
        if supabase:
            project_result = supabase.table("projects").select("id,name,customer_id,customer_name").execute()
            projects = project_result.data if project_result.data else []
        else:
            projects = [
                {"id": 1, "name": "Office Renovation", "customer_id": 1, "customer_name": "Acme Corp"},
                {"id": 2, "name": "Warehouse Construction", "customer_id": 2, "customer_name": "Beta Industries"}
            ]
        
        # Generate a new invoice number
        today = datetime.now()
        invoice_number = f"INV-{today.year}-{len(MOCK_INVOICES) + 1:03d}"
        
        # Set default due date (30 days from now)
        issue_date = today.strftime("%Y-%m-%d")
        due_date = (today + timedelta(days=30)).strftime("%Y-%m-%d")
        
        return templates.TemplateResponse(
            "invoice_form.html",
            {
                "request": request,
                "invoice": {
                    "invoice_number": invoice_number,
                    "issue_date": issue_date,
                    "due_date": due_date,
                    "project_id": project_id
                },
                "projects": projects,
                "is_new": True,
                "session": session
            }
        )
    except Exception as e:
        logging.error(f"Error loading new invoice form: {str(e)}")
        logging.error(traceback.format_exc())
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "session": session,
                "error_code": 500,
                "error_message": "Error loading new invoice form"
            }
        )

@router.post("/", response_class=HTMLResponse)
async def create_invoice(
    request: Request,
    session: dict = Depends(require_auth),
    project_id: int = Form(...),
    invoice_number: str = Form(...),
    issue_date: str = Form(...),
    due_date: str = Form(...),
    items: list = Form(...),
    notes: Optional[str] = Form(None)
):
    """Create a new invoice."""
    try:
        # In a real implementation, we'd save the invoice to Supabase
        # For now, just redirect to the invoices list
        
        return RedirectResponse(url="/invoices", status_code=303)
    except Exception as e:
        logging.error(f"Error creating invoice: {str(e)}")
        logging.error(traceback.format_exc())
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "session": session,
                "error_code": 500,
                "error_message": "Error creating new invoice"
            }
        )

@router.get("/{invoice_id}", response_class=HTMLResponse)
async def invoice_detail(
    request: Request,
    invoice_id: int,
    session: dict = Depends(require_auth),
    print: bool = False
):
    """Show invoice details."""
    try:
        # In a real implementation, we'd get the invoice from Supabase
        # For now, find it in our mock data
        invoice = next((inv for inv in MOCK_INVOICES if inv["id"] == invoice_id), None)
        
        if not invoice:
            return templates.TemplateResponse(
                "error.html",
                {
                    "request": request,
                    "session": session,
                    "error_code": 404,
                    "error_message": f"Invoice {invoice_id} not found"
                }
            )
        
        template = "invoice_print.html" if print else "invoice_detail.html"
        
        return templates.TemplateResponse(
            template,
            {
                "request": request,
                "invoice": invoice,
                "session": session
            }
        )
    except Exception as e:
        logging.error(f"Error showing invoice {invoice_id}: {str(e)}")
        logging.error(traceback.format_exc())
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "session": session,
                "error_code": 500,
                "error_message": f"Error loading invoice {invoice_id}"
            }
        )

@router.post("/{invoice_id}/send")
async def send_invoice(
    request: Request,
    invoice_id: int,
    session: dict = Depends(require_auth),
    recipient_email: str = Form(...)
):
    """Send invoice by email."""
    try:
        # In a real implementation, we'd send the invoice via email
        # For now, just redirect to the invoice detail page
        
        # Redirect back to invoice with success message
        return RedirectResponse(url=f"/invoices/{invoice_id}", status_code=303)
    except Exception as e:
        logging.error(f"Error sending invoice {invoice_id}: {str(e)}")
        logging.error(traceback.format_exc())
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "session": session,
                "error_code": 500,
                "error_message": f"Error sending invoice {invoice_id}"
            }
        )

@router.post("/{invoice_id}/payment")
async def record_payment(
    request: Request,
    invoice_id: int,
    session: dict = Depends(require_auth),
    amount: float = Form(...),
    payment_date: str = Form(...),
    payment_method: str = Form(...),
    reference: Optional[str] = Form(None)
):
    """Record a payment for an invoice."""
    try:
        # In a real implementation, we'd update the invoice in Supabase
        # For now, just redirect to the invoice detail page
        
        # Redirect back to invoice with success message
        return RedirectResponse(url=f"/invoices/{invoice_id}", status_code=303)
    except Exception as e:
        logging.error(f"Error recording payment for invoice {invoice_id}: {str(e)}")
        logging.error(traceback.format_exc())
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "session": session,
                "error_code": 500,
                "error_message": f"Error recording payment for invoice {invoice_id}"
            }
        )

@router.post("/{invoice_id}/cancel")
async def cancel_invoice(
    request: Request,
    invoice_id: int,
    session: dict = Depends(require_auth),
    reason: str = Form(...)
):
    """Cancel an invoice."""
    try:
        # In a real implementation, we'd update the invoice in Supabase
        # For now, just redirect to the invoice detail page
        
        # Redirect back to invoice with success message
        return RedirectResponse(url=f"/invoices/{invoice_id}", status_code=303)
    except Exception as e:
        logging.error(f"Error canceling invoice {invoice_id}: {str(e)}")
        logging.error(traceback.format_exc())
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "session": session,
                "error_code": 500,
                "error_message": f"Error canceling invoice {invoice_id}"
            }
        ) 