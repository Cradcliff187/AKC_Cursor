#!/usr/bin/env python
"""
Test Supabase API Integration

This script tests the integration between the FastAPI routes and Supabase.
It verifies that the API endpoints can successfully interact with Supabase
for CRUD operations on users, clients, and projects.
"""

import os
import sys
import json
import requests
from dotenv import load_dotenv
import uuid
import time
from datetime import datetime, date

# Load environment variables
load_dotenv()

# API base URL - use local development server or deployed URL
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# Test user credentials
TEST_USER_EMAIL = f"test-{uuid.uuid4()}@example.com"
TEST_USER_PASSWORD = "Test@123456"
TEST_USER_DATA = {
    "email": TEST_USER_EMAIL,
    "password": TEST_USER_PASSWORD,
    "first_name": "Test",
    "last_name": "User",
    "display_name": "Test User",
    "role": "employee"
}

# Test data
TEST_CLIENT = {
    "name": f"Test Client {uuid.uuid4()}",
    "contact_name": "John Contact",
    "email": "contact@example.com",
    "phone": "555-123-4567",
    "address": "123 Test St",
    "city": "Test City",
    "state": "TS",
    "zip_code": "12345",
    "company": "Test Company",
    "status": "active"
}

TEST_PROJECT = {
    "name": f"Test Project {uuid.uuid4()}",
    "description": "A test project for API integration",
    "status": "pending",
    "start_date": date.today().isoformat(),
    "budget": 50000.0,
    "address": "456 Project St",
    "city": "Project City",
    "state": "PS",
    "zip_code": "54321"
}

# Store created resources for cleanup
created_resources = {
    "user": None,
    "client": None,
    "project": None,
    "access_token": None
}

def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80)

def print_result(test_name, success, details=None):
    """Print a test result"""
    status = "✅ PASSED" if success else "❌ FAILED"
    print(f"{status} - {test_name}")
    if details and not success:
        print(f"  Details: {details}")

def register_user():
    """Register a test user"""
    print_header("REGISTERING TEST USER")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/users/register",
            json=TEST_USER_DATA
        )
        
        if response.status_code == 201:
            user_data = response.json()
            created_resources["user"] = user_data
            print_result("User Registration", True)
            print(f"Created user with ID: {user_data.get('id')}")
            return True
        else:
            print_result("User Registration", False, f"Status: {response.status_code}, Response: {response.text}")
            return False
    except Exception as e:
        print_result("User Registration", False, str(e))
        return False

def login_user():
    """Login with the test user"""
    print_header("LOGGING IN TEST USER")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/users/login",
            json={
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD
            }
        )
        
        if response.status_code == 200:
            login_data = response.json()
            created_resources["access_token"] = login_data.get("access_token")
            print_result("User Login", True)
            print(f"Received access token: {login_data.get('access_token')[:20]}...")
            return True
        else:
            print_result("User Login", False, f"Status: {response.status_code}, Response: {response.text}")
            return False
    except Exception as e:
        print_result("User Login", False, str(e))
        return False

def create_client():
    """Create a test client"""
    print_header("CREATING TEST CLIENT")
    
    if not created_resources["access_token"]:
        print_result("Create Client", False, "No access token available")
        return False
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/clients",
            json=TEST_CLIENT,
            headers={"Authorization": f"Bearer {created_resources['access_token']}"}
        )
        
        if response.status_code == 201:
            client_data = response.json()
            created_resources["client"] = client_data
            print_result("Create Client", True)
            print(f"Created client with ID: {client_data.get('id')}")
            return True
        else:
            print_result("Create Client", False, f"Status: {response.status_code}, Response: {response.text}")
            return False
    except Exception as e:
        print_result("Create Client", False, str(e))
        return False

def get_client():
    """Get the test client"""
    print_header("GETTING TEST CLIENT")
    
    if not created_resources["access_token"] or not created_resources["client"]:
        print_result("Get Client", False, "No access token or client available")
        return False
    
    try:
        client_id = created_resources["client"]["id"]
        response = requests.get(
            f"{API_BASE_URL}/api/clients/{client_id}",
            headers={"Authorization": f"Bearer {created_resources['access_token']}"}
        )
        
        if response.status_code == 200:
            client_data = response.json()
            print_result("Get Client", True)
            print(f"Retrieved client: {client_data.get('name')}")
            return True
        else:
            print_result("Get Client", False, f"Status: {response.status_code}, Response: {response.text}")
            return False
    except Exception as e:
        print_result("Get Client", False, str(e))
        return False

def create_project():
    """Create a test project"""
    print_header("CREATING TEST PROJECT")
    
    if not created_resources["access_token"] or not created_resources["client"]:
        print_result("Create Project", False, "No access token or client available")
        return False
    
    try:
        # Add client ID to project data
        project_data = TEST_PROJECT.copy()
        project_data["client_id"] = created_resources["client"]["id"]
        
        response = requests.post(
            f"{API_BASE_URL}/api/projects",
            json=project_data,
            headers={"Authorization": f"Bearer {created_resources['access_token']}"}
        )
        
        if response.status_code == 201:
            project_data = response.json()
            created_resources["project"] = project_data
            print_result("Create Project", True)
            print(f"Created project with ID: {project_data.get('id')}")
            return True
        else:
            print_result("Create Project", False, f"Status: {response.status_code}, Response: {response.text}")
            return False
    except Exception as e:
        print_result("Create Project", False, str(e))
        return False

def get_project():
    """Get the test project"""
    print_header("GETTING TEST PROJECT")
    
    if not created_resources["access_token"] or not created_resources["project"]:
        print_result("Get Project", False, "No access token or project available")
        return False
    
    try:
        project_id = created_resources["project"]["id"]
        response = requests.get(
            f"{API_BASE_URL}/api/projects/{project_id}",
            headers={"Authorization": f"Bearer {created_resources['access_token']}"}
        )
        
        if response.status_code == 200:
            project_data = response.json()
            print_result("Get Project", True)
            print(f"Retrieved project: {project_data.get('name')}")
            return True
        else:
            print_result("Get Project", False, f"Status: {response.status_code}, Response: {response.text}")
            return False
    except Exception as e:
        print_result("Get Project", False, str(e))
        return False

def update_project():
    """Update the test project"""
    print_header("UPDATING TEST PROJECT")
    
    if not created_resources["access_token"] or not created_resources["project"]:
        print_result("Update Project", False, "No access token or project available")
        return False
    
    try:
        project_id = created_resources["project"]["id"]
        update_data = {
            "status": "in_progress",
            "description": "Updated project description"
        }
        
        response = requests.patch(
            f"{API_BASE_URL}/api/projects/{project_id}",
            json=update_data,
            headers={"Authorization": f"Bearer {created_resources['access_token']}"}
        )
        
        if response.status_code == 200:
            project_data = response.json()
            print_result("Update Project", True)
            print(f"Updated project status: {project_data.get('status')}")
            return True
        else:
            print_result("Update Project", False, f"Status: {response.status_code}, Response: {response.text}")
            return False
    except Exception as e:
        print_result("Update Project", False, str(e))
        return False

def cleanup():
    """Clean up created resources"""
    print_header("CLEANING UP RESOURCES")
    
    if not created_resources["access_token"]:
        print("No access token available for cleanup")
        return
    
    # Delete project
    if created_resources["project"]:
        try:
            project_id = created_resources["project"]["id"]
            response = requests.delete(
                f"{API_BASE_URL}/api/projects/{project_id}",
                headers={"Authorization": f"Bearer {created_resources['access_token']}"}
            )
            print_result("Delete Project", response.status_code == 204)
        except Exception as e:
            print_result("Delete Project", False, str(e))
    
    # Delete client
    if created_resources["client"]:
        try:
            client_id = created_resources["client"]["id"]
            response = requests.delete(
                f"{API_BASE_URL}/api/clients/{client_id}",
                headers={"Authorization": f"Bearer {created_resources['access_token']}"}
            )
            print_result("Delete Client", response.status_code == 204)
        except Exception as e:
            print_result("Delete Client", False, str(e))
    
    # Delete user (if API supports it)
    if created_resources["user"]:
        try:
            user_id = created_resources["user"]["id"]
            response = requests.delete(
                f"{API_BASE_URL}/api/users/{user_id}",
                headers={"Authorization": f"Bearer {created_resources['access_token']}"}
            )
            print_result("Delete User", response.status_code == 204)
        except Exception as e:
            print_result("Delete User", False, str(e))

def run_tests():
    """Run all tests"""
    print_header("SUPABASE API INTEGRATION TESTS")
    print(f"Testing API at: {API_BASE_URL}")
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Run tests in sequence
        if not register_user():
            print("❌ Cannot continue without user registration")
            return 1
        
        if not login_user():
            print("❌ Cannot continue without user login")
            return 1
        
        if not create_client():
            print("❌ Cannot continue without client creation")
            return 1
        
        get_client()
        
        if not create_project():
            print("❌ Cannot continue without project creation")
            return 1
        
        get_project()
        update_project()
        
        # Print summary
        print_header("TEST SUMMARY")
        print("All tests completed.")
        
        return 0
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return 1
    finally:
        # Always attempt cleanup
        cleanup()

if __name__ == "__main__":
    sys.exit(run_tests()) 