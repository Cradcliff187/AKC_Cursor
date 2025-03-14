"""
Simple FastAPI Application with Supabase Integration

This is a simple FastAPI application that integrates with Supabase.
"""

import os
from fastapi import FastAPI, HTTPException, Depends, Header, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv
from supabase import create_client, Client
import json
import jwt
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

# Get environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
JWT_SECRET = os.getenv("FLASK_SECRET_KEY", "default-secret-key")

# Security
security = HTTPBearer()

# Create Supabase clients
def get_supabase_client() -> Client:
    """Get a Supabase client with anonymous key"""
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def get_supabase_admin_client() -> Client:
    """Get a Supabase client with service role key for admin operations"""
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

# JWT Authentication
def verify_jwt_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Verify JWT token and return user information."""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        
        # Check if token is expired
        if datetime.fromtimestamp(payload.get("exp", 0)) < datetime.now():
            raise HTTPException(status_code=401, detail="Token has expired")
        
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication error: {str(e)}")

# Admin role verification
def verify_admin_role(payload: dict = Depends(verify_jwt_token)):
    """Verify that the user has admin role."""
    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to access this resource")
    return payload

# Create FastAPI app
app = FastAPI(
    title="AKC Construction CRM API",
    description="API for AKC Construction CRM with Supabase Integration",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class UserProfile(BaseModel):
    """Model for user profile."""
    id: str
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[str] = None
    status: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class Client(BaseModel):
    """Model for client."""
    id: Optional[str] = None
    name: str
    contact_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    status: Optional[str] = "active"
    notes: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class ClientCreate(BaseModel):
    """Model for client creation."""
    name: str
    contact_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    status: Optional[str] = "active"
    notes: Optional[str] = None

class ClientUpdate(BaseModel):
    """Model for client update."""
    name: Optional[str] = None
    contact_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None

class Project(BaseModel):
    """Model for project."""
    id: Optional[str] = None
    client_id: str
    name: str
    description: Optional[str] = None
    status: Optional[str] = "pending"
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    budget: Optional[float] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class ProjectCreate(BaseModel):
    """Model for project creation."""
    client_id: str
    name: str
    description: Optional[str] = None
    status: Optional[str] = "pending"
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    budget: Optional[float] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None

class ProjectUpdate(BaseModel):
    """Model for project update."""
    client_id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    budget: Optional[float] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None

# Authentication endpoints
class LoginRequest(BaseModel):
    """Model for login request."""
    email: str
    password: str

class LoginResponse(BaseModel):
    """Model for login response."""
    access_token: str
    token_type: str
    user: Dict[str, Any]

@app.post("/api/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """Login with email and password."""
    try:
        # Get Supabase client
        supabase = get_supabase_client()
        
        # Sign in with email and password
        response = supabase.auth.sign_in_with_password({
            "email": request.email,
            "password": request.password
        })
        
        # Get user data
        user_data = response.user
        
        # Get user profile from database
        user_profile_response = supabase.table("user_profiles").select("*").eq("id", user_data.id).execute()
        
        if user_profile_response.data:
            user_profile = user_profile_response.data[0]
            
            # Create JWT token
            payload = {
                "sub": user_data.id,
                "email": user_data.email,
                "role": user_profile.get("role", "user"),
                "exp": datetime.now() + timedelta(days=1)
            }
            
            token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
            
            # Return token and user data
            return {
                "access_token": token,
                "token_type": "bearer",
                "user": {
                    "id": user_data.id,
                    "email": user_data.email,
                    "first_name": user_profile.get("first_name"),
                    "last_name": user_profile.get("last_name"),
                    "role": user_profile.get("role")
                }
            }
        else:
            raise HTTPException(status_code=404, detail="User profile not found")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")

@app.get("/api/auth/me")
async def get_current_user(payload: dict = Depends(verify_jwt_token)):
    """Get current user information."""
    try:
        # Get Supabase client
        supabase = get_supabase_admin_client()
        
        # Get user profile from database
        user_profile_response = supabase.table("user_profiles").select("*").eq("id", payload.get("sub")).execute()
        
        if user_profile_response.data:
            return user_profile_response.data[0]
        else:
            raise HTTPException(status_code=404, detail="User profile not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting user profile: {str(e)}")

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint for the API."""
    return {
        "message": "Welcome to the AKC Construction CRM API",
        "version": "1.0.0",
        "documentation": "/docs",
        "endpoints": {
            "authentication": {
                "login": "/api/auth/login",
                "current_user": "/api/auth/me"
            },
            "users": {
                "list": "/api/users",
                "get": "/api/users/{user_id}"
            },
            "clients": {
                "list": "/api/clients",
                "get": "/api/clients/{client_id}",
                "create": "/api/clients",
                "update": "/api/clients/{client_id}",
                "delete": "/api/clients/{client_id}"
            },
            "projects": {
                "list": "/api/projects",
                "get": "/api/projects/{project_id}",
                "create": "/api/projects",
                "update": "/api/projects/{project_id}",
                "delete": "/api/projects/{project_id}"
            },
            "database": {
                "tables": "/api/tables",
                "table_schema": "/api/tables/{table_name}/schema",
                "table_data": "/api/tables/{table_name}/data"
            }
        }
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for the API."""
    return {"status": "healthy"}

# Get user profiles endpoint
@app.get("/api/users", response_model=List[UserProfile])
async def get_user_profiles(payload: dict = Depends(verify_admin_role)):
    """Get all user profiles. Requires admin role."""
    try:
        # Get Supabase client with service role key
        supabase = get_supabase_admin_client()
        
        # Get all user profiles
        response = supabase.table("user_profiles").select("*").execute()
        
        # Return the data
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting user profiles: {str(e)}")

# Get user profile by ID endpoint
@app.get("/api/users/{user_id}", response_model=UserProfile)
async def get_user_profile(user_id: str):
    """Get a user profile by ID."""
    try:
        # Get Supabase client with service role key
        supabase = get_supabase_admin_client()
        
        # Get the user profile
        response = supabase.table("user_profiles").select("*").eq("id", user_id).execute()
        
        # Check if the user profile exists
        if not response.data:
            raise HTTPException(status_code=404, detail=f"User profile with ID {user_id} not found")
        
        # Return the data
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting user profile: {str(e)}")

# Get database tables endpoint
@app.get("/api/tables")
async def get_tables():
    """Get all database tables."""
    try:
        # Get Supabase client with service role key
        supabase = get_supabase_admin_client()
        
        # Get a list of tables by querying each known table
        # This is a workaround since we can't directly query pg_catalog
        known_tables = [
            "user_profiles",
            "user_notifications",
            "clients",
            "projects",
            "project_tasks",
            "invoices",
            "invoice_items",
            "payments",
            "bids",
            "bid_items",
            "expenses",
            "time_entries",
            "documents"
        ]
        
        # Verify which tables exist
        existing_tables = []
        for table in known_tables:
            try:
                # Try to get a single row from the table
                response = supabase.table(table).select("*").limit(1).execute()
                # If no error, the table exists
                existing_tables.append(table)
            except Exception:
                # If error, the table doesn't exist or is not accessible
                pass
        
        # Return the data
        return {"tables": existing_tables}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting tables: {str(e)}")

# Get table schema endpoint
@app.get("/api/tables/{table_name}/schema")
async def get_table_schema(table_name: str):
    """Get the schema of a specific table."""
    try:
        # Get Supabase client with service role key
        supabase = get_supabase_admin_client()
        
        # First, check if the table exists by trying to query it
        try:
            supabase.table(table_name).select("*").limit(1).execute()
        except Exception as e:
            raise HTTPException(status_code=404, detail=f"Table {table_name} not found: {str(e)}")
        
        # Since we can't directly query information_schema, we'll infer the schema
        # by examining the structure of a row from the table
        response = supabase.table(table_name).select("*").limit(1).execute()
        
        # If the table is empty, we can't infer the schema
        if not response.data:
            return {"table_name": table_name, "columns": [], "note": "Table is empty, schema cannot be inferred"}
        
        # Extract column names and infer types from the first row
        first_row = response.data[0]
        columns = []
        
        for column_name, value in first_row.items():
            data_type = "unknown"
            if value is None:
                data_type = "unknown (null value)"
            elif isinstance(value, str):
                data_type = "text"
            elif isinstance(value, int):
                data_type = "integer"
            elif isinstance(value, float):
                data_type = "numeric"
            elif isinstance(value, bool):
                data_type = "boolean"
            elif isinstance(value, dict):
                data_type = "json"
            elif isinstance(value, list):
                data_type = "array"
            
            columns.append({
                "column_name": column_name,
                "data_type": data_type,
                "is_nullable": "YES",  # We can't determine this without information_schema
                "column_default": None  # We can't determine this without information_schema
            })
        
        # Return the data
        return {
            "table_name": table_name, 
            "columns": columns,
            "note": "Schema is inferred from data types, nullable and default values are approximations"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting table schema: {str(e)}")

# Get table data endpoint
@app.get("/api/tables/{table_name}/data")
async def get_table_data(
    table_name: str, 
    page: int = 1, 
    page_size: int = 10,
    order_by: Optional[str] = None,
    order_direction: Optional[str] = "asc"
):
    """Get data from a specific table with pagination."""
    try:
        # Get Supabase client with service role key
        supabase = get_supabase_admin_client()
        
        # Calculate offset
        offset = (page - 1) * page_size
        
        # Build query
        query = supabase.table(table_name).select("*", count="exact")
        
        # Add pagination
        query = query.range(offset, offset + page_size - 1)
        
        # Add ordering if specified
        if order_by:
            if order_direction.lower() == "desc":
                query = query.order(order_by, desc=True)
            else:
                query = query.order(order_by)
        
        # Execute query
        response = query.execute()
        
        # Get total count
        total_count = response.count if hasattr(response, 'count') else None
        
        # Return the data with pagination info
        return {
            "table_name": table_name,
            "data": response.data,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total_count": total_count,
                "total_pages": (total_count + page_size - 1) // page_size if total_count else None
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting table data: {str(e)}")

# Client management endpoints
@app.get("/api/clients", response_model=List[Client])
async def get_clients(
    payload: dict = Depends(verify_jwt_token),
    status: Optional[str] = None,
    search: Optional[str] = None,
    page: int = 1,
    page_size: int = 10
):
    """Get all clients with optional filtering."""
    try:
        # Get Supabase client
        supabase = get_supabase_admin_client()
        
        # Build query
        query = supabase.table("clients").select("*", count="exact")
        
        # Add filters
        if status:
            query = query.eq("status", status)
        
        if search:
            query = query.or_(f"name.ilike.%{search}%,contact_name.ilike.%{search}%,email.ilike.%{search}%")
        
        # Add pagination
        offset = (page - 1) * page_size
        query = query.range(offset, offset + page_size - 1)
        
        # Execute query
        response = query.execute()
        
        # Return the data
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting clients: {str(e)}")

@app.get("/api/clients/{client_id}", response_model=Client)
async def get_client(client_id: str, payload: dict = Depends(verify_jwt_token)):
    """Get a client by ID."""
    try:
        # Get Supabase client
        supabase = get_supabase_admin_client()
        
        # Get the client
        response = supabase.table("clients").select("*").eq("id", client_id).execute()
        
        # Check if the client exists
        if not response.data:
            raise HTTPException(status_code=404, detail=f"Client with ID {client_id} not found")
        
        # Return the data
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting client: {str(e)}")

@app.post("/api/clients", response_model=Client)
async def create_client(client: ClientCreate, payload: dict = Depends(verify_jwt_token)):
    """Create a new client."""
    try:
        # Get Supabase client
        supabase = get_supabase_admin_client()
        
        # Create the client
        now = datetime.now().isoformat()
        client_data = {
            **client.dict(),
            "created_at": now,
            "updated_at": now
        }
        
        response = supabase.table("clients").insert(client_data).execute()
        
        # Return the created client
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating client: {str(e)}")

@app.put("/api/clients/{client_id}", response_model=Client)
async def update_client(client_id: str, client: ClientUpdate, payload: dict = Depends(verify_jwt_token)):
    """Update a client."""
    try:
        # Get Supabase client
        supabase = get_supabase_admin_client()
        
        # Check if the client exists
        check_response = supabase.table("clients").select("*").eq("id", client_id).execute()
        
        if not check_response.data:
            raise HTTPException(status_code=404, detail=f"Client with ID {client_id} not found")
        
        # Update the client
        client_data = {
            **client.dict(exclude_unset=True),
            "updated_at": datetime.now().isoformat()
        }
        
        response = supabase.table("clients").update(client_data).eq("id", client_id).execute()
        
        # Return the updated client
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating client: {str(e)}")

@app.delete("/api/clients/{client_id}")
async def delete_client(client_id: str, payload: dict = Depends(verify_admin_role)):
    """Delete a client. Requires admin role."""
    try:
        # Get Supabase client
        supabase = get_supabase_admin_client()
        
        # Check if the client exists
        check_response = supabase.table("clients").select("*").eq("id", client_id).execute()
        
        if not check_response.data:
            raise HTTPException(status_code=404, detail=f"Client with ID {client_id} not found")
        
        # Delete the client
        supabase.table("clients").delete().eq("id", client_id).execute()
        
        # Return success message
        return {"message": f"Client with ID {client_id} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting client: {str(e)}")

# Project management endpoints
@app.get("/api/projects", response_model=List[Project])
async def get_projects(
    payload: dict = Depends(verify_jwt_token),
    client_id: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    page: int = 1,
    page_size: int = 10
):
    """Get all projects with optional filtering."""
    try:
        # Get Supabase client
        supabase = get_supabase_admin_client()
        
        # Build query
        query = supabase.table("projects").select("*", count="exact")
        
        # Add filters
        if client_id:
            query = query.eq("client_id", client_id)
            
        if status:
            query = query.eq("status", status)
        
        if search:
            query = query.or_(f"name.ilike.%{search}%,description.ilike.%{search}%")
        
        # Add pagination
        offset = (page - 1) * page_size
        query = query.range(offset, offset + page_size - 1)
        
        # Execute query
        response = query.execute()
        
        # Return the data
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting projects: {str(e)}")

@app.get("/api/projects/{project_id}", response_model=Project)
async def get_project(project_id: str, payload: dict = Depends(verify_jwt_token)):
    """Get a project by ID."""
    try:
        # Get Supabase client
        supabase = get_supabase_admin_client()
        
        # Get the project
        response = supabase.table("projects").select("*").eq("id", project_id).execute()
        
        # Check if the project exists
        if not response.data:
            raise HTTPException(status_code=404, detail=f"Project with ID {project_id} not found")
        
        # Return the data
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting project: {str(e)}")

@app.post("/api/projects", response_model=Project)
async def create_project(project: ProjectCreate, payload: dict = Depends(verify_jwt_token)):
    """Create a new project."""
    try:
        # Get Supabase client
        supabase = get_supabase_admin_client()
        
        # Check if the client exists
        client_response = supabase.table("clients").select("id").eq("id", project.client_id).execute()
        
        if not client_response.data:
            raise HTTPException(status_code=404, detail=f"Client with ID {project.client_id} not found")
        
        # Create the project
        now = datetime.now().isoformat()
        project_data = {
            **project.dict(),
            "created_at": now,
            "updated_at": now
        }
        
        response = supabase.table("projects").insert(project_data).execute()
        
        # Return the created project
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating project: {str(e)}")

@app.put("/api/projects/{project_id}", response_model=Project)
async def update_project(project_id: str, project: ProjectUpdate, payload: dict = Depends(verify_jwt_token)):
    """Update a project."""
    try:
        # Get Supabase client
        supabase = get_supabase_admin_client()
        
        # Check if the project exists
        check_response = supabase.table("projects").select("*").eq("id", project_id).execute()
        
        if not check_response.data:
            raise HTTPException(status_code=404, detail=f"Project with ID {project_id} not found")
        
        # If client_id is being updated, check if the client exists
        if project.client_id:
            client_response = supabase.table("clients").select("id").eq("id", project.client_id).execute()
            
            if not client_response.data:
                raise HTTPException(status_code=404, detail=f"Client with ID {project.client_id} not found")
        
        # Update the project
        project_data = {
            **project.dict(exclude_unset=True),
            "updated_at": datetime.now().isoformat()
        }
        
        response = supabase.table("projects").update(project_data).eq("id", project_id).execute()
        
        # Return the updated project
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating project: {str(e)}")

@app.delete("/api/projects/{project_id}")
async def delete_project(project_id: str, payload: dict = Depends(verify_admin_role)):
    """Delete a project. Requires admin role."""
    try:
        # Get Supabase client
        supabase = get_supabase_admin_client()
        
        # Check if the project exists
        check_response = supabase.table("projects").select("*").eq("id", project_id).execute()
        
        if not check_response.data:
            raise HTTPException(status_code=404, detail=f"Project with ID {project_id} not found")
        
        # Delete the project
        supabase.table("projects").delete().eq("id", project_id).execute()
        
        # Return success message
        return {"message": f"Project with ID {project_id} deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting project: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    
    # Run the application
    uvicorn.run("supabase_api:app", host="0.0.0.0", port=8000, reload=True) 