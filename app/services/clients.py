from app.services.supabase import supabase
import uuid
from datetime import datetime

# Mock data for development
MOCK_CLIENTS = [
    {
        'id': '1',
        'name': 'Acme Corporation',
        'contact_name': 'John Smith',
        'email': 'john@acmecorp.com',
        'phone': '555-123-4567',
        'address': '123 Main St, Anytown, USA',
        'notes': 'Commercial client for office renovations'
    },
    {
        'id': '2',
        'name': 'Johnson Family',
        'contact_name': 'Sarah Johnson',
        'email': 'sarah@example.com',
        'phone': '555-987-6543',
        'address': '456 Oak Ave, Somewhere, USA',
        'notes': 'Residential client for home remodeling'
    },
    {
        'id': '3',
        'name': 'City Government',
        'contact_name': 'Mayor Williams',
        'email': 'mayor@citygovt.gov',
        'phone': '555-456-7890',
        'address': '789 Government Rd, Cityville, USA',
        'notes': 'Municipal client for public works project'
    }
]

def get_all_clients():
    """Get all clients"""
    try:
        if supabase is None:
            print("Using mock client data")
            return MOCK_CLIENTS
            
        response = supabase.from_("clients").select("*").execute()
        return response.data
    except Exception as e:
        print(f"Error loading clients: {e}")
        return MOCK_CLIENTS

def get_client_by_id(client_id):
    """Get a client by ID"""
    try:
        if supabase is None:
            print("Using mock client data")
            for client in MOCK_CLIENTS:
                if client['id'] == client_id:
                    return client
            return None
            
        response = supabase.from_("clients").select("*").eq("id", client_id).execute()
        clients = response.data
        if clients and len(clients) > 0:
            return clients[0]
        return None
    except Exception as e:
        print(f"Error getting client by id: {e}")
        for client in MOCK_CLIENTS:
            if client['id'] == client_id:
                return client
        return None

def create_client(client_data):
    """Create a new client"""
    try:
        if 'id' not in client_data:
            client_data['id'] = str(uuid.uuid4())
            
        if supabase is None:
            print("Using mock client data for creation")
            MOCK_CLIENTS.append(client_data)
            return client_data
            
        response = supabase.from_("clients").insert(client_data).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error creating client: {e}")
        # Still try to add to mock data for development
        MOCK_CLIENTS.append(client_data)
        return client_data

def update_client(client_id, client_data):
    """Update a client"""
    try:
        if supabase is None:
            print("Using mock client data for update")
            for i, client in enumerate(MOCK_CLIENTS):
                if client['id'] == client_id:
                    MOCK_CLIENTS[i] = {**client, **client_data}
                    return MOCK_CLIENTS[i]
            return None
            
        response = supabase.from_("clients").update(client_data).eq("id", client_id).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error updating client: {e}")
        for i, client in enumerate(MOCK_CLIENTS):
            if client['id'] == client_id:
                MOCK_CLIENTS[i] = {**client, **client_data}
                return MOCK_CLIENTS[i]
        return None

def delete_client(client_id):
    """Delete a client"""
    try:
        if supabase is None:
            print("Using mock client data for deletion")
            global MOCK_CLIENTS
            MOCK_CLIENTS = [c for c in MOCK_CLIENTS if c['id'] != client_id]
            return True
            
        response = supabase.from_("clients").delete().eq("id", client_id).execute()
        return True
    except Exception as e:
        print(f"Error deleting client: {e}")
        return False

def get_client_projects(client_id):
    """Get projects for a client"""
    try:
        if supabase is None:
            print("Using mock project data for client")
            # Mock projects for this client
            return [
                {
                    'id': 1,
                    'name': 'Office Renovation',
                    'description': 'Complete renovation of the main office space',
                    'client': 'Acme Corporation',
                    'status': 'In Progress',
                    'start_date': '2023-02-15',
                    'end_date': '2023-06-30',
                    'budget': 150000.00,
                    'budget_spent': 75000.00,
                    'location': 'Downtown',
                    'progress': 50
                }
            ]
            
        client = get_client_by_id(client_id)
        if not client:
            return []
            
        response = supabase.from_("projects").select("*").eq("client", client['name']).execute()
        return response.data
    except Exception as e:
        print(f"Error getting client projects: {e}")
        return [] 