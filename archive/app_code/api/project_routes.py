"""
API routes for project operations.

This module defines the API endpoints for creating, retrieving, updating, and deleting projects.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Path, Query
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime, date

# Import the Project model
from models.project import Project
from app.services.supabase import create_record, get_record, update_record, delete_record, query_records
from api.user_routes import get_current_user, UserProfile

router = APIRouter(
    prefix="/api/projects",
    tags=["projects"],
    responses={404: {"description": "Not found"}},
)

# Pydantic models for request and response
class ProjectCreate(BaseModel):
    name: str
    client_id: int
    description: Optional[str] = None
    status: Optional[str] = "pending"
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    budget: Optional[float] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    manager_id: Optional[int] = None
    notes: Optional[str] = None

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    client_id: Optional[int] = None
    description: Optional[str] = None
    status: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    actual_start_date: Optional[date] = None
    actual_end_date: Optional[date] = None
    budget: Optional[float] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    manager_id: Optional[int] = None
    notes: Optional[str] = None

class ProjectResponse(BaseModel):
    id: int
    name: str
    client_id: int
    description: Optional[str] = None
    status: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    actual_start_date: Optional[date] = None
    actual_end_date: Optional[date] = None
    budget: Optional[float] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    manager_id: Optional[int] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None

# Routes
@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    current_user: UserProfile = Depends(get_current_user)
):
    """Create a new project"""
    try:
        # Add the current user as the creator
        project_dict = project_data.dict()
        project_dict["created_by"] = current_user.id
        
        # Create the project in Supabase
        project = create_record("projects", project_dict)
        
        return project
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating project: {str(e)}"
        )

@router.get("", response_model=List[ProjectResponse])
async def get_projects(
    client_id: Optional[int] = Query(None, description="Filter by client ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    manager_id: Optional[int] = Query(None, description="Filter by manager ID"),
    search: Optional[str] = Query(None, description="Search by name or description"),
    limit: int = Query(100, description="Limit the number of results"),
    offset: int = Query(0, description="Offset for pagination"),
    current_user: UserProfile = Depends(get_current_user)
):
    """Get all projects with optional filtering"""
    try:
        # Define the query function
        def query_builder(query):
            if client_id:
                query = query.eq("client_id", client_id)
            if status:
                query = query.eq("status", status)
            if manager_id:
                query = query.eq("manager_id", manager_id)
            if search:
                query = query.or_(f"name.ilike.%{search}%,description.ilike.%{search}%")
            return query.range(offset, offset + limit - 1).order("name")
        
        # Query the projects
        projects = query_records("projects", query_builder)
        
        return projects
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting projects: {str(e)}"
        )

@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int = Path(..., description="The ID of the project to get"),
    current_user: UserProfile = Depends(get_current_user)
):
    """Get a project by ID"""
    try:
        project = get_record("projects", project_id)
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        return project
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting project: {str(e)}"
        )

@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_data: ProjectUpdate,
    project_id: int = Path(..., description="The ID of the project to update"),
    current_user: UserProfile = Depends(get_current_user)
):
    """Update a project"""
    try:
        # Check if project exists
        existing_project = get_record("projects", project_id)
        if not existing_project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        # Update the project
        updated_project = update_record("projects", project_id, project_data.dict(exclude_unset=True))
        
        return updated_project
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating project: {str(e)}"
        )

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: int = Path(..., description="The ID of the project to delete"),
    current_user: UserProfile = Depends(get_current_user)
):
    """Delete a project"""
    try:
        # Check if project exists
        existing_project = get_record("projects", project_id)
        if not existing_project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        # Delete the project
        success = delete_record("projects", project_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete project"
            )
        
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting project: {str(e)}"
        ) 