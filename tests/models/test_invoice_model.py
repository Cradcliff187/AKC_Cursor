import pytest
from datetime import datetime, timedelta
from app.models.invoice import Invoice
from app.models.invoice_item import InvoiceItem

@pytest.mark.unit
@pytest.mark.models
class TestInvoiceModel:
    
    def test_invoice_init(self):
        """Test Invoice initialization with default values."""
        invoice = Invoice()
        assert invoice.id is None
        assert invoice.status == Invoice.STATUS_DRAFT
        assert invoice.subtotal == 0.0
        assert invoice.tax_rate == 0.0
        assert invoice.tax_amount == 0.0
        assert invoice.total_amount == 0.0
        assert invoice.amount_paid == 0.0
        assert invoice.balance_due == 0.0
    
    def test_invoice_init_with_values(self):
        """Test Invoice initialization with provided values."""
        invoice_date = datetime.now().date()
        due_date = invoice_date + timedelta(days=30)
        
        invoice = Invoice(
            id=1,
            invoice_number="INV-001",
            client_id=2,
            project_id=3,
            status=Invoice.STATUS_SENT,
            issue_date=invoice_date,
            due_date=due_date,
            subtotal=1000.0,
            tax_rate=10.0,
            tax_amount=100.0,
            discount_amount=50.0,
            total_amount=1050.0,
            amount_paid=0.0,
            balance_due=1050.0,
            notes="Test notes",
            terms="Test terms",
            footer="Test footer",
            payment_instructions="Test payment instructions"
        )
        
        assert invoice.id == 1
        assert invoice.invoice_number == "INV-001"
        assert invoice.client_id == 2
        assert invoice.project_id == 3
        assert invoice.status == Invoice.STATUS_SENT
        assert invoice.issue_date == invoice_date
        assert invoice.due_date == due_date
        assert invoice.subtotal == 1000.0
        assert invoice.tax_rate == 10.0
        assert invoice.tax_amount == 100.0
        assert invoice.discount_amount == 50.0
        assert invoice.total_amount == 1050.0
        assert invoice.amount_paid == 0.0
        assert invoice.balance_due == 1050.0
        assert invoice.notes == "Test notes"
        assert invoice.terms == "Test terms"
        assert invoice.footer == "Test footer"
        assert invoice.payment_instructions == "Test payment instructions"
    
    def test_from_dict(self):
        """Test creating Invoice from dictionary."""
        today = datetime.now().date()
        due_date = today + timedelta(days=30)
        
        data = {
            'id': 1,
            'invoice_number': 'INV-001',
            'client_id': 2,
            'project_id': 3,
            'status': Invoice.STATUS_DRAFT,
            'issue_date': today.isoformat(),
            'due_date': due_date.isoformat(),
            'subtotal': 1000.0,
            'tax_rate': 10.0,
            'tax_amount': 100.0,
            'discount_amount': 50.0,
            'total_amount': 1050.0,
            'amount_paid': 0.0,
            'balance_due': 1050.0,
            'notes': 'Test notes',
            'terms': 'Test terms',
            'footer': 'Test footer',
            'payment_instructions': 'Test payment instructions'
        }
        
        invoice = Invoice.from_dict(data)
        
        assert invoice.id == 1
        assert invoice.invoice_number == 'INV-001'
        assert invoice.client_id == 2
        assert invoice.project_id == 3
        assert invoice.status == Invoice.STATUS_DRAFT
        assert invoice.issue_date.isoformat() == today.isoformat()
        assert invoice.due_date.isoformat() == due_date.isoformat()
        assert invoice.subtotal == 1000.0
        assert invoice.tax_rate == 10.0
        assert invoice.tax_amount == 100.0
        assert invoice.discount_amount == 50.0
        assert invoice.total_amount == 1050.0
        assert invoice.amount_paid == 0.0
        assert invoice.balance_due == 1050.0
        assert invoice.notes == 'Test notes'
        assert invoice.terms == 'Test terms'
        assert invoice.footer == 'Test footer'
        assert invoice.payment_instructions == 'Test payment instructions'
    
    def test_to_dict(self):
        """Test converting Invoice to dictionary."""
        today = datetime.now().date()
        due_date = today + timedelta(days=30)
        
        invoice = Invoice(
            id=1,
            invoice_number="INV-001",
            client_id=2,
            project_id=3,
            status=Invoice.STATUS_DRAFT,
            issue_date=today,
            due_date=due_date,
            subtotal=1000.0,
            tax_rate=10.0,
            tax_amount=100.0,
            discount_amount=50.0,
            total_amount=1050.0,
            amount_paid=0.0,
            balance_due=1050.0,
            notes="Test notes",
            terms="Test terms",
            footer="Test footer",
            payment_instructions="Test payment instructions"
        )
        
        data = invoice.to_dict()
        
        assert data['id'] == 1
        assert data['invoice_number'] == 'INV-001'
        assert data['client_id'] == 2
        assert data['project_id'] == 3
        assert data['status'] == Invoice.STATUS_DRAFT
        assert data['issue_date'] == today.isoformat()
        assert data['due_date'] == due_date.isoformat()
        assert data['subtotal'] == 1000.0
        assert data['tax_rate'] == 10.0
        assert data['tax_amount'] == 100.0
        assert data['discount_amount'] == 50.0
        assert data['total_amount'] == 1050.0
        assert data['amount_paid'] == 0.0
        assert data['balance_due'] == 1050.0
        assert data['notes'] == 'Test notes'
        assert data['terms'] == 'Test terms'
        assert data['footer'] == 'Test footer'
        assert data['payment_instructions'] == 'Test payment instructions'
    
    def test_calculate_totals(self):
        """Test calculating invoice totals from items."""
        invoice = Invoice(tax_rate=10.0)
        
        items = [
            InvoiceItem(quantity=2, unit_price=100.0, taxable=True),   # 200.00 taxable
            InvoiceItem(quantity=1, unit_price=300.0, taxable=True),   # 300.00 taxable
            InvoiceItem(quantity=5, unit_price=50.0, taxable=False)    # 250.00 non-taxable
        ]
        
        # Calculate amounts for each item
        for item in items:
            item.calculate_amount()
        
        # Calculate invoice totals
        invoice.calculate_totals(items)
        
        # Expected values
        expected_subtotal = 750.0  # 200 + 300 + 250
        expected_taxable_amount = 500.0  # 200 + 300
        expected_tax_amount = 50.0  # 10% of 500
        expected_total = 800.0  # 750 + 50
        
        assert invoice.subtotal == expected_subtotal
        assert invoice.tax_amount == expected_tax_amount
        assert invoice.total_amount == expected_total
        assert invoice.balance_due == expected_total  # No payments
    
    def test_is_overdue(self):
        """Test detecting overdue invoices."""
        # Past due date
        past_invoice = Invoice(
            status=Invoice.STATUS_SENT,
            due_date=datetime.now().date() - timedelta(days=5)
        )
        assert past_invoice.is_overdue() is True
        
        # Future due date
        future_invoice = Invoice(
            status=Invoice.STATUS_SENT,
            due_date=datetime.now().date() + timedelta(days=5)
        )
        assert future_invoice.is_overdue() is False
        
        # Paid invoice (should not be overdue regardless of date)
        paid_invoice = Invoice(
            status=Invoice.STATUS_PAID,
            due_date=datetime.now().date() - timedelta(days=5),
            total_amount=1000.0,
            amount_paid=1000.0,
            balance_due=0.0
        )
        assert paid_invoice.is_overdue() is False
        
        # Draft invoice (should not be overdue)
        draft_invoice = Invoice(
            status=Invoice.STATUS_DRAFT,
            due_date=datetime.now().date() - timedelta(days=5)
        )
        assert draft_invoice.is_overdue() is False
    
    def test_days_overdue(self):
        """Test calculating days overdue."""
        days = 5
        invoice = Invoice(
            status=Invoice.STATUS_SENT,
            due_date=datetime.now().date() - timedelta(days=days)
        )
        
        assert invoice.days_overdue() == days
        
        # Future due date should return 0
        future_invoice = Invoice(
            status=Invoice.STATUS_SENT,
            due_date=datetime.now().date() + timedelta(days=5)
        )
        assert future_invoice.days_overdue() == 0
    
    def test_days_until_due(self):
        """Test calculating days until due."""
        days = 5
        invoice = Invoice(
            status=Invoice.STATUS_SENT,
            due_date=datetime.now().date() + timedelta(days=days)
        )
        
        assert invoice.days_until_due() == days
        
        # Past due date should return 0
        past_invoice = Invoice(
            status=Invoice.STATUS_SENT,
            due_date=datetime.now().date() - timedelta(days=5)
        )
        assert past_invoice.days_until_due() == 0
    
    def test_add_payment(self):
        """Test adding a payment to an invoice."""
        invoice = Invoice(
            status=Invoice.STATUS_SENT,
            total_amount=1000.0,
            amount_paid=0.0,
            balance_due=1000.0
        )
        
        # Add partial payment
        payment_date = datetime.now().date()
        invoice.add_payment(500.0, payment_date)
        
        assert invoice.amount_paid == 500.0
        assert invoice.balance_due == 500.0
        assert invoice.status == Invoice.STATUS_PARTIAL  # Partially paid
        
        # Add another payment to fully pay
        invoice.add_payment(500.0, payment_date)
        
        assert invoice.amount_paid == 1000.0
        assert invoice.balance_due == 0.0
        assert invoice.status == Invoice.STATUS_PAID  # Fully paid
        assert invoice.paid_date == payment_date
    
    def test_update_status_from_payment(self):
        """Test updating status based on payment."""
        invoice = Invoice(
            status=Invoice.STATUS_SENT,
            total_amount=1000.0,
            amount_paid=0.0,
            balance_due=1000.0
        )
        
        # No payment
        invoice._update_status_from_payment()
        assert invoice.status == Invoice.STATUS_SENT
        
        # Partial payment
        invoice.amount_paid = 500.0
        invoice.balance_due = 500.0
        invoice._update_status_from_payment()
        assert invoice.status == Invoice.STATUS_PARTIAL
        
        # Full payment
        invoice.amount_paid = 1000.0
        invoice.balance_due = 0.0
        invoice._update_status_from_payment()
        assert invoice.status == Invoice.STATUS_PAID
        
        # Overpayment (edge case)
        invoice.amount_paid = 1100.0
        invoice.balance_due = -100.0
        invoice._update_status_from_payment()
        assert invoice.status == Invoice.STATUS_PAID 