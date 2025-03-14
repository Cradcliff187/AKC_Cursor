"""
User Profile Model

This module defines the UserProfile model and related functionality.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum


class UserRole(str, Enum):
    """Enum representing the possible user roles."""
    ADMIN = "admin"
    MANAGER = "manager"
    EMPLOYEE = "employee"
    CLIENT = "client"
    CONTRACTOR = "contractor"
    GUEST = "guest"


class UserStatus(str, Enum):
    """Enum representing the possible user statuses."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    SUSPENDED = "suspended"


class UserProfile:
    """
    Represents a user profile in the system.
    
    Attributes:
        id (str): The unique identifier for the user profile.
        auth_id (str): The ID of the user in the authentication system.
        email (str): The email address of the user.
        first_name (str): The first name of the user.
        last_name (str): The last name of the user.
        display_name (str): The display name of the user.
        role (UserRole): The role of the user in the system.
        status (UserStatus): The status of the user in the system.
        phone (str): The phone number of the user.
        avatar_url (str): URL to the user's avatar image.
        title (str): The job title of the user.
        department (str): The department the user belongs to.
        hire_date (datetime): The date the user was hired.
        last_login (datetime): The date and time of the user's last login.
        preferences (Dict[str, Any]): User preferences and settings.
        created_at (datetime): When the user profile was created.
        updated_at (datetime): When the user profile was last updated.
    """
    
    def __init__(
        self,
        id: str,
        auth_id: str,
        email: str,
        first_name: str = None,
        last_name: str = None,
        display_name: str = None,
        role: UserRole = UserRole.EMPLOYEE,
        status: UserStatus = UserStatus.ACTIVE,
        phone: str = None,
        avatar_url: str = None,
        title: str = None,
        department: str = None,
        hire_date: datetime = None,
        last_login: datetime = None,
        preferences: Dict[str, Any] = None,
        created_at: datetime = None,
        updated_at: datetime = None
    ):
        self.id = id
        self.auth_id = auth_id
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.display_name = display_name or self._generate_display_name()
        self.role = role if isinstance(role, UserRole) else UserRole(role)
        self.status = status if isinstance(status, UserStatus) else UserStatus(status)
        self.phone = phone
        self.avatar_url = avatar_url
        self.title = title
        self.department = department
        self.hire_date = hire_date
        self.last_login = last_login
        self.preferences = preferences or {}
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
    
    def _generate_display_name(self) -> str:
        """Generate a display name from first and last name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        else:
            return self.email.split('@')[0]
    
    @property
    def full_name(self) -> str:
        """Get the full name of the user."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.display_name
    
    @property
    def is_active(self) -> bool:
        """Check if the user is active."""
        return self.status == UserStatus.ACTIVE
    
    @property
    def is_admin(self) -> bool:
        """Check if the user is an admin."""
        return self.role == UserRole.ADMIN
    
    @property
    def is_manager(self) -> bool:
        """Check if the user is a manager."""
        return self.role in [UserRole.ADMIN, UserRole.MANAGER]
    
    @property
    def is_employee(self) -> bool:
        """Check if the user is an employee."""
        return self.role in [UserRole.ADMIN, UserRole.MANAGER, UserRole.EMPLOYEE]
    
    @property
    def is_client(self) -> bool:
        """Check if the user is a client."""
        return self.role == UserRole.CLIENT
    
    @property
    def is_contractor(self) -> bool:
        """Check if the user is a contractor."""
        return self.role == UserRole.CONTRACTOR
    
    def has_permission(self, permission: str) -> bool:
        """Check if the user has a specific permission."""
        # This is a simplified implementation
        # In a real system, you would have a more complex permission system
        admin_permissions = ['create', 'read', 'update', 'delete', 'admin']
        manager_permissions = ['create', 'read', 'update']
        employee_permissions = ['create', 'read']
        client_permissions = ['read']
        contractor_permissions = ['read']
        guest_permissions = ['read']
        
        if self.role == UserRole.ADMIN:
            return permission in admin_permissions
        elif self.role == UserRole.MANAGER:
            return permission in manager_permissions
        elif self.role == UserRole.EMPLOYEE:
            return permission in employee_permissions
        elif self.role == UserRole.CLIENT:
            return permission in client_permissions
        elif self.role == UserRole.CONTRACTOR:
            return permission in contractor_permissions
        elif self.role == UserRole.GUEST:
            return permission in guest_permissions
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the user profile to a dictionary."""
        return {
            'id': self.id,
            'auth_id': self.auth_id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'display_name': self.display_name,
            'role': self.role.value if isinstance(self.role, UserRole) else self.role,
            'status': self.status.value if isinstance(self.status, UserStatus) else self.status,
            'phone': self.phone,
            'avatar_url': self.avatar_url,
            'title': self.title,
            'department': self.department,
            'hire_date': self.hire_date.isoformat() if self.hire_date else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'preferences': self.preferences,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserProfile':
        """Create a user profile from a dictionary."""
        return cls(
            id=data.get('id'),
            auth_id=data.get('auth_id'),
            email=data.get('email'),
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            display_name=data.get('display_name'),
            role=data.get('role', UserRole.EMPLOYEE),
            status=data.get('status', UserStatus.ACTIVE),
            phone=data.get('phone'),
            avatar_url=data.get('avatar_url'),
            title=data.get('title'),
            department=data.get('department'),
            hire_date=datetime.fromisoformat(data.get('hire_date')) if data.get('hire_date') else None,
            last_login=datetime.fromisoformat(data.get('last_login')) if data.get('last_login') else None,
            preferences=data.get('preferences', {}),
            created_at=datetime.fromisoformat(data.get('created_at')) if data.get('created_at') else None,
            updated_at=datetime.fromisoformat(data.get('updated_at')) if data.get('updated_at') else None
        )


class UserNotification:
    """
    Represents a notification for a user.
    
    Attributes:
        id (str): The unique identifier for the notification.
        user_id (str): The ID of the user this notification is for.
        title (str): The title of the notification.
        message (str): The message content of the notification.
        type (str): The type of notification (e.g., 'info', 'warning', 'error').
        is_read (bool): Whether the notification has been read.
        link (str): A link associated with the notification.
        created_at (datetime): When the notification was created.
        read_at (datetime): When the notification was read.
    """
    
    def __init__(
        self,
        id: str,
        user_id: str,
        title: str,
        message: str,
        type: str = 'info',
        is_read: bool = False,
        link: str = None,
        created_at: datetime = None,
        read_at: datetime = None
    ):
        self.id = id
        self.user_id = user_id
        self.title = title
        self.message = message
        self.type = type
        self.is_read = is_read
        self.link = link
        self.created_at = created_at or datetime.now()
        self.read_at = read_at
    
    def mark_as_read(self) -> None:
        """Mark the notification as read."""
        self.is_read = True
        self.read_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the notification to a dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'message': self.message,
            'type': self.type,
            'is_read': self.is_read,
            'link': self.link,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'read_at': self.read_at.isoformat() if self.read_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserNotification':
        """Create a notification from a dictionary."""
        return cls(
            id=data.get('id'),
            user_id=data.get('user_id'),
            title=data.get('title'),
            message=data.get('message'),
            type=data.get('type', 'info'),
            is_read=data.get('is_read', False),
            link=data.get('link'),
            created_at=datetime.fromisoformat(data.get('created_at')) if data.get('created_at') else None,
            read_at=datetime.fromisoformat(data.get('read_at')) if data.get('read_at') else None
        )


class UserService:
    """Service for managing user profiles and notifications."""
    
    @staticmethod
    def create_user_profile(user_data: Dict[str, Any]) -> Optional[UserProfile]:
        """Create a new user profile."""
        from services.user_service import UserProfileService
        service = UserProfileService()
        return service.create(user_data)
    
    @staticmethod
    def get_user_profile(user_id: str) -> Optional[UserProfile]:
        """Get a user profile by ID."""
        from services.user_service import UserProfileService
        service = UserProfileService()
        return service.get(user_id)
    
    @staticmethod
    def get_user_profile_by_auth_id(auth_id: str) -> Optional[UserProfile]:
        """Get a user profile by authentication ID."""
        from services.user_service import UserProfileService
        service = UserProfileService()
        return service.get_by_auth_id(auth_id)
    
    @staticmethod
    def get_user_profile_by_email(email: str) -> Optional[UserProfile]:
        """Get a user profile by email."""
        from services.user_service import UserProfileService
        service = UserProfileService()
        return service.get_by_email(email)
    
    @staticmethod
    def update_user_profile(user_id: str, user_data: Dict[str, Any]) -> Optional[UserProfile]:
        """Update an existing user profile."""
        from services.user_service import UserProfileService
        service = UserProfileService()
        return service.update(user_id, user_data)
    
    @staticmethod
    def delete_user_profile(user_id: str) -> bool:
        """Delete a user profile."""
        from services.user_service import UserProfileService
        service = UserProfileService()
        return service.delete(user_id)
    
    @staticmethod
    def list_user_profiles(
        role: str = None,
        status: str = None,
        department: str = None,
        search_term: str = None
    ) -> List[UserProfile]:
        """List user profiles with optional filtering."""
        from services.user_service import UserProfileService
        service = UserProfileService()
        
        if search_term:
            return service.search(search_term)
        
        filters = {}
        if role:
            filters['role'] = role
        if status:
            filters['status'] = status
        if department:
            filters['department'] = department
        
        return service.list(filters)
    
    @staticmethod
    def update_last_login(user_id: str) -> Optional[UserProfile]:
        """Update the last login timestamp for a user."""
        from services.user_service import UserProfileService
        service = UserProfileService()
        return service.update_last_login(user_id)
    
    @staticmethod
    def create_notification(notification_data: Dict[str, Any]) -> Optional[UserNotification]:
        """Create a new notification."""
        from services.user_service import UserNotificationService
        service = UserNotificationService()
        return service.create(notification_data)
    
    @staticmethod
    def get_notification(notification_id: str) -> Optional[UserNotification]:
        """Get a notification by ID."""
        from services.user_service import UserNotificationService
        service = UserNotificationService()
        return service.get(notification_id)
    
    @staticmethod
    def list_notifications(user_id: str, include_read: bool = False) -> List[UserNotification]:
        """List notifications for a user."""
        from services.user_service import UserNotificationService
        service = UserNotificationService()
        return service.list_for_user(user_id, include_read)
    
    @staticmethod
    def mark_notification_as_read(notification_id: str) -> Optional[UserNotification]:
        """Mark a notification as read."""
        from services.user_service import UserNotificationService
        service = UserNotificationService()
        return service.mark_as_read(notification_id)
    
    @staticmethod
    def mark_all_notifications_as_read(user_id: str) -> bool:
        """Mark all notifications for a user as read."""
        from services.user_service import UserNotificationService
        service = UserNotificationService()
        return service.mark_all_as_read(user_id)
    
    @staticmethod
    def delete_notification(notification_id: str) -> bool:
        """Delete a notification."""
        from services.user_service import UserNotificationService
        service = UserNotificationService()
        return service.delete(notification_id)
    
    @staticmethod
    def send_notification_to_user(
        user_id: str,
        title: str,
        message: str,
        type: str = 'info',
        link: str = None
    ) -> Optional[UserNotification]:
        """Send a notification to a user."""
        from services.user_service import UserNotificationService
        service = UserNotificationService()
        return service.send_to_user(user_id, title, message, type, link)
    
    @staticmethod
    def send_notification_to_role(
        role: UserRole,
        title: str,
        message: str,
        type: str = 'info',
        link: str = None
    ) -> List[UserNotification]:
        """Send a notification to all users with a specific role."""
        from services.user_service import UserNotificationService
        service = UserNotificationService()
        return service.send_to_role(role, title, message, type, link) 