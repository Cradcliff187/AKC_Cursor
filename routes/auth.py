from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from dependencies import templates, get_session, check_auth
from fastapi import status

# Create auth router with a distinct prefix
router = APIRouter(
    prefix="",  # No prefix to keep root-level paths like /login
    tags=["auth"]
)

@router.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    """Display login form."""
    # Check if user is already logged in
    if check_auth(request.session):
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    
    # Get the original URL the user was trying to access
    next_url = request.query_params.get("next", "/dashboard")
    request.session["next_url"] = next_url
    
    return templates.TemplateResponse("login.html", {"request": request, "session": request.session})

@router.post("/login", response_class=RedirectResponse)
async def login_post(request: Request, email: str = Form(...), password: str = Form(...)):
    """Handle login form submission."""
    # Mock authentication - hardcoded credentials for testing
    if email == "admin@akc.org" and password == "admin123":
        request.session["user_id"] = 1
        request.session["user_name"] = "Admin User"
        request.session["user_role"] = "admin"
        
        # Redirect to the original URL or dashboard
        next_url = request.session.get("next_url", "/dashboard")
        return RedirectResponse(url=next_url, status_code=status.HTTP_303_SEE_OTHER)
    
    # If authentication fails, set error message and redirect back to login
    request.session["login_error"] = "Invalid email or password"
    return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/logout")
async def logout(request: Request):
    """Handle logout."""
    request.session.clear()
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

# Authentication dependency for routes
def require_auth(session: dict = Depends(get_session)):
    """Check if user is authenticated and return session."""
    if not check_auth(session):
        # Redirect to login page with next parameter
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    return session 