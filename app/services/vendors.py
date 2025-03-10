from app.services.supabase import supabase
import uuid
from datetime import datetime

# Mock data for development
MOCK_VENDORS = [
    {
        'id': '1',
        'name': 'ABC Lumber Supply',
        'contact_name': 'John Smith',
        'email': 'john@abclumber.com',
        'phone': '555-123-4567',
        'address': '123 Main St, Anytown, USA',
        'notes': 'Reliable supplier for lumber and building materials'
    },
    {
        'id': '2',
        'name': 'XYZ Electrical',
        'contact_name': 'Jane Doe',
        'email': 'jane@xyzelectrical.com',
        'phone': '555-987-6543',
        'address': '456 Oak Ave, Somewhere, USA',
        'notes': 'Preferred vendor for electrical supplies'
    },
    {
        'id': '3',
        'name': 'Acme Plumbing',
        'contact_name': 'Bob Johnson',
        'email': 'bob@acmeplumbing.com',
        'phone': '555-456-7890',
        'address': '789 Pine Rd, Elsewhere, USA',
        'notes': 'Plumbing supplies and fixtures'
    }
]

# Mock purchase data
MOCK_PURCHASES = [
    {
        'id': '1',
        'vendor_id': '1',
        'project_id': 1,
        'description': 'Lumber for framing',
        'amount': 2500.00,
        'date': '2023-03-01',
        'receipt_url': None
    },
    {
        'id': '2',
        'vendor_id': '1',
        'project_id': 2,
        'description': 'Finishing materials',
        'amount': 1200.00,
        'date': '2023-03-15',
        'receipt_url': None
    },
    {
        'id': '3',
        'vendor_id': '2',
        'project_id': 1,
        'description': 'Electrical components',
        'amount': 1800.00,
        'date': '2023-03-10',
        'receipt_url': None
    },
    {
        'id': '4',
        'vendor_id': '3',
        'project_id': 3,
        'description': 'Plumbing fixtures',
        'amount': 950.00,
        'date': '2023-02-20',
        'receipt_url': None
    }
]

def get_all_vendors():
    """Get all vendors"""
    try:
        if supabase is None:
            print("Using mock vendor data")
            return MOCK_VENDORS
            
        response = supabase.from_("vendors").select("*").execute()
        return response.data
    except Exception as e:
        print(f"Error loading vendors: {e}")
        return MOCK_VENDORS

def get_vendor_by_id(vendor_id):
    """Get a vendor by ID"""
    try:
        if supabase is None:
            print("Using mock vendor data")
            for vendor in MOCK_VENDORS:
                if vendor['id'] == vendor_id:
                    return vendor
            return None
            
        response = supabase.from_("vendors").select("*").eq("id", vendor_id).execute()
        vendors = response.data
        if vendors and len(vendors) > 0:
            return vendors[0]
        return None
    except Exception as e:
        print(f"Error getting vendor by id: {e}")
        for vendor in MOCK_VENDORS:
            if vendor['id'] == vendor_id:
                return vendor
        return None

def create_vendor(vendor_data):
    """Create a new vendor"""
    try:
        if 'id' not in vendor_data:
            vendor_data['id'] = str(uuid.uuid4())
            
        if supabase is None:
            print("Using mock vendor data for creation")
            MOCK_VENDORS.append(vendor_data)
            return vendor_data
            
        response = supabase.from_("vendors").insert(vendor_data).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error creating vendor: {e}")
        # Still try to add to mock data for development
        MOCK_VENDORS.append(vendor_data)
        return vendor_data

def update_vendor(vendor_id, vendor_data):
    """Update a vendor"""
    try:
        if supabase is None:
            print("Using mock vendor data for update")
            for i, vendor in enumerate(MOCK_VENDORS):
                if vendor['id'] == vendor_id:
                    MOCK_VENDORS[i] = {**vendor, **vendor_data}
                    return MOCK_VENDORS[i]
            return None
            
        response = supabase.from_("vendors").update(vendor_data).eq("id", vendor_id).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error updating vendor: {e}")
        for i, vendor in enumerate(MOCK_VENDORS):
            if vendor['id'] == vendor_id:
                MOCK_VENDORS[i] = {**vendor, **vendor_data}
                return MOCK_VENDORS[i]
        return None

def delete_vendor(vendor_id):
    """Delete a vendor"""
    try:
        if supabase is None:
            print("Using mock vendor data for deletion")
            global MOCK_VENDORS
            MOCK_VENDORS = [v for v in MOCK_VENDORS if v['id'] != vendor_id]
            return True
            
        response = supabase.from_("vendors").delete().eq("id", vendor_id).execute()
        return True
    except Exception as e:
        print(f"Error deleting vendor: {e}")
        return False

def get_vendor_purchases(vendor_id):
    """Get purchases for a vendor"""
    try:
        if supabase is None:
            print("Using mock purchase data for vendor")
            return [p for p in MOCK_PURCHASES if p['vendor_id'] == vendor_id]
            
        response = supabase.from_("purchases").select("*").eq("vendor_id", vendor_id).execute()
        return response.data
    except Exception as e:
        print(f"Error getting vendor purchases: {e}")
        return [p for p in MOCK_PURCHASES if p['vendor_id'] == vendor_id]

def add_purchase(purchase_data):
    """Add a purchase record"""
    try:
        if 'id' not in purchase_data:
            purchase_data['id'] = str(uuid.uuid4())
            
        if supabase is None:
            print("Using mock purchase data for creation")
            MOCK_PURCHASES.append(purchase_data)
            return purchase_data
            
        response = supabase.from_("purchases").insert(purchase_data).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error adding purchase: {e}")
        MOCK_PURCHASES.append(purchase_data)
        return purchase_data

def update_purchase(purchase_id, purchase_data):
    """Update a purchase record"""
    try:
        if supabase is None:
            print("Using mock purchase data for update")
            for i, purchase in enumerate(MOCK_PURCHASES):
                if purchase['id'] == purchase_id:
                    MOCK_PURCHASES[i] = {**purchase, **purchase_data}
                    return MOCK_PURCHASES[i]
            return None
            
        response = supabase.from_("purchases").update(purchase_data).eq("id", purchase_id).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error updating purchase: {e}")
        for i, purchase in enumerate(MOCK_PURCHASES):
            if purchase['id'] == purchase_id:
                MOCK_PURCHASES[i] = {**purchase, **purchase_data}
                return MOCK_PURCHASES[i]
        return None

def delete_purchase(purchase_id):
    """Delete a purchase record"""
    try:
        if supabase is None:
            print("Using mock purchase data for deletion")
            global MOCK_PURCHASES
            MOCK_PURCHASES = [p for p in MOCK_PURCHASES if p['id'] != purchase_id]
            return True
            
        response = supabase.from_("purchases").delete().eq("id", purchase_id).execute()
        return True
    except Exception as e:
        print(f"Error deleting purchase: {e}")
        return False 