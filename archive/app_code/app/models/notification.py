from app.models import BaseModel
from datetime import datetime

class Notification(BaseModel):
    """Notification model for user notifications"""
    
    # Notification types
    TYPES = ['info', 'success', 'warning', 'danger']
    
    # Notification categories
    CATEGORIES = ['project', 'task', 'document', 'system', 'schedule', 'expense']
    
    def __init__(self, id=None, user_id=None, title=None, message=None, 
                 notification_type='info', category='system', is_read=False, 
                 created_at=None, entity_id=None, entity_type=None, 
                 action_url=None, **kwargs):
        self.id = id
        self.user_id = user_id
        self.title = title
        self.message = message
        self.notification_type = notification_type
        self.category = category
        self.is_read = is_read
        self.created_at = created_at or datetime.now()
        self.entity_id = entity_id  # ID of related entity (project/task/etc)
        self.entity_type = entity_type  # Type of related entity
        self.action_url = action_url  # URL to redirect when notification is clicked
        
        # Store any additional attributes
        for key, value in kwargs.items():
            setattr(self, key, value)
            
    def mark_as_read(self):
        """Mark the notification as read"""
        self.is_read = True
        
    def mark_as_unread(self):
        """Mark the notification as unread"""
        self.is_read = False
        
    def __repr__(self):
        return f"<Notification {self.title} ({self.notification_type})>" 