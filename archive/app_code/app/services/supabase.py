from supabase import create_client, Client
import os
from dotenv import load_dotenv
from werkzeug.security import check_password_hash, generate_password_hash
import asyncio
import psycopg2
from psycopg2.pool import SimpleConnectionPool
import atexit
import json
import base64
from datetime import datetime, timezone
import jwt
import logging
from functools import wraps
from typing import Dict, List, Any, Optional, Union, Callable

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("supabase_service")

# Load environment variables
load_dotenv()

# Get environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://olfbvahswnkpxlnhbwds.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
FLASK_ENV = os.getenv("FLASK_ENV", "development")

# OAuth credentials
OAUTH_CLIENT_ID = os.getenv("SUPABASE_OAUTH_CLIENT_ID", "800e45d6-b9c2-4ebe-837d-851dff4b4301")
OAUTH_CLIENT_SECRET = os.getenv("SUPABASE_OAUTH_CLIENT_SECRET", "sba_26c506df32fde22cac8fcea895c8bf012bf86f0b")

# Database connection settings
DB_PASSWORD = os.getenv("SUPABASE_DB_PASSWORD", "q1lPZ3saArCiZHeB")  # Updated default to match .env
POSTGRES_CONNECTION_STRING = os.getenv("POSTGRES_CONNECTION_STRING", 
    f"postgresql://postgres.olfbvahswnkpxlnhbwds:{DB_PASSWORD}@aws-0-us-west-1.pooler.supabase.com:6543/postgres")

# Set a flag for development mode based on environment
DEV_MODE = FLASK_ENV == "development"

# Connection pool for direct database access
db_pool = None

# Global Supabase clients
_supabase_client = None
_supabase_admin_client = None

def get_supabase_client() -> Client:
    """Get or create a Supabase client with anonymous key"""
    global _supabase_client
    if _supabase_client is None:
        if not SUPABASE_URL or not SUPABASE_KEY:
            logger.error("Supabase URL or key not set")
            raise ValueError("Supabase URL or key not set")
        _supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _supabase_client

def get_supabase_admin_client() -> Client:
    """Get or create a Supabase client with service role key for admin operations"""
    global _supabase_admin_client
    if _supabase_admin_client is None:
        if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
            logger.error("Supabase URL or service role key not set")
            raise ValueError("Supabase URL or service role key not set")
        _supabase_admin_client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
    return _supabase_admin_client

def validate_jwt_token(token):
    """Validate JWT token structure and expiration"""
    try:
        # Split the token
        parts = token.split('.')
        if len(parts) != 3:
            logger.warning("Invalid JWT format: Token does not have three parts")
            return False

        # Decode the payload
        try:
            payload = jwt.decode(token, options={"verify_signature": False})
            
            # Check expiration
            exp = payload.get('exp')
            if exp:
                now = datetime.now(timezone.utc).timestamp()
                if now > exp:
                    logger.warning("Token has expired")
                    return False
                
            logger.debug("JWT validation successful")
            logger.debug(f"Token expires at: {datetime.fromtimestamp(exp).strftime('%Y-%m-%d %H:%M:%S')}")
            return True
            
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {str(e)}")
            return False
            
    except Exception as e:
        logger.error(f"Error validating JWT: {str(e)}")
        return False

def init_db_pool():
    """Initialize the database connection pool"""
    global db_pool
    try:
        if db_pool is None and not DEV_MODE:
            db_pool = SimpleConnectionPool(
                minconn=1,
                maxconn=10,
                dsn=POSTGRES_CONNECTION_STRING
            )
            # Register cleanup function
            atexit.register(cleanup_db_pool)
            logger.info("Database connection pool initialized")
    except Exception as e:
        logger.error(f"Error initializing database pool: {str(e)}")
        raise

def cleanup_db_pool():
    """Clean up the database connection pool"""
    global db_pool
    if db_pool:
        db_pool.closeall()
        logger.info("Database connection pool closed")

def get_db_connection():
    """Get a connection from the pool"""
    global db_pool
    if db_pool is None:
        init_db_pool()
    return db_pool.getconn()

def release_db_connection(conn):
    """Release a connection back to the pool"""
    global db_pool
    if db_pool:
        db_pool.putconn(conn)

# Decorator for database operations
def with_db_connection(func):
    """Decorator to handle database connections"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        conn = None
        try:
            conn = get_db_connection()
            return func(conn, *args, **kwargs)
        except Exception as e:
            logger.error(f"Database error in {func.__name__}: {str(e)}")
            raise
        finally:
            if conn:
                release_db_connection(conn)
    return wrapper

# Authentication functions
def sign_up(email: str, password: str, user_data: Dict[str, Any] = None) -> Dict[str, Any]:
    """Sign up a new user with Supabase Auth"""
    try:
        supabase = get_supabase_client()
        
        # Register user with Supabase Auth
        auth_response = supabase.auth.sign_up({
            "email": email,
            "password": password
        })
        
        if auth_response.user and user_data:
            # Create user profile in the database
            user_id = auth_response.user.id
            
            # Add the user ID to the user data
            user_data["id"] = user_id
            
            # Insert into user_profiles table
            profile_response = supabase.table("user_profiles").insert(user_data).execute()
            
            if hasattr(profile_response, "error") and profile_response.error:
                logger.error(f"Error creating user profile: {profile_response.error}")
                # Consider rolling back the auth user here
        
        return auth_response
    except Exception as e:
        logger.error(f"Error in sign_up: {str(e)}")
        raise

def sign_in(email: str, password: str) -> Dict[str, Any]:
    """Sign in a user with Supabase Auth"""
    try:
        supabase = get_supabase_client()
        auth_response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        return auth_response
    except Exception as e:
        logger.error(f"Error in sign_in: {str(e)}")
        raise

def sign_out(access_token: str) -> bool:
    """Sign out a user with Supabase Auth"""
    try:
        supabase = get_supabase_client()
        # Set the auth token for the client
        supabase.auth.set_session(access_token)
        # Sign out
        supabase.auth.sign_out()
        return True
    except Exception as e:
        logger.error(f"Error in sign_out: {str(e)}")
        return False

# Generic CRUD operations
def create_record(table: str, data: Dict[str, Any], access_token: Optional[str] = None) -> Dict[str, Any]:
    """Create a record in the specified table"""
    try:
        supabase = get_supabase_client()
        
        # Set auth token if provided
        if access_token:
            supabase.auth.set_session(access_token)
            
        response = supabase.table(table).insert(data).execute()
        
        if hasattr(response, "error") and response.error:
            logger.error(f"Error creating record in {table}: {response.error}")
            raise Exception(f"Error creating record: {response.error}")
            
        return response.data[0] if response.data else {}
    except Exception as e:
        logger.error(f"Error in create_record for table {table}: {str(e)}")
        raise

def get_record(table: str, id: Union[str, int], access_token: Optional[str] = None) -> Dict[str, Any]:
    """Get a record by ID from the specified table"""
    try:
        supabase = get_supabase_client()
        
        # Set auth token if provided
        if access_token:
            supabase.auth.set_session(access_token)
            
        response = supabase.table(table).select("*").eq("id", id).execute()
        
        if hasattr(response, "error") and response.error:
            logger.error(f"Error getting record from {table}: {response.error}")
            raise Exception(f"Error getting record: {response.error}")
            
        return response.data[0] if response.data else None
    except Exception as e:
        logger.error(f"Error in get_record for table {table}: {str(e)}")
        raise

def update_record(table: str, id: Union[str, int], data: Dict[str, Any], access_token: Optional[str] = None) -> Dict[str, Any]:
    """Update a record in the specified table"""
    try:
        supabase = get_supabase_client()
        
        # Set auth token if provided
        if access_token:
            supabase.auth.set_session(access_token)
            
        response = supabase.table(table).update(data).eq("id", id).execute()
        
        if hasattr(response, "error") and response.error:
            logger.error(f"Error updating record in {table}: {response.error}")
            raise Exception(f"Error updating record: {response.error}")
            
        return response.data[0] if response.data else {}
    except Exception as e:
        logger.error(f"Error in update_record for table {table}: {str(e)}")
        raise

def delete_record(table: str, id: Union[str, int], access_token: Optional[str] = None) -> bool:
    """Delete a record from the specified table"""
    try:
        supabase = get_supabase_client()
        
        # Set auth token if provided
        if access_token:
            supabase.auth.set_session(access_token)
            
        response = supabase.table(table).delete().eq("id", id).execute()
        
        if hasattr(response, "error") and response.error:
            logger.error(f"Error deleting record from {table}: {response.error}")
            raise Exception(f"Error deleting record: {response.error}")
            
        return True
    except Exception as e:
        logger.error(f"Error in delete_record for table {table}: {str(e)}")
        raise

def query_records(table: str, query_func: Callable, access_token: Optional[str] = None) -> List[Dict[str, Any]]:
    """Query records from the specified table using a custom query function"""
    try:
        supabase = get_supabase_client()
        
        # Set auth token if provided
        if access_token:
            supabase.auth.set_session(access_token)
            
        # Start with the table query
        query = supabase.table(table)
        
        # Apply the custom query function
        query = query_func(query)
        
        # Execute the query
        response = query.execute()
        
        if hasattr(response, "error") and response.error:
            logger.error(f"Error querying records from {table}: {response.error}")
            raise Exception(f"Error querying records: {response.error}")
            
        return response.data
    except Exception as e:
        logger.error(f"Error in query_records for table {table}: {str(e)}")
        raise

# Initialize on module load
if not DEV_MODE:
    init_db_pool()

# Debug information
if DEV_MODE:
    logger.info("\n=== Supabase Configuration Debug ===")
    logger.info(f"FLASK_ENV: {FLASK_ENV}")
    logger.info(f"SUPABASE_URL: {SUPABASE_URL}")
    logger.info(f"SUPABASE_KEY present: {SUPABASE_KEY is not None}")

    if SUPABASE_KEY:
        logger.info("\nValidating SUPABASE_KEY (anon key):")
        is_valid = validate_jwt_token(SUPABASE_KEY)
        logger.info(f"SUPABASE_KEY validation result: {'Valid' if is_valid else 'Invalid'}")

    if SUPABASE_SERVICE_ROLE_KEY:
        logger.info("\nValidating SUPABASE_SERVICE_ROLE_KEY:")
        is_valid = validate_jwt_token(SUPABASE_SERVICE_ROLE_KEY)
        logger.info(f"SUPABASE_SERVICE_ROLE_KEY validation result: {'Valid' if is_valid else 'Invalid'}")

    logger.info("=== End Supabase Configuration ===\n")

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

# Update execute_query to use the connection pool for direct database access when needed
def execute_query(query, params=None, use_pool=False):
    """Execute a raw SQL query against Supabase or direct database connection"""
    try:
        if use_pool and not DEV_MODE:
            conn = get_db_connection()
            if conn:
                try:
                    with conn.cursor() as cur:
                        cur.execute(query, params)
                        if cur.description:  # If the query returns data
                            result = cur.fetchall()
                            return {"data": result}
                        return {"success": True}
                finally:
                    release_db_connection(conn)
        
        # Fall back to Supabase client if not using pool or in dev mode
        supabase = get_supabase_client()
        if supabase is None:
            if DEV_MODE:
                logger.warning("Warning: Using mock data as Supabase is not available")
                return None
            else:
                raise ValueError("Supabase client not initialized")
            
        if params:
            response = supabase.rpc(query, params)
        else:
            response = supabase.rpc(query)
        return response
    except Exception as e:
        logger.error(f"Error executing query: {e}")
        if not DEV_MODE:
            raise
        return None

# User functions
def get_user_by_email(email):
    """Get user by email from database."""
    try:
        supabase = get_supabase_client()
        if supabase is None:
            logger.warning("Warning: Using mock data as Supabase is not available")
            # Return mock user for development
            for user in MOCK_USERS.values():
                if user.get('email') == email:
                    return user
            return None
            
        # Query user_profiles and join with auth.users to get email
        response = supabase.from_("user_profiles") \
            .select("*, auth.users!inner(email)") \
            .eq("auth.users.email", email) \
            .single() \
            .execute()
            
        if response.data:
            # Restructure the response to include email at the top level
            user_data = response.data
            user_data['email'] = user_data['users']['email']
            del user_data['users']
            return user_data
        return None
    except Exception as e:
        logger.error(f"Error getting user by email: {e}")
        return None

def get_user_by_id(user_id):
    """Get a user by ID"""
    try:
        supabase = get_supabase_client()
        if supabase is None:
            logger.warning("Warning: Using mock data as Supabase is not available")
            # Return mock user for development
            for user in MOCK_USERS.values():
                if user.get('id') == user_id:
                    return user
            return None
            
        response = supabase.from_("user_profiles") \
            .select("*, auth.users!inner(email)") \
            .eq("id", user_id) \
            .single() \
            .execute()
            
        if response.data:
            # Restructure to include email at top level
            user_data = response.data
            user_data['email'] = user_data['users']['email']
            del user_data['users']
            return user_data
        return None
    except Exception as e:
        logger.error(f"Error getting user by ID: {e}")
        return None

def create_user(user_data):
    """Create a new user"""
    try:
        supabase = get_supabase_client()
        if supabase is None:
            logger.warning("Warning: Using mock data as Supabase is not available")
            # Simulate creating a user for development
            new_id = max(MOCK_USERS.keys()) + 1 if MOCK_USERS else 1
            MOCK_USERS[new_id] = {**user_data, 'id': new_id}
            return MOCK_USERS[new_id]
            
        # First create the auth user
        auth_response = supabase.auth.sign_up({
            "email": user_data["email"],
            "password": user_data["password"]
        })
        
        if not auth_response.user:
            raise Exception("Failed to create auth user")
            
        # The trigger will automatically create the user in public.users table
        return get_user_by_id(auth_response.user.id)
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        return None

def update_user(user_id, user_data):
    """Update a user's profile"""
    try:
        supabase = get_supabase_client()
        if supabase is None:
            logger.warning("Warning: Using mock data as Supabase is not available")
            return user_data
            
        # Only update fields that belong in user_profiles
        profile_data = {
            k: v for k, v in user_data.items()
            if k in ['username', 'first_name', 'last_name', 'role']
        }
        
        if profile_data:
            response = supabase.from_("user_profiles") \
                .update(profile_data) \
                .eq("id", user_id) \
                .single() \
                .execute()
                
            if response.data:
                # Get the updated user with email
                return get_user_by_id(user_id)
        return None
    except Exception as e:
        logger.error(f"Error updating user: {e}")
        return None

# Basic auth functions
def authenticate_user(email, password):
    """Authenticate a user with email and password."""
    try:
        supabase = get_supabase_client()
        if supabase is None:
            logger.warning("Warning: Using mock data as Supabase is not available")
            # Return mock user for development
            user = get_user_by_email(email)
            if user and check_password_hash(user['password'], password):
                return user
            return None
            
        # Use Supabase auth to sign in
        auth_response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        if not auth_response.user:
            return None
            
        # Get the user data from our public.users table
        return get_user_by_id(auth_response.user.id)
    except Exception as e:
        logger.error(f"Error authenticating user: {e}")
        return None

# Project functions with mock data fallback
def get_projects_by_user(user_id):
    """Get all projects for a user"""
    try:
        supabase = get_supabase_client()
        if supabase is None:
            logger.warning("Warning: Using mock data as Supabase is not available")
            # Return mock projects for development
            return [p for p in MOCK_PROJECTS if p['user_id'] == user_id]
            
        response = supabase.from_("projects").select("*").eq("user_id", user_id).execute()
        return response.data
    except Exception as e:
        logger.error(f"Error getting projects by user: {e}")
        # Return mock data as fallback
        return [p for p in MOCK_PROJECTS if p['user_id'] == user_id]

# Add more comprehensive Supabase functions

def get_table_data(table_name, columns="*", filters=None, limit=None):
    """Generic function to get data from a Supabase table with optional filters"""
    try:
        supabase = get_supabase_client()
        if supabase is None and DEV_MODE:
            logger.warning(f"Warning: Using mock data for {table_name}")
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
        logger.error(f"Error fetching data from {table_name}: {e}")
        if not DEV_MODE:
            raise
        return []

# Storage functions for document management
def upload_file_to_storage(bucket, file_path, file_name, content_type=None):
    """Upload a file to Supabase Storage"""
    try:
        supabase = get_supabase_client()
        if supabase is None and DEV_MODE:
            logger.warning(f"Warning: Mock file upload to {bucket}")
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
        logger.error(f"Error uploading file to storage: {e}")
        if not DEV_MODE:
            raise
        return None

def get_file_url(bucket, file_name):
    """Get a public URL for a file in Supabase Storage"""
    try:
        supabase = get_supabase_client()
        if supabase is None and DEV_MODE:
            logger.warning(f"Warning: Mock file URL from {bucket}")
            return f"/mock_storage/{bucket}/{file_name}"
            
        response = supabase.storage.from_(bucket).get_public_url(file_name)
        return response
    except Exception as e:
        logger.error(f"Error getting file URL: {e}")
        if not DEV_MODE:
            raise
        return None 