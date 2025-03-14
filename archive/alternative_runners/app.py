"""
AKC Construction CRM API

This is the main entry point for the AKC Construction CRM API.
"""

import os
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import API routes
from api.user_routes import router as user_router
from api.client_routes import router as client_router
from api.project_routes import router as project_router

# Create FastAPI app
app = FastAPI(
    title="AKC Construction CRM API",
    description="API for the AKC Construction CRM system",
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

# Include routers
app.include_router(user_router)
app.include_router(client_router)
app.include_router(project_router)

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint for the API."""
    return {
        "message": "Welcome to the AKC Construction CRM API",
        "version": "1.0.0",
        "documentation": "/docs"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for the API."""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    
    # Get port from environment variable or use default
    port = int(os.getenv("PORT", 8000))
    
    # Run the application
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True) 