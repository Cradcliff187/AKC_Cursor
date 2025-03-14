from app.models import BaseModel
from datetime import datetime

class User(BaseModel):
    """User model representing a system user"""
    
    def __init__(self, id=None, username=None, email=None, first_name=None, 
                 last_name=None, role='user', created_at=None, **kwargs):
        self.id = id
        self.username = username
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.role = role
        self.created_at = created_at or datetime.now()
        
        # Store any additional attributes
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    @property
    def full_name(self):
        """Get the user's full name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        else:
            return self.username or self.email or "Unknown"
    
    @property
    def is_admin(self):
        """Check if the user is an admin"""
        return self.role == 'admin'
    
    @property
    def is_project_manager(self):
        """Check if the user is a project manager"""
        return self.role == 'project_manager'
        
    @property
    def is_foreman(self):
        """Check if the user is a foreman"""
        return self.role == 'foreman'
        
    @property
    def is_field_worker(self):
        """Check if the user is a field worker"""
        return self.role == 'field_worker'
        
    def can_manage_projects(self):
        """Check if the user can manage projects"""
        return self.is_admin or self.is_project_manager
        
    def can_manage_tasks(self):
        """Check if the user can manage tasks"""
        return self.is_admin or self.is_project_manager or self.is_foreman
        
    def can_record_time(self):
        """Check if the user can record time entries"""
        return True  # All users can record time
        
    def __repr__(self):
        return f"<User {self.full_name} ({self.role})>" 