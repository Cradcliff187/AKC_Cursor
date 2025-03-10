from supabase import create_client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set a flag for development mode based on environment
DEV_MODE = os.environ.get("FLASK_ENV") == "development"

# Initialize Supabase client
try:
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    
    if not url or not key:
        print("Warning: SUPABASE_URL or SUPABASE_KEY environment variables are not set.")
        # Only use mock data in development mode
        if DEV_MODE:
            print("Using mock data in development mode.")
            supabase = None
        else:
            raise ValueError("Supabase credentials must be provided in production mode")
    else:
        supabase = create_client(url, key)
        print("Supabase client initialized successfully")
except Exception as e:
    print(f"Error initializing Supabase client: {e}")
    if DEV_MODE:
        print("Falling back to mock data in development mode")
        supabase = None
    else:
        # In production, we should raise the error
        raise

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
            if DEV_MODE:
                print("Warning: Using mock data as Supabase is not available")
                return None
            else:
                raise ValueError("Supabase client not initialized")
            
        if params:
            response = supabase.rpc(query, params)
        else:
            response = supabase.rpc(query)
        return response
    except Exception as e:
        print(f"Error executing query: {e}")
        if not DEV_MODE:
            raise
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

# Add more comprehensive Supabase functions

def get_table_data(table_name, columns="*", filters=None, limit=None):
    """Generic function to get data from a Supabase table with optional filters"""
    try:
        if supabase is None and DEV_MODE:
            print(f"Warning: Using mock data for {table_name}")
            # Return appropriate mock data based on table_name
            if table_name == "users":
                return list(MOCK_USERS.values())
            elif table_name == "projects":
                return MOCK_PROJECTS
            return []
            
        query = supabase.from_(table_name).select(columns)
        
        # Apply filters if provided
        if filters:
            for field, value in filters.items():
                query = query.eq(field, value)
        
        # Apply limit if provided
        if limit:
            query = query.limit(limit)
            
        response = query.execute()
        return response.data
    except Exception as e:
        print(f"Error fetching data from {table_name}: {e}")
        if not DEV_MODE:
            raise
        return []

def insert_record(table_name, data):
    """Insert a record into a Supabase table"""
    try:
        if supabase is None and DEV_MODE:
            print(f"Warning: Mock insert into {table_name}")
            return {"id": 999, **data}  # Fake ID for development
            
        response = supabase.from_(table_name).insert(data).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error inserting into {table_name}: {e}")
        if not DEV_MODE:
            raise
        return None

def update_record(table_name, record_id, data, id_field="id"):
    """Update a record in a Supabase table"""
    try:
        if supabase is None and DEV_MODE:
            print(f"Warning: Mock update for {table_name}")
            return {"id": record_id, **data}
            
        response = supabase.from_(table_name).update(data).eq(id_field, record_id).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error updating record in {table_name}: {e}")
        if not DEV_MODE:
            raise
        return None

def delete_record(table_name, record_id, id_field="id"):
    """Delete a record from a Supabase table"""
    try:
        if supabase is None and DEV_MODE:
            print(f"Warning: Mock delete from {table_name}")
            return True
            
        response = supabase.from_(table_name).delete().eq(id_field, record_id).execute()
        return True if response.data else False
    except Exception as e:
        print(f"Error deleting record from {table_name}: {e}")
        if not DEV_MODE:
            raise
        return False

# Storage functions for document management
def upload_file_to_storage(bucket, file_path, file_name, content_type=None):
    """Upload a file to Supabase Storage"""
    try:
        if supabase is None and DEV_MODE:
            print(f"Warning: Mock file upload to {bucket}")
            return {"key": file_name, "status": "mocked"}
            
        with open(file_path, 'rb') as f:
            file_data = f.read()
        
        # Create the bucket if it doesn't exist
        try:
            supabase.storage.get_bucket(bucket)
        except:
            supabase.storage.create_bucket(bucket)
        
        response = supabase.storage.from_(bucket).upload(
            path=file_name,
            file=file_data,
            file_options={"content-type": content_type} if content_type else None
        )
        return response
    except Exception as e:
        print(f"Error uploading file to storage: {e}")
        if not DEV_MODE:
            raise
        return None

def get_file_url(bucket, file_name):
    """Get a public URL for a file in Supabase Storage"""
    try:
        if supabase is None and DEV_MODE:
            print(f"Warning: Mock file URL from {bucket}")
            return f"/mock_storage/{bucket}/{file_name}"
            
        response = supabase.storage.from_(bucket).get_public_url(file_name)
        return response
    except Exception as e:
        print(f"Error getting file URL: {e}")
        if not DEV_MODE:
            raise
        return None 