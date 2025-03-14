from app.services.supabase import supabase
import uuid
from datetime import datetime
from app.services.utils import generate_id

# User roles with their display names, permission levels, and specific permissions
USER_ROLES = {
    'admin': {
        'display': 'Administrator', 
        'level': 100,
        'permissions': [
            'view_all_projects',
            'create_projects',
            'update_projects',
            'create_tasks',
            'assign_tasks',
            'view_all_time',
            'view_reports',
            'manage_clients',
            'manage_vendors',
            'manage_budget',
            'manage_users',
            'manage_settings'
        ],
        'default_landing': 'admin_dashboard'
    },
    'project_manager': {
        'display': 'Project Manager', 
        'level': 80,
        'permissions': [
            'view_all_projects',
            'create_projects',
            'update_projects',
            'create_tasks',
            'assign_tasks',
            'view_all_time',
            'view_reports',
            'manage_clients',
            'manage_vendors',
            'manage_budget'
        ],
        'default_landing': 'admin_dashboard'
    },
    'foreman': {
        'display': 'Foreman', 
        'level': 60,
        'permissions': [
            'view_assigned_projects',
            'update_task_status',
            'log_time',
            'upload_photos',
            'view_materials',
            'view_documents',
            'assign_tasks',
            'view_worker_time',
            'request_materials'
        ],
        'default_landing': 'foreman_dashboard'
    },
    'field_worker': {
        'display': 'Field Worker', 
        'level': 40,
        'permissions': [
            'view_assigned_projects',
            'update_task_status',
            'log_time',
            'upload_photos',
            'view_materials',
            'view_documents'
        ],
        'default_landing': 'field_dashboard'
    },
    'accountant': {
        'display': 'Accountant', 
        'level': 40,
        'permissions': [
            'view_all_projects',
            'view_reports',
            'manage_budget',
            'view_invoices',
            'manage_payments'
        ],
        'default_landing': 'accounting_dashboard'
    },
    'client': {
        'display': 'Client', 
        'level': 20,
        'permissions': [
            'view_own_projects',
            'view_own_invoices',
            'view_own_documents'
        ],
        'default_landing': 'client_dashboard'
    }
}

# Mock data for users
MOCK_USERS = [
    {
        'id': 'admin',
        'username': 'admin',
        'email': 'admin@example.com',
        'first_name': 'Admin',
        'last_name': 'User',
        'role': 'admin',
        'phone': '555-123-4567',
        'created_at': '2023-01-01T00:00:00',
        'active': True
    },
    {
        'id': 'pm',
        'username': 'pm',
        'email': 'pm@example.com',
        'first_name': 'Project',
        'last_name': 'Manager',
        'role': 'project_manager',
        'phone': '555-234-5678',
        'created_at': '2023-01-02T00:00:00',
        'active': True
    },
    {
        'id': 'foreman',
        'username': 'foreman',
        'email': 'foreman@example.com',
        'first_name': 'Foreman',
        'last_name': 'User',
        'role': 'foreman',
        'phone': '555-345-6789',
        'created_at': '2023-01-03T00:00:00',
        'active': True
    },
    {
        'id': 'worker1',
        'username': 'worker1',
        'email': 'worker1@example.com',
        'first_name': 'Field',
        'last_name': 'Worker',
        'role': 'field_worker',
        'phone': '555-456-7890',
        'created_at': '2023-01-04T00:00:00',
        'active': True
    },
    {
        'id': 'accountant',
        'username': 'accountant',
        'email': 'accountant@example.com',
        'first_name': 'Account',
        'last_name': 'Manager',
        'role': 'accountant',
        'phone': '555-567-8901',
        'created_at': '2023-01-05T00:00:00',
        'active': True
    }
]

def get_all_users():
    """Get all users"""
    try:
        if supabase is not None:
            response = supabase.from_("user_profiles") \
                .select("*, auth.users!inner(email)") \
                .execute()
            if response.data:
                # Restructure to include email at top level
                for user in response.data:
                    user['email'] = user['users']['email']
                    del user['users']
            return response.data
        else:
            return MOCK_USERS
    except Exception as e:
        print(f"Error fetching users: {str(e)}")
        return MOCK_USERS

def get_user_by_id(user_id):
    """Get a single user by ID"""
    try:
        if supabase is not None:
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
        else:
            for user in MOCK_USERS:
                if user['id'] == user_id:
                    return user
        return None
    except Exception as e:
        print(f"Error fetching user {user_id}: {str(e)}")
        # Fall back to mock data
        for user in MOCK_USERS:
            if user['id'] == user_id:
                return user
        return None

def get_users_by_role(role):
    """Get all users with a specific role"""
    try:
        if supabase is not None:
            response = supabase.from_("user_profiles") \
                .select("*, auth.users!inner(email)") \
                .eq("role", role) \
                .execute()
            if response.data:
                # Restructure to include email at top level
                for user in response.data:
                    user['email'] = user['users']['email']
                    del user['users']
            return response.data
        else:
            return [user for user in MOCK_USERS if user['role'] == role]
    except Exception as e:
        print(f"Error fetching users with role {role}: {str(e)}")
        return [user for user in MOCK_USERS if user['role'] == role]

def get_user_by_email(email):
    """Get a user by their email address"""
    try:
        if supabase is not None:
            response = supabase.from_("user_profiles") \
                .select("*, auth.users!inner(email)") \
                .eq("auth.users.email", email) \
                .single() \
                .execute()
            if response.data:
                # Restructure to include email at top level
                user_data = response.data
                user_data['email'] = user_data['users']['email']
                del user_data['users']
                return user_data
        else:
            for user in MOCK_USERS:
                if user['email'] == email:
                    return user
        return None
    except Exception as e:
        print(f"Error fetching user with email {email}: {str(e)}")
        # Fall back to mock data
        for user in MOCK_USERS:
            if user['email'] == email:
                return user
        return None

def get_user_by_username(username):
    """Get a user by their username"""
    try:
        if supabase is not None:
            response = supabase.from_("user_profiles") \
                .select("*, auth.users!inner(email)") \
                .eq("username", username) \
                .single() \
                .execute()
            if response.data:
                # Restructure to include email at top level
                user_data = response.data
                user_data['email'] = user_data['users']['email']
                del user_data['users']
                return user_data
        else:
            for user in MOCK_USERS:
                if user['username'] == username:
                    return user
        return None
    except Exception as e:
        print(f"Error fetching user with username {username}: {str(e)}")
        # Fall back to mock data
        for user in MOCK_USERS:
            if user['username'] == username:
                return user
        return None

def create_user(user_data):
    """Create a new user"""
    try:
        # Note: User creation should be handled through Supabase Auth
        # This function should only update the user_profiles table
        if 'id' not in user_data:
            raise ValueError("User ID is required for creating a user profile")
            
        profile_data = {
            'id': user_data['id'],
            'username': user_data.get('username'),
            'first_name': user_data.get('first_name'),
            'last_name': user_data.get('last_name'),
            'role': user_data.get('role', 'employee')
        }
            
        if supabase is None:
            # Add to mock data
            MOCK_USERS.append(user_data)
            return user_data
        else:
            # Add to supabase
            response = supabase.from_("user_profiles").insert(profile_data).execute()
            if response.data:
                user_profile = response.data[0]
                # Add email from the original user_data
                user_profile['email'] = user_data.get('email')
                return user_profile
            return None
    except Exception as e:
        print(f"Error creating user: {str(e)}")
        return None

def update_user(user_id, user_data):
    """Update a user"""
    try:
        if supabase is None:
            # Update in mock data
            for i, user in enumerate(MOCK_USERS):
                if user['id'] == user_id:
                    MOCK_USERS[i] = {**user, **user_data}
                    return MOCK_USERS[i]
            return None
        else:
            # Update in supabase
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
        print(f"Error updating user {user_id}: {str(e)}")
        return None

def deactivate_user(user_id):
    """Deactivate a user (instead of deleting)"""
    return update_user(user_id, {'active': False})

def can_access_role(user_role, required_role):
    """Check if a user with the given role can access resources requiring the specified role"""
    if user_role not in USER_ROLES or required_role not in USER_ROLES:
        return False
        
    # Higher role level means more privileges
    return USER_ROLES[user_role]['level'] >= USER_ROLES[required_role]['level']

def get_role_display(role):
    """Get the display name for a role"""
    if role in USER_ROLES:
        return USER_ROLES[role]['display']
    return role.capitalize()

def get_active_users():
    """Get all active users"""
    try:
        if supabase is not None:
            response = supabase.from_("user_profiles") \
                .select("*, auth.users!inner(email)") \
                .execute()
            if response.data:
                # Restructure to include email at top level
                for user in response.data:
                    user['email'] = user['users']['email']
                    del user['users']
            return response.data
        else:
            return [user for user in MOCK_USERS if user.get('active', True)]
    except Exception as e:
        print(f"Error fetching active users: {str(e)}")
        return [user for user in MOCK_USERS if user.get('active', True)]

def authenticate_user(username, password):
    """
    Mock authentication function - in real implementation this would verify credentials
    In production, Google Workspace authentication would replace this
    """
    # For development/testing only - always returns the user with matching username
    user = get_user_by_username(username)
    return user

def get_user_projects(user_id):
    """Get projects associated with a user"""
    # This would typically query a project_users join table or similar
    # For mock purposes, just return an empty list
    return []

def has_permission(user_id, permission):
    """Check if a user has a specific permission"""
    user = get_user_by_id(user_id)
    if not user or 'role' not in user:
        return False
        
    role = user['role']
    if role not in USER_ROLES:
        return False
        
    return permission in USER_ROLES[role]['permissions']

def get_user_permissions(user_id):
    """Get all permissions for a user"""
    user = get_user_by_id(user_id)
    if not user or 'role' not in user:
        return []
        
    role = user['role']
    if role not in USER_ROLES:
        return []
        
    return USER_ROLES[role]['permissions'] 