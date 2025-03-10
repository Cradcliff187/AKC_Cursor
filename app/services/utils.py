import uuid
import random
import string
from datetime import datetime

def generate_id(prefix='', length=8):
    """Generate a unique ID with optional prefix
    
    Args:
        prefix (str): Optional prefix for the ID (e.g., 'PROJ', 'CUST')
        length (int): Length of the random part of the ID
        
    Returns:
        str: A unique ID with the format: {prefix}-{random_alphanumeric}
    """
    # Generate a random alphanumeric string
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
    
    if prefix:
        return f"{prefix}-{random_part}"
    else:
        return random_part

def generate_project_id():
    """Generate a project ID following the pattern: PROJ-{random_alphanumeric}"""
    return generate_id(prefix='PROJ')

def generate_customer_id():
    """Generate a customer ID following the pattern: CUST-{random_alphanumeric}"""
    return generate_id(prefix='CUST')

def generate_vendor_id():
    """Generate a vendor ID following the pattern: VEND-{random_alphanumeric}"""
    return generate_id(prefix='VEND')

def generate_task_id():
    """Generate a task ID following the pattern: TASK-{random_alphanumeric}"""
    return generate_id(prefix='TASK')

def generate_document_id():
    """Generate a document ID following the pattern: DOC-{random_alphanumeric}"""
    return generate_id(prefix='DOC')

def generate_time_entry_id():
    """Generate a time entry ID following the pattern: TIME-{random_alphanumeric}"""
    return generate_id(prefix='TIME')

def generate_folder_name(customer_id, project_id, project_name):
    """Generate a folder name following the pattern in the JSON guide
    
    Args:
        customer_id (str): Customer ID
        project_id (str): Project ID
        project_name (str): Project name
        
    Returns:
        str: A folder name with the format: {CustomerID}-{ProjectID}-{ProjectName}
    """
    # Clean project name for folder use (remove special chars, replace spaces with underscores)
    clean_project_name = ''.join(c if c.isalnum() else '_' for c in project_name)
    return f"{customer_id}-{project_id}-{clean_project_name}" 