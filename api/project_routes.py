"""
API routes for project operations.

This module defines the API endpoints for creating, retrieving, updating, and deleting projects.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime, date

# Import the Project model
from models.project import Project

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
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

class ProjectStatusUpdate(BaseModel):
    status: str

# API Routes
@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(project: ProjectCreate):
    """
    Create a new project.
    """
    # Create a new Project instance
    new_project = Project(
        name=project.name,
        client_id=project.client_id,
        description=project.description,
        status=project.status,
        start_date=project.start_date,
        end_date=project.end_date,
        budget=project.budget,
        address=project.address,
        city=project.city,
        state=project.state,
        zip_code=project.zip_code,
        manager_id=project.manager_id,
        notes=project.notes
    )
    
    # Save the project to the database
    # This would typically involve a database operation
    # For now, we'll just return the project with a dummy ID
    new_project.id = 1  # This would be set by the database
    new_project.created_at = datetime.now()
    new_project.updated_at = datetime.now()
    
    return new_project

@router.get("/", response_model=List[ProjectResponse])
async def get_projects(
    client_id: Optional[int] = None,
    status: Optional[str] = None,
    manager_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100
):
    """
    Retrieve all projects with optional filtering.
    """
    # This would typically involve a database query
    # For now, we'll just return an empty list
    return []

@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: int):
    """
    Retrieve a specific project by ID.
    """
    # This would typically involve a database query
    # For now, we'll raise a not found exception
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Project with ID {project_id} not found"
    )

@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(project_id: int, project: ProjectUpdate):
    """
    Update a specific project by ID.
    """
    # This would typically involve a database query and update
    # For now, we'll raise a not found exception
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Project with ID {project_id} not found"
    )

@router.patch("/{project_id}/status", response_model=ProjectResponse)
async def update_project_status(project_id: int, status_update: ProjectStatusUpdate):
    """
    Update the status of a specific project.
    """
    # This would typically involve a database query and update
    # For now, we'll raise a not found exception
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Project with ID {project_id} not found"
    )

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(project_id: int):
    """
    Delete a specific project by ID.
    """
    # This would typically involve a database query and delete
    # For now, we'll raise a not found exception
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Project with ID {project_id} not found"
    )

@router.get("/client/{client_id}", response_model=List[ProjectResponse])
async def get_client_projects(client_id: int):
    """
    Retrieve all projects for a specific client.
    """
    # This would typically involve a database query
    # For now, we'll just return an empty list
    return [] 