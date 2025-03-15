"""
Project routes for the AKC CRM application.
"""

from fastapi import APIRouter, Depends, Form, Request, UploadFile, File, HTTPException, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from datetime import datetime
from typing import Optional
import traceback
import logging

from dependencies import get_session, check_auth, templates, get_supabase_client
from routes.auth import require_auth
from mock_data import MOCK_PROJECTS, MOCK_EXPENSES, MOCK_CUSTOMERS, MOCK_TIME_LOGS

router = APIRouter(prefix="/projects", tags=["projects"])

# Mock project data for when Supabase is unavailable
MOCK_PROJECTS = [
    {
        "id": "proj1",
        "name": "Commercial Building Renovation",
        "client_id": "client1",
        "client_name": "ABC Corporation",
        "status": "In Progress",
        "start_date": "2024-02-15",
        "end_date": "2024-05-30",
        "budget": 250000.00,
        "description": "Complete renovation of a 3-story commercial building including electrical, plumbing, and structural work.",
        "created_at": "2024-02-01T09:30:00"
    },
    {
        "id": "proj2",
        "name": "Residential Kitchen Remodel",
        "client_id": "client2",
        "client_name": "Johnson Family",
        "status": "Planning",
        "start_date": "2024-04-01",
        "end_date": "2024-04-30",
        "budget": 45000.00,
        "description": "High-end kitchen remodel with custom cabinetry, new appliances, and granite countertops.",
        "created_at": "2024-03-10T14:45:00"
    },
    {
        "id": "proj3",
        "name": "Office Complex Development",
        "client_id": "client3",
        "client_name": "XYZ Enterprises",
        "status": "Pending",
        "start_date": "2024-06-01",
        "end_date": "2025-02-28",
        "budget": 1200000.00,
        "description": "New construction of a 10,000 sq ft office complex with parking facility and landscaping.",
        "created_at": "2024-03-05T10:15:00"
    }
]

@router.get("/", response_class=HTMLResponse)
async def list_projects(
    request: Request,
    session: dict = Depends(require_auth),
    status: Optional[str] = None,
    customer_id: Optional[int] = None
):
    """List all projects with optional filters"""
    try:
        # Optional filters
        filters = {}
        if status:
            filters["status"] = status
        if customer_id:
            filters["customer_id"] = customer_id

        # In real app, these would come from the database
        projects = MOCK_PROJECTS
        customers = MOCK_CUSTOMERS
        
        # Apply filters if specified
        if status:
            projects = [p for p in projects if p.get("status") == status]
        if customer_id:
            projects = [p for p in projects if p.get("customer_id") == customer_id]

        # Sort projects by date (newest first)
        projects = sorted(projects, key=lambda x: x.get("created_at", ""), reverse=True)
        
        # Get status counts for filter badges
        status_counts = {}
        for p in MOCK_PROJECTS:
            s = p.get("status", "Unknown")
            status_counts[s] = status_counts.get(s, 0) + 1
        
        # Calculate additional metrics for each project
        for project in projects:
            # Calculate time spent
            project_time_logs = [log for log in MOCK_TIME_LOGS if log.get("project_id") == project.get("id")]
            total_hours = sum(log.get("hours", 0) for log in project_time_logs)
            project["total_hours"] = total_hours
            
            # Calculate total expenses
            project_expenses = [expense for expense in MOCK_EXPENSES if expense.get("project_id") == project.get("id")]
            total_expenses = sum(expense.get("amount", 0) for expense in project_expenses)
            project["total_expenses"] = total_expenses
            
            # Get customer name
            customer = next((c for c in customers if c.get("id") == project.get("customer_id")), None)
            project["customer_name"] = customer.get("name", "Unknown") if customer else "Unknown"

        return templates.TemplateResponse(
            "projects.html",
            {
                "request": request,
                "session": session,
                "projects": projects,
                "customers": customers,
                "status_counts": status_counts,
                "filters": {
                    "status": status,
                    "customer_id": customer_id
                }
            }
        )
    except Exception as e:
        logging.error(f"Error listing projects: {str(e)}")
        logging.error(traceback.format_exc())
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "session": session,
                "error_code": 500,
                "error_message": "Error loading projects list"
            }
        )

@router.get("/new", response_class=HTMLResponse)
async def new_project_form(request: Request, session: dict = Depends(require_auth)):
    """Show form to create a new project"""
    try:
        # Get customers for dropdown
        customers = MOCK_CUSTOMERS
        
        return templates.TemplateResponse(
            "projects/new.html",
            {
                "request": request,
                "session": session,
                "customers": customers
            }
        )
    except Exception as e:
        logging.error(f"Error showing new project form: {str(e)}")
        logging.error(traceback.format_exc())
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "session": session,
                "error_code": 500,
                "error_message": "Error loading new project form"
            }
        )

@router.post("/create", response_class=HTMLResponse)
async def create_project(
    request: Request,
    session: dict = Depends(require_auth),
    name: str = Form(...),
    description: str = Form(None),
    customer_id: int = Form(...),
    start_date: str = Form(...),
    end_date: Optional[str] = Form(None),
    budget: Optional[float] = Form(None),
    status: str = Form("planned")
):
    """Create a new project"""
    try:
        # Validate inputs
        if not name:
            raise ValueError("Project name is required")
        
        # In a real app, save to database
        # For mock, just return success
        
        return RedirectResponse(url="/projects", status_code=303)
    except ValueError as e:
        # Return to form with error message
        customers = MOCK_CUSTOMERS
        return templates.TemplateResponse(
            "projects/new.html",
            {
                "request": request,
                "session": session,
                "customers": customers,
                "error_message": str(e),
                "form_data": {
                    "name": name,
                    "description": description,
                    "customer_id": customer_id,
                    "start_date": start_date,
                    "end_date": end_date,
                    "budget": budget,
                    "status": status
                }
            }
        )
    except Exception as e:
        logging.error(f"Error creating project: {str(e)}")
        logging.error(traceback.format_exc())
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "session": session,
                "error_code": 500,
                "error_message": "Error creating project"
            }
        )

@router.get("/{project_id}", response_class=HTMLResponse)
async def project_detail(
    request: Request,
    project_id: int,
    session: dict = Depends(require_auth)
):
    """Show project details"""
    try:
        # In real app, get project from database
        project = next((p for p in MOCK_PROJECTS if p.get("id") == project_id), None)
        
        if not project:
            return templates.TemplateResponse(
                "error.html",
                {
                    "request": request,
                    "session": session,
                    "error_code": 404,
                    "error_message": f"Project with ID {project_id} not found"
                }
            )
        
        # Get customer info
        customer = next((c for c in MOCK_CUSTOMERS if c.get("id") == project.get("customer_id")), None)
        
        # Get time logs for this project
        time_logs = [log for log in MOCK_TIME_LOGS if log.get("project_id") == project_id]
        total_hours = sum(log.get("hours", 0) for log in time_logs)
        billable_hours = sum(log.get("hours", 0) for log in time_logs if log.get("billable", True))
        
        # Get expenses for this project
        expenses = [expense for expense in MOCK_EXPENSES if expense.get("project_id") == project_id]
        total_expenses = sum(expense.get("amount", 0) for expense in expenses)
        
        # Calculate financials
        hourly_rate = project.get("hourly_rate", 100)  # Default rate
        expected_revenue = billable_hours * hourly_rate
        
        return templates.TemplateResponse(
            "projects/detail.html",
            {
                "request": request,
                "session": session,
                "project": project,
                "customer": customer,
                "time_logs": time_logs[:5],  # Just show the 5 most recent
                "expenses": expenses[:5],    # Just show the 5 most recent
                "total_hours": total_hours,
                "billable_hours": billable_hours,
                "total_expenses": total_expenses,
                "expected_revenue": expected_revenue
            }
        )
    except Exception as e:
        logging.error(f"Error showing project detail: {str(e)}")
        logging.error(traceback.format_exc())
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "session": session,
                "error_code": 500,
                "error_message": "Error loading project details"
            }
        )

@router.get("/{project_id}/edit", response_class=HTMLResponse)
async def edit_project_form(
    request: Request,
    project_id: int,
    session: dict = Depends(require_auth)
):
    """Show form to edit a project"""
    try:
        # In real app, get project from database
        project = next((p for p in MOCK_PROJECTS if p.get("id") == project_id), None)
        
        if not project:
            return templates.TemplateResponse(
                "error.html",
                {
                    "request": request,
                    "session": session,
                    "error_code": 404,
                    "error_message": f"Project with ID {project_id} not found"
                }
            )
        
        # Get customers for dropdown
        customers = MOCK_CUSTOMERS
        
        return templates.TemplateResponse(
            "projects/edit.html",
            {
                "request": request,
                "session": session,
                "project": project,
                "customers": customers
            }
        )
    except Exception as e:
        logging.error(f"Error showing edit project form: {str(e)}")
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

@router.post("/{project_id}/update", response_class=HTMLResponse)
async def update_project(
    request: Request,
    project_id: int,
    session: dict = Depends(require_auth),
    name: str = Form(...),
    description: str = Form(None),
    customer_id: int = Form(...),
    start_date: str = Form(...),
    end_date: Optional[str] = Form(None),
    budget: Optional[float] = Form(None),
    status: str = Form(...)
):
    """Update an existing project"""
    try:
        # Validate inputs
        if not name:
            raise ValueError("Project name is required")
        
        # In a real app, update in database
        # For mock, just return success
        
        return RedirectResponse(url=f"/projects/{project_id}", status_code=303)
    except ValueError as e:
        # Return to form with error message
        project = next((p for p in MOCK_PROJECTS if p.get("id") == project_id), None)
        customers = MOCK_CUSTOMERS
        
        return templates.TemplateResponse(
            "projects/edit.html",
            {
                "request": request,
                "session": session,
                "project": project,
                "customers": customers,
                "error_message": str(e),
                "form_data": {
                    "name": name,
                    "description": description,
                    "customer_id": customer_id,
                    "start_date": start_date,
                    "end_date": end_date,
                    "budget": budget,
                    "status": status
                }
            }
        )
    except Exception as e:
        logging.error(f"Error updating project: {str(e)}")
        logging.error(traceback.format_exc())
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "session": session,
                "error_code": 500,
                "error_message": "Error updating project"
            }
        )

@router.get("/{project_id}/delete", response_class=HTMLResponse)
async def delete_project(
    request: Request,
    project_id: int,
    session: dict = Depends(require_auth)
):
    """Delete a project"""
    try:
        # In a real app, check if project exists and delete
        project = next((p for p in MOCK_PROJECTS if p.get("id") == project_id), None)
        
        if not project:
            return templates.TemplateResponse(
                "error.html",
                {
                    "request": request,
                    "session": session,
                    "error_code": 404,
                    "error_message": f"Project with ID {project_id} not found"
                }
            )
        
        # Normally would delete from database here
        
        return RedirectResponse(url="/projects", status_code=303)
    except Exception as e:
        logging.error(f"Error deleting project: {str(e)}")
        logging.error(traceback.format_exc())
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "session": session,
                "error_code": 500,
                "error_message": "Error deleting project"
            }
        )

@router.get("/{project_id}/expenses", response_class=HTMLResponse)
async def project_expenses(
    request: Request,
    project_id: int,
    session: dict = Depends(require_auth)
):
    """Show expenses for a specific project"""
    try:
        # In real app, get project from database
        project = next((p for p in MOCK_PROJECTS if p.get("id") == project_id), None)
        
        if not project:
            return templates.TemplateResponse(
                "error.html",
                {
                    "request": request,
                    "session": session,
                    "error_code": 404,
                    "error_message": f"Project with ID {project_id} not found"
                }
            )
        
        # Get customer info
        customer = next((c for c in MOCK_CUSTOMERS if c.get("id") == project.get("customer_id")), None)
        
        # Get expenses for this project
        expenses = [expense for expense in MOCK_EXPENSES if expense.get("project_id") == project_id]
        total_expenses = sum(expense.get("amount", 0) for expense in expenses)
        
        # Group expenses by category
        expenses_by_category = {}
        for expense in expenses:
            category = expense.get("category", "Other")
            if category not in expenses_by_category:
                expenses_by_category[category] = 0
            expenses_by_category[category] += expense.get("amount", 0)
        
        return templates.TemplateResponse(
            "project_expenses.html",
            {
                "request": request,
                "session": session,
                "project": project,
                "customer": customer,
                "expenses": expenses,
                "total_expenses": total_expenses,
                "expenses_by_category": expenses_by_category
            }
        )
    except Exception as e:
        logging.error(f"Error showing project expenses: {str(e)}")
        logging.error(traceback.format_exc())
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "session": session,
                "error_code": 500,
                "error_message": "Error loading project expenses"
            }
        ) 