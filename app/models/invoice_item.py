from datetime import datetime

class InvoiceItem:
    """Represents a line item in an invoice"""
    
    # Item type constants
    TYPE_SERVICE = "Service"
    TYPE_PRODUCT = "Product"
    TYPE_LABOR = "Labor"
    TYPE_MATERIAL = "Material"
    TYPE_EQUIPMENT = "Equipment"
    TYPE_OTHER = "Other"
    
    def __init__(self, 
                 id=None, 
                 invoice_id=None, 
                 description=None, 
                 quantity=1.0, 
                 unit_price=0.0, 
                 amount=0.0, 
                 type=TYPE_SERVICE, 
                 sort_order=0, 
                 taxable=True, 
                 created_at=None, 
                 updated_at=None):
        """Initialize a new InvoiceItem object"""
        self.id = id
        self.invoice_id = invoice_id
        self.description = description
        self.quantity = float(quantity) if quantity is not None else 1.0
        self.unit_price = float(unit_price) if unit_price is not None else 0.0
        self.amount = float(amount) if amount is not None else 0.0
        self.type = type if type else self.TYPE_SERVICE
        self.sort_order = int(sort_order) if sort_order is not None else 0
        self.taxable = bool(taxable)
        self.created_at = created_at if created_at else datetime.now()
        self.updated_at = updated_at if updated_at else datetime.now()
        
        # Calculate amount if not provided
        if self.amount == 0.0 and self.quantity and self.unit_price:
            self.calculate_amount()
    
    @staticmethod
    def from_dict(data):
        """Create an InvoiceItem object from a dictionary"""
        if not data:
            return None
        return InvoiceItem(
            id=data.get('id'),
            invoice_id=data.get('invoice_id'),
            description=data.get('description'),
            quantity=data.get('quantity'),
            unit_price=data.get('unit_price'),
            amount=data.get('amount'),
            type=data.get('type'),
            sort_order=data.get('sort_order'),
            taxable=data.get('taxable'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
    
    def to_dict(self):
        """Convert an InvoiceItem object to a dictionary"""
        return {
            'id': self.id,
            'invoice_id': self.invoice_id,
            'description': self.description,
            'quantity': self.quantity,
            'unit_price': self.unit_price,
            'amount': self.amount,
            'type': self.type,
            'sort_order': self.sort_order,
            'taxable': self.taxable,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    def calculate_amount(self):
        """Calculate the amount based on quantity and unit price"""
        self.amount = round(self.quantity * self.unit_price, 2)
        self.updated_at = datetime.now()
        return self.amount 