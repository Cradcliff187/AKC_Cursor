"""
Unit tests for calendar service
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from app.services.calendar import (
    get_oauth_flow,
    get_authorization_url,
    get_credentials_from_code,
    credentials_to_dict,
    dict_to_credentials,
    get_calendar_service,
    list_calendars,
    create_project_calendar,
    add_project_events,
    generate_ical_link,
    generate_calendar_embed_code
)

@pytest.fixture
def mock_credentials():
    return {
        'token': 'mock_token',
        'refresh_token': 'mock_refresh_token',
        'token_uri': 'mock_token_uri',
        'client_id': 'mock_client_id',
        'client_secret': 'mock_client_secret',
        'scopes': ['https://www.googleapis.com/auth/calendar']
    }

@pytest.fixture
def mock_calendar():
    return {
        'id': 'mock_calendar_id',
        'summary': 'Test Calendar',
        'description': 'Test Calendar Description',
        'timeZone': 'America/New_York'
    }

@pytest.fixture
def mock_project():
    project = MagicMock()
    project.name = "Test Project"
    project.start_date = datetime.now()
    project.end_date = datetime.now() + timedelta(days=30)
    return project

@pytest.fixture
def mock_tasks():
    tasks = []
    for i in range(3):
        task = MagicMock()
        task.name = f"Task {i}"
        task.due_date = datetime.now() + timedelta(days=i)
        task.status = "pending"
        tasks.append(task)
    return tasks

def test_get_oauth_flow():
    with patch('app.services.calendar.Flow') as mock_flow:
        mock_flow.from_client_config.return_value = MagicMock()
        
        flow = get_oauth_flow()
        assert flow is not None
        mock_flow.from_client_config.assert_called_once()

def test_get_authorization_url():
    with patch('app.services.calendar.get_oauth_flow') as mock_get_flow:
        mock_flow = MagicMock()
        mock_flow.authorization_url.return_value = ('http://test.com', 'test_state')
        mock_get_flow.return_value = mock_flow
        
        url, state = get_authorization_url()
        assert url == 'http://test.com'
        assert state == 'test_state'
        mock_flow.authorization_url.assert_called_once()

def test_get_credentials_from_code():
    with patch('app.services.calendar.Flow') as mock_flow:
        mock_flow_instance = MagicMock()
        mock_flow_instance.fetch_token.return_value = {'token': 'test_token'}
        mock_flow.from_client_config.return_value = mock_flow_instance
        
        credentials = get_credentials_from_code('test_code')
        assert credentials is not None
        assert credentials['token'] == 'test_token'
        mock_flow_instance.fetch_token.assert_called_once()

def test_credentials_to_dict():
    with patch('app.services.calendar.Credentials') as mock_credentials:
        mock_credentials_instance = MagicMock()
        mock_credentials_instance.to_json.return_value = '{"token": "test_token"}'
        mock_credentials.return_value = mock_credentials_instance
        
        credentials_dict = credentials_to_dict(mock_credentials_instance)
        assert credentials_dict is not None
        assert credentials_dict['token'] == 'test_token'
        mock_credentials_instance.to_json.assert_called_once()

def test_dict_to_credentials():
    with patch('app.services.calendar.Credentials') as mock_credentials:
        mock_credentials_instance = MagicMock()
        mock_credentials.from_authorized_user_info.return_value = mock_credentials_instance
        
        credentials = dict_to_credentials({'token': 'test_token'})
        assert credentials is not None
        mock_credentials.from_authorized_user_info.assert_called_once()

def test_get_calendar_service():
    with patch('app.services.calendar.build') as mock_build:
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        
        service = get_calendar_service(MagicMock())
        assert service is not None
        mock_build.assert_called_once()

def test_list_calendars():
    with patch('app.services.calendar.get_calendar_service') as mock_get_service:
        mock_service = MagicMock()
        mock_service.calendarList.return_value.list.return_value.execute.return_value = {'items': [{'id': 'test_id'}]}
        mock_get_service.return_value = mock_service
        
        calendars = list_calendars(MagicMock())
        assert len(calendars) == 1
        assert calendars[0]['id'] == 'test_id'
        mock_service.calendarList.return_value.list.return_value.execute.assert_called_once()

def test_create_project_calendar():
    with patch('app.services.calendar.get_calendar_service') as mock_get_service:
        mock_service = MagicMock()
        mock_service.calendars.return_value.insert.return_value.execute.return_value = {'id': 'test_id'}
        mock_get_service.return_value = mock_service
        
        calendar = create_project_calendar(MagicMock(), MagicMock())
        assert calendar is not None
        assert calendar['id'] == 'test_id'
        mock_service.calendars.return_value.insert.return_value.execute.assert_called_once()

def test_add_project_events():
    with patch('app.services.calendar.get_calendar_service') as mock_get_service:
        mock_service = MagicMock()
        mock_service.events.return_value.insert.return_value.execute.return_value = {'id': 'test_id'}
        mock_get_service.return_value = mock_service
        
        event = add_project_events(MagicMock(), 'test_calendar_id', MagicMock())
        assert event is not None
        assert event['id'] == 'test_id'
        mock_service.events.return_value.insert.return_value.execute.assert_called_once()

def test_generate_ical_link():
    with patch('app.services.calendar.get_calendar_service') as mock_get_service:
        mock_service = MagicMock()
        mock_service.calendars.return_value.get.return_value.execute.return_value = {'id': 'test_id'}
        mock_get_service.return_value = mock_service
        
        link = generate_ical_link(MagicMock(), 'test_calendar_id')
        assert link is not None
        assert 'test_calendar_id' in link
        mock_service.calendars.return_value.get.return_value.execute.assert_called_once()

def test_generate_calendar_embed_code():
    with patch('app.services.calendar.get_calendar_service') as mock_get_service:
        mock_service = MagicMock()
        mock_service.calendars.return_value.get.return_value.execute.return_value = {'id': 'test_id'}
        mock_get_service.return_value = mock_service
        
        embed_code = generate_calendar_embed_code(MagicMock(), 'test_calendar_id')
        assert embed_code is not None
        assert 'test_calendar_id' in embed_code
        mock_service.calendars.return_value.get.return_value.execute.assert_called_once() 