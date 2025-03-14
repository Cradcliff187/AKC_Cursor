from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import json
import base64
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError

# Load environment variables
load_dotenv()

# Define scopes for Google Calendar
SCOPES = ['https://www.googleapis.com/auth/calendar']

# Configure OAuth settings
CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
REDIRECT_URI = os.environ.get('GOOGLE_REDIRECT_URI', 'http://localhost:5000/auth/google/callback')

def get_oauth_flow():
    """Create and configure OAuth flow"""
    client_config = {
        "web": {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [REDIRECT_URI]
        }
    }
    return Flow.from_client_config(
        client_config=client_config,
        scopes=SCOPES
    )

def get_authorization_url():
    """Get the Google authorization URL"""
    flow = get_oauth_flow()
    flow.redirect_uri = REDIRECT_URI
    
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    
    return authorization_url, state

def get_credentials_from_code(code):
    """Exchange authorization code for credentials"""
    flow = get_oauth_flow()
    flow.redirect_uri = REDIRECT_URI
    
    try:
        flow.fetch_token(code=code)
        credentials = flow.credentials
        return credentials
    except Exception as e:
        print(f"Error getting credentials: {e}")
        return None

def credentials_to_dict(credentials):
    """Convert credentials object to dictionary for storage"""
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }

def dict_to_credentials(credentials_dict):
    """Convert credentials dictionary back to Credentials object"""
    if not credentials_dict:
        return None
        
    return Credentials(
        token=credentials_dict.get('token'),
        refresh_token=credentials_dict.get('refresh_token'),
        token_uri=credentials_dict.get('token_uri'),
        client_id=credentials_dict.get('client_id'),
        client_secret=credentials_dict.get('client_secret'),
        scopes=credentials_dict.get('scopes')
    )

def get_calendar_service(credentials_dict):
    """Build Google Calendar service from credentials"""
    credentials = dict_to_credentials(credentials_dict)
    
    if not credentials:
        return None
        
    # Check if token is expired and refresh if needed
    if credentials.expired and credentials.refresh_token:
        try:
            credentials.refresh(Request())
        except RefreshError as e:
            print(f"Error refreshing token: {e}")
            return None
    
    try:
        service = build('calendar', 'v3', credentials=credentials)
        return service, credentials_to_dict(credentials)
    except Exception as e:
        print(f"Error building calendar service: {e}")
        return None, None

def list_calendars(credentials_dict):
    """List available calendars for the authenticated user"""
    service_result = get_calendar_service(credentials_dict)
    if not service_result:
        return None, None
        
    service, updated_credentials = service_result
    
    try:
        calendar_list = service.calendarList().list().execute()
        return calendar_list.get('items', []), updated_credentials
    except HttpError as e:
        print(f"Error listing calendars: {e}")
        return None, updated_credentials

def create_project_calendar(credentials_dict, project_name):
    """Create a new calendar for a project"""
    service_result = get_calendar_service(credentials_dict)
    if not service_result:
        return None, None
        
    service, updated_credentials = service_result
    
    calendar = {
        'summary': f"Construction CRM: {project_name}",
        'description': f"Calendar for construction project: {project_name}",
        'timeZone': 'America/New_York'  # Default timezone, could make configurable
    }
    
    try:
        created_calendar = service.calendars().insert(body=calendar).execute()
        return created_calendar, updated_credentials
    except HttpError as e:
        print(f"Error creating calendar: {e}")
        return None, updated_credentials

def add_project_events(credentials_dict, calendar_id, project, tasks):
    """Add project milestones and tasks to the calendar"""
    service_result = get_calendar_service(credentials_dict)
    if not service_result:
        return False, None
        
    service, updated_credentials = service_result
    
    try:
        # Add project start event
        if project.start_date:
            start_event = {
                'summary': f"Project Start: {project.name}",
                'description': f"Start of project {project.name}",
                'start': {
                    'date': project.start_date.strftime('%Y-%m-%d'),
                    'timeZone': 'America/New_York'
                },
                'end': {
                    'date': (project.start_date + timedelta(days=1)).strftime('%Y-%m-%d'),
                    'timeZone': 'America/New_York'
                },
                'colorId': '7',  # Green
                'reminders': {
                    'useDefault': True
                }
            }
            service.events().insert(calendarId=calendar_id, body=start_event).execute()
        
        # Add project end event
        if project.end_date:
            end_event = {
                'summary': f"Project End: {project.name}",
                'description': f"End of project {project.name}",
                'start': {
                    'date': project.end_date.strftime('%Y-%m-%d'),
                    'timeZone': 'America/New_York'
                },
                'end': {
                    'date': (project.end_date + timedelta(days=1)).strftime('%Y-%m-%d'),
                    'timeZone': 'America/New_York'
                },
                'colorId': '11',  # Red
                'reminders': {
                    'useDefault': True
                }
            }
            service.events().insert(calendarId=calendar_id, body=end_event).execute()
        
        # Add task events
        for task in tasks:
            if task.due_date:
                # Determine color based on priority
                color_map = {
                    'Low': '9',      # Blue
                    'Medium': '5',    # Yellow
                    'High': '6',      # Orange
                    'Urgent': '11'    # Red
                }
                color_id = color_map.get(task.priority, '5')
                
                task_event = {
                    'summary': f"Task Due: {task.title}",
                    'description': task.description,
                    'start': {
                        'date': task.due_date.strftime('%Y-%m-%d'),
                        'timeZone': 'America/New_York'
                    },
                    'end': {
                        'date': (task.due_date + timedelta(days=1)).strftime('%Y-%m-%d'),
                        'timeZone': 'America/New_York'
                    },
                    'colorId': color_id,
                    'reminders': {
                        'useDefault': True
                    }
                }
                service.events().insert(calendarId=calendar_id, body=task_event).execute()
        
        return True, updated_credentials
    except HttpError as e:
        print(f"Error adding events to calendar: {e}")
        return False, updated_credentials

def generate_ical_link(calendar_id):
    """Generate iCal link for a calendar"""
    if not calendar_id:
        return None
        
    return f"https://calendar.google.com/calendar/ical/{calendar_id}/public/basic.ics"

def generate_calendar_embed_code(calendar_id):
    """Generate HTML embed code for a calendar"""
    if not calendar_id:
        return None
        
    embed_code = f"""<iframe src="https://calendar.google.com/calendar/embed?src={calendar_id}&ctz=America%2FNew_York" 
                      style="border: 0" width="800" height="600" frameborder="0" scrolling="no"></iframe>"""
    return embed_code 