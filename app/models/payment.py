from datetime import datetime

class Payment:
    """Represents a payment made against an invoice"""
    
    # Payment method constants
    METHOD_CASH = "Cash"
    METHOD_CHECK = "Check"
    METHOD_CREDIT_CARD = "Credit Card"
    METHOD_BANK_TRANSFER = "Bank Transfer"
    METHOD_PAYPAL = "PayPal"
    METHOD_OTHER = "Other"
    
    def __init__(self, 
                 id=None, 
                 invoice_id=None, 
                 amount=0.0, 
                 payment_date=None, 
                 payment_method=METHOD_CHECK, 
                 reference_number=None, 
                 notes=None, 
                 created_by_id=None, 
                 created_at=None, 
                 updated_at=None):
        """Initialize a new Payment object"""
        self.id = id
        self.invoice_id = invoice_id
        self.amount = float(amount) if amount is not None else 0.0
        
        # Handle payment date - could be a string, date object, or None
        if payment_date is None:
            self.payment_date = datetime.now().date()
        elif isinstance(payment_date, str):
            # Try to parse the string date
            try:
                self.payment_date = datetime.strptime(payment_date, '%Y-%m-%d').date()
            except ValueError:
                self.payment_date = datetime.now().date()
        else:
            self.payment_date = payment_date
        
        self.payment_method = payment_method
        self.reference_number = reference_number
        self.notes = notes
        self.created_by_id = created_by_id
        self.created_at = created_at if created_at else datetime.now()
        self.updated_at = updated_at if updated_at else datetime.now()
    
    @staticmethod
    def from_dict(data):
        """Create a Payment object from a dictionary"""
        if not data:
            return Payment()  # Return an empty Payment object instead of None
        return Payment(
            id=data.get('id'),
            invoice_id=data.get('invoice_id'),
            amount=data.get('amount', 0.0),
            payment_date=data.get('payment_date'),
            payment_method=data.get('payment_method', Payment.METHOD_CHECK),
            reference_number=data.get('reference_number'),
            notes=data.get('notes'),
            created_by_id=data.get('created_by_id'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
    
    def to_dict(self):
        """Convert a Payment object to a dictionary"""
        return {
            'id': self.id,
            'invoice_id': self.invoice_id,
            'amount': self.amount,
            'payment_date': self.payment_date,
            'payment_method': self.payment_method,
            'reference_number': self.reference_number,
            'notes': self.notes,
            'created_by_id': self.created_by_id,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        } 