"""
Unit tests for the Invoice model
"""
import pytest
from datetime import datetime, timedelta
from app.models.invoice import Invoice

def test_invoice_init():
    """Test Invoice initialization with various parameters"""
    # Test with minimal required params
    invoice = Invoice(
        invoice_number='INV-001',
        client_id=1,
        issue_date='2023-01-01',
        due_date='2023-01-31',
        subtotal=1000.00,
        total_amount=1000.00,
        balance_due=1000.00
    )
    assert invoice.invoice_number == 'INV-001'
    assert invoice.client_id == 1
    assert invoice.subtotal == 1000.00
    assert invoice.status == Invoice.STATUS_DRAFT  # Default status
    
    # Test with all params
    invoice = Invoice(
        id=1,
        invoice_number='INV-002',
        client_id=2,
        project_id=3,
        status=Invoice.STATUS_SENT,
        issue_date='2023-02-01',
        due_date='2023-02-28',
        subtotal=2000.00,
        tax_rate=10.0,
        tax_amount=200.00,
        discount_amount=100.00,
        total_amount=2100.00,
        amount_paid=500.00,
        balance_due=1600.00,
        notes='Test notes',
        terms='Net 30',
        footer='Thank you for your business',
        payment_instructions='Pay by bank transfer',
        sent_date='2023-02-02',
        paid_date=None,
        last_reminder_date=None,
        created_by_id=1,
        created_at='2023-02-01 10:00:00',
        updated_at='2023-02-01 10:00:00'
    )
    assert invoice.id == 1
    assert invoice.project_id == 3
    assert invoice.status == Invoice.STATUS_SENT
    assert invoice.tax_rate == 10.0
    assert invoice.amount_paid == 500.00
    assert invoice.balance_due == 1600.00

def test_from_dict():
    """Test creating an Invoice from a dictionary"""
    data = {
        'id': 1,
        'invoice_number': 'INV-001',
        'client_id': 2,
        'project_id': 3,
        'status': 'sent',
        'issue_date': '2023-01-01',
        'due_date': '2023-01-31',
        'subtotal': 1000.00,
        'tax_rate': 10.0,
        'tax_amount': 100.00,
        'discount_amount': 50.00,
        'total_amount': 1050.00,
        'amount_paid': 0.00,
        'balance_due': 1050.00
    }
    invoice = Invoice.from_dict(data)
    assert invoice.id == 1
    assert invoice.invoice_number == 'INV-001'
    assert invoice.client_id == 2
    assert invoice.project_id == 3
    assert invoice.status == 'sent'
    assert invoice.subtotal == 1000.00
    assert invoice.tax_rate == 10.0
    assert invoice.tax_amount == 100.00
    assert invoice.total_amount == 1050.00
    assert invoice.balance_due == 1050.00
    
    # Test with minimal data
    minimal_data = {
        'invoice_number': 'INV-002',
        'client_id': 3,
        'issue_date': '2023-02-01',
        'due_date': '2023-02-28',
        'subtotal': 500.00,
        'total_amount': 500.00,
        'balance_due': 500.00
    }
    invoice = Invoice.from_dict(minimal_data)
    assert invoice.invoice_number == 'INV-002'
    assert invoice.client_id == 3
    assert invoice.status == Invoice.STATUS_DRAFT  # Default status
    assert invoice.subtotal == 500.00
    assert invoice.tax_rate == 0.0  # Default value
    
    # Test with empty data
    invoice = Invoice.from_dict({})
    assert invoice.invoice_number is None
    assert invoice.client_id is None
    assert invoice.status == Invoice.STATUS_DRAFT

def test_to_dict():
    """Test converting an Invoice to a dictionary"""
    invoice = Invoice(
        id=1,
        invoice_number='INV-001',
        client_id=2,
        project_id=3,
        status=Invoice.STATUS_SENT,
        issue_date='2023-01-01',
        due_date='2023-01-31',
        subtotal=1000.00,
        tax_rate=10.0,
        tax_amount=100.00,
        discount_amount=50.00,
        total_amount=1050.00,
        amount_paid=0.00,
        balance_due=1050.00,
        notes='Test notes',
        terms='Net 30'
    )
    data = invoice.to_dict()
    assert data['id'] == 1
    assert data['invoice_number'] == 'INV-001'
    assert data['client_id'] == 2
    assert data['project_id'] == 3
    assert data['status'] == Invoice.STATUS_SENT
    assert data['subtotal'] == 1000.00
    assert data['tax_rate'] == 10.0
    assert data['total_amount'] == 1050.00
    assert data['notes'] == 'Test notes'
    assert data['terms'] == 'Net 30'

def test_calculate_totals():
    """Test calculating invoice totals from items"""
    invoice = Invoice(
        invoice_number='INV-001',
        client_id=1,
        issue_date='2023-01-01',
        due_date='2023-01-31',
        subtotal=0.00,
        tax_rate=10.0,
        tax_amount=0.00,
        total_amount=0.00,
        balance_due=0.00
    )
    
    items = [
        {'quantity': 2, 'unit_price': 100.00, 'amount': 200.00, 'taxable': True},
        {'quantity': 1, 'unit_price': 300.00, 'amount': 300.00, 'taxable': True},
        {'quantity': 1, 'unit_price': 100.00, 'amount': 100.00, 'taxable': False}
    ]
    
    invoice.calculate_totals(items)
    assert invoice.subtotal == 600.00
    assert invoice.tax_amount == 50.00  # 10% of taxable amount (500.00)
    assert invoice.total_amount == 650.00
    assert invoice.balance_due == 650.00
    
    # Test with discount
    invoice.discount_amount = 100.00
    invoice.calculate_totals(items)
    assert invoice.subtotal == 600.00
    assert invoice.tax_amount == 50.00
    assert invoice.total_amount == 550.00  # With 100.00 discount
    assert invoice.balance_due == 550.00

def test_is_overdue():
    """Test the is_overdue method"""
    today = datetime.now().date()
    yesterday = (today - timedelta(days=1)).strftime('%Y-%m-%d')
    tomorrow = (today + timedelta(days=1)).strftime('%Y-%m-%d')
    
    # Overdue invoice
    invoice = Invoice(
        invoice_number='INV-001',
        client_id=1,
        status=Invoice.STATUS_SENT,
        issue_date=yesterday,
        due_date=yesterday,
        subtotal=1000.00,
        total_amount=1000.00,
        balance_due=1000.00
    )
    assert invoice.is_overdue() is True
    
    # Future due date
    invoice.due_date = tomorrow
    assert invoice.is_overdue() is False
    
    # Paid invoice should not be overdue
    invoice.due_date = yesterday
    invoice.status = Invoice.STATUS_PAID
    assert invoice.is_overdue() is False

def test_add_payment():
    """Test adding a payment to an invoice"""
    invoice = Invoice(
        id=1,
        invoice_number='INV-001',
        client_id=1,
        status=Invoice.STATUS_SENT,
        issue_date='2023-01-01',
        due_date='2023-01-31',
        subtotal=1000.00,
        total_amount=1000.00,
        amount_paid=0.00,
        balance_due=1000.00
    )
    
    # Add partial payment
    invoice.add_payment(500.00)
    assert invoice.amount_paid == 500.00
    assert invoice.balance_due == 500.00
    assert invoice.status == Invoice.STATUS_PARTIALLY_PAID
    
    # Add another partial payment
    invoice.add_payment(300.00)
    assert invoice.amount_paid == 800.00
    assert invoice.balance_due == 200.00
    assert invoice.status == Invoice.STATUS_PARTIALLY_PAID
    
    # Pay the remaining balance
    invoice.add_payment(200.00)
    assert invoice.amount_paid == 1000.00
    assert invoice.balance_due == 0.00
    assert invoice.status == Invoice.STATUS_PAID
    assert invoice.paid_date is not None
    
    # Test overpayment
    invoice.add_payment(100.00)
    assert invoice.amount_paid == 1100.00
    assert invoice.balance_due == -100.00  # Negative balance due 