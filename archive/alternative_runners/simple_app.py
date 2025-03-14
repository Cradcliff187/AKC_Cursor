"""
Simple FastAPI Application

This is a simple FastAPI application to test if we can run it.
"""

from fastapi import FastAPI

# Create FastAPI app
app = FastAPI(
    title="Simple FastAPI Application",
    description="A simple FastAPI application to test if we can run it",
    version="1.0.0"
)

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint for the API."""
    return {
        "message": "Welcome to the Simple FastAPI Application",
        "version": "1.0.0"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for the API."""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    
    # Run the application
    uvicorn.run("simple_app:app", host="0.0.0.0", port=8000, reload=True) 