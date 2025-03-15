"""
Time logging routes for the AKC CRM application.
"""

from fastapi import APIRouter, Request, Depends, Form, HTTPException, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from dependencies import get_session, check_auth, templates, get_supabase_client
from datetime import datetime, timedelta
import traceback
from typing import Optional, List
import json
from routes.auth import require_auth

router = APIRouter(prefix="/time-logs", tags=["time_logs"])

# Mock time log data
MOCK_TIME_LOGS = [
    {
        "id": 1,
        "user_id": 1,
        "user_name": "John Doe",
        "project_id": 1,
        "project_name": "Office Renovation",
        "task_id": 1,
        "task_name": "Initial Consultation",
        "date": "2025-03-15",
        "hours": 2.5,
        "description": "Meeting with client to discuss project requirements",
        "billable": True,
        "created_at": "2025-03-15T18:00:00Z",
        "updated_at": "2025-03-15T18:00:00Z"
    },
    {
        "id": 2,
        "user_id": 2,
        "user_name": "Jane Smith",
        "project_id": 1,
        "project_name": "Office Renovation",
        "task_id": 2,
        "task_name": "Design Phase",
        "date": "2025-03-16",
        "hours": 4.0,
        "description": "Creating initial designs",
        "billable": True,
        "created_at": "2025-03-16T16:30:00Z",
        "updated_at": "2025-03-16T16:30:00Z"
    },
    {
        "id": 3,
        "user_id": 1,
        "user_name": "John Doe",
        "project_id": 2,
        "project_name": "Warehouse Construction",
        "task_id": 5,
        "task_name": "Project Planning",
        "date": "2025-03-17",
        "hours": 3.5,
        "description": "Developing project timeline and resource allocation",
        "billable": True,
        "created_at": "2025-03-17T14:15:00Z",
        "updated_at": "2025-03-17T14:15:00Z"
    }
]

# Mock projects for dropdown selection
MOCK_PROJECTS = [
    {"id": "proj1", "name": "Commercial Building Renovation"},
    {"id": "proj2", "name": "Residential Kitchen Remodel"},
    {"id": "proj3", "name": "Office Complex Development"}
]

@router.get("/", response_class=HTMLResponse)
async def list_time_logs(
    request: Request,
    session: dict = Depends(require_auth),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    project_id: Optional[int] = None,
    user_id: Optional[int] = None
):
    """Show all time logs with optional filters"""
    try:
        # Set default date range if not provided (current week)
        today = datetime.now()
        if not end_date:
            end_date = today.strftime("%Y-%m-%d")
        if not start_date:
            # Default to beginning of week (Monday)
            start_of_week = today - timedelta(days=today.weekday())
            start_date = start_of_week.strftime("%Y-%m-%d")
        
        # Get data (in real app, these would come from the database)
        time_logs = MOCK_TIME_LOGS
        projects = MOCK_PROJECTS
        users = MOCK_USERS
        
        # Apply filters
        filtered_logs = time_logs
        
        # Date filter
        filtered_logs = [
            log for log in filtered_logs 
            if log.get("date", "") >= start_date and log.get("date", "") <= end_date
        ]
        
        # Project filter
        if project_id:
            filtered_logs = [log for log in filtered_logs if log.get("project_id") == project_id]
        
        # User filter
        if user_id:
            filtered_logs = [log for log in filtered_logs if log.get("user_id") == user_id]
        
        # Calculate summary stats
        total_hours = sum(log.get("hours", 0) for log in filtered_logs)
        billable_hours = sum(log.get("hours", 0) for log in filtered_logs if log.get("billable", False))
        non_billable_hours = total_hours - billable_hours
        
        # Group hours by project
        hours_by_project = {}
        for log in filtered_logs:
            project_id = log.get("project_id")
            project = next((p for p in projects if p.get("id") == project_id), None)
            project_name = project.get("name", "Unknown") if project else "Unknown"
            
            if project_name not in hours_by_project:
                hours_by_project[project_name] = 0
            
            hours_by_project[project_name] += log.get("hours", 0)
        
        # Group hours by day for chart
        hours_by_day = {}
        for log in filtered_logs:
            date = log.get("date", "")
            if date not in hours_by_day:
                hours_by_day[date] = 0
            hours_by_day[date] += log.get("hours", 0)
        
        # Sort logs by date (newest first)
        filtered_logs = sorted(filtered_logs, key=lambda x: x.get("date", ""), reverse=True)
        
        # Enhance logs with project and user names
        enhanced_logs = []
        for log in filtered_logs:
            project_id = log.get("project_id")
            user_id = log.get("user_id")
            
            project = next((p for p in projects if p.get("id") == project_id), None)
            user = next((u for u in users if u.get("id") == user_id), None)
            
            enhanced_log = log.copy()
            enhanced_log["project_name"] = project.get("name", "Unknown") if project else "Unknown"
            enhanced_log["user_name"] = user.get("name", "Unknown") if user else "Unknown"
            
            enhanced_logs.append(enhanced_log)
        
        return templates.TemplateResponse(
            "time_logs.html",
            {
                "request": request,
                "session": session,
                "time_logs": enhanced_logs,
                "projects": projects,
                "users": users,
                "filters": {
                    "start_date": start_date,
                    "end_date": end_date,
                    "project_id": project_id,
                    "user_id": user_id
                },
                "summary": {
                    "total_hours": total_hours,
                    "billable_hours": billable_hours,
                    "non_billable_hours": non_billable_hours,
                    "hours_by_project": hours_by_project,
                    "hours_by_day": hours_by_day
                }
            }
        )
    except Exception as e:
        logging.error(f"Error listing time logs: {str(e)}")
        logging.error(traceback.format_exc())
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "session": session,
                "error_code": 500,
                "error_message": "Error loading time logs"
            }
        )

@router.get("/new", response_class=HTMLResponse)
async def new_time_log_form(
    request: Request,
    session: dict = Depends(require_auth),
    project_id: Optional[int] = None
):
    """Show form to create a new time log"""
    try:
        # Get projects for dropdown
        projects = MOCK_PROJECTS
        
        # Pre-select today's date
        today = datetime.now().strftime("%Y-%m-%d")
        
        # If user is an admin or manager, show user selection field
        is_admin = session.get("role") in ["admin", "manager"]
        users = MOCK_USERS if is_admin else []
        
        return templates.TemplateResponse(
            "time_logs/new.html",
            {
                "request": request,
                "session": session,
                "projects": projects,
                "users": users,
                "today": today,
                "selected_project_id": project_id,
                "is_admin": is_admin
            }
        )
    except Exception as e:
        logging.error(f"Error showing new time log form: {str(e)}")
        logging.error(traceback.format_exc())
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "session": session,
                "error_code": 500,
                "error_message": "Error loading new time log form"
            }
        )

@router.post("/create", response_class=HTMLResponse)
async def create_time_log(
    request: Request,
    session: dict = Depends(require_auth),
    project_id: int = Form(...),
    date: str = Form(...),
    hours: float = Form(...),
    description: str = Form(...),
    billable: bool = Form(False),
    user_id: Optional[int] = Form(None)
):
    """Create a new time log entry"""
    try:
        # Validate hours (positive number)
        if hours <= 0:
            raise ValueError("Hours must be a positive number")
        
        # If not admin/manager, user can only log time for themselves
        if session.get("role") not in ["admin", "manager"]:
            user_id = session.get("user_id")
        elif not user_id:
            user_id = session.get("user_id")
        
        # In a real app, save to database
        # For mock, just return success
        
        return RedirectResponse(url="/time-logs", status_code=303)
    except ValueError as e:
        # Return to form with error
        projects = MOCK_PROJECTS
        is_admin = session.get("role") in ["admin", "manager"]
        users = MOCK_USERS if is_admin else []
        
        return templates.TemplateResponse(
            "time_logs/new.html",
            {
                "request": request,
                "session": session,
                "projects": projects,
                "users": users,
                "today": date,
                "selected_project_id": project_id,
                "hours": hours,
                "description": description,
                "billable": billable,
                "selected_user_id": user_id,
                "is_admin": is_admin,
                "error_message": str(e)
            }
        )
    except Exception as e:
        logging.error(f"Error creating time log: {str(e)}")
        logging.error(traceback.format_exc())
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "session": session,
                "error_code": 500,
                "error_message": "Error creating time log"
            }
        )

@router.get("/{log_id}", response_class=HTMLResponse)
async def time_log_detail(
    request: Request,
    log_id: int,
    session: dict = Depends(require_auth)
):
    """Show time log details"""
    try:
        # In real app, get time log from database
        time_log = next((log for log in MOCK_TIME_LOGS if log.get("id") == log_id), None)
        
        if not time_log:
            return templates.TemplateResponse(
                "error.html",
                {
                    "request": request,
                    "session": session,
                    "error_code": 404,
                    "error_message": f"Time log with ID {log_id} not found"
                }
            )
        
        # Get project and user info
        project = next((p for p in MOCK_PROJECTS if p.get("id") == time_log.get("project_id")), None)
        user = next((u for u in MOCK_USERS if u.get("id") == time_log.get("user_id")), None)
        
        return templates.TemplateResponse(
            "time_logs/detail.html",
            {
                "request": request,
                "session": session,
                "time_log": time_log,
                "project": project,
                "user": user
            }
        )
    except Exception as e:
        logging.error(f"Error showing time log detail: {str(e)}")
        logging.error(traceback.format_exc())
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "session": session,
                "error_code": 500,
                "error_message": "Error loading time log details"
            }
        )

@router.get("/{log_id}/edit", response_class=HTMLResponse)
async def edit_time_log_form(
    request: Request,
    log_id: int,
    session: dict = Depends(require_auth)
):
    """Show form to edit a time log"""
    try:
        # In real app, get time log from database
        time_log = next((log for log in MOCK_TIME_LOGS if log.get("id") == log_id), None)
        
        if not time_log:
            return templates.TemplateResponse(
                "error.html",
                {
                    "request": request,
                    "session": session,
                    "error_code": 404,
                    "error_message": f"Time log with ID {log_id} not found"
                }
            )
        
        # Get projects for dropdown
        projects = MOCK_PROJECTS
        
        # Check if user has permission to edit this time log
        is_admin = session.get("role") in ["admin", "manager"]
        is_owner = session.get("user_id") == time_log.get("user_id")
        
        if not (is_admin or is_owner):
            return templates.TemplateResponse(
                "error.html",
                {
                    "request": request,
                    "session": session,
                    "error_code": 403,
                    "error_message": "You don't have permission to edit this time log"
                }
            )
        
        # If user is an admin or manager, show user selection field
        users = MOCK_USERS if is_admin else []
        
        return templates.TemplateResponse(
            "time_logs/edit.html",
            {
                "request": request,
                "session": session,
                "time_log": time_log,
                "projects": projects,
                "users": users,
                "is_admin": is_admin
            }
        )
    except Exception as e:
        logging.error(f"Error showing edit time log form: {str(e)}")
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

@router.post("/{log_id}/update", response_class=HTMLResponse)
async def update_time_log(
    request: Request,
    log_id: int,
    session: dict = Depends(require_auth),
    project_id: int = Form(...),
    date: str = Form(...),
    hours: float = Form(...),
    description: str = Form(...),
    billable: bool = Form(False),
    user_id: Optional[int] = Form(None)
):
    """Update an existing time log entry"""
    try:
        # In real app, get time log from database
        time_log = next((log for log in MOCK_TIME_LOGS if log.get("id") == log_id), None)
        
        if not time_log:
            return templates.TemplateResponse(
                "error.html",
                {
                    "request": request,
                    "session": session,
                    "error_code": 404,
                    "error_message": f"Time log with ID {log_id} not found"
                }
            )
        
        # Check if user has permission to edit this time log
        is_admin = session.get("role") in ["admin", "manager"]
        is_owner = session.get("user_id") == time_log.get("user_id")
        
        if not (is_admin or is_owner):
            return templates.TemplateResponse(
                "error.html",
                {
                    "request": request,
                    "session": session,
                    "error_code": 403,
                    "error_message": "You don't have permission to edit this time log"
                }
            )
        
        # Validate hours (positive number)
        if hours <= 0:
            raise ValueError("Hours must be a positive number")
        
        # If not admin/manager, user can only log time for themselves
        if not is_admin:
            user_id = session.get("user_id")
        elif not user_id:
            user_id = session.get("user_id")
        
        # In a real app, update in database
        # For mock, just return success
        
        return RedirectResponse(url=f"/time-logs/{log_id}", status_code=303)
    except ValueError as e:
        # Return to form with error
        projects = MOCK_PROJECTS
        is_admin = session.get("role") in ["admin", "manager"]
        users = MOCK_USERS if is_admin else []
        
        return templates.TemplateResponse(
            "time_logs/edit.html",
            {
                "request": request,
                "session": session,
                "time_log": {
                    "id": log_id,
                    "project_id": project_id,
                    "date": date,
                    "hours": hours,
                    "description": description,
                    "billable": billable,
                    "user_id": user_id
                },
                "projects": projects,
                "users": users,
                "is_admin": is_admin,
                "error_message": str(e)
            }
        )
    except Exception as e:
        logging.error(f"Error updating time log: {str(e)}")
        logging.error(traceback.format_exc())
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "session": session,
                "error_code": 500,
                "error_message": "Error updating time log"
            }
        )

@router.get("/{log_id}/delete", response_class=HTMLResponse)
async def delete_time_log(
    request: Request,
    log_id: int,
    session: dict = Depends(require_auth)
):
    """Delete a time log entry"""
    try:
        # In real app, get time log from database
        time_log = next((log for log in MOCK_TIME_LOGS if log.get("id") == log_id), None)
        
        if not time_log:
            return templates.TemplateResponse(
                "error.html",
                {
                    "request": request,
                    "session": session,
                    "error_code": 404,
                    "error_message": f"Time log with ID {log_id} not found"
                }
            )
        
        # Check if user has permission to delete this time log
        is_admin = session.get("role") in ["admin", "manager"]
        is_owner = session.get("user_id") == time_log.get("user_id")
        
        if not (is_admin or is_owner):
            return templates.TemplateResponse(
                "error.html",
                {
                    "request": request,
                    "session": session,
                    "error_code": 403,
                    "error_message": "You don't have permission to delete this time log"
                }
            )
        
        # In a real app, delete from database
        # For mock, just return success
        
        return RedirectResponse(url="/time-logs", status_code=303)
    except Exception as e:
        logging.error(f"Error deleting time log: {str(e)}")
        logging.error(traceback.format_exc())
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "session": session,
                "error_code": 500,
                "error_message": "Error deleting time log"
            }
        ) 