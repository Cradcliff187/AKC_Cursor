"""
Expense Model

This module defines the Expense model and related functionality.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from decimal import Decimal
from enum import Enum


class ExpenseCategory(str, Enum):
    """Enum representing the possible expense categories."""
    MATERIALS = "materials"
    LABOR = "labor"
    EQUIPMENT = "equipment"
    SUBCONTRACTOR = "subcontractor"
    OFFICE = "office"
    TRAVEL = "travel"
    UTILITIES = "utilities"
    INSURANCE = "insurance"
    TAXES = "taxes"
    MARKETING = "marketing"
    RENT = "rent"
    OTHER = "other"


class ExpenseStatus(str, Enum):
    """Enum representing the possible expense statuses."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    PAID = "paid"


class Expense:
    """
    Represents an expense in the system.
    
    Attributes:
        id (str): The unique identifier for the expense.
        project_id (str): The ID of the project this expense is for (optional).
        vendor_id (str): The ID of the vendor this expense is paid to (optional).
        description (str): Description of the expense.
        amount (Decimal): The amount of the expense.
        expense_date (datetime): The date the expense was incurred.
        category (ExpenseCategory): The category of the expense.
        status (ExpenseStatus): The status of the expense.
        receipt_url (str): URL to the receipt image/document.
        payment_method (str): The method used to pay the expense.
        payment_reference (str): Reference number for the payment.
        notes (str): Additional notes about the expense.
        tax_deductible (bool): Whether the expense is tax deductible.
        created_by (str): The ID of the user who created the expense.
        approved_by (str): The ID of the user who approved the expense.
        created_at (datetime): When the expense record was created.
        updated_at (datetime): When the expense record was last updated.
    """
    
    def __init__(
        self,
        id: str,
        description: str,
        amount: Decimal,
        expense_date: datetime,
        category: ExpenseCategory = ExpenseCategory.OTHER,
        status: ExpenseStatus = ExpenseStatus.PENDING,
        project_id: str = None,
        vendor_id: str = None,
        receipt_url: str = None,
        payment_method: str = None,
        payment_reference: str = None,
        notes: str = None,
        tax_deductible: bool = True,
        created_by: str = None,
        approved_by: str = None,
        created_at: datetime = None,
        updated_at: datetime = None
    ):
        self.id = id
        self.description = description
        self.amount = amount
        self.expense_date = expense_date
        self.category = category if isinstance(category, ExpenseCategory) else ExpenseCategory(category)
        self.status = status if isinstance(status, ExpenseStatus) else ExpenseStatus(status)
        self.project_id = project_id
        self.vendor_id = vendor_id
        self.receipt_url = receipt_url
        self.payment_method = payment_method
        self.payment_reference = payment_reference
        self.notes = notes
        self.tax_deductible = tax_deductible
        self.created_by = created_by
        self.approved_by = approved_by
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
    
    @property
    def is_approved(self) -> bool:
        """Check if the expense is approved."""
        return self.status in [ExpenseStatus.APPROVED, ExpenseStatus.PAID]
    
    @property
    def is_paid(self) -> bool:
        """Check if the expense is paid."""
        return self.status == ExpenseStatus.PAID
    
    @property
    def is_billable(self) -> bool:
        """Check if the expense is billable to a project."""
        return self.project_id is not None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the expense to a dictionary."""
        return {
            'id': self.id,
            'description': self.description,
            'amount': str(self.amount),
            'expense_date': self.expense_date.isoformat() if self.expense_date else None,
            'category': self.category.value if isinstance(self.category, ExpenseCategory) else self.category,
            'status': self.status.value if isinstance(self.status, ExpenseStatus) else self.status,
            'project_id': self.project_id,
            'vendor_id': self.vendor_id,
            'receipt_url': self.receipt_url,
            'payment_method': self.payment_method,
            'payment_reference': self.payment_reference,
            'notes': self.notes,
            'tax_deductible': self.tax_deductible,
            'created_by': self.created_by,
            'approved_by': self.approved_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Expense':
        """Create an expense from a dictionary."""
        return cls(
            id=data.get('id'),
            description=data.get('description'),
            amount=Decimal(data.get('amount', '0.00')),
            expense_date=datetime.fromisoformat(data.get('expense_date')) if data.get('expense_date') else None,
            category=data.get('category', ExpenseCategory.OTHER),
            status=data.get('status', ExpenseStatus.PENDING),
            project_id=data.get('project_id'),
            vendor_id=data.get('vendor_id'),
            receipt_url=data.get('receipt_url'),
            payment_method=data.get('payment_method'),
            payment_reference=data.get('payment_reference'),
            notes=data.get('notes'),
            tax_deductible=data.get('tax_deductible', True),
            created_by=data.get('created_by'),
            approved_by=data.get('approved_by'),
            created_at=datetime.fromisoformat(data.get('created_at')) if data.get('created_at') else None,
            updated_at=datetime.fromisoformat(data.get('updated_at')) if data.get('updated_at') else None
        )


class Vendor:
    """
    Represents a vendor in the system.
    
    Attributes:
        id (str): The unique identifier for the vendor.
        name (str): The name of the vendor.
        contact_name (str): The primary contact person's name.
        email (str): The primary email address for the vendor.
        phone (str): The primary phone number for the vendor.
        address (str): The physical address of the vendor.
        city (str): The city where the vendor is located.
        state (str): The state where the vendor is located.
        zip_code (str): The ZIP code where the vendor is located.
        website (str): The vendor's website URL.
        notes (str): Additional notes about the vendor.
        tax_id (str): The tax ID or EIN for the vendor.
        created_at (datetime): When the vendor was created.
        updated_at (datetime): When the vendor was last updated.
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
        website: str = None,
        notes: str = None,
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
        self.website = website
        self.notes = notes
        self.tax_id = tax_id
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
    
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
        """Convert the vendor to a dictionary."""
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
            'website': self.website,
            'notes': self.notes,
            'tax_id': self.tax_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Vendor':
        """Create a vendor from a dictionary."""
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
            website=data.get('website'),
            notes=data.get('notes'),
            tax_id=data.get('tax_id'),
            created_at=datetime.fromisoformat(data.get('created_at')) if data.get('created_at') else None,
            updated_at=datetime.fromisoformat(data.get('updated_at')) if data.get('updated_at') else None
        )


class ExpenseService:
    """Service for managing expenses and vendors."""
    
    @staticmethod
    def create_expense(expense_data: Dict[str, Any]) -> Expense:
        """Create a new expense."""
        # Implementation would depend on your database access layer
        pass
    
    @staticmethod
    def get_expense(expense_id: str) -> Optional[Expense]:
        """Get an expense by ID."""
        # Implementation would depend on your database access layer
        pass
    
    @staticmethod
    def update_expense(expense_id: str, expense_data: Dict[str, Any]) -> Optional[Expense]:
        """Update an existing expense."""
        # Implementation would depend on your database access layer
        pass
    
    @staticmethod
    def delete_expense(expense_id: str) -> bool:
        """Delete an expense."""
        # Implementation would depend on your database access layer
        pass
    
    @staticmethod
    def list_expenses(
        project_id: str = None,
        vendor_id: str = None,
        category: str = None,
        status: str = None,
        start_date: datetime = None,
        end_date: datetime = None,
        created_by: str = None
    ) -> List[Expense]:
        """List expenses with optional filtering."""
        # Implementation would depend on your database access layer
        pass
    
    @staticmethod
    def approve_expense(expense_id: str, approved_by: str) -> Optional[Expense]:
        """Approve an expense."""
        # Implementation would depend on your database access layer
        pass
    
    @staticmethod
    def reject_expense(expense_id: str, reason: str = None) -> Optional[Expense]:
        """Reject an expense."""
        # Implementation would depend on your database access layer
        pass
    
    @staticmethod
    def mark_as_paid(expense_id: str, payment_method: str = None, payment_reference: str = None) -> Optional[Expense]:
        """Mark an expense as paid."""
        # Implementation would depend on your database access layer
        pass
    
    @staticmethod
    def upload_receipt(expense_id: str, receipt_file) -> Optional[str]:
        """Upload a receipt for an expense."""
        # Implementation would depend on your file storage system
        pass
    
    @staticmethod
    def create_vendor(vendor_data: Dict[str, Any]) -> Vendor:
        """Create a new vendor."""
        # Implementation would depend on your database access layer
        pass
    
    @staticmethod
    def get_vendor(vendor_id: str) -> Optional[Vendor]:
        """Get a vendor by ID."""
        # Implementation would depend on your database access layer
        pass
    
    @staticmethod
    def update_vendor(vendor_id: str, vendor_data: Dict[str, Any]) -> Optional[Vendor]:
        """Update an existing vendor."""
        # Implementation would depend on your database access layer
        pass
    
    @staticmethod
    def delete_vendor(vendor_id: str) -> bool:
        """Delete a vendor."""
        # Implementation would depend on your database access layer
        pass
    
    @staticmethod
    def list_vendors(search_term: str = None) -> List[Vendor]:
        """List vendors with optional filtering."""
        # Implementation would depend on your database access layer
        pass
    
    @staticmethod
    def get_expense_summary(
        project_id: str = None,
        category: str = None,
        start_date: datetime = None,
        end_date: datetime = None
    ) -> Dict[str, Any]:
        """Get a summary of expenses."""
        # Implementation would depend on your database access layer
        # Example return:
        # {
        #     'total_amount': Decimal('5000.00'),
        #     'by_category': {
        #         'materials': Decimal('2000.00'),
        #         'labor': Decimal('1500.00'),
        #         'equipment': Decimal('1000.00'),
        #         'other': Decimal('500.00')
        #     },
        #     'by_status': {
        #         'pending': Decimal('1000.00'),
        #         'approved': Decimal('1500.00'),
        #         'paid': Decimal('2500.00')
        #     }
        # }
        pass 