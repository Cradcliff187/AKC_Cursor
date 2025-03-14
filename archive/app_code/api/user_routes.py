"""
User API Routes

This module defines the API routes for user profiles and notifications.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Query, Path, Header, status
from pydantic import BaseModel, Field, EmailStr
import jwt
from datetime import datetime, timedelta
import os

from models.user_profile import UserProfile, UserNotification, UserRole, UserStatus, UserService
from app.services.supabase import sign_up, sign_in, sign_out, get_user_by_id, get_user_by_email, create_record, get_record, update_record, delete_record

router = APIRouter(prefix="/api/users", tags=["users"])

# JWT Configuration
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_MINUTES = 60 * 24  # 24 hours

# Pydantic models for request and response validation
class UserProfileCreate(BaseModel):
    """Model for creating a user profile."""
    email: EmailStr
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    display_name: Optional[str] = None
    role: str = UserRole.EMPLOYEE.value
    status: str = UserStatus.ACTIVE.value
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    title: Optional[str] = None
    department: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None


class UserProfileUpdate(BaseModel):
    """Model for updating a user profile."""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    display_name: Optional[str] = None
    role: Optional[str] = None
    status: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    title: Optional[str] = None
    department: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None


class UserProfileResponse(BaseModel):
    """Model for user profile response."""
    id: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    display_name: Optional[str] = None
    role: str
    status: str
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    title: Optional[str] = None
    department: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class UserLoginRequest(BaseModel):
    """Model for user login request."""
    email: EmailStr
    password: str


class UserLoginResponse(BaseModel):
    """Model for user login response."""
    access_token: str
    token_type: str
    user: UserProfileResponse


# Authentication functions
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=JWT_EXPIRATION_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt


async def get_current_user(authorization: Optional[str] = Header(None)) -> UserProfile:
    """Get the current user from the JWT token"""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        # Extract token from "Bearer <token>"
        token = authorization.split(" ")[1]
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except (jwt.PyJWTError, IndexError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from database
    user = get_user_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return UserProfile(**user)


# Routes
@router.post("/register", response_model=UserProfileResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserProfileCreate):
    """Register a new user"""
    # Check if user already exists
    existing_user = get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    # Create user in Supabase Auth and user_profiles table
    try:
        auth_response = sign_up(user_data.email, user_data.password, user_data.dict(exclude={"password"}))
        
        if not auth_response or not auth_response.user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user"
            )
        
        # Get the created user
        user = get_user_by_id(auth_response.user.id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="User created but profile not found"
            )
        
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating user: {str(e)}"
        )


@router.post("/login", response_model=UserLoginResponse)
async def login(login_data: UserLoginRequest):
    """Login a user"""
    try:
        # Authenticate with Supabase
        auth_response = sign_in(login_data.email, login_data.password)
        
        if not auth_response or not auth_response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Get user profile
        user = get_user_by_id(auth_response.user.id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="User authenticated but profile not found"
            )
        
        # Create access token
        access_token = create_access_token(
            data={"sub": user["id"]}
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error logging in: {str(e)}"
        )


@router.post("/logout")
async def logout(current_user: UserProfile = Depends(get_current_user), authorization: Optional[str] = Header(None)):
    """Logout a user"""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    try:
        # Extract token from "Bearer <token>"
        token = authorization.split(" ")[1]
        
        # Sign out from Supabase
        sign_out(token)
        
        return {"message": "Successfully logged out"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error logging out: {str(e)}"
        )


@router.get("/me", response_model=UserProfileResponse)
async def get_current_user_profile(current_user: UserProfile = Depends(get_current_user)):
    """Get the current user's profile"""
    return current_user


@router.get("/{user_id}", response_model=UserProfileResponse)
async def get_user_profile(
    user_id: str = Path(..., description="The ID of the user to get"),
    current_user: UserProfile = Depends(get_current_user)
):
    """Get a user profile by ID"""
    # Check if user has permission to view this profile
    if current_user.id != user_id and current_user.role != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this profile"
        )
    
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.patch("/{user_id}", response_model=UserProfileResponse)
async def update_user_profile(
    user_data: UserProfileUpdate,
    user_id: str = Path(..., description="The ID of the user to update"),
    current_user: UserProfile = Depends(get_current_user)
):
    """Update a user profile"""
    # Check if user has permission to update this profile
    if current_user.id != user_id and current_user.role != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this profile"
        )
    
    # Check if user exists
    existing_user = get_user_by_id(user_id)
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update user profile
    try:
        updated_user = update_record("user_profiles", user_id, user_data.dict(exclude_unset=True))
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update user profile"
            )
        
        return updated_user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating user profile: {str(e)}"
        )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_profile(
    user_id: str = Path(..., description="The ID of the user to delete"),
    current_user: UserProfile = Depends(get_current_user)
):
    """Delete a user profile"""
    # Only admins can delete users
    if current_user.role != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete users"
        )
    
    # Check if user exists
    existing_user = get_user_by_id(user_id)
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Delete user profile
    try:
        success = delete_record("user_profiles", user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete user profile"
            )
        
        # Note: This doesn't delete the auth user in Supabase
        # For complete deletion, you would need to use the admin client
        
        return None
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting user profile: {str(e)}"
        )


@router.get("/", response_model=List[UserProfileResponse])
async def list_user_profiles(
    role: Optional[str] = Query(None, description="Filter by user role"),
    status: Optional[str] = Query(None, description="Filter by user status"),
    department: Optional[str] = Query(None, description="Filter by department"),
    search: Optional[str] = Query(None, description="Search term for name or email")
) -> List[UserProfileResponse]:
    """List user profiles with optional filtering."""
    user_profiles = UserService.list_user_profiles(role, status, department, search)
    return [UserProfileResponse.from_model(profile) for profile in user_profiles]


@router.put("/{user_id}/last-login", response_model=UserProfileResponse)
async def update_last_login(user_id: str = Path(..., description="The ID of the user profile")) -> UserProfileResponse:
    """Update the last login timestamp for a user."""
    user_profile = UserService.update_last_login(user_id)
    if not user_profile:
        raise HTTPException(status_code=404, detail="User profile not found")
    return UserProfileResponse.from_model(user_profile)


@router.post("/{user_id}/notifications", response_model=NotificationResponse)
async def create_notification(
    notification_data: NotificationCreate,
    user_id: str = Path(..., description="The ID of the user")
) -> NotificationResponse:
    """Create a new notification for a user."""
    notification = UserService.send_notification_to_user(
        user_id,
        notification_data.title,
        notification_data.message,
        notification_data.type,
        notification_data.link
    )
    if not notification:
        raise HTTPException(status_code=500, detail="Failed to create notification")
    return NotificationResponse.from_model(notification)


@router.get("/{user_id}/notifications", response_model=List[NotificationResponse])
async def list_notifications(
    user_id: str = Path(..., description="The ID of the user"),
    include_read: bool = Query(False, description="Whether to include read notifications")
) -> List[NotificationResponse]:
    """List notifications for a user."""
    notifications = UserService.list_notifications(user_id, include_read)
    return [NotificationResponse.from_model(notification) for notification in notifications]


@router.put("/notifications/{notification_id}/read", response_model=NotificationResponse)
async def mark_notification_as_read(
    notification_id: str = Path(..., description="The ID of the notification")
) -> NotificationResponse:
    """Mark a notification as read."""
    notification = UserService.mark_notification_as_read(notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return NotificationResponse.from_model(notification)


@router.put("/{user_id}/notifications/read-all", response_model=Dict[str, bool])
async def mark_all_notifications_as_read(
    user_id: str = Path(..., description="The ID of the user")
) -> Dict[str, bool]:
    """Mark all notifications for a user as read."""
    success = UserService.mark_all_notifications_as_read(user_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to mark notifications as read")
    return {"success": True}


@router.delete("/notifications/{notification_id}", response_model=Dict[str, bool])
async def delete_notification(
    notification_id: str = Path(..., description="The ID of the notification")
) -> Dict[str, bool]:
    """Delete a notification."""
    success = UserService.delete_notification(notification_id)
    if not success:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"success": True} 