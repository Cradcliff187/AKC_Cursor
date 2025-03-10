"""
Models package to organize data structures and business logic.
"""

from datetime import datetime

# Base class for all models
class BaseModel:
    """Base class with common functionality for all models"""
    
    @classmethod
    def from_dict(cls, data):
        """Create a model instance from a dictionary"""
        if not data:
            return None
        return cls(**data)
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {key: value for key, value in self.__dict__.items() 
                if not key.startswith('_')}

# Import all models
from app.models.user import User
from app.models.project import Project
from app.models.task import Task
from app.models.notification import Notification
from app.models.bid import Bid
from app.models.bid_item import BidItem
from app.models.invoice import Invoice
from app.models.invoice_item import InvoiceItem
from app.models.payment import Payment
