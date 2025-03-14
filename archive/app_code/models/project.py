"""
Project Model

This module defines the Project model and related functionality.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from decimal import Decimal
from enum import Enum


class ProjectStatus(str, Enum):
    """Enum representing the possible statuses of a project."""
    PLANNING = "planning"
    IN_PROGRESS = "in_progress"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Project:
    """
    Represents a construction project in the system.
    
    Attributes:
        id (str): The unique identifier for the project.
        name (str): The name of the project.
        client_id (str): The ID of the client this project is for.
        description (str): Detailed description of the project.
        status (ProjectStatus): The current status of the project.
        start_date (datetime): The date the project is scheduled to start.
        end_date (datetime): The date the project is scheduled to end.
        actual_start_date (datetime): The date the project actually started.
        actual_end_date (datetime): The date the project actually ended.
        budget (Decimal): The total budget for the project.
        address (str): The physical address of the project.
        city (str): The city where the project is located.
        state (str): The state where the project is located.
        zip_code (str): The ZIP code where the project is located.
        manager_id (str): The ID of the employee managing the project.
        notes (str): Additional notes about the project.
        created_at (datetime): When the project was created.
        updated_at (datetime): When the project was last updated.
    """
    
    def __init__(
        self,
        id: str,
        name: str,
        client_id: str,
        description: str = None,
        status: ProjectStatus = ProjectStatus.PLANNING,
        start_date: datetime = None,
        end_date: datetime = None,
        actual_start_date: datetime = None,
        actual_end_date: datetime = None,
        budget: Decimal = Decimal('0.00'),
        address: str = None,
        city: str = None,
        state: str = None,
        zip_code: str = None,
        manager_id: str = None,
        notes: str = None,
        created_at: datetime = None,
        updated_at: datetime = None
    ):
        self.id = id
        self.name = name
        self.client_id = client_id
        self.description = description
        self.status = status if isinstance(status, ProjectStatus) else ProjectStatus(status)
        self.start_date = start_date
        self.end_date = end_date
        self.actual_start_date = actual_start_date
        self.actual_end_date = actual_end_date
        self.budget = budget
        self.address = address
        self.city = city
        self.state = state
        self.zip_code = zip_code
        self.manager_id = manager_id
        self.notes = notes
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
    
    @property
    def is_active(self) -> bool:
        """Check if the project is currently active."""
        return self.status == ProjectStatus.IN_PROGRESS
    
    @property
    def is_completed(self) -> bool:
        """Check if the project is completed."""
        return self.status == ProjectStatus.COMPLETED
    
    @property
    def is_overdue(self) -> bool:
        """Check if the project is overdue."""
        if not self.end_date:
            return False
        return self.end_date < datetime.now() and not self.is_completed
    
    @property
    def duration_days(self) -> Optional[int]:
        """Calculate the planned duration in days."""
        if not self.start_date or not self.end_date:
            return None
        return (self.end_date - self.start_date).days
    
    @property
    def actual_duration_days(self) -> Optional[int]:
        """Calculate the actual duration in days."""
        if not self.actual_start_date or not self.actual_end_date:
            return None
        return (self.actual_end_date - self.actual_start_date).days
    
    @property
    def full_address(self) -> Optional[str]:
        """Get the full address as a formatted string."""
        if not self.address:
            return None
        
        parts = [self.address]
        if self.city:
            parts.append(self.city)
        if self.state:
            parts.append(self.state)
        if self.zip_code:
            parts.append(self.zip_code)
        
        return ", ".join(parts)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the project to a dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'client_id': self.client_id,
            'description': self.description,
            'status': self.status.value if isinstance(self.status, ProjectStatus) else self.status,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'actual_start_date': self.actual_start_date.isoformat() if self.actual_start_date else None,
            'actual_end_date': self.actual_end_date.isoformat() if self.actual_end_date else None,
            'budget': str(self.budget),
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'zip_code': self.zip_code,
            'manager_id': self.manager_id,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Project':
        """Create a project from a dictionary."""
        return cls(
            id=data.get('id'),
            name=data.get('name'),
            client_id=data.get('client_id'),
            description=data.get('description'),
            status=data.get('status'),
            start_date=datetime.fromisoformat(data.get('start_date')) if data.get('start_date') else None,
            end_date=datetime.fromisoformat(data.get('end_date')) if data.get('end_date') else None,
            actual_start_date=datetime.fromisoformat(data.get('actual_start_date')) if data.get('actual_start_date') else None,
            actual_end_date=datetime.fromisoformat(data.get('actual_end_date')) if data.get('actual_end_date') else None,
            budget=Decimal(data.get('budget', '0.00')),
            address=data.get('address'),
            city=data.get('city'),
            state=data.get('state'),
            zip_code=data.get('zip_code'),
            manager_id=data.get('manager_id'),
            notes=data.get('notes'),
            created_at=datetime.fromisoformat(data.get('created_at')) if data.get('created_at') else None,
            updated_at=datetime.fromisoformat(data.get('updated_at')) if data.get('updated_at') else None
        )


class ProjectTask:
    """
    Represents a task within a project.
    
    Attributes:
        id (str): The unique identifier for the task.
        project_id (str): The ID of the project this task belongs to.
        name (str): The name of the task.
        description (str): Detailed description of the task.
        status (str): The current status of the task (not_started, in_progress, completed, etc.).
        priority (str): The priority level of the task (low, medium, high, urgent).
        assigned_to (str): The ID of the employee assigned to the task.
        start_date (datetime): The date the task is scheduled to start.
        due_date (datetime): The date the task is due.
        completion_date (datetime): The date the task was completed.
        estimated_hours (Decimal): Estimated hours to complete the task.
        actual_hours (Decimal): Actual hours spent on the task.
        dependencies (List[str]): IDs of tasks that must be completed before this task.
        created_at (datetime): When the task was created.
        updated_at (datetime): When the task was last updated.
    """
    
    def __init__(
        self,
        id: str,
        project_id: str,
        name: str,
        description: str = None,
        status: str = "not_started",
        priority: str = "medium",
        assigned_to: str = None,
        start_date: datetime = None,
        due_date: datetime = None,
        completion_date: datetime = None,
        estimated_hours: Decimal = Decimal('0.00'),
        actual_hours: Decimal = Decimal('0.00'),
        dependencies: List[str] = None,
        created_at: datetime = None,
        updated_at: datetime = None
    ):
        self.id = id
        self.project_id = project_id
        self.name = name
        self.description = description
        self.status = status
        self.priority = priority
        self.assigned_to = assigned_to
        self.start_date = start_date
        self.due_date = due_date
        self.completion_date = completion_date
        self.estimated_hours = estimated_hours
        self.actual_hours = actual_hours
        self.dependencies = dependencies or []
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
    
    @property
    def is_completed(self) -> bool:
        """Check if the task is completed."""
        return self.status == "completed"
    
    @property
    def is_overdue(self) -> bool:
        """Check if the task is overdue."""
        if not self.due_date:
            return False
        return self.due_date < datetime.now() and not self.is_completed
    
    @property
    def progress_percentage(self) -> int:
        """Calculate the progress percentage based on status."""
        status_map = {
            "not_started": 0,
            "in_progress": 50,
            "completed": 100
        }
        return status_map.get(self.status, 0)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the task to a dictionary."""
        return {
            'id': self.id,
            'project_id': self.project_id,
            'name': self.name,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'assigned_to': self.assigned_to,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'completion_date': self.completion_date.isoformat() if self.completion_date else None,
            'estimated_hours': str(self.estimated_hours),
            'actual_hours': str(self.actual_hours),
            'dependencies': self.dependencies,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProjectTask':
        """Create a task from a dictionary."""
        return cls(
            id=data.get('id'),
            project_id=data.get('project_id'),
            name=data.get('name'),
            description=data.get('description'),
            status=data.get('status', 'not_started'),
            priority=data.get('priority', 'medium'),
            assigned_to=data.get('assigned_to'),
            start_date=datetime.fromisoformat(data.get('start_date')) if data.get('start_date') else None,
            due_date=datetime.fromisoformat(data.get('due_date')) if data.get('due_date') else None,
            completion_date=datetime.fromisoformat(data.get('completion_date')) if data.get('completion_date') else None,
            estimated_hours=Decimal(data.get('estimated_hours', '0.00')),
            actual_hours=Decimal(data.get('actual_hours', '0.00')),
            dependencies=data.get('dependencies', []),
            created_at=datetime.fromisoformat(data.get('created_at')) if data.get('created_at') else None,
            updated_at=datetime.fromisoformat(data.get('updated_at')) if data.get('updated_at') else None
        )


class ProjectService:
    """Service for managing projects and project tasks."""
    
    @staticmethod
    def create_project(project_data: Dict[str, Any]) -> Project:
        """Create a new project."""
        # Implementation would depend on your database access layer
        pass
    
    @staticmethod
    def get_project(project_id: str) -> Optional[Project]:
        """Get a project by ID."""
        # Implementation would depend on your database access layer
        pass
    
    @staticmethod
    def update_project(project_id: str, project_data: Dict[str, Any]) -> Optional[Project]:
        """Update an existing project."""
        # Implementation would depend on your database access layer
        pass
    
    @staticmethod
    def delete_project(project_id: str) -> bool:
        """Delete a project."""
        # Implementation would depend on your database access layer
        pass
    
    @staticmethod
    def list_projects(
        client_id: str = None,
        status: str = None,
        manager_id: str = None,
        start_date_from: datetime = None,
        start_date_to: datetime = None
    ) -> List[Project]:
        """List projects with optional filtering."""
        # Implementation would depend on your database access layer
        pass
    
    @staticmethod
    def create_task(task_data: Dict[str, Any]) -> ProjectTask:
        """Create a new project task."""
        # Implementation would depend on your database access layer
        pass
    
    @staticmethod
    def get_task(task_id: str) -> Optional[ProjectTask]:
        """Get a task by ID."""
        # Implementation would depend on your database access layer
        pass
    
    @staticmethod
    def update_task(task_id: str, task_data: Dict[str, Any]) -> Optional[ProjectTask]:
        """Update an existing task."""
        # Implementation would depend on your database access layer
        pass
    
    @staticmethod
    def delete_task(task_id: str) -> bool:
        """Delete a task."""
        # Implementation would depend on your database access layer
        pass
    
    @staticmethod
    def list_tasks(
        project_id: str,
        status: str = None,
        assigned_to: str = None,
        due_date_from: datetime = None,
        due_date_to: datetime = None
    ) -> List[ProjectTask]:
        """List tasks for a project with optional filtering."""
        # Implementation would depend on your database access layer
        pass
    
    @staticmethod
    def complete_task(task_id: str, completion_date: datetime = None, actual_hours: Decimal = None) -> Optional[ProjectTask]:
        """Mark a task as completed."""
        # Implementation would depend on your database access layer
        pass
    
    @staticmethod
    def get_project_progress(project_id: str) -> Dict[str, Any]:
        """Get the progress statistics for a project."""
        # Implementation would depend on your database access layer
        # Example return:
        # {
        #     'total_tasks': 10,
        #     'completed_tasks': 5,
        #     'progress_percentage': 50,
        #     'estimated_hours': 100,
        #     'actual_hours': 45,
        #     'remaining_hours': 55
        # }
        pass 