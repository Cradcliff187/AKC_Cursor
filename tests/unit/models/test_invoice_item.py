"""
Unit tests for the InvoiceItem model
"""
import pytest
from app.models.invoice_item import InvoiceItem

@pytest.mark.unit
@pytest.mark.models
class TestInvoiceItemModel:
    
    def test_invoice_item_init(self):
        """Test InvoiceItem initialization with various parameters"""
        # Test with minimal required params
        item = InvoiceItem(
            invoice_id=1,
            description='Test item',
            quantity=1,
            unit_price=100.00,
            amount=100.00
        )
        assert item.invoice_id == 1
        assert item.description == 'Test item'
        assert item.quantity == 1
        assert item.unit_price == 100.00
        assert item.amount == 100.00
        assert item.type == InvoiceItem.TYPE_SERVICE  # Default type
        assert item.taxable is True  # Default taxable
        
        # Test with all params
        item = InvoiceItem(
            id=1,
            invoice_id=2,
            description='Complete item',
            quantity=2,
            unit_price=150.00,
            amount=300.00,
            type=InvoiceItem.TYPE_PRODUCT,
            sort_order=1,
            taxable=False,
            created_at='2023-01-01 10:00:00',
            updated_at='2023-01-01 10:00:00'
        )
        assert item.id == 1
        assert item.invoice_id == 2
        assert item.description == 'Complete item'
        assert item.quantity == 2
        assert item.unit_price == 150.00
        assert item.amount == 300.00
        assert item.type == InvoiceItem.TYPE_PRODUCT
        assert item.sort_order == 1
        assert item.taxable is False

    def test_from_dict(self):
        """Test creating an InvoiceItem from a dictionary"""
        data = {
            'id': 1,
            'invoice_id': 2,
            'description': 'Test item',
            'quantity': 2,
            'unit_price': 150.00,
            'amount': 300.00,
            'type': 'product',
            'sort_order': 1,
            'taxable': False
        }
        item = InvoiceItem.from_dict(data)
        assert item.id == 1
        assert item.invoice_id == 2
        assert item.description == 'Test item'
        assert item.quantity == 2
        assert item.unit_price == 150.00
        assert item.amount == 300.00
        assert item.type == 'product'
        assert item.sort_order == 1
        assert item.taxable is False
        
        # Test with minimal data
        minimal_data = {
            'invoice_id': 3,
            'description': 'Minimal item',
            'quantity': 1,
            'unit_price': 100.00,
            'amount': 100.00
        }
        item = InvoiceItem.from_dict(minimal_data)
        assert item.invoice_id == 3
        assert item.description == 'Minimal item'
        assert item.quantity == 1
        assert item.unit_price == 100.00
        assert item.amount == 100.00
        assert item.type == InvoiceItem.TYPE_SERVICE  # Default type
        assert item.taxable is True  # Default taxable
        
        # Test with empty data
        item = InvoiceItem.from_dict({})
        assert item.invoice_id is None
        assert item.description is None
        assert item.quantity == 1.0  # Default quantity
        assert item.unit_price == 0.0  # Default unit price
        assert item.amount == 0.0  # Default amount
        assert item.type == InvoiceItem.TYPE_SERVICE  # Default type
        assert item.taxable is True  # Default taxable

    def test_to_dict(self):
        """Test converting an InvoiceItem to a dictionary"""
        item = InvoiceItem(
            id=1,
            invoice_id=2,
            description='Test item',
            quantity=2,
            unit_price=150.00,
            amount=300.00,
            type=InvoiceItem.TYPE_PRODUCT,
            sort_order=1,
            taxable=False
        )
        data = item.to_dict()
        assert data['id'] == 1
        assert data['invoice_id'] == 2
        assert data['description'] == 'Test item'
        assert data['quantity'] == 2
        assert data['unit_price'] == 150.00
        assert data['amount'] == 300.00
        assert data['type'] == InvoiceItem.TYPE_PRODUCT
        assert data['sort_order'] == 1
        assert data['taxable'] is False

    def test_calculate_amount(self):
        """Test calculating item amount based on quantity and unit price"""
        item = InvoiceItem(
            invoice_id=1,
            description='Test item',
            quantity=2,
            unit_price=150.00,
            amount=0.00  # Initialize with 0
        )
        
        # Calculate the amount
        item.calculate_amount()
        assert item.amount == 300.00
        
        # Test with updated quantity
        item.quantity = 3
        item.calculate_amount()
        assert item.amount == 450.00
        
        # Test with updated unit price
        item.unit_price = 200.00
        item.calculate_amount()
        assert item.amount == 600.00
        
        # Test with zero quantity
        item.quantity = 0
        item.calculate_amount()
        assert item.amount == 0.00
        
        # Test with None values (should handle gracefully)
        item.quantity = None
        item.unit_price = 100.00
        item.calculate_amount()
        assert item.amount == 0.00
        
        item.quantity = 1
        item.unit_price = None
        item.calculate_amount()
        assert item.amount == 0.00 