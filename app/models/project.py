from app.models import BaseModel
from datetime import datetime

class Project(BaseModel):
    """Project model representing a construction project"""
    
    # Define valid project statuses
    STATUSES = ['Planning', 'In Progress', 'On Hold', 'Completed', 'Cancelled']
    
    def __init__(self, id=None, name=None, description=None, client_id=None, 
                 client=None, status='Planning', start_date=None, end_date=None,
                 budget=0.0, budget_spent=0.0, location=None, created_at=None, 
                 user_id=None, progress=0, **kwargs):
        self.id = id
        self.name = name
        self.description = description
        self.client_id = client_id
        self.client = client
        self.status = status
        
        # Handle date values that may come as strings
        if isinstance(start_date, str):
            try:
                self.start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            except ValueError:
                self.start_date = None
        else:
            self.start_date = start_date
            
        if isinstance(end_date, str):
            try:
                self.end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            except ValueError:
                self.end_date = None
        else:
            self.end_date = end_date
        
        self.budget = float(budget) if budget is not None else 0.0
        self.budget_spent = float(budget_spent) if budget_spent is not None else 0.0
        self.location = location
        self.created_at = created_at or datetime.now()
        self.user_id = user_id
        self.progress = progress
        
        # Store any additional attributes
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    @property
    def is_active(self):
        """Check if the project is active"""
        return self.status == 'In Progress'
    
    @property
    def is_completed(self):
        """Check if the project is completed"""
        return self.status == 'Completed'
    
    @property
    def is_over_budget(self):
        """Check if the project is over budget"""
        if not self.budget:
            return False
        return self.budget_spent > self.budget
    
    @property
    def budget_percentage(self):
        """Calculate percentage of budget spent"""
        if not self.budget:
            return 0
        return min(100, round((self.budget_spent / self.budget) * 100, 1))
    
    @property
    def days_remaining(self):
        """Calculate days remaining until the end date"""
        if not self.end_date:
            return None
            
        now = datetime.now()
        if now > self.end_date:
            return 0
            
        delta = self.end_date - now
        return delta.days
    
    @property
    def is_overdue(self):
        """Check if the project is overdue"""
        if not self.end_date or self.is_completed:
            return False
            
        return datetime.now() > self.end_date
    
    def can_transition_to(self, new_status):
        """Check if the project can transition to a new status"""
        # Define valid transitions
        valid_transitions = {
            'Planning': ['In Progress', 'On Hold', 'Cancelled'],
            'In Progress': ['On Hold', 'Completed', 'Cancelled'],
            'On Hold': ['In Progress', 'Cancelled'],
            'Completed': [],  # Can't transition out of completed
            'Cancelled': ['Planning']  # Can restart a cancelled project
        }
        
        return new_status in valid_transitions.get(self.status, [])
    
    def __repr__(self):
        return f"<Project {self.name} ({self.status})>" 