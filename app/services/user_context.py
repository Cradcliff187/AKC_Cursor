from flask import request, session, g, current_app
import re
from app.services.users import get_user_by_id, USER_ROLES, can_access_role

def get_user_role():
    """Get the role of the current user
    
    Returns:
        str: The role of the current user, defaults to 'field_worker' if not set
    """
    # Get from session if available
    if 'user_role' in session:
        return session['user_role']
    
    # Try to get role from user in session
    if 'user_id' in session:
        user = get_user_by_id(session['user_id'])
        if user and 'role' in user:
            return user['role']
    
    # Default to field worker if no role set
    return 'field_worker'

def get_current_user():
    """Get the current user from session
    
    Returns:
        dict: The current user object, or None if not logged in
    """
    if 'user_id' in session:
        return get_user_by_id(session['user_id'])
    return None

def has_permission(permission):
    """Check if the current user has a specific permission
    
    Args:
        permission (str): The permission to check
        
    Returns:
        bool: True if the user has the permission, False otherwise
    """
    role = get_user_role()
    if role in USER_ROLES:
        return permission in USER_ROLES[role]['permissions']
    return False

def is_mobile_device(user_agent=None):
    """Determine if the request is coming from a mobile device
    
    Args:
        user_agent (str, optional): User agent string to check. If None, gets from request.
        
    Returns:
        bool: True if the request is from a mobile device, False otherwise
    """
    if user_agent is None:
        user_agent = request.headers.get('User-Agent', '').lower()
    
    # Check for common mobile device identifiers
    mobile_patterns = [
        'android', 'iphone', 'ipad', 'ipod', 'blackberry', 'windows phone',
        'mobile', 'tablet', 'opera mini', 'iemobile'
    ]
    
    return any(pattern in user_agent.lower() for pattern in mobile_patterns)

def is_admin_level_user():
    """Check if the current user is an admin or project manager
    
    Returns:
        bool: True if the user is an admin or project manager, False otherwise
    """
    role = get_user_role()
    return can_access_role(role, 'project_manager')

def is_field_level_user():
    """Check if the current user is a field worker or foreman
    
    Returns:
        bool: True if the user is a field worker or foreman, False otherwise
    """
    role = get_user_role()
    return role in ['field_worker', 'foreman']

def get_appropriate_template(template_name):
    """Get the appropriate template path based on user role and device type
    
    Args:
        template_name (str): Base template name without path
        
    Returns:
        str: Complete template path appropriate for the user
    """
    # Check if we're in a mobile context
    is_mobile = getattr(g, 'is_mobile', is_mobile_device())
    user_role = get_user_role()
    
    # First check if a mobile-specific template exists
    if is_mobile:
        mobile_template = f'mobile/{template_name}'
        mobile_role_template = f'mobile/{user_role}/{template_name}'
        
        # Try role-specific mobile template first
        try:
            return mobile_role_template
        except:
            # Then try general mobile template
            try:
                return mobile_template
            except:
                # Fall back to standard template
                pass
    
    # If we're here, use standard template
    return template_name

def render_appropriate_template(template_name, **context):
    """Render the appropriate template based on user role and device type
    
    Args:
        template_name (str): Base template name without path
        **context: Template context variables
        
    Returns:
        Response: Rendered template response
    """
    from flask import render_template
    
    template_path = get_appropriate_template(template_name)
    
    # Add device and role info to context
    context.update({
        'is_mobile': getattr(g, 'is_mobile', is_mobile_device()),
        'user_role': get_user_role(),
        'current_user': get_current_user(),
        'has_permission': has_permission
    })
    
    return render_template(template_path, **context)

def get_user_dashboard_url():
    """Get the appropriate dashboard URL for the current user
    
    Returns:
        str: URL for the user's dashboard
    """
    from flask import url_for
    
    role = get_user_role()
    
    # Role-specific dashboards
    if role == 'admin' or role == 'project_manager':
        return url_for('main.dashboard')
    elif role == 'foreman':
        return url_for('field.dashboard')
    elif role == 'field_worker':
        return url_for('field.dashboard')
    elif role == 'accountant':
        return url_for('reports.accounting')
    else:
        # Default dashboard
        return url_for('main.dashboard')

def can_edit_project(project_id):
    """Check if the current user can edit a specific project
    This is a placeholder for a more sophisticated permission system
    
    Args:
        project_id (str): The project ID to check
        
    Returns:
        bool: True if the user can edit the project, False otherwise
    """
    # In a real system, this would check if the user is assigned to the project
    # or has the necessary role to edit any project
    
    role = get_user_role()
    
    # Admin and project managers can edit any project
    if role in ['admin', 'project_manager']:
        return True
    
    # Foremen can only edit their assigned projects
    if role == 'foreman':
        # Here we would check if the foreman is assigned to this project
        # For now, just return True for simplicity
        return True
    
    # Field workers can't edit projects
    return False

def can_access_client(client_id):
    """Check if the current user can access a specific client
    
    Args:
        client_id (str): The client ID to check
        
    Returns:
        bool: True if the user can access the client, False otherwise
    """
    # In a real system, this would check if the user is associated with the client
    # or has the necessary role to access any client
    
    role = get_user_role()
    
    # Admin and project managers can access any client
    if role in ['admin', 'project_manager', 'accountant']:
        return True
    
    # Other roles typically don't need client access
    return False 