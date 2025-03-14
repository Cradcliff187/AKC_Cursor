from app.models import BaseModel
from datetime import datetime

class Task(BaseModel):
    """Task model representing a project task"""
    
    # Define valid task statuses
    STATUSES = ['Not Started', 'In Progress', 'On Hold', 'Completed', 'Cancelled']
    
    # Define priority levels
    PRIORITIES = ['Low', 'Medium', 'High', 'Urgent']
    
    def __init__(self, id=None, project_id=None, title=None, description=None, 
                 assigned_to=None, assignee_name=None, status='Not Started', 
                 priority='Medium', due_date=None, completion_date=None, 
                 estimated_hours=None, actual_hours=0, created_at=None, 
                 created_by=None, tags=None, **kwargs):
        self.id = id
        self.project_id = project_id
        self.title = title
        self.description = description
        self.assigned_to = assigned_to
        self.assignee_name = assignee_name
        self.status = status
        self.priority = priority
        
        # Handle date values that may come as strings
        if isinstance(due_date, str):
            try:
                self.due_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
            except ValueError:
                self.due_date = None
        else:
            self.due_date = due_date
            
        if isinstance(completion_date, str):
            try:
                self.completion_date = datetime.fromisoformat(completion_date.replace('Z', '+00:00'))
            except ValueError:
                self.completion_date = None
        else:
            self.completion_date = completion_date
        
        self.estimated_hours = float(estimated_hours) if estimated_hours is not None else None
        self.actual_hours = float(actual_hours) if actual_hours is not None else 0
        self.created_at = created_at or datetime.now()
        self.created_by = created_by
        self.tags = tags or []
        
        # Store any additional attributes
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    @property
    def is_completed(self):
        """Check if the task is completed"""
        return self.status == 'Completed'
    
    @property
    def is_active(self):
        """Check if the task is active"""
        return self.status == 'In Progress'
    
    @property
    def is_overdue(self):
        """Check if the task is overdue"""
        if not self.due_date or self.is_completed:
            return False
            
        return datetime.now() > self.due_date
    
    @property
    def days_remaining(self):
        """Calculate days remaining until due date"""
        if not self.due_date:
            return None
            
        now = datetime.now()
        if now > self.due_date:
            return 0
            
        delta = self.due_date - now
        return delta.days
    
    @property
    def hours_variance(self):
        """Calculate variance between estimated and actual hours"""
        if self.estimated_hours is None:
            return None
            
        return self.actual_hours - self.estimated_hours
    
    @property
    def progress_percentage(self):
        """Calculate progress percentage based on status"""
        status_progress = {
            'Not Started': 0,
            'In Progress': 50,
            'On Hold': 30,
            'Completed': 100,
            'Cancelled': 0
        }
        return status_progress.get(self.status, 0)
    
    def complete(self):
        """Mark the task as completed"""
        self.status = 'Completed'
        self.completion_date = datetime.now()
        
    def add_time(self, hours):
        """Add time to the task's actual hours"""
        if hours > 0:
            self.actual_hours += hours
            
    def __repr__(self):
        return f"<Task {self.title} ({self.status})>" 