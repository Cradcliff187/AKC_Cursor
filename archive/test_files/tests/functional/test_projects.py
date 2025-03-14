import pytest
from app.db import get_db

@pytest.mark.functional
class TestProjects:
    
    def test_project_list(self, with_admin_user):
        """Test listing projects."""
        response = with_admin_user.get('/projects/')
        assert response.status_code == 200
        assert b'Test Project 1' in response.data
        assert b'Test Project 2' in response.data
    
    def test_project_detail(self, with_admin_user, test_project_id):
        """Test viewing project details."""
        response = with_admin_user.get(f'/projects/{test_project_id}')
        assert response.status_code == 200
        assert b'Test Project 1' in response.data
        assert b'This is a test project' in response.data
        assert b'In Progress' in response.data
    
    def test_create_project(self, with_admin_user, app, test_project_data):
        """Test creating a new project."""
        response = with_admin_user.post(
            '/projects/create',
            data=test_project_data,
            follow_redirects=True
        )
        assert response.status_code == 200
        assert b'Project created successfully' in response.data or b'Test New Project' in response.data
        
        # Verify project was added to the database
        with app.app_context():
            db = get_db()
            project = db.execute(
                "SELECT * FROM projects WHERE name = 'Test New Project'"
            ).fetchone()
            assert project is not None
            assert project['description'] == 'This is a test project'
            assert project['status'] == 'Planning'
            assert float(project['budget']) == 25000.00
    
    def test_edit_project(self, with_admin_user, app, test_project_id):
        """Test editing an existing project."""
        # Get current project data
        with app.app_context():
            db = get_db()
            project = db.execute(f"SELECT * FROM projects WHERE id = {test_project_id}").fetchone()
        
        # Modify data
        updated_data = {
            'name': project['name'],
            'client_id': project['client_id'],
            'description': 'Updated project description',  # Changed
            'status': 'Completed',  # Changed
            'start_date': project['start_date'],
            'end_date': project['end_date'],
            'budget': 60000.00,  # Changed
            'notes': 'Updated notes'  # New
        }
        
        response = with_admin_user.post(
            f'/projects/{test_project_id}/edit',
            data=updated_data,
            follow_redirects=True
        )
        assert response.status_code == 200
        assert b'Project updated successfully' in response.data or b'Updated project description' in response.data
        
        # Verify project was updated in the database
        with app.app_context():
            db = get_db()
            updated_project = db.execute(
                f"SELECT * FROM projects WHERE id = {test_project_id}"
            ).fetchone()
            assert updated_project['description'] == 'Updated project description'
            assert updated_project['status'] == 'Completed'
            assert float(updated_project['budget']) == 60000.00
    
    def test_add_task_to_project(self, with_admin_user, app, test_project_id, test_task_data):
        """Test adding a task to a project."""
        response = with_admin_user.post(
            f'/projects/{test_project_id}/tasks/add',
            data=test_task_data,
            follow_redirects=True
        )
        assert response.status_code == 200
        assert b'Task added successfully' in response.data or b'Test Task' in response.data
        
        # Verify task was added to the database
        with app.app_context():
            db = get_db()
            task = db.execute(
                "SELECT * FROM tasks WHERE title = 'Test Task'"
            ).fetchone()
            assert task is not None
            assert task['description'] == 'This is a test task'
            assert task['status'] == 'To Do'
            assert task['priority'] == 'Medium'
            assert task['project_id'] == test_project_id
    
    def test_delete_project(self, with_admin_user, app, test_project_id):
        """Test deleting a project."""
        response = with_admin_user.post(
            f'/projects/{test_project_id}/delete',
            follow_redirects=True
        )
        assert response.status_code == 200
        assert b'Project deleted successfully' in response.data or b'Project removed' in response.data
        
        # Verify project was deleted/deactivated in the database
        with app.app_context():
            db = get_db()
            project = db.execute(
                f"SELECT * FROM projects WHERE id = {test_project_id}"
            ).fetchone()
            
            # Depending on implementation, either project is deleted or marked inactive
            if project:
                assert 'active' in project.keys() and project['active'] == 0
            else:
                assert project is None
    
    def test_project_timeline(self, with_admin_user, test_project_id):
        """Test viewing project timeline."""
        response = with_admin_user.get(f'/projects/{test_project_id}/timeline')
        assert response.status_code == 200
        assert b'Timeline' in response.data
        assert b'Test Project 1' in response.data
    
    def test_unauthorized_project_access(self, client):
        """Test unauthorized access to project pages."""
        # Try accessing projects without login
        response = client.get('/projects/', follow_redirects=True)
        assert response.status_code == 200
        assert b'Log In' in response.data 