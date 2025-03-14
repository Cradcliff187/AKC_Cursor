"""
Bid Model

This module defines the Bid model and related functionality.
"""

from datetime import datetime
from typing import List, Optional
from decimal import Decimal

class Bid:
    """
    Represents a bid in the system.
    
    Attributes:
        id (str): The unique identifier for the bid.
        client_id (str): The ID of the client this bid is for.
        project_id (str): The ID of the project this bid is for.
        bid_number (str): The bid number (e.g., BID-2023-001).
        status (str): The status of the bid (draft, submitted, accepted, rejected, etc.).
        submission_date (datetime): The date the bid was submitted.
        expiration_date (datetime): The date the bid expires.
        amount (Decimal): The total amount of the bid.
        labor_cost (Decimal): The labor cost component of the bid.
        material_cost (Decimal): The material cost component of the bid.
        overhead_cost (Decimal): The overhead cost component of the bid.
        profit_margin (Decimal): The profit margin percentage.
        notes (str): Additional notes about the bid.
        terms (str): Terms and conditions for the bid.
        created_at (datetime): When the bid was created.
        updated_at (datetime): When the bid was last updated.
    """
    
    def __init__(
        self,
        id: str,
        client_id: str,
        project_id: str,
        bid_number: str,
        status: str,
        submission_date: datetime,
        expiration_date: datetime,
        amount: Decimal,
        labor_cost: Decimal = Decimal('0.00'),
        material_cost: Decimal = Decimal('0.00'),
        overhead_cost: Decimal = Decimal('0.00'),
        profit_margin: Decimal = Decimal('0.00'),
        notes: str = None,
        terms: str = None,
        created_at: datetime = None,
        updated_at: datetime = None
    ):
        self.id = id
        self.client_id = client_id
        self.project_id = project_id
        self.bid_number = bid_number
        self.status = status
        self.submission_date = submission_date
        self.expiration_date = expiration_date
        self.amount = amount
        self.labor_cost = labor_cost
        self.material_cost = material_cost
        self.overhead_cost = overhead_cost
        self.profit_margin = profit_margin
        self.notes = notes
        self.terms = terms
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
    
    @property
    def is_expired(self) -> bool:
        """Check if the bid is expired."""
        return self.expiration_date < datetime.now() and self.status not in ['accepted', 'rejected']
    
    @property
    def cost_subtotal(self) -> Decimal:
        """Calculate the subtotal of all costs."""
        return self.labor_cost + self.material_cost + self.overhead_cost
    
    @property
    def profit_amount(self) -> Decimal:
        """Calculate the profit amount."""
        return self.amount - self.cost_subtotal
    
    def to_dict(self) -> dict:
        """Convert the bid to a dictionary."""
        return {
            'id': self.id,
            'client_id': self.client_id,
            'project_id': self.project_id,
            'bid_number': self.bid_number,
            'status': self.status,
            'submission_date': self.submission_date.isoformat() if self.submission_date else None,
            'expiration_date': self.expiration_date.isoformat() if self.expiration_date else None,
            'amount': str(self.amount),
            'labor_cost': str(self.labor_cost),
            'material_cost': str(self.material_cost),
            'overhead_cost': str(self.overhead_cost),
            'profit_margin': str(self.profit_margin),
            'notes': self.notes,
            'terms': self.terms,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Bid':
        """Create a bid from a dictionary."""
        return cls(
            id=data.get('id'),
            client_id=data.get('client_id'),
            project_id=data.get('project_id'),
            bid_number=data.get('bid_number'),
            status=data.get('status'),
            submission_date=datetime.fromisoformat(data.get('submission_date')) if data.get('submission_date') else None,
            expiration_date=datetime.fromisoformat(data.get('expiration_date')) if data.get('expiration_date') else None,
            amount=Decimal(data.get('amount', '0.00')),
            labor_cost=Decimal(data.get('labor_cost', '0.00')),
            material_cost=Decimal(data.get('material_cost', '0.00')),
            overhead_cost=Decimal(data.get('overhead_cost', '0.00')),
            profit_margin=Decimal(data.get('profit_margin', '0.00')),
            notes=data.get('notes'),
            terms=data.get('terms'),
            created_at=datetime.fromisoformat(data.get('created_at')) if data.get('created_at') else None,
            updated_at=datetime.fromisoformat(data.get('updated_at')) if data.get('updated_at') else None
        )


class BidItem:
    """
    Represents an item in a bid.
    
    Attributes:
        id (str): The unique identifier for the bid item.
        bid_id (str): The ID of the bid this item belongs to.
        description (str): Description of the item.
        quantity (Decimal): The quantity of the item.
        unit_price (Decimal): The unit price of the item.
        unit_cost (Decimal): The unit cost of the item.
        category (str): The category of the item (labor, material, equipment, etc.).
        created_at (datetime): When the bid item was created.
        updated_at (datetime): When the bid item was last updated.
    """
    
    def __init__(
        self,
        id: str,
        bid_id: str,
        description: str,
        quantity: Decimal,
        unit_price: Decimal,
        unit_cost: Decimal = None,
        category: str = None,
        created_at: datetime = None,
        updated_at: datetime = None
    ):
        self.id = id
        self.bid_id = bid_id
        self.description = description
        self.quantity = quantity
        self.unit_price = unit_price
        self.unit_cost = unit_cost or unit_price
        self.category = category
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
    
    @property
    def subtotal(self) -> Decimal:
        """Calculate the subtotal for this item."""
        return self.quantity * self.unit_price
    
    @property
    def cost_subtotal(self) -> Decimal:
        """Calculate the cost subtotal for this item."""
        return self.quantity * self.unit_cost
    
    @property
    def profit(self) -> Decimal:
        """Calculate the profit for this item."""
        return self.subtotal - self.cost_subtotal
    
    @property
    def profit_margin(self) -> Decimal:
        """Calculate the profit margin percentage for this item."""
        if self.subtotal == Decimal('0.00'):
            return Decimal('0.00')
        return (self.profit / self.subtotal) * Decimal('100.00')
    
    def to_dict(self) -> dict:
        """Convert the bid item to a dictionary."""
        return {
            'id': self.id,
            'bid_id': self.bid_id,
            'description': self.description,
            'quantity': str(self.quantity),
            'unit_price': str(self.unit_price),
            'unit_cost': str(self.unit_cost),
            'category': self.category,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'BidItem':
        """Create a bid item from a dictionary."""
        return cls(
            id=data.get('id'),
            bid_id=data.get('bid_id'),
            description=data.get('description'),
            quantity=Decimal(data.get('quantity', '0')),
            unit_price=Decimal(data.get('unit_price', '0.00')),
            unit_cost=Decimal(data.get('unit_cost', '0.00')),
            category=data.get('category'),
            created_at=datetime.fromisoformat(data.get('created_at')) if data.get('created_at') else None,
            updated_at=datetime.fromisoformat(data.get('updated_at')) if data.get('updated_at') else None
        )


class BidService:
    """Service for managing bids."""
    
    @staticmethod
    def create_bid(bid_data: dict) -> Bid:
        """Create a new bid."""
        # Implementation would depend on your database access layer
        pass
    
    @staticmethod
    def get_bid(bid_id: str) -> Optional[Bid]:
        """Get a bid by ID."""
        # Implementation would depend on your database access layer
        pass
    
    @staticmethod
    def update_bid(bid_id: str, bid_data: dict) -> Optional[Bid]:
        """Update an existing bid."""
        # Implementation would depend on your database access layer
        pass
    
    @staticmethod
    def delete_bid(bid_id: str) -> bool:
        """Delete a bid."""
        # Implementation would depend on your database access layer
        pass
    
    @staticmethod
    def list_bids(
        client_id: str = None,
        project_id: str = None,
        status: str = None,
        start_date: datetime = None,
        end_date: datetime = None
    ) -> List[Bid]:
        """List bids with optional filtering."""
        # Implementation would depend on your database access layer
        pass
    
    @staticmethod
    def add_bid_item(bid_id: str, item_data: dict) -> BidItem:
        """Add an item to a bid."""
        # Implementation would depend on your database access layer
        pass
    
    @staticmethod
    def update_bid_item(item_id: str, item_data: dict) -> Optional[BidItem]:
        """Update a bid item."""
        # Implementation would depend on your database access layer
        pass
    
    @staticmethod
    def delete_bid_item(item_id: str) -> bool:
        """Delete a bid item."""
        # Implementation would depend on your database access layer
        pass
    
    @staticmethod
    def accept_bid(bid_id: str, acceptance_date: datetime = None) -> Optional[Bid]:
        """Mark a bid as accepted."""
        # Implementation would depend on your database access layer
        pass
    
    @staticmethod
    def reject_bid(bid_id: str, rejection_date: datetime = None, reason: str = None) -> Optional[Bid]:
        """Mark a bid as rejected."""
        # Implementation would depend on your database access layer
        pass
    
    @staticmethod
    def generate_bid_number() -> str:
        """Generate a unique bid number."""
        # Implementation would depend on your business logic
        # Example: BID-2023-001
        pass 