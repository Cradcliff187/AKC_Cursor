from supabase import create_client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Supabase client
try:
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    
    if not url or not key:
        print("Warning: SUPABASE_URL or SUPABASE_KEY environment variables are not set.")
        # Setting a dummy client for development mode
        supabase = None
    else:
        supabase = create_client(url, key)
except Exception as e:
    print(f"Error initializing Supabase client: {e}")
    # Setting a dummy client for development mode
    supabase = None

# Mock data for development when Supabase is not available
MOCK_USERS = {
    1: {
        'id': 1,
        'email': 'admin@example.com',
        'first_name': 'Admin',
        'last_name': 'User',
        'role': 'admin'
    }
}

MOCK_PROJECTS = [
    {
        'id': 1,
        'name': 'Sample Project 1',
        'description': 'This is a sample project for development.',
        'client': 'Sample Client',
        'status': 'In Progress',
        'start_date': '2023-01-01',
        'end_date': '2023-12-31',
        'budget': 50000.00,
        'budget_spent': 25000.00,
        'location': 'New York',
        'user_id': 1,
        'progress': 50
    },
    {
        'id': 2,
        'name': 'Sample Project 2',
        'description': 'Another sample project for testing.',
        'client': 'Test Client',
        'status': 'Planning',
        'start_date': '2023-02-15',
        'end_date': '2023-11-30',
        'budget': 75000.00,
        'budget_spent': 15000.00,
        'location': 'Los Angeles',
        'user_id': 1,
        'progress': 20
    },
    {
        'id': 3,
        'name': 'Completed Example',
        'description': 'A completed project example.',
        'client': 'Example Corp',
        'status': 'Completed',
        'start_date': '2022-06-01',
        'end_date': '2022-12-31',
        'budget': 100000.00,
        'budget_spent': 98500.00,
        'location': 'Chicago',
        'user_id': 1,
        'progress': 100
    }
]

# General database functions
def execute_query(query, params=None):
    """Execute a raw SQL query against Supabase"""
    try:
        if supabase is None:
            print("Warning: Using mock data as Supabase is not available")
            return None
            
        if params:
            response = supabase.rpc(query, params)
        else:
            response = supabase.rpc(query)
        return response
    except Exception as e:
        print(f"Error executing query: {e}")
        return None

# User functions
def get_user_by_email(email):
    """Get a user by email"""
    try:
        if supabase is None:
            print("Warning: Using mock data as Supabase is not available")
            # Return mock user for development
            for user in MOCK_USERS.values():
                if user['email'] == email:
                    return user
            return None
            
        response = supabase.from_("users").select("*").eq("email", email).execute()
        users = response.data
        if users and len(users) > 0:
            return users[0]
        return None
    except Exception as e:
        print(f"Error getting user by email: {e}")
        return None

def get_user_by_id(user_id):
    """Get a user by ID"""
    try:
        if supabase is None:
            print("Warning: Using mock data as Supabase is not available")
            # Return mock user for development
            return MOCK_USERS.get(user_id)
            
        response = supabase.from_("users").select("*").eq("id", user_id).execute()
        users = response.data
        if users and len(users) > 0:
            return users[0]
        return None
    except Exception as e:
        print(f"Error getting user by id: {e}")
        return None

def create_user(user_data):
    """Create a new user"""
    try:
        if supabase is None:
            print("Warning: Using mock data as Supabase is not available")
            # Simulate creating a user for development
            new_id = max(MOCK_USERS.keys()) + 1 if MOCK_USERS else 1
            MOCK_USERS[new_id] = {**user_data, 'id': new_id}
            return MOCK_USERS[new_id]
            
        response = supabase.from_("users").insert(user_data).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error creating user: {e}")
        return None

def update_user(user_id, user_data):
    """Update a user"""
    try:
        if supabase is None:
            print("Warning: Using mock data as Supabase is not available")
            # Simulate updating a user for development
            if user_id in MOCK_USERS:
                MOCK_USERS[user_id] = {**MOCK_USERS[user_id], **user_data}
                return MOCK_USERS[user_id]
            return None
            
        response = supabase.from_("users").update(user_data).eq("id", user_id).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error updating user: {e}")
        return None

# Basic auth functions
def authenticate_user(email, password):
    """Authenticate a user"""
    try:
        if supabase is None:
            print("Warning: Using mock data as Supabase is not available")
            # In development mode, allow any login
            for user in MOCK_USERS.values():
                if user['email'] == email:
                    return {'user': user}
            return None
            
        response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        return response
    except Exception as e:
        print(f"Error authenticating user: {e}")
        return None

# Project functions with mock data fallback
def get_projects_by_user(user_id):
    """Get all projects for a user"""
    try:
        if supabase is None:
            print("Warning: Using mock data as Supabase is not available")
            # Return mock projects for development
            return [p for p in MOCK_PROJECTS if p['user_id'] == user_id]
            
        response = supabase.from_("projects").select("*").eq("user_id", user_id).execute()
        return response.data
    except Exception as e:
        print(f"Error getting projects by user: {e}")
        # Return mock data as fallback
        return [p for p in MOCK_PROJECTS if p['user_id'] == user_id] 