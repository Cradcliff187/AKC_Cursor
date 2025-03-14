import pytest
from unittest.mock import MagicMock, patch

# Import the functions to test
from app.services.employees import get_department_statistics, get_employee_hourly_cost, get_all_employees


class TestEmployeeStatistics:
    def test_get_department_statistics(self, app, monkeypatch):
        """Test getting department statistics"""
        # Mock data for employees
        mock_employees = [
            {
                'id': 1,
                'name': 'John Doe',
                'department': 'Engineering',
                'is_active': True
            },
            {
                'id': 2,
                'name': 'Jane Smith',
                'department': 'Engineering',
                'is_active': True
            },
            {
                'id': 3,
                'name': 'Bob Johnson',
                'department': 'HR',
                'is_active': True
            },
            {
                'id': 4,
                'name': 'Alice Brown',
                'department': 'Marketing',
                'is_active': True
            },
            {
                'id': 5,
                'name': 'Inactive Employee',
                'department': 'Engineering',
                'is_active': False  # This one should be ignored
            }
        ]
        
        # Mock hourly costs
        hourly_costs = {
            1: 50.0,  # Engineering
            2: 60.0,  # Engineering
            3: 40.0,  # HR
            4: 45.0,  # Marketing
            5: 55.0,  # Inactive - should be ignored
        }
        
        # Mock the get_all_employees function
        monkeypatch.setattr('app.services.employees.get_all_employees', lambda: mock_employees)
        
        # Mock the get_employee_hourly_cost function
        def mock_get_hourly_cost(employee_id):
            return hourly_costs.get(employee_id, 0.0)
        
        monkeypatch.setattr('app.services.employees.get_employee_hourly_cost', mock_get_hourly_cost)
        
        with app.app_context():
            result = get_department_statistics()
            
            # Check result structure
            assert 'department_labels' in result
            assert 'department_counts' in result
            assert 'department_costs' in result
            
            # Verify departments
            assert set(result['department_labels']) == {'Engineering', 'HR', 'Marketing'}
            
            # Get positions for easy lookup
            positions = {dept: i for i, dept in enumerate(result['department_labels'])}
            
            # Verify employee counts
            assert result['department_counts'][positions['Engineering']] == 2
            assert result['department_counts'][positions['HR']] == 1
            assert result['department_counts'][positions['Marketing']] == 1
            
            # Verify average hourly costs
            assert result['department_costs'][positions['Engineering']] == 55.0  # (50 + 60) / 2
            assert result['department_costs'][positions['HR']] == 40.0
            assert result['department_costs'][positions['Marketing']] == 45.0
    
    def test_get_department_statistics_empty(self, app, monkeypatch):
        """Test getting department statistics with no employees"""
        # Mock empty employees list
        monkeypatch.setattr('app.services.employees.get_all_employees', lambda: [])
        
        with app.app_context():
            result = get_department_statistics()
            
            # Check result structure with empty data
            assert 'department_labels' in result
            assert 'department_counts' in result
            assert 'department_costs' in result
            
            # All should be empty lists
            assert result['department_labels'] == []
            assert result['department_counts'] == []
            assert result['department_costs'] == []
            
    def test_get_department_statistics_inactive_only(self, app, monkeypatch):
        """Test getting department statistics with only inactive employees"""
        # Mock data with only inactive employees
        mock_employees = [
            {
                'id': 1,
                'name': 'John Doe',
                'department': 'Engineering',
                'is_active': False
            },
            {
                'id': 2,
                'name': 'Jane Smith',
                'department': 'HR',
                'is_active': False
            }
        ]
        
        # Mock the get_all_employees function
        monkeypatch.setattr('app.services.employees.get_all_employees', lambda: mock_employees)
        
        with app.app_context():
            result = get_department_statistics()
            
            # Check result structure with empty data
            assert 'department_labels' in result
            assert 'department_counts' in result
            assert 'department_costs' in result
            
            # All should be empty lists since no active employees
            assert result['department_labels'] == []
            assert result['department_counts'] == []
            assert result['department_costs'] == []
            
    def test_get_department_statistics_null_department(self, app, monkeypatch):
        """Test getting department statistics with null department values"""
        # Mock data with some null department values
        mock_employees = [
            {
                'id': 1,
                'name': 'John Doe',
                'department': None,  # Null department
                'is_active': True
            },
            {
                'id': 2,
                'name': 'Jane Smith',
                'department': 'HR',
                'is_active': True
            },
            {
                'id': 3,
                'name': 'Bob Johnson',
                'department': '',  # Empty string department
                'is_active': True
            }
        ]
        
        # Mock hourly costs
        hourly_costs = {
            1: 50.0,  # None department
            2: 40.0,  # HR
            3: 45.0,  # Empty department
        }
        
        # Mock the get_all_employees function
        monkeypatch.setattr('app.services.employees.get_all_employees', lambda: mock_employees)
        
        # Mock the get_employee_hourly_cost function
        def mock_get_hourly_cost(employee_id):
            return hourly_costs.get(employee_id, 0.0)
        
        monkeypatch.setattr('app.services.employees.get_employee_hourly_cost', mock_get_hourly_cost)
        
        with app.app_context():
            result = get_department_statistics()
            
            # Check result structure
            assert 'department_labels' in result
            assert 'department_counts' in result
            assert 'department_costs' in result
            
            # Verify departments (should include None and empty string as departments)
            department_set = set(result['department_labels'])
            assert 'HR' in department_set
            assert None in department_set or '' in department_set
            
            # Get positions for easy lookup
            positions = {dept: i for i, dept in enumerate(result['department_labels'])}
            
            # Verify employee counts
            assert result['department_counts'][positions['HR']] == 1
            
            # Verify average hourly costs
            assert result['department_costs'][positions['HR']] == 40.0 