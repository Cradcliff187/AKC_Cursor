"""
Payment Model

This module defines the Payment model and related functionality.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from decimal import Decimal
from enum import Enum


class PaymentMethod(str, Enum):
    """Enum representing the possible payment methods."""
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    BANK_TRANSFER = "bank_transfer"
    CHECK = "check"
    CASH = "cash"
    PAYPAL = "paypal"
    OTHER = "other"


class PaymentStatus(str, Enum):
    """Enum representing the possible payment statuses."""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"


class Payment:
    """
    Represents a payment in the system.
    
    Attributes:
        id (str): The unique identifier for the payment.
        invoice_id (str): The ID of the invoice this payment is for.
        client_id (str): The ID of the client making the payment.
        amount (Decimal): The amount of the payment.
        payment_date (datetime): The date the payment was made.
        payment_method (PaymentMethod): The method of payment.
        status (PaymentStatus): The status of the payment.
        reference_number (str): A reference number for the payment (e.g., check number).
        notes (str): Additional notes about the payment.
        transaction_id (str): The ID of the transaction from the payment processor.
        created_at (datetime): When the payment record was created.
        updated_at (datetime): When the payment record was last updated.
    """
    
    def __init__(
        self,
        id: str,
        invoice_id: str,
        client_id: str,
        amount: Decimal,
        payment_date: datetime,
        payment_method: PaymentMethod = PaymentMethod.BANK_TRANSFER,
        status: PaymentStatus = PaymentStatus.COMPLETED,
        reference_number: str = None,
        notes: str = None,
        transaction_id: str = None,
        created_at: datetime = None,
        updated_at: datetime = None
    ):
        self.id = id
        self.invoice_id = invoice_id
        self.client_id = client_id
        self.amount = amount
        self.payment_date = payment_date
        self.payment_method = payment_method if isinstance(payment_method, PaymentMethod) else PaymentMethod(payment_method)
        self.status = status if isinstance(status, PaymentStatus) else PaymentStatus(status)
        self.reference_number = reference_number
        self.notes = notes
        self.transaction_id = transaction_id
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
    
    @property
    def is_completed(self) -> bool:
        """Check if the payment is completed."""
        return self.status == PaymentStatus.COMPLETED
    
    @property
    def is_refunded(self) -> bool:
        """Check if the payment is refunded."""
        return self.status in [PaymentStatus.REFUNDED, PaymentStatus.PARTIALLY_REFUNDED]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the payment to a dictionary."""
        return {
            'id': self.id,
            'invoice_id': self.invoice_id,
            'client_id': self.client_id,
            'amount': str(self.amount),
            'payment_date': self.payment_date.isoformat() if self.payment_date else None,
            'payment_method': self.payment_method.value if isinstance(self.payment_method, PaymentMethod) else self.payment_method,
            'status': self.status.value if isinstance(self.status, PaymentStatus) else self.status,
            'reference_number': self.reference_number,
            'notes': self.notes,
            'transaction_id': self.transaction_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Payment':
        """Create a payment from a dictionary."""
        return cls(
            id=data.get('id'),
            invoice_id=data.get('invoice_id'),
            client_id=data.get('client_id'),
            amount=Decimal(data.get('amount', '0.00')),
            payment_date=datetime.fromisoformat(data.get('payment_date')) if data.get('payment_date') else None,
            payment_method=data.get('payment_method', PaymentMethod.BANK_TRANSFER),
            status=data.get('status', PaymentStatus.COMPLETED),
            reference_number=data.get('reference_number'),
            notes=data.get('notes'),
            transaction_id=data.get('transaction_id'),
            created_at=datetime.fromisoformat(data.get('created_at')) if data.get('created_at') else None,
            updated_at=datetime.fromisoformat(data.get('updated_at')) if data.get('updated_at') else None
        )


class Refund:
    """
    Represents a refund of a payment.
    
    Attributes:
        id (str): The unique identifier for the refund.
        payment_id (str): The ID of the payment being refunded.
        amount (Decimal): The amount of the refund.
        refund_date (datetime): The date the refund was processed.
        reason (str): The reason for the refund.
        notes (str): Additional notes about the refund.
        transaction_id (str): The ID of the transaction from the payment processor.
        created_at (datetime): When the refund record was created.
        updated_at (datetime): When the refund record was last updated.
    """
    
    def __init__(
        self,
        id: str,
        payment_id: str,
        amount: Decimal,
        refund_date: datetime,
        reason: str = None,
        notes: str = None,
        transaction_id: str = None,
        created_at: datetime = None,
        updated_at: datetime = None
    ):
        self.id = id
        self.payment_id = payment_id
        self.amount = amount
        self.refund_date = refund_date
        self.reason = reason
        self.notes = notes
        self.transaction_id = transaction_id
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the refund to a dictionary."""
        return {
            'id': self.id,
            'payment_id': self.payment_id,
            'amount': str(self.amount),
            'refund_date': self.refund_date.isoformat() if self.refund_date else None,
            'reason': self.reason,
            'notes': self.notes,
            'transaction_id': self.transaction_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Refund':
        """Create a refund from a dictionary."""
        return cls(
            id=data.get('id'),
            payment_id=data.get('payment_id'),
            amount=Decimal(data.get('amount', '0.00')),
            refund_date=datetime.fromisoformat(data.get('refund_date')) if data.get('refund_date') else None,
            reason=data.get('reason'),
            notes=data.get('notes'),
            transaction_id=data.get('transaction_id'),
            created_at=datetime.fromisoformat(data.get('created_at')) if data.get('created_at') else None,
            updated_at=datetime.fromisoformat(data.get('updated_at')) if data.get('updated_at') else None
        )


class PaymentService:
    """Service for managing payments and refunds."""
    
    @staticmethod
    def create_payment(payment_data: Dict[str, Any]) -> Payment:
        """Create a new payment."""
        # Implementation would depend on your database access layer
        pass
    
    @staticmethod
    def get_payment(payment_id: str) -> Optional[Payment]:
        """Get a payment by ID."""
        # Implementation would depend on your database access layer
        pass
    
    @staticmethod
    def update_payment(payment_id: str, payment_data: Dict[str, Any]) -> Optional[Payment]:
        """Update an existing payment."""
        # Implementation would depend on your database access layer
        pass
    
    @staticmethod
    def delete_payment(payment_id: str) -> bool:
        """Delete a payment."""
        # Implementation would depend on your database access layer
        pass
    
    @staticmethod
    def list_payments(
        client_id: str = None,
        invoice_id: str = None,
        status: str = None,
        start_date: datetime = None,
        end_date: datetime = None
    ) -> List[Payment]:
        """List payments with optional filtering."""
        # Implementation would depend on your database access layer
        pass
    
    @staticmethod
    def create_refund(refund_data: Dict[str, Any]) -> Refund:
        """Create a new refund."""
        # Implementation would depend on your database access layer
        pass
    
    @staticmethod
    def get_refund(refund_id: str) -> Optional[Refund]:
        """Get a refund by ID."""
        # Implementation would depend on your database access layer
        pass
    
    @staticmethod
    def list_refunds(payment_id: str) -> List[Refund]:
        """List refunds for a payment."""
        # Implementation would depend on your database access layer
        pass
    
    @staticmethod
    def process_payment(
        invoice_id: str,
        amount: Decimal,
        payment_method: PaymentMethod,
        reference_number: str = None
    ) -> Payment:
        """Process a payment for an invoice."""
        # Implementation would depend on your payment processing integration
        pass
    
    @staticmethod
    def process_refund(
        payment_id: str,
        amount: Decimal,
        reason: str = None
    ) -> Refund:
        """Process a refund for a payment."""
        # Implementation would depend on your payment processing integration
        pass
    
    @staticmethod
    def get_payment_summary(
        client_id: str = None,
        start_date: datetime = None,
        end_date: datetime = None
    ) -> Dict[str, Any]:
        """Get a summary of payments."""
        # Implementation would depend on your database access layer
        # Example return:
        # {
        #     'total_payments': Decimal('1000.00'),
        #     'total_refunds': Decimal('100.00'),
        #     'net_payments': Decimal('900.00'),
        #     'payment_count': 10,
        #     'refund_count': 2
        # }
        pass 