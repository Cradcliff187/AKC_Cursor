"""
API routes for client operations.

This module defines the API endpoints for creating, retrieving, updating, and deleting clients.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

# Import the Client model
from models.client import Client

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
    email: Optional[EmailStr] = None
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
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

# API Routes
@router.post("/", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
async def create_client(client: ClientCreate):
    """
    Create a new client.
    """
    # Create a new Client instance
    new_client = Client(
        name=client.name,
        contact_name=client.contact_name,
        email=client.email,
        phone=client.phone,
        address=client.address,
        city=client.city,
        state=client.state,
        zip_code=client.zip_code,
        company=client.company,
        website=client.website,
        notes=client.notes,
        status=client.status,
        type=client.type,
        tax_id=client.tax_id
    )
    
    # Save the client to the database
    # This would typically involve a database operation
    # For now, we'll just return the client with a dummy ID
    new_client.id = 1  # This would be set by the database
    new_client.created_at = datetime.now()
    new_client.updated_at = datetime.now()
    
    return new_client

@router.get("/", response_model=List[ClientResponse])
async def get_clients(
    status: Optional[str] = None,
    type: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
):
    """
    Retrieve all clients with optional filtering.
    """
    # This would typically involve a database query
    # For now, we'll just return an empty list
    return []

@router.get("/{client_id}", response_model=ClientResponse)
async def get_client(client_id: int):
    """
    Retrieve a specific client by ID.
    """
    # This would typically involve a database query
    # For now, we'll raise a not found exception
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Client with ID {client_id} not found"
    )

@router.put("/{client_id}", response_model=ClientResponse)
async def update_client(client_id: int, client: ClientUpdate):
    """
    Update a specific client by ID.
    """
    # This would typically involve a database query and update
    # For now, we'll raise a not found exception
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Client with ID {client_id} not found"
    )

@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client(client_id: int):
    """
    Delete a specific client by ID.
    """
    # This would typically involve a database query and delete
    # For now, we'll raise a not found exception
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Client with ID {client_id} not found"
    ) 