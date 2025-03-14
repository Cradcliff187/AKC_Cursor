"""
Client Model

This module defines the Client model and related functionality.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from decimal import Decimal


class Client:
    """
    Represents a client in the system.
    
    Attributes:
        id (str): The unique identifier for the client.
        name (str): The name of the client (company or individual).
        contact_name (str): The primary contact person's name.
        email (str): The primary email address for the client.
        phone (str): The primary phone number for the client.
        address (str): The physical address of the client.
        city (str): The city where the client is located.
        state (str): The state where the client is located.
        zip_code (str): The ZIP code where the client is located.
        company (str): The company name if different from client name.
        website (str): The client's website URL.
        notes (str): Additional notes about the client.
        status (str): The status of the client (active, inactive, etc.).
        type (str): The type of client (residential, commercial, etc.).
        tax_id (str): The tax ID or EIN for the client.
        created_at (datetime): When the client was created.
        updated_at (datetime): When the client was last updated.
    """
    
    def __init__(
        self,
        id: str,
        name: str,
        contact_name: str = None,
        email: str = None,
        phone: str = None,
        address: str = None,
        city: str = None,
        state: str = None,
        zip_code: str = None,
        company: str = None,
        website: str = None,
        notes: str = None,
        status: str = "active",
        type: str = "residential",
        tax_id: str = None,
        created_at: datetime = None,
        updated_at: datetime = None
    ):
        self.id = id
        self.name = name
        self.contact_name = contact_name
        self.email = email
        self.phone = phone
        self.address = address
        self.city = city
        self.state = state
        self.zip_code = zip_code
        self.company = company
        self.website = website
        self.notes = notes
        self.status = status
        self.type = type
        self.tax_id = tax_id
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
    
    @property
    def is_active(self) -> bool:
        """Check if the client is active."""
        return self.status == "active"
    
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
    
    @property
    def display_name(self) -> str:
        """Get a display name for the client."""
        if self.company and self.company != self.name:
            return f"{self.name} ({self.company})"
        return self.name
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the client to a dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'contact_name': self.contact_name,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'zip_code': self.zip_code,
            'company': self.company,
            'website': self.website,
            'notes': self.notes,
            'status': self.status,
            'type': self.type,
            'tax_id': self.tax_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Client':
        """Create a client from a dictionary."""
        return cls(
            id=data.get('id'),
            name=data.get('name'),
            contact_name=data.get('contact_name'),
            email=data.get('email'),
            phone=data.get('phone'),
            address=data.get('address'),
            city=data.get('city'),
            state=data.get('state'),
            zip_code=data.get('zip_code'),
            company=data.get('company'),
            website=data.get('website'),
            notes=data.get('notes'),
            status=data.get('status', 'active'),
            type=data.get('type', 'residential'),
            tax_id=data.get('tax_id'),
            created_at=datetime.fromisoformat(data.get('created_at')) if data.get('created_at') else None,
            updated_at=datetime.fromisoformat(data.get('updated_at')) if data.get('updated_at') else None
        )


class ClientContact:
    """
    Represents an additional contact for a client.
    
    Attributes:
        id (str): The unique identifier for the contact.
        client_id (str): The ID of the client this contact belongs to.
        name (str): The name of the contact.
        title (str): The job title of the contact.
        email (str): The email address of the contact.
        phone (str): The phone number of the contact.
        is_primary (bool): Whether this is the primary contact for the client.
        notes (str): Additional notes about the contact.
        created_at (datetime): When the contact was created.
        updated_at (datetime): When the contact was last updated.
    """
    
    def __init__(
        self,
        id: str,
        client_id: str,
        name: str,
        title: str = None,
        email: str = None,
        phone: str = None,
        is_primary: bool = False,
        notes: str = None,
        created_at: datetime = None,
        updated_at: datetime = None
    ):
        self.id = id
        self.client_id = client_id
        self.name = name
        self.title = title
        self.email = email
        self.phone = phone
        self.is_primary = is_primary
        self.notes = notes
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the contact to a dictionary."""
        return {
            'id': self.id,
            'client_id': self.client_id,
            'name': self.name,
            'title': self.title,
            'email': self.email,
            'phone': self.phone,
            'is_primary': self.is_primary,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ClientContact':
        """Create a contact from a dictionary."""
        return cls(
            id=data.get('id'),
            client_id=data.get('client_id'),
            name=data.get('name'),
            title=data.get('title'),
            email=data.get('email'),
            phone=data.get('phone'),
            is_primary=data.get('is_primary', False),
            notes=data.get('notes'),
            created_at=datetime.fromisoformat(data.get('created_at')) if data.get('created_at') else None,
            updated_at=datetime.fromisoformat(data.get('updated_at')) if data.get('updated_at') else None
        )


class ClientService:
    """Service for managing clients and client contacts."""
    
    @staticmethod
    def create_client(client_data: Dict[str, Any]) -> Client:
        """Create a new client."""
        # Implementation would depend on your database access layer
        pass
    
    @staticmethod
    def get_client(client_id: str) -> Optional[Client]:
        """Get a client by ID."""
        # Implementation would depend on your database access layer
        pass
    
    @staticmethod
    def update_client(client_id: str, client_data: Dict[str, Any]) -> Optional[Client]:
        """Update an existing client."""
        # Implementation would depend on your database access layer
        pass
    
    @staticmethod
    def delete_client(client_id: str) -> bool:
        """Delete a client."""
        # Implementation would depend on your database access layer
        pass
    
    @staticmethod
    def list_clients(
        status: str = None,
        type: str = None,
        search_term: str = None
    ) -> List[Client]:
        """List clients with optional filtering."""
        # Implementation would depend on your database access layer
        pass
    
    @staticmethod
    def create_contact(contact_data: Dict[str, Any]) -> ClientContact:
        """Create a new client contact."""
        # Implementation would depend on your database access layer
        pass
    
    @staticmethod
    def get_contact(contact_id: str) -> Optional[ClientContact]:
        """Get a contact by ID."""
        # Implementation would depend on your database access layer
        pass
    
    @staticmethod
    def update_contact(contact_id: str, contact_data: Dict[str, Any]) -> Optional[ClientContact]:
        """Update an existing contact."""
        # Implementation would depend on your database access layer
        pass
    
    @staticmethod
    def delete_contact(contact_id: str) -> bool:
        """Delete a contact."""
        # Implementation would depend on your database access layer
        pass
    
    @staticmethod
    def list_contacts(client_id: str) -> List[ClientContact]:
        """List contacts for a client."""
        # Implementation would depend on your database access layer
        pass
    
    @staticmethod
    def get_client_projects(client_id: str) -> List[Dict[str, Any]]:
        """Get all projects for a client."""
        # Implementation would depend on your database access layer
        pass
    
    @staticmethod
    def get_client_invoices(client_id: str) -> List[Dict[str, Any]]:
        """Get all invoices for a client."""
        # Implementation would depend on your database access layer
        pass
    
    @staticmethod
    def get_client_bids(client_id: str) -> List[Dict[str, Any]]:
        """Get all bids for a client."""
        # Implementation would depend on your database access layer
        pass 