"""
API routes for client operations.

This module defines the API endpoints for creating, retrieving, updating, and deleting clients.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Path, Query
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

# Import the Client model
from models.client import Client
from app.services.supabase import create_record, get_record, update_record, delete_record, query_records
from api.user_routes import get_current_user, UserProfile

router = APIRouter(
    prefix="/api/clients",
    tags=["clients"],
    responses={404: {"description": "Not found"}},
)

# Pydantic models for request and response
class ClientCreate(BaseModel):
    name: str
    contact_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    company: Optional[str] = None
    website: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = "active"
    type: Optional[str] = None
    tax_id: Optional[str] = None

class ClientUpdate(BaseModel):
    name: Optional[str] = None
    contact_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    company: Optional[str] = None
    website: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = None
    type: Optional[str] = None
    tax_id: Optional[str] = None

class ClientResponse(BaseModel):
    id: int
    name: str
    contact_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    company: Optional[str] = None
    website: Optional[str] = None
    notes: Optional[str] = None
    status: str
    type: Optional[str] = None
    tax_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None

# Routes
@router.post("", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
async def create_client(
    client_data: ClientCreate,
    current_user: UserProfile = Depends(get_current_user)
):
    """Create a new client"""
    try:
        # Add the current user as the creator
        client_dict = client_data.dict()
        client_dict["created_by"] = current_user.id
        
        # Create the client in Supabase
        client = create_record("clients", client_dict)
        
        return client
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating client: {str(e)}"
        )

@router.get("", response_model=List[ClientResponse])
async def get_clients(
    status: Optional[str] = Query(None, description="Filter by status"),
    type: Optional[str] = Query(None, description="Filter by type"),
    search: Optional[str] = Query(None, description="Search by name or company"),
    limit: int = Query(100, description="Limit the number of results"),
    offset: int = Query(0, description="Offset for pagination"),
    current_user: UserProfile = Depends(get_current_user)
):
    """Get all clients with optional filtering"""
    try:
        # Define the query function
        def query_builder(query):
            if status:
                query = query.eq("status", status)
            if type:
                query = query.eq("type", type)
            if search:
                query = query.or_(f"name.ilike.%{search}%,company.ilike.%{search}%")
            return query.range(offset, offset + limit - 1).order("name")
        
        # Query the clients
        clients = query_records("clients", query_builder)
        
        return clients
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting clients: {str(e)}"
        )

@router.get("/{client_id}", response_model=ClientResponse)
async def get_client(
    client_id: int = Path(..., description="The ID of the client to get"),
    current_user: UserProfile = Depends(get_current_user)
):
    """Get a client by ID"""
    try:
        client = get_record("clients", client_id)
        
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client not found"
            )
        
        return client
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting client: {str(e)}"
        )

@router.patch("/{client_id}", response_model=ClientResponse)
async def update_client(
    client_data: ClientUpdate,
    client_id: int = Path(..., description="The ID of the client to update"),
    current_user: UserProfile = Depends(get_current_user)
):
    """Update a client"""
    try:
        # Check if client exists
        existing_client = get_record("clients", client_id)
        if not existing_client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client not found"
            )
        
        # Update the client
        updated_client = update_record("clients", client_id, client_data.dict(exclude_unset=True))
        
        return updated_client
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating client: {str(e)}"
        )

@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client(
    client_id: int = Path(..., description="The ID of the client to delete"),
    current_user: UserProfile = Depends(get_current_user)
):
    """Delete a client"""
    try:
        # Check if client exists
        existing_client = get_record("clients", client_id)
        if not existing_client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Client not found"
            )
        
        # Delete the client
        success = delete_record("clients", client_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete client"
            )
        
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting client: {str(e)}"
        ) 