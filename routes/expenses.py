"""
Expense management routes for the AKC CRM application.
"""

from fastapi import APIRouter, Request, Depends, Form, UploadFile, File, HTTPException, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from dependencies import get_session, check_auth, templates, get_supabase_client
from routes.auth import require_auth
from datetime import datetime
import traceback
import logging
from pathlib import Path
import os
import shutil

router = APIRouter()

# Ensure uploads directory exists
RECEIPT_DIR = Path("static/uploads/receipts")
RECEIPT_DIR.mkdir(parents=True, exist_ok=True)

# Mock expense data
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
        "receipt_url": "/static/uploads/receipts/receipt1.pdf",
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
        "receipt_url": "/static/uploads/receipts/receipt2.pdf",
        "created_at": "2025-03-14T09:00:00Z",
        "updated_at": "2025-03-14T09:30:00Z"
    },
    {
        "id": 3,
        "date": "2025-03-13",
        "vendor_id": 3,
        "vendor_name": "City Permits",
        "project_id": 2,
        "project_name": "Warehouse Construction",
        "category": "Permits",
        "description": "Building permits and fees",
        "amount": 2200.00,
        "status": "approved",
        "receipt_url": "/static/uploads/receipts/receipt3.pdf",
        "created_at": "2025-03-13T14:30:00Z",
        "updated_at": "2025-03-13T16:45:00Z"
    }
]

# Mock categories and statuses for form options
EXPENSE_CATEGORIES = ["Materials", "Labor", "Equipment", "Travel", "Office Supplies", "Utilities", "Other"]
EXPENSE_STATUSES = ["pending", "approved", "rejected"]

@router.get("/expenses", response_class=HTMLResponse)
async def list_expenses(
    request: Request,
    session: dict = Depends(require_auth),
    search: str = "",
    project_id: int = None,
    category: str = "",
    status: str = "",
    start_date: str = None,
    end_date: str = None,
    page: int = 1,
    per_page: int = 10
):
    """List expenses with filtering, sorting, and pagination."""
    try:
        # Get Supabase client
        supabase_client = get_supabase_client()
        
        if supabase_client:
            # Build query
            query = supabase_client.table("expenses").select("*")
            
            # Apply filters
            if search:
                query = query.or_(f"description.ilike.%{search}%,vendor_name.ilike.%{search}%")
            if project_id:
                query = query.eq("project_id", project_id)
            if category:
                query = query.eq("category", category)
            if status:
                query = query.eq("status", status)
            if start_date:
                query = query.gte("date", start_date)
            if end_date:
                query = query.lte("date", end_date)
                
            # Execute query
            response = query.execute()
            
            if hasattr(response, 'data'):
                all_expenses = response.data
            else:
                all_expenses = []
                
            # Get project and vendor data for form dropdowns if needed
            projects_response = supabase_client.table("projects").select("id, name").execute()
            vendors_response = supabase_client.table("vendors").select("id, name").execute()
            
            projects = projects_response.data if hasattr(projects_response, 'data') else []
            vendors = vendors_response.data if hasattr(vendors_response, 'data') else []
        else:
            # Use mock data when Supabase client is not available
            all_expenses = MOCK_EXPENSES
            
            # Apply filters to mock data
            filtered_expenses = []
            for expense in all_expenses:
                if search and not (
                    search.lower() in expense["description"].lower() or
                    search.lower() in expense["vendor_name"].lower()
                ):
                    continue
                if project_id and expense["project_id"] != project_id:
                    continue
                if category and expense["category"] != category:
                    continue
                if status and expense["status"] != status:
                    continue
                if start_date and expense["date"] < start_date:
                    continue
                if end_date and expense["date"] > end_date:
                    continue
                filtered_expenses.append(expense)
            
            all_expenses = filtered_expenses
            
            # Mock projects and vendors for dropdowns
            projects = [
                {"id": 1, "name": "Office Renovation"},
                {"id": 2, "name": "Website Redesign"},
                {"id": 3, "name": "Marketing Campaign"}
            ]
            
            vendors = [
                {"id": 1, "name": "ABC Supply"},
                {"id": 2, "name": "XYZ Contractors"},
                {"id": 3, "name": "Office Depot"}
            ]
        
        # Pagination
        total_expenses = len(all_expenses)
        total_pages = (total_expenses + per_page - 1) // per_page
        page = max(1, min(page, total_pages if total_pages > 0 else 1))
        start_idx = (page - 1) * per_page
        end_idx = min(start_idx + per_page, total_expenses)
        expenses = all_expenses[start_idx:end_idx]
        
        # Calculate summary statistics
        total_amount = sum(expense["amount"] for expense in all_expenses)
        
        return templates.TemplateResponse(
            "expenses.html",
            {
                "request": request,
                "expenses": expenses,
                "projects": projects,
                "vendors": vendors,
                "categories": EXPENSE_CATEGORIES,
                "statuses": EXPENSE_STATUSES,
                "search": search,
                "project_id": project_id,
                "category": category,
                "status": status,
                "start_date": start_date,
                "end_date": end_date,
                "current_page": page,
                "total_pages": total_pages,
                "total_expenses": total_expenses,
                "total_amount": total_amount,
                "session": session
            }
        )
    except Exception as e:
        logging.error(f"Error listing expenses: {str(e)}")
        logging.error(traceback.format_exc())
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "error_code": 500,
                "error_message": "An error occurred while retrieving expenses.",
                "session": session
            }
        )

@router.get("/expenses/{expense_id}", response_class=HTMLResponse)
async def expense_detail(
    request: Request,
    expense_id: int,
    session: dict = Depends(require_auth)
):
    """View expense details."""
    try:
        # Get expense with specified ID from mock data or Supabase
        expense = next((e for e in MOCK_EXPENSES if e["id"] == expense_id), None)
        
        if not expense:
            return templates.TemplateResponse(
                "error.html",
                {
                    "request": request,
                    "session": session,
                    "error_code": 404,
                    "error_message": f"Expense with ID {expense_id} not found"
                }
            )
        
        return templates.TemplateResponse(
            "expense_detail.html",
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
                "error_code": 500,
                "error_message": f"Error loading expense {expense_id}"
            }
        )

@router.get("/expenses/new", response_class=HTMLResponse)
async def new_expense_form(
    request: Request,
    session: dict = Depends(require_auth),
    project_id: int = None
):
    """Display form to create a new expense."""
    try:
        # Get projects and vendors for dropdown
        projects = [
            {"id": 1, "name": "Office Renovation"},
            {"id": 2, "name": "Warehouse Construction"}
        ]
        
        vendors = [
            {"id": 1, "name": "ABC Supply"},
            {"id": 2, "name": "XYZ Tools"},
            {"id": 3, "name": "City Permits"}
        ]
        
        categories = ["Materials", "Equipment", "Labor", "Permits", "Transportation", "Other"]
        
        # Default to today's date
        today = datetime.now().strftime("%Y-%m-%d")
        
        return templates.TemplateResponse(
            "expense_form.html",
            {
                "request": request,
                "session": session,
                "expense": {"date": today, "project_id": project_id},
                "projects": projects,
                "vendors": vendors,
                "categories": categories,
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
                "error_code": 500,
                "error_message": "Error loading expense form"
            }
        )

@router.post("/expenses/new", response_class=RedirectResponse)
async def create_expense(
    request: Request,
    session: dict = Depends(require_auth),
    project_id: int = Form(...),
    vendor_id: int = Form(...),
    date: str = Form(...),
    category: str = Form(...),
    amount: float = Form(...),
    description: str = Form(None),
    receipt: UploadFile = File(None)
):
    """Create a new expense."""
    try:
        # Handle receipt upload if provided
        receipt_path = None
        if receipt and receipt.filename:
            # Generate a unique filename to prevent collisions
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            filename = f"{timestamp}_{receipt.filename}"
            file_path = RECEIPT_DIR / filename
            
            # Save the file
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(receipt.file, buffer)
            
            receipt_path = f"/static/uploads/receipts/{filename}"
            
        # In real implementation, would insert into Supabase
        # For now, just redirect to expenses list
        return RedirectResponse(url="/expenses", status_code=303)
    except Exception as e:
        print(f"Error creating expense: {str(e)}")
        traceback.print_exc()
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "session": session,
                "error_code": 500,
                "error_message": "Error creating expense"
            }
        )

@router.get("/expenses/{expense_id}/edit", response_class=HTMLResponse)
async def edit_expense_form(
    request: Request,
    expense_id: int,
    session: dict = Depends(require_auth)
):
    """Display form to edit an expense."""
    try:
        # Get expense with specified ID from mock data or Supabase
        expense = next((e for e in MOCK_EXPENSES if e["id"] == expense_id), None)
        
        if not expense:
            return templates.TemplateResponse(
                "error.html",
                {
                    "request": request,
                    "session": session,
                    "error_code": 404,
                    "error_message": f"Expense with ID {expense_id} not found"
                }
            )
        
        # Get projects and vendors for dropdown
        projects = [
            {"id": 1, "name": "Office Renovation"},
            {"id": 2, "name": "Warehouse Construction"}
        ]
        
        vendors = [
            {"id": 1, "name": "ABC Supply"},
            {"id": 2, "name": "XYZ Tools"},
            {"id": 3, "name": "City Permits"}
        ]
        
        categories = ["Materials", "Equipment", "Labor", "Permits", "Transportation", "Other"]
        
        return templates.TemplateResponse(
            "expense_form.html",
            {
                "request": request,
                "session": session,
                "expense": expense,
                "projects": projects,
                "vendors": vendors,
                "categories": categories,
                "is_new": False
            }
        )
    except Exception as e:
        print(f"Error loading expense {expense_id} for editing: {str(e)}")
        traceback.print_exc()
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "session": session,
                "error_code": 500,
                "error_message": f"Error loading expense {expense_id} for editing"
            }
        )

@router.post("/expenses/{expense_id}/edit", response_class=RedirectResponse)
async def update_expense(
    request: Request,
    expense_id: int,
    session: dict = Depends(require_auth),
    project_id: int = Form(...),
    vendor_id: int = Form(...),
    date: str = Form(...),
    category: str = Form(...),
    amount: float = Form(...),
    description: str = Form(None),
    receipt: UploadFile = File(None)
):
    """Update an existing expense."""
    try:
        # Handle receipt upload if provided
        receipt_path = None
        if receipt and receipt.filename:
            # Generate a unique filename to prevent collisions
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            filename = f"{timestamp}_{receipt.filename}"
            file_path = RECEIPT_DIR / filename
            
            # Save the file
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(receipt.file, buffer)
            
            receipt_path = f"/static/uploads/receipts/{filename}"
            
        # In real implementation, would update in Supabase
        # For now, just redirect to expense detail
        return RedirectResponse(url=f"/expenses/{expense_id}", status_code=303)
    except Exception as e:
        print(f"Error updating expense {expense_id}: {str(e)}")
        traceback.print_exc()
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "session": session,
                "error_code": 500,
                "error_message": f"Error updating expense {expense_id}"
            }
        )

@router.post("/expenses/{expense_id}/delete", response_class=RedirectResponse)
async def delete_expense(
    request: Request,
    expense_id: int,
    session: dict = Depends(require_auth)
):
    """Delete an expense."""
    try:
        # In real implementation, would delete from Supabase and remove receipt file
        # For now, just redirect to expenses list
        return RedirectResponse(url="/expenses", status_code=303)
    except Exception as e:
        print(f"Error deleting expense {expense_id}: {str(e)}")
        traceback.print_exc()
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "session": session,
                "error_code": 500,
                "error_message": f"Error deleting expense {expense_id}"
            }
        )

@router.get("/projects/{project_id}/expenses", response_class=HTMLResponse)
async def project_expenses(
    request: Request,
    project_id: int,
    session: dict = Depends(require_auth),
    start_date: str = None,
    end_date: str = None,
    category: str = "",
    page: int = 1
):
    """List expenses for a specific project."""
    try:
        # Get expenses for the specified project
        project_expenses = [e for e in MOCK_EXPENSES if e["project_id"] == project_id]
        
        # Apply filters
        filtered_expenses = project_expenses.copy()
        
        # Category filter
        if category:
            filtered_expenses = [e for e in filtered_expenses if e["category"] == category]
            
        # Date range filter
        if start_date:
            start = datetime.strptime(start_date, "%Y-%m-%d").date()
            filtered_expenses = [e for e in filtered_expenses if datetime.strptime(e["date"], "%Y-%m-%d").date() >= start]
            
        if end_date:
            end = datetime.strptime(end_date, "%Y-%m-%d").date()
            filtered_expenses = [e for e in filtered_expenses if datetime.strptime(e["date"], "%Y-%m-%d").date() <= end]
        
        # Pagination
        items_per_page = 10
        total_items = len(filtered_expenses)
        total_pages = (total_items + items_per_page - 1) // items_per_page
        
        # Ensure page is within valid range
        if page < 1:
            page = 1
        elif page > total_pages and total_pages > 0:
            page = total_pages
            
        # Calculate pagination indices
        start_idx = (page - 1) * items_per_page
        end_idx = min(start_idx + items_per_page, total_items)
        
        # Get expenses for current page
        paginated_expenses = filtered_expenses[start_idx:end_idx]
        
        # Get project details
        project = {"id": project_id, "name": f"Project {project_id}"}
        if project_id == 1:
            project["name"] = "Office Renovation"
        elif project_id == 2:
            project["name"] = "Warehouse Construction"
        
        categories = ["Materials", "Equipment", "Labor", "Permits", "Transportation", "Other"]
        
        return templates.TemplateResponse(
            "project_expenses.html",
            {
                "request": request,
                "session": session,
                "project": project,
                "expenses": paginated_expenses,
                "categories": categories,
                "category": category,
                "start_date": start_date,
                "end_date": end_date,
                "page": page,
                "total_pages": total_pages,
                "total_items": total_items
            }
        )
    except Exception as e:
        print(f"Error loading expenses for project {project_id}: {str(e)}")
        traceback.print_exc()
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "session": session,
                "error_code": 500,
                "error_message": f"Error loading expenses for project {project_id}"
            }
        ) 