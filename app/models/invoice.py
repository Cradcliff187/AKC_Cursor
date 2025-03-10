from datetime import datetime, timedelta

class Invoice:
    """Represents a client invoice in the system"""
    
    # Invoice status constants
    STATUS_DRAFT = "Draft"
    STATUS_SENT = "Sent"
    STATUS_VIEWED = "Viewed"
    STATUS_PARTIAL = "Partially Paid"
    STATUS_PAID = "Paid"
    STATUS_OVERDUE = "Overdue"
    STATUS_CANCELLED = "Cancelled"
    
    def __init__(self, 
                 id=None, 
                 invoice_number=None, 
                 client_id=None, 
                 project_id=None, 
                 status=STATUS_DRAFT, 
                 issue_date=None, 
                 due_date=None, 
                 subtotal=0.0, 
                 tax_rate=0.0, 
                 tax_amount=0.0, 
                 discount_amount=0.0, 
                 total_amount=0.0, 
                 amount_paid=0.0, 
                 balance_due=0.0, 
                 notes=None, 
                 terms=None, 
                 footer=None, 
                 payment_instructions=None, 
                 sent_date=None, 
                 paid_date=None, 
                 last_reminder_date=None, 
                 created_by_id=None, 
                 created_at=None, 
                 updated_at=None):
        """Initialize a new Invoice object"""
        self.id = id
        self.invoice_number = invoice_number
        self.client_id = client_id
        self.project_id = project_id
        self.status = status
        self.issue_date = issue_date if issue_date else datetime.now().date()
        
        # Set due date to 30 days after issue date by default
        if due_date:
            self.due_date = due_date
        elif issue_date:
            self.due_date = datetime.strptime(issue_date, '%Y-%m-%d').date() + timedelta(days=30) if isinstance(issue_date, str) else issue_date + timedelta(days=30)
        else:
            self.due_date = datetime.now().date() + timedelta(days=30)
            
        self.subtotal = float(subtotal) if subtotal is not None else 0.0
        self.tax_rate = float(tax_rate) if tax_rate is not None else 0.0
        self.tax_amount = float(tax_amount) if tax_amount is not None else 0.0
        self.discount_amount = float(discount_amount) if discount_amount is not None else 0.0
        self.total_amount = float(total_amount) if total_amount is not None else 0.0
        self.amount_paid = float(amount_paid) if amount_paid is not None else 0.0
        self.balance_due = float(balance_due) if balance_due is not None else 0.0
        self.notes = notes
        self.terms = terms
        self.footer = footer
        self.payment_instructions = payment_instructions
        self.sent_date = sent_date
        self.paid_date = paid_date
        self.last_reminder_date = last_reminder_date
        self.created_by_id = created_by_id
        self.created_at = created_at if created_at else datetime.now()
        self.updated_at = updated_at if updated_at else datetime.now()
    
    @staticmethod
    def from_dict(data):
        """Create an Invoice object from a dictionary"""
        if not data:
            return None
        return Invoice(
            id=data.get('id'),
            invoice_number=data.get('invoice_number'),
            client_id=data.get('client_id'),
            project_id=data.get('project_id'),
            status=data.get('status'),
            issue_date=data.get('issue_date'),
            due_date=data.get('due_date'),
            subtotal=data.get('subtotal'),
            tax_rate=data.get('tax_rate'),
            tax_amount=data.get('tax_amount'),
            discount_amount=data.get('discount_amount'),
            total_amount=data.get('total_amount'),
            amount_paid=data.get('amount_paid'),
            balance_due=data.get('balance_due'),
            notes=data.get('notes'),
            terms=data.get('terms'),
            footer=data.get('footer'),
            payment_instructions=data.get('payment_instructions'),
            sent_date=data.get('sent_date'),
            paid_date=data.get('paid_date'),
            last_reminder_date=data.get('last_reminder_date'),
            created_by_id=data.get('created_by_id'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
    
    def to_dict(self):
        """Convert an Invoice object to a dictionary"""
        return {
            'id': self.id,
            'invoice_number': self.invoice_number,
            'client_id': self.client_id,
            'project_id': self.project_id,
            'status': self.status,
            'issue_date': self.issue_date,
            'due_date': self.due_date,
            'subtotal': self.subtotal,
            'tax_rate': self.tax_rate,
            'tax_amount': self.tax_amount,
            'discount_amount': self.discount_amount,
            'total_amount': self.total_amount,
            'amount_paid': self.amount_paid,
            'balance_due': self.balance_due,
            'notes': self.notes,
            'terms': self.terms,
            'footer': self.footer,
            'payment_instructions': self.payment_instructions,
            'sent_date': self.sent_date,
            'paid_date': self.paid_date,
            'last_reminder_date': self.last_reminder_date,
            'created_by_id': self.created_by_id,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    def calculate_totals(self, items=None):
        """Calculate invoice totals based on items"""
        # If items are provided, use them to calculate subtotal
        if items:
            self.subtotal = sum(item.amount for item in items)
        
        # Calculate tax
        self.tax_amount = self.subtotal * (self.tax_rate / 100) if self.tax_rate else 0.0
        
        # Calculate total
        self.total_amount = self.subtotal + self.tax_amount - self.discount_amount
        
        # Calculate balance due
        self.balance_due = self.total_amount - self.amount_paid
        
        # Update status based on payment status
        self._update_status_from_payment()
        
        return self
    
    def _update_status_from_payment(self):
        """Update invoice status based on payment amount"""
        # Don't change status if it's draft or cancelled
        if self.status in [self.STATUS_DRAFT, self.STATUS_CANCELLED]:
            return
        
        # If fully paid
        if self.balance_due <= 0:
            self.status = self.STATUS_PAID
            if not self.paid_date:
                self.paid_date = datetime.now().date()
        # If partially paid
        elif self.amount_paid > 0:
            self.status = self.STATUS_PARTIAL
        # If not paid and overdue
        elif self.due_date and datetime.now().date() > self.due_date:
            self.status = self.STATUS_OVERDUE
        # Otherwise, it's just sent or viewed
        elif self.status not in [self.STATUS_SENT, self.STATUS_VIEWED]:
            self.status = self.STATUS_SENT
    
    def is_overdue(self):
        """Check if the invoice is overdue"""
        if not self.due_date:
            return False
        
        if isinstance(self.due_date, str):
            due_date = datetime.strptime(self.due_date, '%Y-%m-%d').date()
        else:
            due_date = self.due_date
            
        return datetime.now().date() > due_date and self.balance_due > 0
    
    def days_overdue(self):
        """Get the number of days this invoice is overdue"""
        if not self.is_overdue():
            return 0
            
        if isinstance(self.due_date, str):
            due_date = datetime.strptime(self.due_date, '%Y-%m-%d').date()
        else:
            due_date = self.due_date
            
        return (datetime.now().date() - due_date).days
    
    def days_until_due(self):
        """Get the number of days until this invoice is due"""
        if self.is_overdue():
            return 0
            
        if isinstance(self.due_date, str):
            due_date = datetime.strptime(self.due_date, '%Y-%m-%d').date()
        else:
            due_date = self.due_date
            
        return (due_date - datetime.now().date()).days
    
    def add_payment(self, amount, payment_date=None):
        """Add a payment to this invoice"""
        if amount <= 0:
            return False
        
        self.amount_paid += amount
        self.balance_due = self.total_amount - self.amount_paid
        
        # Update status based on new payment
        self._update_status_from_payment()
        
        self.updated_at = datetime.now()
        return True 