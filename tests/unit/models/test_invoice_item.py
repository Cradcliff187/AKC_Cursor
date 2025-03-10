import pytest
from app.models.invoice_item import InvoiceItem

@pytest.mark.unit
@pytest.mark.models
class TestInvoiceItemModel:
    
    def test_invoice_item_init(self):
        """Test InvoiceItem initialization with default values."""
        item = InvoiceItem()
        assert item.id is None
        assert item.invoice_id is None
        assert item.description is None
        assert item.quantity == 1.0
        assert item.unit_price == 0.0
        assert item.amount == 0.0
        assert item.type == InvoiceItem.TYPE_SERVICE
        assert item.sort_order == 0
        assert item.taxable is True
    
    def test_invoice_item_init_with_values(self):
        """Test InvoiceItem initialization with provided values."""
        item = InvoiceItem(
            id=1,
            invoice_id=2,
            description="Test Item",
            quantity=5.0,
            unit_price=10.0,
            amount=50.0,
            type=InvoiceItem.TYPE_MATERIAL,
            sort_order=1,
            taxable=False
        )
        
        assert item.id == 1
        assert item.invoice_id == 2
        assert item.description == "Test Item"
        assert item.quantity == 5.0
        assert item.unit_price == 10.0
        assert item.amount == 50.0
        assert item.type == InvoiceItem.TYPE_MATERIAL
        assert item.sort_order == 1
        assert item.taxable is False
    
    def test_from_dict(self):
        """Test creating InvoiceItem from dictionary."""
        data = {
            'id': 1,
            'invoice_id': 2,
            'description': 'Test Item',
            'quantity': 5.0,
            'unit_price': 10.0,
            'amount': 50.0,
            'type': InvoiceItem.TYPE_MATERIAL,
            'sort_order': 1,
            'taxable': False
        }
        
        item = InvoiceItem.from_dict(data)
        
        assert item.id == 1
        assert item.invoice_id == 2
        assert item.description == 'Test Item'
        assert item.quantity == 5.0
        assert item.unit_price == 10.0
        assert item.amount == 50.0
        assert item.type == InvoiceItem.TYPE_MATERIAL
        assert item.sort_order == 1
        assert item.taxable is False
    
    def test_to_dict(self):
        """Test converting InvoiceItem to dictionary."""
        item = InvoiceItem(
            id=1,
            invoice_id=2,
            description="Test Item",
            quantity=5.0,
            unit_price=10.0,
            amount=50.0,
            type=InvoiceItem.TYPE_MATERIAL,
            sort_order=1,
            taxable=False
        )
        
        data = item.to_dict()
        
        assert data['id'] == 1
        assert data['invoice_id'] == 2
        assert data['description'] == 'Test Item'
        assert data['quantity'] == 5.0
        assert data['unit_price'] == 10.0
        assert data['amount'] == 50.0
        assert data['type'] == InvoiceItem.TYPE_MATERIAL
        assert data['sort_order'] == 1
        assert data['taxable'] is False
    
    def test_calculate_amount(self):
        """Test calculating item amount from quantity and unit price."""
        # Test with default values
        item1 = InvoiceItem()
        item1.calculate_amount()
        assert item1.amount == 0.0  # 1.0 * 0.0 = 0.0
        
        # Test with custom values
        item2 = InvoiceItem(quantity=5.0, unit_price=10.0)
        item2.calculate_amount()
        assert item2.amount == 50.0  # 5.0 * 10.0 = 50.0
        
        # Test updating values and recalculating
        item3 = InvoiceItem(quantity=2.0, unit_price=20.0)
        item3.calculate_amount()
        assert item3.amount == 40.0  # 2.0 * 20.0 = 40.0
        
        item3.quantity = 3.0
        item3.unit_price = 15.0
        item3.calculate_amount()
        assert item3.amount == 45.0  # 3.0 * 15.0 = 45.0 