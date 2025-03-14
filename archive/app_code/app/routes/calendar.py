from flask import (
    Blueprint, flash, g, redirect, render_template, 
    request, session, url_for, jsonify
)
from app.routes.auth import login_required
from app.services.calendar import (
    get_authorization_url, get_credentials_from_code, credentials_to_dict,
    list_calendars, create_project_calendar, add_project_events,
    generate_ical_link, generate_calendar_embed_code, get_calendar_service
)
from app.services.projects import get_project_by_id, get_project_tasks
from app.services.supabase import update_record, get_table_data
import os
from dotenv import load_dotenv
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Load environment variables
load_dotenv()

bp = Blueprint('calendar', __name__, url_prefix='/calendar')

# Check if service account is configured
SERVICE_ACCOUNT_INFO = os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON')
SERVICE_ACCOUNT_EMAIL = os.environ.get('GOOGLE_SERVICE_ACCOUNT_EMAIL')
ADMIN_EMAIL = os.environ.get('GOOGLE_WORKSPACE_ADMIN_EMAIL')
DOMAIN = os.environ.get('GOOGLE_WORKSPACE_DOMAIN')

@bp.route('/')
@login_required
def index():
    """Show calendar management page"""
    user_id = session.get('user_id')
    
    # Check if user has Google Calendar credentials
    user_credentials = get_user_calendar_credentials(user_id)
    has_credentials = user_credentials is not None
    
    # Get projects for calendar creation
    projects_data = get_table_data('projects', filters={'user_id': user_id})
    projects = projects_data if projects_data else []
    
    # Get existing calendar links
    calendar_links = get_table_data('project_calendars', filters={'user_id': user_id})
    
    return render_template('calendar/index.html',
                          has_credentials=has_credentials,
                          projects=projects,
                          calendar_links=calendar_links,
                          service_account_available=SERVICE_ACCOUNT_INFO is not None)

@bp.route('/auth')
@login_required
def auth():
    """Start OAuth flow for Google Calendar"""
    # Generate authorization URL
    authorization_url, state = get_authorization_url()
    
    # Store state in session for validation
    session['oauth_state'] = state
    
    # Redirect to Google's OAuth consent screen
    return redirect(authorization_url)

@bp.route('/callback')
@login_required
def callback():
    """Handle OAuth callback from Google"""
    user_id = session.get('user_id')
    
    # Get authorization code from query parameters
    code = request.args.get('code')
    state = request.args.get('state')
    
    # Validate state to prevent CSRF
    if state != session.get('oauth_state'):
        flash('Invalid state parameter. Authentication failed.', 'danger')
        return redirect(url_for('calendar.index'))
    
    # Exchange code for credentials
    credentials = get_credentials_from_code(code)
    
    if not credentials:
        flash('Failed to obtain credentials', 'danger')
        return redirect(url_for('calendar.index'))
    
    # Store credentials for the user
    credentials_dict = credentials_to_dict(credentials)
    save_user_calendar_credentials(user_id, credentials_dict)
    
    flash('Successfully connected to Google Calendar!', 'success')
    return redirect(url_for('calendar.index'))

@bp.route('/create/<project_id>', methods=['POST'])
@login_required
def create_calendar(project_id):
    """Create a new calendar for a project"""
    user_id = session.get('user_id')
    
    # Get the project
    project = get_project_by_id(project_id)
    if not project:
        flash('Project not found', 'danger')
        return redirect(url_for('calendar.index'))
    
    # Determine which auth method to use based on form data
    use_service_account = request.form.get('use_service_account') == 'true'
    
    if use_service_account:
        # Use service account for admin-managed calendars
        if not SERVICE_ACCOUNT_INFO:
            flash('Service account is not configured', 'danger')
            return redirect(url_for('calendar.index'))
            
        calendar = create_calendar_with_service_account(project)
        if not calendar:
            flash('Failed to create calendar with service account', 'danger')
            return redirect(url_for('calendar.index'))
            
        calendar_id = calendar.get('id')
    else:
        # Use user's OAuth credentials
        credentials_dict = get_user_calendar_credentials(user_id)
        
        if not credentials_dict:
            flash('Google Calendar not connected. Please authorize first.', 'danger')
            return redirect(url_for('calendar.index'))
        
        # Create a new calendar
        calendar_result = create_project_calendar(credentials_dict, project.name)
        
        if not calendar_result:
            flash('Failed to create calendar', 'danger')
            return redirect(url_for('calendar.index'))
            
        calendar, updated_credentials = calendar_result
        
        # Update stored credentials if they changed
        if updated_credentials:
            save_user_calendar_credentials(user_id, updated_credentials)
            
        calendar_id = calendar.get('id')
    
    # Add calendar to database
    calendar_data = {
        'user_id': user_id,
        'project_id': project_id,
        'calendar_id': calendar_id,
        'calendar_name': f"Construction CRM: {project.name}",
        'ical_link': generate_ical_link(calendar_id),
        'embed_code': generate_calendar_embed_code(calendar_id),
    }
    
    insert_record('project_calendars', calendar_data)
    
    # Add project events to calendar
    if use_service_account:
        success = add_events_with_service_account(calendar_id, project)
    else:
        tasks = get_project_tasks(project_id)
        success, updated_credentials = add_project_events(credentials_dict, calendar_id, project, tasks)
        
        if updated_credentials:
            save_user_calendar_credentials(user_id, updated_credentials)
    
    if success:
        flash('Calendar created and events added successfully!', 'success')
    else:
        flash('Calendar created but failed to add all events.', 'warning')
    
    return redirect(url_for('calendar.index'))

@bp.route('/view/<calendar_id>')
@login_required
def view_calendar(calendar_id):
    """View a calendar"""
    user_id = session.get('user_id')
    
    # Get the calendar
    calendar_data = get_table_data('project_calendars', filters={'calendar_id': calendar_id})
    
    if not calendar_data or len(calendar_data) == 0:
        flash('Calendar not found', 'danger')
        return redirect(url_for('calendar.index'))
        
    calendar = calendar_data[0]
    
    # Check ownership
    if calendar.get('user_id') != user_id:
        flash('Access denied', 'danger')
        return redirect(url_for('calendar.index'))
    
    # Get the project
    project = get_project_by_id(calendar.get('project_id'))
    
    return render_template('calendar/view.html',
                          calendar=calendar,
                          project=project)

@bp.route('/share/<calendar_id>', methods=['POST'])
@login_required
def share_calendar(calendar_id):
    """Share a calendar with others"""
    user_id = session.get('user_id')
    
    # Get the calendar
    calendar_data = get_table_data('project_calendars', filters={'calendar_id': calendar_id})
    
    if not calendar_data or len(calendar_data) == 0:
        return jsonify({'success': False, 'error': 'Calendar not found'}), 404
        
    calendar = calendar_data[0]
    
    # Check ownership
    if calendar.get('user_id') != user_id:
        return jsonify({'success': False, 'error': 'Access denied'}), 403
    
    # Get email to share with
    email = request.form.get('email')
    if not email:
        return jsonify({'success': False, 'error': 'Email is required'}), 400
    
    # Determine which auth method to use
    use_service_account = request.form.get('use_service_account') == 'true'
    
    if use_service_account:
        success = share_calendar_with_service_account(calendar_id, email)
    else:
        credentials_dict = get_user_calendar_credentials(user_id)
        
        if not credentials_dict:
            return jsonify({'success': False, 'error': 'Google Calendar not connected'}), 400
            
        success, updated_credentials = share_calendar_with_oauth(credentials_dict, calendar_id, email)
        
        if updated_credentials:
            save_user_calendar_credentials(user_id, updated_credentials)
    
    if success:
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'error': 'Failed to share calendar'}), 500

# Helper functions

def get_user_calendar_credentials(user_id):
    """Get Google Calendar credentials for a user"""
    credentials_data = get_table_data('user_calendar_credentials', filters={'user_id': user_id})
    
    if credentials_data and len(credentials_data) > 0:
        return json.loads(credentials_data[0].get('credentials', '{}'))
    return None

def save_user_calendar_credentials(user_id, credentials_dict):
    """Save Google Calendar credentials for a user"""
    credentials_data = get_table_data('user_calendar_credentials', filters={'user_id': user_id})
    
    if credentials_data and len(credentials_data) > 0:
        # Update existing credentials
        update_record('user_calendar_credentials', 
                    credentials_data[0].get('id'),
                    {'credentials': json.dumps(credentials_dict)})
    else:
        # Insert new credentials
        insert_record('user_calendar_credentials', {
            'user_id': user_id,
            'credentials': json.dumps(credentials_dict)
        })

def get_service_account_credentials():
    """Get service account credentials for admin operations"""
    if not SERVICE_ACCOUNT_INFO:
        return None
        
    try:
        service_account_info = json.loads(SERVICE_ACCOUNT_INFO)
        credentials = service_account.Credentials.from_service_account_info(
            service_account_info,
            scopes=['https://www.googleapis.com/auth/calendar']
        )
        
        # Delegate credentials to admin
        if ADMIN_EMAIL:
            credentials = credentials.with_subject(ADMIN_EMAIL)
            
        return credentials
    except Exception as e:
        print(f"Error creating service account credentials: {e}")
        return None

def create_calendar_with_service_account(project):
    """Create a calendar using service account"""
    credentials = get_service_account_credentials()
    if not credentials:
        return None
        
    try:
        service = build('calendar', 'v3', credentials=credentials)
        
        calendar = {
            'summary': f"Construction CRM: {project.name}",
            'description': f"Calendar for construction project: {project.name}",
            'timeZone': 'America/New_York'
        }
        
        created_calendar = service.calendars().insert(body=calendar).execute()
        return created_calendar
    except Exception as e:
        print(f"Error creating calendar with service account: {e}")
        return None

def add_events_with_service_account(calendar_id, project):
    """Add events to a calendar using service account"""
    credentials = get_service_account_credentials()
    if not credentials:
        return False
        
    try:
        service = build('calendar', 'v3', credentials=credentials)
        
        # Add project events similar to the add_project_events function
        # This is simplified but you could expand it to match the full function
        
        # Add project start and end events
        if project.start_date:
            start_date_str = project.start_date.strftime('%Y-%m-%d')
            start_event = {
                'summary': f"Project Start: {project.name}",
                'description': f"Start of project {project.name}",
                'start': {'date': start_date_str},
                'end': {'date': start_date_str},
                'colorId': '7'  # Green
            }
            service.events().insert(calendarId=calendar_id, body=start_event).execute()
        
        if project.end_date:
            end_date_str = project.end_date.strftime('%Y-%m-%d')
            end_event = {
                'summary': f"Project End: {project.name}",
                'description': f"End of project {project.name}",
                'start': {'date': end_date_str},
                'end': {'date': end_date_str},
                'colorId': '11'  # Red
            }
            service.events().insert(calendarId=calendar_id, body=end_event).execute()
        
        # Tasks would be added here
        tasks = get_project_tasks(project.id)
        for task in tasks:
            if task.due_date:
                due_date_str = task.due_date.strftime('%Y-%m-%d')
                task_event = {
                    'summary': f"Task Due: {task.title}",
                    'description': task.description,
                    'start': {'date': due_date_str},
                    'end': {'date': due_date_str},
                    'colorId': '9'  # Blue
                }
                service.events().insert(calendarId=calendar_id, body=task_event).execute()
        
        return True
    except Exception as e:
        print(f"Error adding events with service account: {e}")
        return False

def share_calendar_with_service_account(calendar_id, email):
    """Share a calendar using service account"""
    credentials = get_service_account_credentials()
    if not credentials:
        return False
        
    try:
        service = build('calendar', 'v3', credentials=credentials)
        
        rule = {
            'scope': {
                'type': 'user',
                'value': email
            },
            'role': 'reader'
        }
        
        service.acl().insert(calendarId=calendar_id, body=rule).execute()
        return True
    except Exception as e:
        print(f"Error sharing calendar with service account: {e}")
        return False

def share_calendar_with_oauth(credentials_dict, calendar_id, email):
    """Share a calendar using OAuth credentials"""
    result = get_calendar_service(credentials_dict)
    if not result:
        return False, None
        
    service, updated_credentials = result
    
    try:
        rule = {
            'scope': {
                'type': 'user',
                'value': email
            },
            'role': 'reader'
        }
        
        service.acl().insert(calendarId=calendar_id, body=rule).execute()
        return True, updated_credentials
    except Exception as e:
        print(f"Error sharing calendar with OAuth: {e}")
        return False, updated_credentials 