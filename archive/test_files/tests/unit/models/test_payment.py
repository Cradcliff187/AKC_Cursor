"""
Unit tests for the Payment model
"""
import pytest
from datetime import datetime
from app.models.payment import Payment

@pytest.mark.unit
@pytest.mark.models
class TestPaymentModel:
    
    def test_payment_init(self):
        """Test Payment initialization with various parameters"""
        # Test with minimal required params
        payment = Payment(
            invoice_id=1,
            amount=100.00,
            payment_date='2023-01-01',
            payment_method=Payment.METHOD_CASH
        )
        assert payment.invoice_id == 1
        assert payment.amount == 100.00
        assert payment.payment_date.strftime('%Y-%m-%d') == '2023-01-01'
        assert payment.payment_method == Payment.METHOD_CASH
        assert payment.reference_number is None
        assert payment.notes is None
        
        # Test with all params
        payment = Payment(
            id=1,
            invoice_id=2,
            amount=500.00,
            payment_date='2023-02-01',
            payment_method=Payment.METHOD_CREDIT_CARD,
            reference_number='REF12345',
            notes='Test payment notes',
            created_by_id=1,
            created_at='2023-02-01 10:00:00',
            updated_at='2023-02-01 10:00:00'
        )
        assert payment.id == 1
        assert payment.invoice_id == 2
        assert payment.amount == 500.00
        assert payment.payment_date.strftime('%Y-%m-%d') == '2023-02-01'
        assert payment.payment_method == Payment.METHOD_CREDIT_CARD
        assert payment.reference_number == 'REF12345'
        assert payment.notes == 'Test payment notes'
        assert payment.created_by_id == 1
        
        # Test with defaults
        today = datetime.now().strftime('%Y-%m-%d')
        payment = Payment(invoice_id=3)
        assert payment.invoice_id == 3
        assert payment.amount == 0.00
        assert payment.payment_date.strftime('%Y-%m-%d') == today  # Default to today
        assert payment.payment_method == Payment.METHOD_CHECK  # Default method
    
    def test_from_dict(self):
        """Test creating a Payment from a dictionary"""
        data = {
            'id': 1,
            'invoice_id': 2,
            'amount': 500.00,
            'payment_date': '2023-02-01',
            'payment_method': Payment.METHOD_CREDIT_CARD,
            'reference_number': 'REF12345',
            'notes': 'Test payment notes',
            'created_by_id': 1
        }
        payment = Payment.from_dict(data)
        assert payment.id == 1
        assert payment.invoice_id == 2
        assert payment.amount == 500.00
        assert payment.payment_date.strftime('%Y-%m-%d') == '2023-02-01'
        assert payment.payment_method == Payment.METHOD_CREDIT_CARD
        assert payment.reference_number == 'REF12345'
        assert payment.notes == 'Test payment notes'
        assert payment.created_by_id == 1
        
        # Test with minimal data
        minimal_data = {
            'invoice_id': 3,
            'amount': 100.00
        }
        today = datetime.now().strftime('%Y-%m-%d')
        payment = Payment.from_dict(minimal_data)
        assert payment.invoice_id == 3
        assert payment.amount == 100.00
        assert payment.payment_date.strftime('%Y-%m-%d') == today  # Default to today
        assert payment.payment_method == Payment.METHOD_CHECK  # Default method
        assert payment.reference_number is None
        
        # Test with empty data
        payment = Payment.from_dict({})
        assert payment.invoice_id is None
        assert payment.amount == 0.00  # Default amount
        assert payment.payment_date.strftime('%Y-%m-%d') == today  # Default to today
        assert payment.payment_method == Payment.METHOD_CHECK  # Default method
    
    def test_to_dict(self):
        """Test converting a Payment to a dictionary"""
        payment = Payment(
            id=1,
            invoice_id=2,
            amount=500.00,
            payment_date='2023-02-01',
            payment_method=Payment.METHOD_CREDIT_CARD,
            reference_number='REF12345',
            notes='Test payment notes',
            created_by_id=1
        )
        data = payment.to_dict()
        assert data['id'] == 1
        assert data['invoice_id'] == 2
        assert data['amount'] == 500.00
        if isinstance(data['payment_date'], str):
            assert data['payment_date'] == '2023-02-01'
        else:
            assert data['payment_date'].strftime('%Y-%m-%d') == '2023-02-01'
        assert data['payment_method'] == Payment.METHOD_CREDIT_CARD
        assert data['reference_number'] == 'REF12345'
        assert data['notes'] == 'Test payment notes'
        assert data['created_by_id'] == 1
    
    def test_payment_methods(self):
        """Test payment method constants."""
        # Test all payment method constants are defined
        assert Payment.METHOD_CASH == "Cash"
        assert Payment.METHOD_CHECK == "Check"
        assert Payment.METHOD_CREDIT_CARD == "Credit Card"
        assert Payment.METHOD_BANK_TRANSFER == "Bank Transfer"
        assert Payment.METHOD_PAYPAL == "PayPal"
        assert Payment.METHOD_OTHER == "Other" 