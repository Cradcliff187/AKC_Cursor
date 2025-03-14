"""
Time Entry Model

This module defines the TimeEntry model and related functionality.
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from decimal import Decimal
from enum import Enum


class TimeEntryStatus(str, Enum):
    """Enum representing the possible time entry statuses."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    BILLED = "billed"


class TimeEntry:
    """
    Represents a time entry in the system.
    
    Attributes:
        id (str): The unique identifier for the time entry.
        user_id (str): The ID of the user who logged the time.
        project_id (str): The ID of the project this time is for.
        task_id (str): The ID of the specific task this time is for (optional).
        description (str): Description of the work performed.
        start_time (datetime): When the work started.
        end_time (datetime): When the work ended.
        duration (timedelta): The duration of the work (calculated from start and end times).
        billable (bool): Whether the time is billable to the client.
        billable_rate (Decimal): The hourly rate for billable time.
        status (TimeEntryStatus): The status of the time entry.
        approved_by (str): The ID of the user who approved the time entry.
        approved_at (datetime): When the time entry was approved.
        notes (str): Additional notes about the time entry.
        created_at (datetime): When the time entry was created.
        updated_at (datetime): When the time entry was last updated.
    """
    
    def __init__(
        self,
        id: str,
        user_id: str,
        project_id: str,
        description: str,
        start_time: datetime,
        end_time: datetime = None,
        duration: timedelta = None,
        task_id: str = None,
        billable: bool = True,
        billable_rate: Decimal = None,
        status: TimeEntryStatus = TimeEntryStatus.PENDING,
        approved_by: str = None,
        approved_at: datetime = None,
        notes: str = None,
        created_at: datetime = None,
        updated_at: datetime = None
    ):
        self.id = id
        self.user_id = user_id
        self.project_id = project_id
        self.task_id = task_id
        self.description = description
        self.start_time = start_time
        self.end_time = end_time
        
        # Calculate duration if not provided
        if duration is None and end_time is not None:
            self.duration = end_time - start_time
        else:
            self.duration = duration
        
        self.billable = billable
        self.billable_rate = billable_rate
        self.status = status if isinstance(status, TimeEntryStatus) else TimeEntryStatus(status)
        self.approved_by = approved_by
        self.approved_at = approved_at
        self.notes = notes
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
    
    @property
    def is_approved(self) -> bool:
        """Check if the time entry is approved."""
        return self.status in [TimeEntryStatus.APPROVED, TimeEntryStatus.BILLED]
    
    @property
    def is_billed(self) -> bool:
        """Check if the time entry is billed."""
        return self.status == TimeEntryStatus.BILLED
    
    @property
    def hours(self) -> float:
        """Get the duration in hours."""
        if self.duration is None:
            return 0.0
        return self.duration.total_seconds() / 3600
    
    @property
    def billable_amount(self) -> Optional[Decimal]:
        """Calculate the billable amount."""
        if not self.billable or self.billable_rate is None or self.duration is None:
            return None
        hours = Decimal(str(self.hours))
        return hours * self.billable_rate
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the time entry to a dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'project_id': self.project_id,
            'task_id': self.task_id,
            'description': self.description,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration': self.duration.total_seconds() if self.duration else None,
            'billable': self.billable,
            'billable_rate': str(self.billable_rate) if self.billable_rate else None,
            'status': self.status.value if isinstance(self.status, TimeEntryStatus) else self.status,
            'approved_by': self.approved_by,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TimeEntry':
        """Create a time entry from a dictionary."""
        # Handle duration conversion from seconds to timedelta
        duration = None
        if data.get('duration') is not None:
            duration = timedelta(seconds=float(data.get('duration')))
        
        return cls(
            id=data.get('id'),
            user_id=data.get('user_id'),
            project_id=data.get('project_id'),
            task_id=data.get('task_id'),
            description=data.get('description'),
            start_time=datetime.fromisoformat(data.get('start_time')) if data.get('start_time') else None,
            end_time=datetime.fromisoformat(data.get('end_time')) if data.get('end_time') else None,
            duration=duration,
            billable=data.get('billable', True),
            billable_rate=Decimal(data.get('billable_rate')) if data.get('billable_rate') else None,
            status=data.get('status', TimeEntryStatus.PENDING),
            approved_by=data.get('approved_by'),
            approved_at=datetime.fromisoformat(data.get('approved_at')) if data.get('approved_at') else None,
            notes=data.get('notes'),
            created_at=datetime.fromisoformat(data.get('created_at')) if data.get('created_at') else None,
            updated_at=datetime.fromisoformat(data.get('updated_at')) if data.get('updated_at') else None
        )


class TimeEntryService:
    """Service for managing time entries."""
    
    @staticmethod
    def create_time_entry(time_entry_data: Dict[str, Any]) -> TimeEntry:
        """Create a new time entry."""
        # Implementation would depend on your database access layer
        pass
    
    @staticmethod
    def get_time_entry(time_entry_id: str) -> Optional[TimeEntry]:
        """Get a time entry by ID."""
        # Implementation would depend on your database access layer
        pass
    
    @staticmethod
    def update_time_entry(time_entry_id: str, time_entry_data: Dict[str, Any]) -> Optional[TimeEntry]:
        """Update an existing time entry."""
        # Implementation would depend on your database access layer
        pass
    
    @staticmethod
    def delete_time_entry(time_entry_id: str) -> bool:
        """Delete a time entry."""
        # Implementation would depend on your database access layer
        pass
    
    @staticmethod
    def list_time_entries(
        user_id: str = None,
        project_id: str = None,
        task_id: str = None,
        status: str = None,
        start_date: datetime = None,
        end_date: datetime = None,
        billable: bool = None
    ) -> List[TimeEntry]:
        """List time entries with optional filtering."""
        # Implementation would depend on your database access layer
        pass
    
    @staticmethod
    def approve_time_entry(time_entry_id: str, approved_by: str) -> Optional[TimeEntry]:
        """Approve a time entry."""
        # Implementation would depend on your database access layer
        pass
    
    @staticmethod
    def reject_time_entry(time_entry_id: str, reason: str = None) -> Optional[TimeEntry]:
        """Reject a time entry."""
        # Implementation would depend on your database access layer
        pass
    
    @staticmethod
    def mark_as_billed(time_entry_id: str, invoice_id: str = None) -> Optional[TimeEntry]:
        """Mark a time entry as billed."""
        # Implementation would depend on your database access layer
        pass
    
    @staticmethod
    def start_timer(
        user_id: str,
        project_id: str,
        description: str,
        task_id: str = None,
        billable: bool = True
    ) -> TimeEntry:
        """Start a timer for a new time entry."""
        # Implementation would depend on your database access layer
        pass
    
    @staticmethod
    def stop_timer(time_entry_id: str) -> Optional[TimeEntry]:
        """Stop a running timer for a time entry."""
        # Implementation would depend on your database access layer
        pass
    
    @staticmethod
    def get_time_summary(
        user_id: str = None,
        project_id: str = None,
        start_date: datetime = None,
        end_date: datetime = None
    ) -> Dict[str, Any]:
        """Get a summary of time entries."""
        # Implementation would depend on your database access layer
        # Example return:
        # {
        #     'total_hours': 40.5,
        #     'billable_hours': 35.0,
        #     'non_billable_hours': 5.5,
        #     'billable_amount': Decimal('3500.00'),
        #     'by_project': {
        #         'project1': 20.0,
        #         'project2': 15.5,
        #         'project3': 5.0
        #     },
        #     'by_user': {
        #         'user1': 30.0,
        #         'user2': 10.5
        #     }
        # }
        pass 