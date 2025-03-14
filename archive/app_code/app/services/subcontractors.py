from app.services.supabase import supabase
import uuid
from datetime import datetime

# Mock data for development
MOCK_SUBCONTRACTORS = [
    {
        'id': '1',
        'name': 'Elite Electrical',
        'contact_name': 'Mike Johnson',
        'email': 'mike@eliteelectrical.com',
        'phone': '555-123-4567',
        'trade': 'Electrical',
        'rate': 75.00,
        'address': '123 Main St, Anytown, USA',
        'insurance_expiry': '2023-12-31',
        'license': 'EL-12345',
        'notes': 'Reliable electrical contractor'
    },
    {
        'id': '2',
        'name': 'Pro Plumbing',
        'contact_name': 'Sarah Davis',
        'email': 'sarah@proplumbing.com',
        'phone': '555-987-6543',
        'trade': 'Plumbing',
        'rate': 65.00,
        'address': '456 Oak Ave, Somewhere, USA',
        'insurance_expiry': '2023-10-15',
        'license': 'PL-67890',
        'notes': 'Specializes in commercial plumbing'
    },
    {
        'id': '3',
        'name': 'Master HVAC',
        'contact_name': 'Tom Wilson',
        'email': 'tom@masterhvac.com',
        'phone': '555-456-7890',
        'trade': 'HVAC',
        'rate': 70.00,
        'address': '789 Pine Rd, Elsewhere, USA',
        'insurance_expiry': '2023-11-30',
        'license': 'HVAC-54321',
        'notes': 'Commercial and residential HVAC'
    }
]

# Mock subcontractor invoices
MOCK_INVOICES = [
    {
        'id': '1',
        'subcontractor_id': '1',
        'project_id': 1,
        'invoice_number': 'INV-001',
        'amount': 2500.00,
        'date': '2023-03-01',
        'due_date': '2023-03-31',
        'status': 'Paid',
        'description': 'Electrical work for Phase 1'
    },
    {
        'id': '2',
        'subcontractor_id': '1',
        'project_id': 2,
        'invoice_number': 'INV-002',
        'amount': 1800.00,
        'date': '2023-03-15',
        'due_date': '2023-04-15',
        'status': 'Pending',
        'description': 'Wiring and panel installation'
    },
    {
        'id': '3',
        'subcontractor_id': '2',
        'project_id': 1,
        'invoice_number': 'INV-003',
        'amount': 1200.00,
        'date': '2023-02-20',
        'due_date': '2023-03-20',
        'status': 'Paid',
        'description': 'Plumbing rough-in'
    },
    {
        'id': '4',
        'subcontractor_id': '3',
        'project_id': 3,
        'invoice_number': 'INV-004',
        'amount': 3000.00,
        'date': '2023-03-05',
        'due_date': '2023-04-05',
        'status': 'Pending',
        'description': 'HVAC installation'
    }
]

# Mock subcontractor project assignments
MOCK_ASSIGNMENTS = [
    {
        'id': '1',
        'subcontractor_id': '1',
        'project_id': 1,
        'project_name': 'Sample Project 1',
        'status': 'In Progress',
        'created_at': '2023-01-15T08:00:00'
    },
    {
        'id': '2',
        'subcontractor_id': '1',
        'project_id': 2,
        'project_name': 'Sample Project 2',
        'status': 'Planning',
        'created_at': '2023-02-01T09:30:00'
    },
    {
        'id': '3',
        'subcontractor_id': '2',
        'project_id': 1,
        'project_name': 'Sample Project 1',
        'status': 'In Progress',
        'created_at': '2023-01-20T10:15:00'
    },
    {
        'id': '4',
        'subcontractor_id': '3',
        'project_id': 3,
        'project_name': 'Completed Example',
        'status': 'Completed',
        'created_at': '2023-01-10T14:00:00'
    }
]

def get_all_subcontractors():
    """Get all subcontractors"""
    try:
        if supabase:
            response = supabase.from_("subcontractors").select("*").execute()
            return response.data
        else:
            return MOCK_SUBCONTRACTORS
    except Exception as e:
        print(f"Error fetching subcontractors: {str(e)}")
        return MOCK_SUBCONTRACTORS

def get_subcontractor_by_id(subcontractor_id):
    """Get a subcontractor by ID"""
    try:
        if supabase:
            response = supabase.from_("subcontractors").select("*").eq("id", subcontractor_id).execute()
            if response.data:
                return response.data[0]
        else:
            for subcontractor in MOCK_SUBCONTRACTORS:
                if subcontractor['id'] == subcontractor_id:
                    return subcontractor
        return None
    except Exception as e:
        print(f"Error fetching subcontractor {subcontractor_id}: {str(e)}")
        # Still attempt to return from mock data on error
        for subcontractor in MOCK_SUBCONTRACTORS:
            if subcontractor['id'] == subcontractor_id:
                return subcontractor
        return None

def create_subcontractor(subcontractor_data):
    """Create a new subcontractor"""
    try:
        if 'id' not in subcontractor_data:
            subcontractor_data['id'] = str(uuid.uuid4())
            
        if 'created_at' not in subcontractor_data:
            subcontractor_data['created_at'] = datetime.now().isoformat()
            
        if supabase:
            response = supabase.from_("subcontractors").insert(subcontractor_data).execute()
            if response.data:
                return response.data[0]
            return None
        else:
            # Add to mock data
            MOCK_SUBCONTRACTORS.append(subcontractor_data)
            return subcontractor_data
    except Exception as e:
        print(f"Error creating subcontractor: {str(e)}")
        # Still try to add to mock data for development
        MOCK_SUBCONTRACTORS.append(subcontractor_data)
        return subcontractor_data

def update_subcontractor(subcontractor_id, subcontractor_data):
    """Update a subcontractor"""
    try:
        subcontractor_data['updated_at'] = datetime.now().isoformat()
        
        if supabase:
            response = supabase.from_("subcontractors").update(subcontractor_data).eq("id", subcontractor_id).execute()
            if response.data:
                return response.data[0]
            return None
        else:
            # Update in mock data
            for i, subcontractor in enumerate(MOCK_SUBCONTRACTORS):
                if subcontractor['id'] == subcontractor_id:
                    MOCK_SUBCONTRACTORS[i] = {**subcontractor, **subcontractor_data}
                    return MOCK_SUBCONTRACTORS[i]
            return None
    except Exception as e:
        print(f"Error updating subcontractor {subcontractor_id}: {str(e)}")
        # Try to update in mock data anyway
        for i, subcontractor in enumerate(MOCK_SUBCONTRACTORS):
            if subcontractor['id'] == subcontractor_id:
                MOCK_SUBCONTRACTORS[i] = {**subcontractor, **subcontractor_data}
                return MOCK_SUBCONTRACTORS[i]
        return None

def delete_subcontractor(subcontractor_id):
    """Delete a subcontractor"""
    try:
        if supabase:
            supabase.from_("subcontractors").delete().eq("id", subcontractor_id).execute()
        else:
            # Remove from mock data
            global MOCK_SUBCONTRACTORS
            MOCK_SUBCONTRACTORS = [s for s in MOCK_SUBCONTRACTORS if s['id'] != subcontractor_id]
        return True
    except Exception as e:
        print(f"Error deleting subcontractor {subcontractor_id}: {str(e)}")
        return False

def get_subcontractor_invoices(subcontractor_id):
    """Get invoices for a subcontractor"""
    try:
        if supabase:
            response = supabase.from_("subcontractor_invoices").select("*").eq("subcontractor_id", subcontractor_id).execute()
            return response.data
        else:
            return [i for i in MOCK_INVOICES if i['subcontractor_id'] == subcontractor_id]
    except Exception as e:
        print(f"Error fetching invoices for subcontractor {subcontractor_id}: {str(e)}")
        return [i for i in MOCK_INVOICES if i['subcontractor_id'] == subcontractor_id]

def create_invoice(invoice_data):
    """Create a new invoice for a subcontractor"""
    try:
        if 'id' not in invoice_data:
            invoice_data['id'] = str(uuid.uuid4())
            
        if 'created_at' not in invoice_data:
            invoice_data['created_at'] = datetime.now().isoformat()
            
        if supabase:
            response = supabase.from_("subcontractor_invoices").insert(invoice_data).execute()
            if response.data:
                return response.data[0]
            return None
        else:
            # Add to mock data
            MOCK_INVOICES.append(invoice_data)
            return invoice_data
    except Exception as e:
        print(f"Error creating invoice: {str(e)}")
        # Still try to add to mock data
        MOCK_INVOICES.append(invoice_data)
        return invoice_data

def update_invoice(invoice_id, invoice_data):
    """Update an invoice"""
    try:
        invoice_data['updated_at'] = datetime.now().isoformat()
        
        if supabase:
            response = supabase.from_("subcontractor_invoices").update(invoice_data).eq("id", invoice_id).execute()
            if response.data:
                return response.data[0]
            return None
        else:
            # Update in mock data
            for i, invoice in enumerate(MOCK_INVOICES):
                if invoice['id'] == invoice_id:
                    MOCK_INVOICES[i] = {**invoice, **invoice_data}
                    return MOCK_INVOICES[i]
            return None
    except Exception as e:
        print(f"Error updating invoice {invoice_id}: {str(e)}")
        # Try to update in mock data anyway
        for i, invoice in enumerate(MOCK_INVOICES):
            if invoice['id'] == invoice_id:
                MOCK_INVOICES[i] = {**invoice, **invoice_data}
                return MOCK_INVOICES[i]
        return None

def delete_invoice(invoice_id):
    """Delete an invoice"""
    try:
        if supabase:
            supabase.from_("subcontractor_invoices").delete().eq("id", invoice_id).execute()
        else:
            # Remove from mock data
            global MOCK_INVOICES
            MOCK_INVOICES = [i for i in MOCK_INVOICES if i['id'] != invoice_id]
        return True
    except Exception as e:
        print(f"Error deleting invoice {invoice_id}: {str(e)}")
        return False

def get_subcontractor_projects(subcontractor_id):
    """Get projects assigned to a subcontractor"""
    try:
        if supabase:
            response = supabase.from_("subcontractor_projects").select("*, projects(*)").eq("subcontractor_id", subcontractor_id).execute()
            if response.data:
                return [item['projects'] for item in response.data]
            return []
        else:
            return [
                {'id': a['project_id'], 'name': a['project_name'], 'status': a['status']}
                for a in MOCK_ASSIGNMENTS if a['subcontractor_id'] == subcontractor_id
            ]
    except Exception as e:
        print(f"Error fetching projects for subcontractor {subcontractor_id}: {str(e)}")
        return [
            {'id': a['project_id'], 'name': a['project_name'], 'status': a['status']}
            for a in MOCK_ASSIGNMENTS if a['subcontractor_id'] == subcontractor_id
        ]

def add_project_assignment(assignment_data):
    """Add a subcontractor to a project"""
    try:
        if 'id' not in assignment_data:
            assignment_data['id'] = str(uuid.uuid4())
            
        if 'created_at' not in assignment_data:
            assignment_data['created_at'] = datetime.now().isoformat()
            
        if supabase:
            response = supabase.from_("subcontractor_projects").insert(assignment_data).execute()
            if response.data:
                return response.data[0]
            return None
        else:
            # Add to mock data
            global MOCK_ASSIGNMENTS
            MOCK_ASSIGNMENTS.append(assignment_data)
            return assignment_data
    except Exception as e:
        print(f"Error adding project assignment: {str(e)}")
        return None

def remove_project_assignment(subcontractor_id, project_id):
    """Remove a subcontractor from a project"""
    try:
        if supabase:
            supabase.from_("subcontractor_projects").delete().eq("subcontractor_id", subcontractor_id).eq("project_id", project_id).execute()
        else:
            # Remove from mock data
            global MOCK_ASSIGNMENTS
            MOCK_ASSIGNMENTS = [
                a for a in MOCK_ASSIGNMENTS 
                if not (a['subcontractor_id'] == subcontractor_id and a['project_id'] == project_id)
            ]
        return True
    except Exception as e:
        print(f"Error removing project assignment: {str(e)}")
        return False 