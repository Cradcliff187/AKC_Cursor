from app.services.supabase import supabase
import uuid
from datetime import datetime, timedelta

# Mock time entry data for development
MOCK_TIME_ENTRIES = [
    {
        'id': '1', 
        'user_id': 'admin',
        'project_id': 1,
        'date': '2023-03-01',
        'hours': 8,
        'description': 'Site preparation and initial groundwork',
        'status': 'approved',
        'billable': True,
        'created_at': '2023-03-01T08:00:00',
        'project_name': 'Sample Project 1'
    },
    {
        'id': '2', 
        'user_id': 'admin',
        'project_id': 2,
        'date': '2023-03-02',
        'hours': 6,
        'description': 'Client meeting and project planning',
        'status': 'pending',
        'billable': True,
        'created_at': '2023-03-02T09:00:00',
        'project_name': 'Sample Project 2'
    },
    {
        'id': '3', 
        'user_id': 'admin',
        'project_id': 3,
        'date': '2023-03-03',
        'hours': 4,
        'description': 'Final inspection and project review',
        'status': 'rejected',
        'billable': False,
        'created_at': '2023-03-03T13:00:00',
        'project_name': 'Completed Example'
    },
    {
        'id': '4', 
        'user_id': 'user1',
        'project_id': 1,
        'date': '2023-03-01',
        'hours': 7.5,
        'description': 'Electrical work for main floor',
        'status': 'approved',
        'billable': True,
        'created_at': '2023-03-01T10:00:00',
        'project_name': 'Sample Project 1'
    },
    {
        'id': '5', 
        'user_id': 'user2',
        'project_id': 2,
        'date': '2023-03-02',
        'hours': 5,
        'description': 'Plumbing installation in bathrooms',
        'status': 'approved',
        'billable': True,
        'created_at': '2023-03-02T11:00:00',
        'project_name': 'Sample Project 2'
    }
]

def get_all_time_entries():
    """Get all time entries"""
    try:
        if supabase is None:
            print("Using mock time entry data")
            return MOCK_TIME_ENTRIES
            
        response = supabase.from_("time_entries").select("*, projects(name)").execute()
        
        # Process entries to match expected format
        entries = []
        for entry in response.data:
            entry['project_name'] = entry['projects']['name'] if 'projects' in entry else 'Unknown'
            entries.append(entry)
            
        return entries
    except Exception as e:
        print(f"Error loading time entries: {e}")
        return MOCK_TIME_ENTRIES

def get_user_time_entries(user_id):
    """Get time entries for a specific user"""
    try:
        if supabase is None:
            print("Using mock time entry data")
            return [entry for entry in MOCK_TIME_ENTRIES if entry['user_id'] == user_id]
            
        response = supabase.from_("time_entries").select("*, projects(name)").eq("user_id", user_id).execute()
        
        # Process entries to match expected format
        entries = []
        for entry in response.data:
            entry['project_name'] = entry['projects']['name'] if 'projects' in entry else 'Unknown'
            entries.append(entry)
            
        return entries
    except Exception as e:
        print(f"Error loading user time entries: {e}")
        return [entry for entry in MOCK_TIME_ENTRIES if entry['user_id'] == user_id]

def get_project_time_entries(project_id):
    """Get time entries for a specific project"""
    try:
        if supabase is None:
            print("Using mock time entry data")
            return [entry for entry in MOCK_TIME_ENTRIES if entry['project_id'] == project_id]
            
        response = supabase.from_("time_entries").select("*, projects(name)").eq("project_id", project_id).execute()
        
        # Process entries to match expected format
        entries = []
        for entry in response.data:
            entry['project_name'] = entry['projects']['name'] if 'projects' in entry else 'Unknown'
            entries.append(entry)
            
        return entries
    except Exception as e:
        print(f"Error loading project time entries: {e}")
        return [entry for entry in MOCK_TIME_ENTRIES if entry['project_id'] == project_id]

def get_time_entry(entry_id):
    """Get a specific time entry"""
    try:
        if supabase is None:
            print("Using mock time entry data")
            for entry in MOCK_TIME_ENTRIES:
                if entry['id'] == entry_id:
                    return entry
            return None
            
        response = supabase.from_("time_entries").select("*, projects(name)").eq("id", entry_id).execute()
        if response.data and len(response.data) > 0:
            entry = response.data[0]
            entry['project_name'] = entry['projects']['name'] if 'projects' in entry else 'Unknown'
            return entry
            
        return None
    except Exception as e:
        print(f"Error loading time entry: {e}")
        for entry in MOCK_TIME_ENTRIES:
            if entry['id'] == entry_id:
                return entry
        return None

def create_time_entry(entry_data):
    """Create a new time entry"""
    try:
        if 'id' not in entry_data:
            entry_data['id'] = str(uuid.uuid4())
            
        if 'created_at' not in entry_data:
            entry_data['created_at'] = datetime.utcnow().isoformat()
            
        if 'status' not in entry_data:
            entry_data['status'] = 'pending'
            
        if supabase is None:
            print("Using mock time entry data for creation")
            
            # If this is a real app, we'd fetch the project name
            # For now, add a mock project name
            from app.services.projects import get_all_projects
            projects = get_all_projects()
            project_name = "Unknown"
            for project in projects:
                if str(project['id']) == str(entry_data['project_id']):
                    project_name = project['name']
                    break
                    
            entry_data['project_name'] = project_name
            
            MOCK_TIME_ENTRIES.append(entry_data)
            return entry_data
            
        response = supabase.from_("time_entries").insert(entry_data).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error creating time entry: {e}")
        # Still try to add to mock data for development
        MOCK_TIME_ENTRIES.append(entry_data)
        return entry_data

def update_time_entry(entry_id, entry_data):
    """Update a time entry"""
    try:
        if supabase is None:
            print("Using mock time entry data for update")
            for i, entry in enumerate(MOCK_TIME_ENTRIES):
                if entry['id'] == entry_id:
                    MOCK_TIME_ENTRIES[i] = {**entry, **entry_data}
                    return MOCK_TIME_ENTRIES[i]
            return None
            
        response = supabase.from_("time_entries").update(entry_data).eq("id", entry_id).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error updating time entry: {e}")
        for i, entry in enumerate(MOCK_TIME_ENTRIES):
            if entry['id'] == entry_id:
                MOCK_TIME_ENTRIES[i] = {**entry, **entry_data}
                return MOCK_TIME_ENTRIES[i]
        return None

def delete_time_entry(entry_id):
    """Delete a time entry"""
    try:
        if supabase is None:
            print("Using mock time entry data for deletion")
            global MOCK_TIME_ENTRIES
            MOCK_TIME_ENTRIES = [e for e in MOCK_TIME_ENTRIES if e['id'] != entry_id]
            return True
            
        response = supabase.from_("time_entries").delete().eq("id", entry_id).execute()
        return True
    except Exception as e:
        print(f"Error deleting time entry: {e}")
        return False

def update_time_entry_status(entry_id, status):
    """Update the status of a time entry"""
    try:
        if supabase is None:
            print("Using mock time entry data for status update")
            for i, entry in enumerate(MOCK_TIME_ENTRIES):
                if entry['id'] == entry_id:
                    MOCK_TIME_ENTRIES[i]['status'] = status
                    return MOCK_TIME_ENTRIES[i]
            return None
            
        response = supabase.from_("time_entries").update({"status": status}).eq("id", entry_id).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        print(f"Error updating time entry status: {e}")
        for i, entry in enumerate(MOCK_TIME_ENTRIES):
            if entry['id'] == entry_id:
                MOCK_TIME_ENTRIES[i]['status'] = status
                return MOCK_TIME_ENTRIES[i]
        return None

def get_time_summary(user_id=None):
    """Get summary of time entries (total hours, billable hours, etc.)"""
    try:
        entries = get_user_time_entries(user_id) if user_id else get_all_time_entries()
        
        total_hours = 0
        billable_hours = 0
        
        for entry in entries:
            hours = float(entry['hours'])
            total_hours += hours
            
            if entry.get('billable', False):
                billable_hours += hours
                
        return {
            'total_hours': total_hours,
            'billable_hours': billable_hours,
            'unbillable_hours': total_hours - billable_hours
        }
    except Exception as e:
        print(f"Error calculating time summary: {e}")
        return {
            'total_hours': 0,
            'billable_hours': 0,
            'unbillable_hours': 0
        } 