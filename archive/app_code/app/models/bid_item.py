from datetime import datetime

class BidItem:
    """Represents a line item in a bid or proposal"""
    
    def __init__(self, id=None, bid_id=None, item_type="Labor", category=None, 
                 description=None, quantity=1, unit="Hours", unit_cost=0.0,
                 total_cost=0.0, markup_percentage=0.0, markup_amount=0.0,
                 total_price=0.0, notes=None, sort_order=0, created_at=None, updated_at=None):
        """Initialize a new BidItem object"""
        self.id = id
        self.bid_id = bid_id
        self.item_type = item_type
        self.category = category
        self.description = description
        self.quantity = float(quantity) if quantity is not None else 1
        self.unit = unit if unit else "Hours"
        self.unit_cost = float(unit_cost) if unit_cost is not None else 0.0
        self.total_cost = float(total_cost) if total_cost is not None else 0.0
        self.markup_percentage = float(markup_percentage) if markup_percentage is not None else 0.0
        self.markup_amount = float(markup_amount) if markup_amount is not None else 0.0
        self.total_price = float(total_price) if total_price is not None else 0.0
        self.notes = notes
        self.sort_order = int(sort_order) if sort_order is not None else 0
        self.created_at = created_at if created_at else datetime.now()
        self.updated_at = updated_at if updated_at else datetime.now()
    
    @staticmethod
    def from_dict(data):
        """Create a BidItem object from a dictionary"""
        return BidItem(
            id=data.get('id'),
            bid_id=data.get('bid_id'),
            item_type=data.get('item_type'),
            category=data.get('category'),
            description=data.get('description'),
            quantity=data.get('quantity'),
            unit=data.get('unit'),
            unit_cost=data.get('unit_cost'),
            total_cost=data.get('total_cost'),
            markup_percentage=data.get('markup_percentage'),
            markup_amount=data.get('markup_amount'),
            total_price=data.get('total_price'),
            notes=data.get('notes'),
            sort_order=data.get('sort_order'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
    
    def to_dict(self):
        """Convert BidItem object to a dictionary"""
        return {
            'id': self.id,
            'bid_id': self.bid_id,
            'item_type': self.item_type,
            'category': self.category,
            'description': self.description,
            'quantity': self.quantity,
            'unit': self.unit,
            'unit_cost': self.unit_cost,
            'total_cost': self.total_cost,
            'markup_percentage': self.markup_percentage,
            'markup_amount': self.markup_amount,
            'total_price': self.total_price,
            'notes': self.notes,
            'sort_order': self.sort_order,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    def calculate_totals(self):
        """Calculate the total cost, markup amount, and total price based on quantity, unit cost, and markup percentage"""
        self.total_cost = self.quantity * self.unit_cost
        self.markup_amount = self.total_cost * (self.markup_percentage / 100)
        self.total_price = self.total_cost + self.markup_amount
        return self 