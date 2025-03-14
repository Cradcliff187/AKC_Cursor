"""
Main API router for the AKC CRM application.

This module imports and includes all API route modules.
"""

from fastapi import APIRouter

from api.user_routes import router as user_router
from api.client_routes import router as client_router
from api.project_routes import router as project_router

# Create the main API router
api_router = APIRouter()

# Include all route modules
api_router.include_router(user_router)
api_router.include_router(client_router)
api_router.include_router(project_router) 