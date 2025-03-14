"""
Invoice Model

This module defines the Invoice model and related functionality.
"""

from datetime import datetime
from typing import List, Optional
from decimal import Decimal

class Invoice:
    """
    Represents an invoice in the system.
    
    Attributes:
        id (str): The unique identifier for the invoice.
        client_id (str): The ID of the client this invoice belongs to.
        project_id (str): The ID of the project this invoice is for.
        invoice_number (str): The invoice number (e.g., INV-2023-001).
        status (str): The status of the invoice (draft, sent, paid, overdue, etc.).
        issue_date (datetime): The date the invoice was issued.
        due_date (datetime): The date the invoice is due.
        amount (Decimal): The total amount of the invoice.
        tax_amount (Decimal): The tax amount applied to the invoice.
        discount_amount (Decimal): Any discount applied to the invoice.
        notes (str): Additional notes about the invoice.
        terms (str): Payment terms for the invoice.
        created_at (datetime): When the invoice was created.
        updated_at (datetime): When the invoice was last updated.
    """
    
    def __init__(
        self,
        id: str,
        client_id: str,
        project_id: str,
        invoice_number: str,
        status: str,
        issue_date: datetime,
        due_date: datetime,
        amount: Decimal,
        tax_amount: Decimal = Decimal('0.00'),
        discount_amount: Decimal = Decimal('0.00'),
        notes: str = None,
        terms: str = None,
        created_at: datetime = None,
        updated_at: datetime = None
    ):
        self.id = id
        self.client_id = client_id
        self.project_id = project_id
        self.invoice_number = invoice_number
        self.status = status
        self.issue_date = issue_date
        self.due_date = due_date
        self.amount = amount
        self.tax_amount = tax_amount
        self.discount_amount = discount_amount
        self.notes = notes
        self.terms = terms
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
    
    @property
    def total_amount(self) -> Decimal:
        """Calculate the total amount including tax and discount."""
        return self.amount + self.tax_amount - self.discount_amount
    
    @property
    def is_overdue(self) -> bool:
        """Check if the invoice is overdue."""
        return self.due_date < datetime.now() and self.status != 'paid'
    
    def to_dict(self) -> dict:
        """Convert the invoice to a dictionary."""
        return {
            'id': self.id,
            'client_id': self.client_id,
            'project_id': self.project_id,
            'invoice_number': self.invoice_number,
            'status': self.status,
            'issue_date': self.issue_date.isoformat() if self.issue_date else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'amount': str(self.amount),
            'tax_amount': str(self.tax_amount),
            'discount_amount': str(self.discount_amount),
            'notes': self.notes,
            'terms': self.terms,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Invoice':
        """Create an invoice from a dictionary."""
        return cls(
            id=data.get('id'),
            client_id=data.get('client_id'),
            project_id=data.get('project_id'),
            invoice_number=data.get('invoice_number'),
            status=data.get('status'),
            issue_date=datetime.fromisoformat(data.get('issue_date')) if data.get('issue_date') else None,
            due_date=datetime.fromisoformat(data.get('due_date')) if data.get('due_date') else None,
            amount=Decimal(data.get('amount', '0.00')),
            tax_amount=Decimal(data.get('tax_amount', '0.00')),
            discount_amount=Decimal(data.get('discount_amount', '0.00')),
            notes=data.get('notes'),
            terms=data.get('terms'),
            created_at=datetime.fromisoformat(data.get('created_at')) if data.get('created_at') else None,
            updated_at=datetime.fromisoformat(data.get('updated_at')) if data.get('updated_at') else None
        )


class InvoiceItem:
    """
    Represents an item in an invoice.
    
    Attributes:
        id (str): The unique identifier for the invoice item.
        invoice_id (str): The ID of the invoice this item belongs to.
        description (str): Description of the item.
        quantity (Decimal): The quantity of the item.
        unit_price (Decimal): The unit price of the item.
        tax_rate (Decimal): The tax rate applied to the item.
        created_at (datetime): When the invoice item was created.
        updated_at (datetime): When the invoice item was last updated.
    """
    
    def __init__(
        self,
        id: str,
        invoice_id: str,
        description: str,
        quantity: Decimal,
        unit_price: Decimal,
        tax_rate: Decimal = Decimal('0.00'),
        created_at: datetime = None,
        updated_at: datetime = None
    ):
        self.id = id
        self.invoice_id = invoice_id
        self.description = description
        self.quantity = quantity
        self.unit_price = unit_price
        self.tax_rate = tax_rate
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
    
    @property
    def subtotal(self) -> Decimal:
        """Calculate the subtotal for this item."""
        return self.quantity * self.unit_price
    
    @property
    def tax_amount(self) -> Decimal:
        """Calculate the tax amount for this item."""
        return self.subtotal * (self.tax_rate / Decimal('100.00'))
    
    @property
    def total(self) -> Decimal:
        """Calculate the total for this item including tax."""
        return self.subtotal + self.tax_amount
    
    def to_dict(self) -> dict:
        """Convert the invoice item to a dictionary."""
        return {
            'id': self.id,
            'invoice_id': self.invoice_id,
            'description': self.description,
            'quantity': str(self.quantity),
            'unit_price': str(self.unit_price),
            'tax_rate': str(self.tax_rate),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'InvoiceItem':
        """Create an invoice item from a dictionary."""
        return cls(
            id=data.get('id'),
            invoice_id=data.get('invoice_id'),
            description=data.get('description'),
            quantity=Decimal(data.get('quantity', '0')),
            unit_price=Decimal(data.get('unit_price', '0.00')),
            tax_rate=Decimal(data.get('tax_rate', '0.00')),
            created_at=datetime.fromisoformat(data.get('created_at')) if data.get('created_at') else None,
            updated_at=datetime.fromisoformat(data.get('updated_at')) if data.get('updated_at') else None
        )


class InvoiceService:
    """Service for managing invoices."""
    
    @staticmethod
    def create_invoice(invoice_data: dict) -> Invoice:
        """Create a new invoice."""
        # Implementation would depend on your database access layer
        pass
    
    @staticmethod
    def get_invoice(invoice_id: str) -> Optional[Invoice]:
        """Get an invoice by ID."""
        # Implementation would depend on your database access layer
        pass
    
    @staticmethod
    def update_invoice(invoice_id: str, invoice_data: dict) -> Optional[Invoice]:
        """Update an existing invoice."""
        # Implementation would depend on your database access layer
        pass
    
    @staticmethod
    def delete_invoice(invoice_id: str) -> bool:
        """Delete an invoice."""
        # Implementation would depend on your database access layer
        pass
    
    @staticmethod
    def list_invoices(
        client_id: str = None,
        project_id: str = None,
        status: str = None,
        start_date: datetime = None,
        end_date: datetime = None
    ) -> List[Invoice]:
        """List invoices with optional filtering."""
        # Implementation would depend on your database access layer
        pass
    
    @staticmethod
    def add_invoice_item(invoice_id: str, item_data: dict) -> InvoiceItem:
        """Add an item to an invoice."""
        # Implementation would depend on your database access layer
        pass
    
    @staticmethod
    def update_invoice_item(item_id: str, item_data: dict) -> Optional[InvoiceItem]:
        """Update an invoice item."""
        # Implementation would depend on your database access layer
        pass
    
    @staticmethod
    def delete_invoice_item(item_id: str) -> bool:
        """Delete an invoice item."""
        # Implementation would depend on your database access layer
        pass
    
    @staticmethod
    def mark_as_paid(invoice_id: str, payment_date: datetime = None) -> Optional[Invoice]:
        """Mark an invoice as paid."""
        # Implementation would depend on your database access layer
        pass
    
    @staticmethod
    def generate_invoice_number() -> str:
        """Generate a unique invoice number."""
        # Implementation would depend on your business logic
        # Example: INV-2023-001
        pass 