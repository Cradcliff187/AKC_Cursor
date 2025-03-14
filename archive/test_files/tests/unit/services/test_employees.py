"""
Unit tests for employees service
"""
import pytest
from datetime import datetime
from app.services.employees import (
    add_employee, edit_employee, delete_employee,
    get_employee_by_id, get_all_employees,
    get_employee_hourly_cost, calculate_labor_cost,
    get_department_statistics
)

def test_add_employee():
    """Test employee creation"""
    employee_data = {
        'name': 'John Doe',
        'email': 'john.doe@example.com',
        'position': 'Developer',
        'department': 'Engineering',
        'payment_type': 'salary',
        'annual_salary': 75000.00,
        'hours_per_week': 40,
        'is_active': True,
        'notes': 'Test employee'
    }
    
    employee = add_employee(employee_data)
    assert employee is not None
    assert employee['name'] == employee_data['name']
    assert employee['email'] == employee_data['email']
    assert employee['position'] == employee_data['position']
    assert employee['department'] == employee_data['department']
    assert employee['payment_type'] == employee_data['payment_type']
    assert employee['annual_salary'] == employee_data['annual_salary']
    assert employee['is_active'] == employee_data['is_active']

def test_edit_employee():
    """Test employee update"""
    # First create an employee
    employee_data = {
        'name': 'John Doe',
        'email': 'john.doe@example.com',
        'position': 'Developer',
        'department': 'Engineering',
        'payment_type': 'salary',
        'annual_salary': 75000.00,
        'hours_per_week': 40,
        'is_active': True,
        'notes': 'Test employee'
    }
    employee = add_employee(employee_data)
    
    # Update the employee
    update_data = {
        'department': 'Product',
        'position': 'Senior Developer',
        'annual_salary': 85000.00
    }
    updated_employee = edit_employee(employee['id'], update_data)
    
    assert updated_employee['department'] == update_data['department']
    assert updated_employee['position'] == update_data['position']
    assert updated_employee['annual_salary'] == update_data['annual_salary']

def test_delete_employee():
    """Test employee deletion"""
    # Create an employee
    employee_data = {
        'name': 'John Doe',
        'email': 'john.doe@example.com',
        'position': 'Developer',
        'department': 'Engineering',
        'payment_type': 'salary',
        'annual_salary': 75000.00,
        'hours_per_week': 40,
        'is_active': True,
        'notes': 'Test employee'
    }
    employee = add_employee(employee_data)
    
    # Delete the employee
    delete_employee(employee['id'])
    
    # Verify employee is marked as inactive
    deleted_employee = get_employee_by_id(employee['id'])
    assert deleted_employee['is_active'] is False

def test_get_employee_hourly_cost():
    """Test calculating employee hourly cost"""
    # Test salary employee
    salary_employee = {
        'name': 'John Doe',
        'email': 'john.doe@example.com',
        'position': 'Developer',
        'department': 'Engineering',
        'payment_type': 'salary',
        'annual_salary': 75000.00,
        'hours_per_week': 40,
        'is_active': True
    }
    employee = add_employee(salary_employee)
    
    hourly_cost = get_employee_hourly_cost(employee['id'])
    expected_hourly = 75000.00 / (52 * 40)  # annual salary / (52 weeks * hours per week)
    assert abs(hourly_cost - expected_hourly) < 0.01
    
    # Test hourly employee
    hourly_employee = {
        'name': 'Jane Doe',
        'email': 'jane.doe@example.com',
        'position': 'Contractor',
        'department': 'Engineering',
        'payment_type': 'hourly',
        'hourly_rate': 50.00,
        'hours_per_week': 40,
        'is_active': True
    }
    employee = add_employee(hourly_employee)
    
    hourly_cost = get_employee_hourly_cost(employee['id'])
    assert hourly_cost == 50.00

def test_calculate_labor_cost():
    """Test calculating labor cost for hours worked"""
    # Create an hourly employee
    employee_data = {
        'name': 'Jane Doe',
        'email': 'jane.doe@example.com',
        'position': 'Contractor',
        'department': 'Engineering',
        'payment_type': 'hourly',
        'hourly_rate': 50.00,
        'hours_per_week': 40,
        'is_active': True
    }
    employee = add_employee(employee_data)
    
    # Calculate cost for 10 hours
    hours_worked = 10
    labor_cost = calculate_labor_cost(employee['id'], hours_worked)
    assert labor_cost == 50.00 * hours_worked

def test_get_department_statistics():
    """Test getting department statistics"""
    # Create employees in different departments
    departments = ['Engineering', 'Product', 'Design']
    for dept in departments:
        for i in range(2):
            employee_data = {
                'name': f'Employee {i}',
                'email': f'employee{i}@{dept.lower()}.com',
                'position': 'Developer',
                'department': dept,
                'payment_type': 'salary',
                'annual_salary': 75000.00,
                'hours_per_week': 40,
                'is_active': True
            }
            add_employee(employee_data)
    
    # Get department statistics
    stats = get_department_statistics()
    
    # Verify statistics
    assert len(stats['department_labels']) == 3
    assert len(stats['department_counts']) == 3
    assert len(stats['department_costs']) == 3
    assert all(count == 2 for count in stats['department_counts'])
    assert all(dept in stats['department_labels'] for dept in departments) 