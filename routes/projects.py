"""
Project routes for the AKC CRM application.
"""

from fastapi import APIRouter, Depends, Form, Request, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from datetime import datetime
from typing import Optional
import traceback

from dependencies import get_session, check_auth, templates, get_supabase_client
from mock_data import MOCK_PROJECTS, MOCK_EXPENSES, MOCK_CUSTOMERS

router = APIRouter()

@router.get("/projects", response_class=HTMLResponse)
async def list_projects(
    request: Request,
    session: dict = Depends(get_session),
    search: str = "",
    status: str = "",
    client_id: int = None,
    date_from: str = None,
    date_to: str = None,
    sort: str = "-start_date",
    page: int = 1
):
    """List projects with filtering, sorting, and pagination."""
    if not check_auth(session):
        return RedirectResponse(url="/login")
        
    try:
        # Get Supabase client
        supabase_client = get_supabase_client()
        
        if supabase_client:
            # Build query
            query = supabase_client.table("projects").select("*")
            
            # Apply filters
            if search:
                query = query.or_(f"name.ilike.%{search}%,client_name.ilike.%{search}%,description.ilike.%{search}%")
            if status:
                query = query.eq("status", status)
            if client_id:
                query = query.eq("client_id", client_id)
            if date_from:
                query = query.gte("start_date", date_from)
            if date_to:
                query = query.lte("end_date", date_to)
                
            # Apply sorting
            sort_column = sort[1:] if sort.startswith("-") else sort
            sort_order = "desc" if sort.startswith("-") else "asc"
            query = query.order(sort_column, desc=(sort_order == "desc"))
            
            # Execute query
            result = query.execute()
            projects = result.data
            
            # Get clients for dropdown
            clients_result = supabase_client.table("customers").select("id,name").execute()
            clients = clients_result.data
        else:
            # Use mock data
            projects = MOCK_PROJECTS
            clients = MOCK_CUSTOMERS
            
            # Apply filters to mock data
            if search:
                search = search.lower()
                projects = [p for p in projects if 
                    search in p["name"].lower() or 
                    search in p["client_name"].lower() or 
                    search in p["description"].lower()]
            if status:
                projects = [p for p in projects if p["status"] == status]
            if client_id:
                projects = [p for p in projects if p.get("client_id") == client_id]
            if date_from:
                projects = [p for p in projects if p["start_date"] >= date_from]
            if date_to:
                projects = [p for p in projects if p["end_date"] <= date_to]
                
            # Apply sorting to mock data
            reverse = sort.startswith("-")
            sort_key = sort[1:] if reverse else sort
            projects = sorted(projects, key=lambda x: x[sort_key], reverse=reverse)
        
        # Calculate pagination
        items_per_page = 10
        total_items = len(projects)
        total_pages = (total_items + items_per_page - 1) // items_per_page
        
        # Ensure page is within valid range
        if page < 1:
            page = 1
        elif page > total_pages and total_pages > 0:
            page = total_pages
            
        # Get projects for current page
        start_idx = (page - 1) * items_per_page
        end_idx = min(start_idx + items_per_page, total_items)
        paginated_projects = projects[start_idx:end_idx]
        
        # Calculate statistics
        total_projects = len(projects)
        active_projects = len([p for p in projects if p["status"] == "in_progress"])
        completed_projects = len([p for p in projects if p["status"] == "completed"])
        total_budget = sum(p["budget"] for p in projects)
        
        # Get project statuses
        PROJECT_STATUSES = [
            "planning",
            "in_progress",
            "on_hold",
            "completed",
            "cancelled"
        ]
        
        return templates.TemplateResponse(
            "projects/list.html",
            {
                "request": request,
                "session": session,
                "projects": paginated_projects,
                "page": page,
                "total_pages": total_pages,
                "total_items": total_items,
                "search": search,
                "status": status,
                "client_id": client_id,
                "date_from": date_from,
                "date_to": date_to,
                "sort": sort,
                "clients": clients,
                "statuses": PROJECT_STATUSES,
                "total_projects": total_projects,
                "active_projects": active_projects,
                "completed_projects": completed_projects,
                "total_budget": total_budget
            }
        )
        
    except Exception as e:
        print(f"Error loading projects: {str(e)}")
        traceback.print_exc()
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "session": session,
                "status_code": 500,
                "detail": "Error loading projects"
            }
        )

@router.get("/projects/{project_id}", response_class=HTMLResponse)
async def project_detail(
    request: Request,
    project_id: int,
    session: dict = Depends(get_session)
):
    """View project details."""
    if not check_auth(session):
        return RedirectResponse(url="/login")
        
    try:
        # Get Supabase client
        supabase_client = get_supabase_client()
        
        if supabase_client:
            # Get project
            result = supabase_client.table("projects").select("*").eq("id", project_id).execute()
            project = result.data[0] if result.data else None
            
            # Get related data
            if project:
                # Get expenses for this project
                expenses_result = supabase_client.table("expenses").select("*").eq("project_id", project_id).order("date", desc=True).limit(5).execute()
                recent_expenses = expenses_result.data
                
                # Get time logs for this project
                time_logs_result = supabase_client.table("time_logs").select("*").eq("project_id", project_id).order("date", desc=True).limit(5).execute()
                recent_time_logs = time_logs_result.data
                
                # Calculate project metrics
                total_expenses = sum(e["amount"] for e in expenses_result.data)
                total_hours = sum(t["hours"] for t in time_logs_result.data)
                budget_remaining = project["budget"] - total_expenses
                
                # Get client details
                if project.get("client_id"):
                    client_result = supabase_client.table("customers").select("*").eq("id", project["client_id"]).execute()
                    client = client_result.data[0] if client_result.data else None
                else:
                    client = None
        else:
            # Use mock data
            project = next((p for p in MOCK_PROJECTS if p["id"] == project_id), None)
            recent_expenses = [e for e in MOCK_EXPENSES if e["project_id"] == project_id][:5]
            recent_time_logs = []  # Mock time logs would be added here
            
            if project:
                total_expenses = sum(e["amount"] for e in recent_expenses)
                total_hours = 0  # Would be calculated from time logs
                budget_remaining = project["budget"] - total_expenses
                client = next((c for c in MOCK_CUSTOMERS if c["id"] == project.get("client_id")), None)
            
        if not project:
            return templates.TemplateResponse(
                "error.html",
                {
                    "request": request,
                    "session": session,
                    "status_code": 404,
                    "detail": f"Project {project_id} not found"
                }
            )
            
        return templates.TemplateResponse(
            "projects/detail.html",
            {
                "request": request,
                "session": session,
                "project": project,
                "client": client,
                "recent_expenses": recent_expenses,
                "recent_time_logs": recent_time_logs,
                "total_expenses": total_expenses,
                "total_hours": total_hours,
                "budget_remaining": budget_remaining
            }
        )
        
    except Exception as e:
        print(f"Error loading project {project_id}: {str(e)}")
        traceback.print_exc()
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "session": session,
                "status_code": 500,
                "detail": f"Error loading project {project_id}"
            }
        )

@router.get("/projects/new", response_class=HTMLResponse)
async def new_project_form(
    request: Request,
    session: dict = Depends(get_session),
    client_id: int = None
):
    """Display form for creating a new project."""
    if not check_auth(session):
        return RedirectResponse(url="/login")
        
    try:
        # Get Supabase client
        supabase_client = get_supabase_client()
        
        # Get clients for dropdown
        if supabase_client:
            result = supabase_client.table("customers").select("id,name").execute()
            clients = result.data
        else:
            clients = MOCK_CUSTOMERS
            
        # Get project statuses
        PROJECT_STATUSES = [
            "planning",
            "in_progress",
            "on_hold",
            "completed",
            "cancelled"
        ]
        
        return templates.TemplateResponse(
            "projects/form.html",
            {
                "request": request,
                "session": session,
                "project": {"client_id": client_id} if client_id else {},
                "clients": clients,
                "statuses": PROJECT_STATUSES,
                "is_new": True
            }
        )
        
    except Exception as e:
        print(f"Error loading project form: {str(e)}")
        traceback.print_exc()
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "session": session,
                "status_code": 500,
                "detail": "Error loading project form"
            }
        )

@router.post("/projects/new", response_class=RedirectResponse)
async def create_project(
    request: Request,
    session: dict = Depends(get_session),
    name: str = Form(...),
    client_id: int = Form(...),
    status: str = Form(...),
    start_date: str = Form(...),
    end_date: str = Form(...),
    budget: float = Form(...),
    description: str = Form(...),
    documents: list[UploadFile] = File(None)
):
    """Create a new project."""
    if not check_auth(session):
        return RedirectResponse(url="/login")
        
    try:
        # Get Supabase client
        supabase_client = get_supabase_client()
        
        # Get client name
        if supabase_client:
            client_result = supabase_client.table("customers").select("name").eq("id", client_id).execute()
            client_name = client_result.data[0]["name"] if client_result.data else "Unknown Client"
        else:
            client = next((c for c in MOCK_CUSTOMERS if c["id"] == client_id), None)
            client_name = client["name"] if client else "Unknown Client"
        
        # Prepare project data
        project_data = {
            "name": name,
            "client_id": client_id,
            "client_name": client_name,
            "status": status,
            "start_date": start_date,
            "end_date": end_date,
            "budget": budget,
            "description": description,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        if supabase_client:
            # Create project in Supabase
            result = supabase_client.table("projects").insert(project_data).execute()
            project_id = result.data[0]["id"]
            
            # Handle document uploads
            if documents:
                for doc in documents:
                    # Upload document to Supabase storage
                    file_path = f"projects/{project_id}/{doc.filename}"
                    content = await doc.read()
                    supabase_client.storage.from_("documents").upload(file_path, content)
        else:
            # Use mock data
            project_id = max(p["id"] for p in MOCK_PROJECTS) + 1
            project_data["id"] = project_id
            MOCK_PROJECTS.append(project_data)
            
        return RedirectResponse(url=f"/projects/{project_id}", status_code=303)
        
    except Exception as e:
        print(f"Error creating project: {str(e)}")
        traceback.print_exc()
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "session": session,
                "status_code": 500,
                "detail": "Error creating project"
            }
        )

@router.get("/projects/{project_id}/edit", response_class=HTMLResponse)
async def edit_project_form(
    request: Request,
    project_id: int,
    session: dict = Depends(get_session)
):
    """Display form for editing a project."""
    if not check_auth(session):
        return RedirectResponse(url="/login")
        
    try:
        # Get Supabase client
        supabase_client = get_supabase_client()
        
        # Get project
        if supabase_client:
            result = supabase_client.table("projects").select("*").eq("id", project_id).execute()
            project = result.data[0] if result.data else None
            
            # Get clients for dropdown
            clients_result = supabase_client.table("customers").select("id,name").execute()
            clients = clients_result.data
        else:
            project = next((p for p in MOCK_PROJECTS if p["id"] == project_id), None)
            clients = MOCK_CUSTOMERS
            
        if not project:
            return templates.TemplateResponse(
                "error.html",
                {
                    "request": request,
                    "session": session,
                    "status_code": 404,
                    "detail": f"Project {project_id} not found"
                }
            )
            
        # Get project statuses
        PROJECT_STATUSES = [
            "planning",
            "in_progress",
            "on_hold",
            "completed",
            "cancelled"
        ]
            
        return templates.TemplateResponse(
            "projects/form.html",
            {
                "request": request,
                "session": session,
                "project": project,
                "clients": clients,
                "statuses": PROJECT_STATUSES,
                "is_new": False
            }
        )
        
    except Exception as e:
        print(f"Error loading project form: {str(e)}")
        traceback.print_exc()
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "session": session,
                "status_code": 500,
                "detail": "Error loading project form"
            }
        )

@router.post("/projects/{project_id}/edit", response_class=RedirectResponse)
async def update_project(
    request: Request,
    project_id: int,
    session: dict = Depends(get_session),
    name: str = Form(...),
    client_id: int = Form(...),
    status: str = Form(...),
    start_date: str = Form(...),
    end_date: str = Form(...),
    budget: float = Form(...),
    description: str = Form(...),
    documents: list[UploadFile] = File(None)
):
    """Update an existing project."""
    if not check_auth(session):
        return RedirectResponse(url="/login")
        
    try:
        # Get Supabase client
        supabase_client = get_supabase_client()
        
        # Get client name
        if supabase_client:
            client_result = supabase_client.table("customers").select("name").eq("id", client_id).execute()
            client_name = client_result.data[0]["name"] if client_result.data else "Unknown Client"
        else:
            client = next((c for c in MOCK_CUSTOMERS if c["id"] == client_id), None)
            client_name = client["name"] if client else "Unknown Client"
        
        # Prepare update data
        update_data = {
            "name": name,
            "client_id": client_id,
            "client_name": client_name,
            "status": status,
            "start_date": start_date,
            "end_date": end_date,
            "budget": budget,
            "description": description,
            "updated_at": datetime.now().isoformat()
        }
        
        if supabase_client:
            # Update project in Supabase
            result = supabase_client.table("projects").update(update_data).eq("id", project_id).execute()
            
            # Handle document uploads
            if documents:
                for doc in documents:
                    # Upload document to Supabase storage
                    file_path = f"projects/{project_id}/{doc.filename}"
                    content = await doc.read()
                    supabase_client.storage.from_("documents").upload(file_path, content)
        else:
            # Update mock data
            project_idx = next((i for i, p in enumerate(MOCK_PROJECTS) if p["id"] == project_id), None)
            if project_idx is not None:
                MOCK_PROJECTS[project_idx].update(update_data)
            
        return RedirectResponse(url=f"/projects/{project_id}", status_code=303)
        
    except Exception as e:
        print(f"Error updating project: {str(e)}")
        traceback.print_exc()
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "session": session,
                "status_code": 500,
                "detail": "Error updating project"
            }
        )

@router.post("/projects/{project_id}/delete", response_class=RedirectResponse)
async def delete_project(
    request: Request,
    project_id: int,
    session: dict = Depends(get_session)
):
    """Delete a project."""
    if not check_auth(session):
        return RedirectResponse(url="/login")
        
    try:
        # Get Supabase client
        supabase_client = get_supabase_client()
        
        if supabase_client:
            # Delete project from Supabase
            result = supabase_client.table("projects").delete().eq("id", project_id).execute()
            
            # Delete associated documents from storage
            # Note: In a real application, you might want to keep these for audit purposes
            storage_result = supabase_client.storage.from_("documents").list(f"projects/{project_id}")
            for file in storage_result:
                supabase_client.storage.from_("documents").remove([f"projects/{project_id}/{file['name']}"])
        else:
            # Delete from mock data
            global MOCK_PROJECTS
            MOCK_PROJECTS = [p for p in MOCK_PROJECTS if p["id"] != project_id]
            
        return RedirectResponse(url="/projects", status_code=303)
        
    except Exception as e:
        print(f"Error deleting project: {str(e)}")
        traceback.print_exc()
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "session": session,
                "status_code": 500,
                "detail": "Error deleting project"
            }
        ) 