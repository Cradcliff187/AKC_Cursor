import pytest
from datetime import datetime
from app.models.payment import Payment

@pytest.mark.unit
@pytest.mark.models
class TestPaymentModel:
    
    def test_payment_init(self):
        """Test Payment initialization with default values."""
        payment = Payment()
        assert payment.id is None
        assert payment.invoice_id is None
        assert payment.amount == 0.0
        assert payment.payment_date is not None  # Should default to today
        assert payment.payment_method == Payment.METHOD_CHECK
        assert payment.reference_number is None
        assert payment.notes is None
        assert payment.created_by_id is None
    
    def test_payment_init_with_values(self):
        """Test Payment initialization with provided values."""
        payment_date = datetime.now().date()
        
        payment = Payment(
            id=1,
            invoice_id=2,
            amount=100.0,
            payment_date=payment_date,
            payment_method=Payment.METHOD_CREDIT_CARD,
            reference_number="REF-123",
            notes="Test payment",
            created_by_id=3
        )
        
        assert payment.id == 1
        assert payment.invoice_id == 2
        assert payment.amount == 100.0
        assert payment.payment_date == payment_date
        assert payment.payment_method == Payment.METHOD_CREDIT_CARD
        assert payment.reference_number == "REF-123"
        assert payment.notes == "Test payment"
        assert payment.created_by_id == 3
    
    def test_from_dict(self):
        """Test creating Payment from dictionary."""
        payment_date = datetime.now().date()
        
        data = {
            'id': 1,
            'invoice_id': 2,
            'amount': 100.0,
            'payment_date': payment_date.isoformat(),
            'payment_method': Payment.METHOD_CREDIT_CARD,
            'reference_number': 'REF-123',
            'notes': 'Test payment',
            'created_by_id': 3
        }
        
        payment = Payment.from_dict(data)
        
        assert payment.id == 1
        assert payment.invoice_id == 2
        assert payment.amount == 100.0
        assert payment.payment_date.isoformat() == payment_date.isoformat()
        assert payment.payment_method == Payment.METHOD_CREDIT_CARD
        assert payment.reference_number == 'REF-123'
        assert payment.notes == 'Test payment'
        assert payment.created_by_id == 3
    
    def test_from_dict_with_empty_data(self):
        """Test creating Payment from empty dictionary."""
        payment = Payment.from_dict({})
        
        assert payment.id is None
        assert payment.invoice_id is None
        assert payment.amount == 0.0
        assert payment.payment_date is not None  # Should default to today
        assert payment.payment_method == Payment.METHOD_CHECK
        assert payment.reference_number is None
        assert payment.notes is None
        assert payment.created_by_id is None
    
    def test_to_dict(self):
        """Test converting Payment to dictionary."""
        payment_date = datetime.now().date()
        
        payment = Payment(
            id=1,
            invoice_id=2,
            amount=100.0,
            payment_date=payment_date,
            payment_method=Payment.METHOD_CREDIT_CARD,
            reference_number="REF-123",
            notes="Test payment",
            created_by_id=3
        )
        
        data = payment.to_dict()
        
        assert data['id'] == 1
        assert data['invoice_id'] == 2
        assert data['amount'] == 100.0
        assert data['payment_date'] == payment_date.isoformat()
        assert data['payment_method'] == Payment.METHOD_CREDIT_CARD
        assert data['reference_number'] == 'REF-123'
        assert data['notes'] == 'Test payment'
        assert data['created_by_id'] == 3
    
    def test_payment_methods(self):
        """Test payment method constants."""
        # Test all payment method constants are defined
        assert Payment.METHOD_CASH == "Cash"
        assert Payment.METHOD_CHECK == "Check"
        assert Payment.METHOD_CREDIT_CARD == "Credit Card"
        assert Payment.METHOD_BANK_TRANSFER == "Bank Transfer"
        assert Payment.METHOD_PAYPAL == "PayPal"
        assert Payment.METHOD_OTHER == "Other" 