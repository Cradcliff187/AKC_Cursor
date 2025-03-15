from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from dependencies import templates

# Create auth router with a distinct prefix
auth_router = APIRouter(
    prefix="",  # No prefix to keep root-level paths like /login
    tags=["auth"]
)

@auth_router.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    """Display login form."""
    print("Login route accessed")
    return templates.TemplateResponse("login.html", {"request": request, "session": request.session})

@auth_router.post("/login", response_class=HTMLResponse)
async def login_post(request: Request, email: str = Form(...), password: str = Form(...)):
    """Handle login form submission."""
    print(f"Login attempt with email: {email}")
    # Mock authentication - hardcoded credentials for testing
    if email == "admin@akc.org" and password == "admin123":
        request.session["user_id"] = 1
        request.session["user_name"] = "Admin User"
        request.session["user_role"] = "admin"
        return RedirectResponse(url="/dashboard", status_code=303)
    
    # If authentication fails, render login page with error
    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "session": request.session,
            "error": "Invalid email or password"
        }
    )

@auth_router.get("/logout")
async def logout(request: Request):
    """Handle logout."""
    request.session.clear()
    return RedirectResponse(url="/") 