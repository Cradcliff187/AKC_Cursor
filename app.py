"""
Simple FastAPI Application with Supabase Integration

This is a simple FastAPI application that integrates with Supabase.
"""

import os
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.middleware.sessions import SessionMiddleware

# Create FastAPI app
app = FastAPI(
    title="AKC CRM",
    description="AKC Construction CRM",
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

# Add session middleware
app.add_middleware(SessionMiddleware, secret_key="your-secret-key")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Add custom template functions
def url_for(name, filename=None):
    if filename:
        return f"/{name}/{filename}"
    return f"/{name}"

# Add template globals
templates.env.globals["url_for"] = url_for
templates.env.globals["get_flashed_messages"] = lambda with_categories=False: []

# Session dependency
def get_session(request: Request):
    return request.session

# Root endpoint
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Root endpoint for the API."""
    # Set a mock session for templates
    request.session["user_id"] = None
    request.session["user_name"] = "Guest"
    request.session["user_role"] = None
    
    # Pass the session to the template context
    return templates.TemplateResponse("index.html", {"request": request, "session": request.session})

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

# Login page
@app.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "session": request.session})

# Dashboard page (placeholder)
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, session: dict = Depends(get_session)):
    # This would normally check for authentication
    if not session.get("user_id"):
        return RedirectResponse(url="/login")
    return templates.TemplateResponse("dashboard.html", {"request": request, "session": request.session})

# Define other route handlers as needed
@app.get("/contacts", response_class=HTMLResponse)
async def contacts(request: Request):
    return templates.TemplateResponse("contacts.html", {"request": request, "session": request.session})

@app.get("/projects", response_class=HTMLResponse)
async def projects(request: Request):
    return templates.TemplateResponse("projects.html", {"request": request, "session": request.session})

@app.get("/time-logs", response_class=HTMLResponse)
async def time_logs(request: Request):
    return templates.TemplateResponse("time_logs.html", {"request": request, "session": request.session})

@app.get("/expenses", response_class=HTMLResponse)
async def expenses(request: Request):
    return templates.TemplateResponse("expenses.html", {"request": request, "session": request.session})

@app.get("/vendors", response_class=HTMLResponse)
async def vendors(request: Request):
    return templates.TemplateResponse("vendors.html", {"request": request, "session": request.session})

@app.get("/reports", response_class=HTMLResponse)
async def reports(request: Request):
    return templates.TemplateResponse("reports.html", {"request": request, "session": request.session})

@app.get("/admin/users", response_class=HTMLResponse)
async def admin_users(request: Request):
    return templates.TemplateResponse("admin_users.html", {"request": request, "session": request.session})

@app.get("/profile", response_class=HTMLResponse)
async def profile(request: Request):
    return templates.TemplateResponse("profile.html", {"request": request, "session": request.session})

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port) 