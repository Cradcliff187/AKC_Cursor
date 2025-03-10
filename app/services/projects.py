from app.services.supabase import supabase, MOCK_PROJECTS
from app.services.utils import generate_project_id
from datetime import datetime

# Project status values from the JSON guide
PROJECT_STATUSES = {
    'PENDING': 'Initial state when project is created',
    'APPROVED': 'Project is approved but work hasn\'t started',
    'IN_PROGRESS': 'Work is actively being done',
    'COMPLETED': 'Work is finished',
    'CANCELED': 'Project was canceled'
}

# Status transition rules
PROJECT_STATUS_TRANSITIONS = {
    'PENDING': ['APPROVED', 'CANCELED'],
    'APPROVED': ['IN_PROGRESS', 'CANCELED'],
    'IN_PROGRESS': ['COMPLETED', 'CANCELED'],
    'COMPLETED': ['CLOSED'],
    'CANCELED': [],
    'CLOSED': []
}

# For backward compatibility with existing code
PROJECT_STATUS_MAPPING = {
    'pending': 'PENDING',
    'planning': 'APPROVED',
    'in progress': 'IN_PROGRESS',
    'completed': 'COMPLETED',
    'canceled': 'CANCELED',
    'closed': 'CLOSED',
    # Also handle variations with capitalization
    'Pending': 'PENDING',
    'Planning': 'APPROVED',
    'In Progress': 'IN_PROGRESS',
    'Completed': 'COMPLETED',
    'Canceled': 'CANCELED',
    'Closed': 'CLOSED'
}

# Project functions
def get_all_projects():
    """Get all projects"""
    try:
        if supabase is None:
            print("Using mock projects data")
            return MOCK_PROJECTS
            
        response = supabase.from_("projects").select("*").execute()
        return response.data
    except Exception as e:
        print(f"Error getting all projects: {e}")
        return MOCK_PROJECTS  # Fall back to mock data on error

def get_project_by_id(project_id):
    """Get a project by ID"""
    try:
        if supabase is None:
            print("Using mock project data")
            for project in MOCK_PROJECTS:
                if project['id'] == project_id:
                    return project
            return None
            
        response = supabase.from_("projects").select("*").eq("id", project_id).execute()
        projects = response.data
        if projects and len(projects) > 0:
            return projects[0]
        return None
    except Exception as e:
        print(f"Error getting project by id: {e}")
        # Try to return mock project if exists
        for project in MOCK_PROJECTS:
            if project['id'] == project_id:
                return project
        return None

def create_project(project_data):
    """Create a new project"""
    try:
        # Map status to standard format if needed
        if 'status' in project_data and project_data['status'] in PROJECT_STATUS_MAPPING:
            project_data['status'] = PROJECT_STATUS_MAPPING[project_data['status']]
        
        # Default status if not provided
        if 'status' not in project_data:
            project_data['status'] = 'PENDING'
            
        # Generate project ID
        project_id = generate_project_id()
        
        if supabase is None:
            print("Using mock project data for creation")
            # Create a new project with the generated ID
            new_project = {
                'id': project_id,
                'name': project_data.get('name', 'New Project'),
                'description': project_data.get('description', ''),
                'client': project_data.get('client', ''),
                'client_id': project_data.get('client_id'),
                'status': project_data.get('status', 'PENDING'),
                'location': project_data.get('location', ''),
                'start_date': project_data.get('start_date'),
                'end_date': project_data.get('end_date'),
                'budget': float(project_data.get('budget', 0)),
                'budget_spent': float(project_data.get('budget_spent', 0)),
                'progress': float(project_data.get('progress', 0)),
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            MOCK_PROJECTS.append(new_project)
            return new_project
            
        response = supabase.from_("projects").insert(project_data).execute()
        if response.data:
            return response.data[0]
        return None
    except Exception as e:
        print(f"Error creating project: {e}")
        return None

def update_project(project_id, project_data):
    """Update a project"""
    try:
        # Map status to standard format if needed
        if 'status' in project_data and project_data['status'] in PROJECT_STATUS_MAPPING:
            project_data['status'] = PROJECT_STATUS_MAPPING[project_data['status']]
        
        # Get current project
        current_project = get_project_by_id(project_id)
        if not current_project:
            return None
            
        # Validate status transition if status is changing
        if ('status' in project_data and 
            project_data['status'] != current_project.get('status') and
            not is_valid_status_transition(current_project.get('status'), project_data['status'])):
            print(f"Invalid status transition: {current_project.get('status')} -> {project_data['status']}")
            return None
        
        # Set updated timestamp
        project_data['updated_at'] = datetime.now().isoformat()
            
        if supabase is None:
            print("Using mock project data for update")
            # Find and update the project
            for i, proj in enumerate(MOCK_PROJECTS):
                if str(proj['id']) == str(project_id):
                    # Update fields
                    for key, value in project_data.items():
                        MOCK_PROJECTS[i][key] = value
                    return MOCK_PROJECTS[i]
            return None
            
        response = supabase.from_("projects").update(project_data).eq("id", project_id).execute()
        if response.data:
            return response.data[0]
        return None
    except Exception as e:
        print(f"Error updating project: {e}")
        return None

def is_valid_status_transition(current_status, new_status):
    """Check if a status transition is valid
    
    Args:
        current_status: Current status
        new_status: New status
        
    Returns:
        bool: True if the transition is valid, False otherwise
    """
    # Map statuses to standard format if needed
    if current_status in PROJECT_STATUS_MAPPING:
        current_status = PROJECT_STATUS_MAPPING[current_status]
    if new_status in PROJECT_STATUS_MAPPING:
        new_status = PROJECT_STATUS_MAPPING[new_status]
    
    # If current and new status are the same, it's valid
    if current_status == new_status:
        return True
        
    # Check if the transition is allowed
    if current_status in PROJECT_STATUS_TRANSITIONS:
        allowed_transitions = PROJECT_STATUS_TRANSITIONS[current_status]
        return new_status in allowed_transitions
        
    return False

def delete_project(project_id):
    """Delete a project"""
    try:
        if supabase is None:
            print("Using mock project data for deletion")
            global MOCK_PROJECTS
            MOCK_PROJECTS = [p for p in MOCK_PROJECTS if p['id'] != project_id]
            return True
            
        # May need cascade deletion logic for related records
        response = supabase.from_("projects").delete().eq("id", project_id).execute()
        return True
    except Exception as e:
        print(f"Error deleting project: {e}")
        return False

def get_projects_by_user(user_id):
    """Get all projects for a user"""
    try:
        if supabase is None:
            print("Using mock projects data for user")
            return [p for p in MOCK_PROJECTS if p.get('user_id') == user_id]
            
        response = supabase.from_("projects").select("*").eq("user_id", user_id).execute()
        return response.data
    except Exception as e:
        print(f"Error getting projects by user: {e}")
        return [p for p in MOCK_PROJECTS if p.get('user_id') == user_id]

def get_project_tasks(project_id):
    """Get all tasks for a project"""
    try:
        if supabase is None:
            print("Using mock task data")
            # Mock tasks based on project ID
            mock_tasks = [
                {
                    'id': 1,
                    'project_id': project_id,
                    'title': 'Sample Task 1',
                    'description': 'This is a sample task',
                    'status': 'In Progress',
                    'due_date': '2023-06-30',
                    'assigned_to': 1
                },
                {
                    'id': 2,
                    'project_id': project_id,
                    'title': 'Sample Task 2',
                    'description': 'Another sample task',
                    'status': 'Pending',
                    'due_date': '2023-07-15',
                    'assigned_to': 1
                }
            ]
            return mock_tasks
            
        response = supabase.from_("tasks").select("*").eq("project_id", project_id).execute()
        return response.data
    except Exception as e:
        print(f"Error getting project tasks: {e}")
        # Return mock tasks
        return [
            {
                'id': 1,
                'project_id': project_id,
                'title': 'Sample Task 1',
                'description': 'This is a sample task',
                'status': 'In Progress',
                'due_date': '2023-06-30',
                'assigned_to': 1
            },
            {
                'id': 2,
                'project_id': project_id,
                'title': 'Sample Task 2',
                'description': 'Another sample task',
                'status': 'Pending',
                'due_date': '2023-07-15',
                'assigned_to': 1
            }
        ] 