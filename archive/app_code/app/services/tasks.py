from app.services.supabase import supabase
import uuid
from datetime import datetime, timedelta
from app.services.utils import generate_task_id

# Priority levels with their display values and badge colors
TASK_PRIORITIES = {
    'HIGH': {'display': 'High', 'badge': 'danger'},
    'MEDIUM': {'display': 'Medium', 'badge': 'warning'},
    'LOW': {'display': 'Low', 'badge': 'success'}
}

# Status options with their display values and badge colors
# Aligned with the project status values from the JSON guide
TASK_STATUSES = {
    'PENDING': {'display': 'Pending', 'badge': 'secondary'},
    'IN_PROGRESS': {'display': 'In Progress', 'badge': 'primary'},
    'ON_HOLD': {'display': 'On Hold', 'badge': 'warning'},
    'COMPLETED': {'display': 'Completed', 'badge': 'success'},
    'CANCELED': {'display': 'Canceled', 'badge': 'danger'}
}

# For backward compatibility with existing code - to be removed after migration
TASK_STATUS_MAPPING = {
    'todo': 'PENDING',
    'in_progress': 'IN_PROGRESS',
    'on_hold': 'ON_HOLD',
    'completed': 'COMPLETED',
    'cancelled': 'CANCELED'
}

# Priority mapping for backward compatibility - to be removed after migration
TASK_PRIORITY_MAPPING = {
    'high': 'HIGH',
    'medium': 'MEDIUM',
    'low': 'LOW'
}

# Task status transitions
TASK_STATUS_TRANSITIONS = {
    'PENDING': ['IN_PROGRESS', 'ON_HOLD', 'CANCELED'],
    'IN_PROGRESS': ['COMPLETED', 'ON_HOLD', 'CANCELED'],
    'ON_HOLD': ['IN_PROGRESS', 'CANCELED'],
    'COMPLETED': [],  # Terminal state
    'CANCELED': []    # Terminal state
}

# Mock data for tasks - standardized with uppercase status and priority
MOCK_TASKS = [
    {
        'id': '1',
        'title': 'Finalize architectural plans',
        'description': 'Review and approve architectural plans from the designer',
        'project_id': '1',
        'assigned_to': 'admin',
        'status': 'COMPLETED',
        'priority': 'HIGH',
        'due_date': (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d'),
        'estimated_hours': 4,
        'actual_hours': 5,
        'created_by': 'admin',
        'created_at': (datetime.now() - timedelta(days=15)).isoformat(),
        'completed_at': (datetime.now() - timedelta(days=5)).isoformat(),
        'updated_at': (datetime.now() - timedelta(days=5)).isoformat()
    },
    {
        'id': '2',
        'title': 'Obtain building permits',
        'description': 'Submit application for building permits with local authority',
        'project_id': '1',
        'assigned_to': 'admin',
        'status': 'IN_PROGRESS',
        'priority': 'HIGH',
        'due_date': (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d'),
        'estimated_hours': 6,
        'actual_hours': 2,
        'created_by': 'admin',
        'created_at': (datetime.now() - timedelta(days=10)).isoformat(),
        'completed_at': None,
        'updated_at': (datetime.now() - timedelta(days=1)).isoformat()
    },
    # Additional mock tasks
    {
        'id': '3',
        'title': 'Order materials for foundation',
        'description': 'Purchase concrete, rebar, and other materials for foundation work',
        'project_id': '1',
        'assigned_to': 'admin',
        'status': 'PENDING',
        'priority': 'MEDIUM',
        'due_date': (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'),
        'estimated_hours': 2,
        'actual_hours': 0,
        'created_by': 'admin',
        'created_at': (datetime.now() - timedelta(days=2)).isoformat(),
        'completed_at': None,
        'updated_at': (datetime.now() - timedelta(days=2)).isoformat()
    },
    {
        'id': '4',
        'title': 'Schedule electrical inspection',
        'description': 'Contact city inspector to schedule electrical rough-in inspection',
        'project_id': '2',
        'assigned_to': 'admin',
        'status': 'ON_HOLD',
        'priority': 'HIGH',
        'due_date': (datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d'),
        'estimated_hours': 1,
        'actual_hours': 0,
        'created_by': 'admin',
        'created_at': (datetime.now() - timedelta(days=5)).isoformat(),
        'completed_at': None,
        'updated_at': (datetime.now() - timedelta(days=1)).isoformat()
    },
    {
        'id': '5',
        'title': 'Prepare project timeline',
        'description': 'Create detailed timeline for client approval',
        'project_id': '3',
        'assigned_to': 'admin',
        'status': 'COMPLETED',
        'priority': 'MEDIUM',
        'due_date': (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d'),
        'estimated_hours': 3,
        'actual_hours': 2.5,
        'created_by': 'admin',
        'created_at': (datetime.now() - timedelta(days=10)).isoformat(),
        'completed_at': (datetime.now() - timedelta(days=3)).isoformat(),
        'updated_at': (datetime.now() - timedelta(days=3)).isoformat()
    }
]

def standardize_task_status(task):
    """Standardize task status to uppercase format"""
    if 'status' in task:
        # Check if status is in legacy format
        if task['status'] in TASK_STATUS_MAPPING:
            task['status'] = TASK_STATUS_MAPPING[task['status']]
        
        # Ensure status is uppercase
        task['status'] = task['status'].upper()
    
    return task

def standardize_task_priority(task):
    """Standardize task priority to uppercase format"""
    if 'priority' in task:
        # Check if priority is in legacy format
        if task['priority'] in TASK_PRIORITY_MAPPING:
            task['priority'] = TASK_PRIORITY_MAPPING[task['priority']]
        
        # Ensure priority is uppercase
        task['priority'] = task['priority'].upper()
    
    return task

def get_all_tasks():
    """Get all tasks"""
    try:
        if supabase is not None:
            response = supabase.from_("tasks").select("*").execute()
            tasks = response.data
            
            # Standardize all tasks
            for task in tasks:
                standardize_task_status(task)
                standardize_task_priority(task)
                
            return tasks
        else:
            return MOCK_TASKS
    except Exception as e:
        print(f"Error fetching tasks: {str(e)}")
        return MOCK_TASKS

def get_task(task_id):
    """Get a single task by ID"""
    try:
        if supabase is not None:
            response = supabase.from_("tasks").select("*").eq("id", task_id).execute()
            if response.data:
                task = response.data[0]
                standardize_task_status(task)
                standardize_task_priority(task)
                return task
        else:
            for task in MOCK_TASKS:
                if task['id'] == task_id:
                    return task
        return None
    except Exception as e:
        print(f"Error fetching task {task_id}: {str(e)}")
        # Still attempt to return from mock data on error
        for task in MOCK_TASKS:
            if task['id'] == task_id:
                return task
        return None

def get_project_tasks(project_id):
    """Get all tasks for a specific project"""
    try:
        if supabase is not None:
            response = supabase.from_("tasks").select("*").eq("project_id", project_id).execute()
            tasks = response.data
            
            # Standardize all tasks
            for task in tasks:
                standardize_task_status(task)
                standardize_task_priority(task)
                
            return tasks
        else:
            return [task for task in MOCK_TASKS if task['project_id'] == project_id]
    except Exception as e:
        print(f"Error fetching tasks for project {project_id}: {str(e)}")
        return [task for task in MOCK_TASKS if task['project_id'] == project_id]

def get_user_tasks(user_id):
    """Get all tasks assigned to a specific user"""
    try:
        if supabase is not None:
            response = supabase.from_("tasks").select("*").eq("assigned_to", user_id).execute()
            tasks = response.data
            
            # Standardize all tasks
            for task in tasks:
                standardize_task_status(task)
                standardize_task_priority(task)
                
            return tasks
        else:
            return [task for task in MOCK_TASKS if task['assigned_to'] == user_id]
    except Exception as e:
        print(f"Error fetching tasks for user {user_id}: {str(e)}")
        return [task for task in MOCK_TASKS if task['assigned_to'] == user_id]

def create_task(task_data):
    """Create a new task"""
    try:
        # Generate a task ID using the utility function
        task_id = generate_task_id()
        
        # Standardize status and priority
        if 'status' in task_data and task_data['status'] in TASK_STATUS_MAPPING:
            task_data['status'] = TASK_STATUS_MAPPING[task_data['status']]
        
        if 'priority' in task_data and task_data['priority'] in TASK_PRIORITY_MAPPING:
            task_data['priority'] = TASK_PRIORITY_MAPPING[task_data['priority']]
        
        # Ensure uppercase
        if 'status' in task_data:
            task_data['status'] = task_data['status'].upper()
        
        if 'priority' in task_data:
            task_data['priority'] = task_data['priority'].upper()
        
        # Create task with current timestamp
        task = {
            'id': task_id,
            'title': task_data.get('title', 'New Task'),
            'description': task_data.get('description', ''),
            'project_id': task_data.get('project_id'),
            'assigned_to': task_data.get('assigned_to', 'admin'),
            'status': task_data.get('status', 'PENDING'),
            'priority': task_data.get('priority', 'MEDIUM'),
            'due_date': task_data.get('due_date'),
            'estimated_hours': float(task_data.get('estimated_hours', 0)),
            'actual_hours': float(task_data.get('actual_hours', 0)),
            'created_by': task_data.get('created_by', 'admin'),
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'completed_at': None
        }
        
        # If status is completed, set the completed_at timestamp
        if task['status'] == 'COMPLETED':
            task['completed_at'] = datetime.now().isoformat()
        
        if supabase is None:
            # Add to mock data
            MOCK_TASKS.append(task)
            return task
        else:
            # Add to supabase
            response = supabase.from_("tasks").insert(task).execute()
            if response.data:
                return response.data[0]
            return None
    except Exception as e:
        print(f"Error creating task: {str(e)}")
        return None

def update_task(task_id, task_data):
    """Update a task"""
    try:
        # Get existing task
        current_task = get_task(task_id)
        if not current_task:
            return None
        
        # Standardize status and priority if present
        if 'status' in task_data:
            if task_data['status'] in TASK_STATUS_MAPPING:
                task_data['status'] = TASK_STATUS_MAPPING[task_data['status']]
            
            # Ensure status is uppercase
            task_data['status'] = task_data['status'].upper()
            
            # Validate status transition
            if not is_valid_status_transition(current_task['status'], task_data['status']):
                print(f"Invalid status transition: {current_task['status']} -> {task_data['status']}")
                return None
            
            # If new status is COMPLETED, set completed_at timestamp
            if task_data['status'] == 'COMPLETED' and current_task['status'] != 'COMPLETED':
                task_data['completed_at'] = datetime.now().isoformat()
            
            # If task was previously completed but now is not, clear completed_at
            if task_data['status'] != 'COMPLETED' and current_task['status'] == 'COMPLETED':
                task_data['completed_at'] = None
        
        if 'priority' in task_data:
            if task_data['priority'] in TASK_PRIORITY_MAPPING:
                task_data['priority'] = TASK_PRIORITY_MAPPING[task_data['priority']]
            
            # Ensure priority is uppercase
            task_data['priority'] = task_data['priority'].upper()
        
        # Update the timestamp
        task_data['updated_at'] = datetime.now().isoformat()
        
        # Merge with current task
        updated_task = {**current_task, **task_data}
        
        if supabase is None:
            # Update in mock data
            for i, task in enumerate(MOCK_TASKS):
                if task['id'] == task_id:
                    MOCK_TASKS[i] = updated_task
                    return updated_task
            return None
        else:
            # Update in supabase
            response = supabase.from_("tasks").update(task_data).eq("id", task_id).execute()
            if response.data:
                return response.data[0]
            return None
    except Exception as e:
        print(f"Error updating task {task_id}: {str(e)}")
        return None

def delete_task(task_id):
    """Delete a task"""
    try:
        if supabase is None:
            # Remove from mock data
            global MOCK_TASKS
            original_length = len(MOCK_TASKS)
            MOCK_TASKS = [task for task in MOCK_TASKS if task['id'] != task_id]
            return len(MOCK_TASKS) < original_length
        else:
            # Delete from supabase
            response = supabase.from_("tasks").delete().eq("id", task_id).execute()
            return bool(response.data)
    except Exception as e:
        print(f"Error deleting task {task_id}: {str(e)}")
        return False

def get_task_stats(project_id=None):
    """Get task statistics (counts by status, priorities, etc.)"""
    tasks = get_project_tasks(project_id) if project_id else get_all_tasks()
    
    # Get counts by status (using standardized statuses)
    completed_tasks = len([t for t in tasks if t['status'] == 'COMPLETED'])
    in_progress_tasks = len([t for t in tasks if t['status'] == 'IN_PROGRESS'])
    pending_tasks = len([t for t in tasks if t['status'] == 'PENDING'])
    on_hold_tasks = len([t for t in tasks if t['status'] == 'ON_HOLD'])
    cancelled_tasks = len([t for t in tasks if t['status'] == 'CANCELED'])
    
    # Get overdue tasks
    today = datetime.now().strftime('%Y-%m-%d')
    overdue_tasks = []
    for t in tasks:
        if t.get('due_date') and t['due_date'] < today and t['status'] not in ['COMPLETED', 'CANCELED']:
            overdue_tasks.append(t)
    
    # Calculate completion rate
    total_tasks = len(tasks)
    completion_rate = 0
    if total_tasks > 0:
        completion_rate = round(completed_tasks / total_tasks * 100, 1)
    
    # Get counts by priority
    high_priority = len([t for t in tasks if t['priority'] == 'HIGH'])
    medium_priority = len([t for t in tasks if t['priority'] == 'MEDIUM'])
    low_priority = len([t for t in tasks if t['priority'] == 'LOW'])
    
    # Calculate time metrics
    estimated_hours = sum(float(t.get('estimated_hours', 0)) for t in tasks)
    actual_hours = sum(float(t.get('actual_hours', 0)) for t in tasks)
    
    return {
        'total': total_tasks,
        'completed': completed_tasks,
        'in_progress': in_progress_tasks,
        'pending': pending_tasks,
        'on_hold': on_hold_tasks,
        'cancelled': cancelled_tasks,
        'overdue': len(overdue_tasks),
        'completion_rate': completion_rate,
        'priority': {
            'high': high_priority,
            'medium': medium_priority,
            'low': low_priority
        },
        'time': {
            'estimated': estimated_hours,
            'actual': actual_hours,
            'efficiency': round(estimated_hours / actual_hours * 100, 1) if actual_hours > 0 else 0
        }
    }

def get_priority_display(priority):
    """Get display information for a priority level"""
    if not priority:
        return {'display': 'Unknown', 'badge': 'secondary'}
    
    # Map legacy priority to new format if needed
    if priority in TASK_PRIORITY_MAPPING:
        priority = TASK_PRIORITY_MAPPING[priority]
    
    # Ensure uppercase
    priority = priority.upper()
    
    return TASK_PRIORITIES.get(priority, {'display': priority, 'badge': 'secondary'})

def get_status_display(status):
    """Get display information for a status"""
    if not status:
        return {'display': 'Unknown', 'badge': 'secondary'}
    
    # Map legacy status to new format if needed
    if status in TASK_STATUS_MAPPING:
        status = TASK_STATUS_MAPPING[status]
    
    # Ensure uppercase
    status = status.upper()
    
    return TASK_STATUSES.get(status, {'display': status, 'badge': 'secondary'})

def is_valid_status_transition(current_status, new_status):
    """Check if a status transition is valid"""
    # If status hasn't changed, always valid
    if current_status == new_status:
        return True
    
    # Standardize statuses
    if current_status in TASK_STATUS_MAPPING:
        current_status = TASK_STATUS_MAPPING[current_status]
    
    if new_status in TASK_STATUS_MAPPING:
        new_status = TASK_STATUS_MAPPING[new_status]
    
    # Ensure uppercase
    current_status = current_status.upper()
    new_status = new_status.upper()
    
    # Check if transition is allowed
    allowed_transitions = TASK_STATUS_TRANSITIONS.get(current_status, [])
    return new_status in allowed_transitions

def get_task_dependencies(task_id):
    """Get tasks that depend on this task (mock implementation)"""
    # In a real implementation, this would query a task_dependencies table
    # For now, return an empty list
    return []

def get_task_timeline(project_id=None):
    """Get tasks organized by timeline"""
    tasks = get_project_tasks(project_id) if project_id else get_all_tasks()
    
    # Sort tasks by due date
    sorted_tasks = sorted(
        [t for t in tasks if t.get('due_date')],
        key=lambda t: t.get('due_date', '9999-12-31')
    )
    
    # Group tasks by week
    timeline = {}
    for task in sorted_tasks:
        due_date = task.get('due_date')
        if due_date:
            # Convert string date to datetime
            try:
                due_datetime = datetime.strptime(due_date, '%Y-%m-%d')
                # Get week number
                week_key = f"{due_datetime.year}-W{due_datetime.isocalendar()[1]}"
                
                if week_key not in timeline:
                    timeline[week_key] = []
                    
                timeline[week_key].append(task)
            except ValueError:
                # Skip tasks with invalid dates
                continue
    
    return timeline 