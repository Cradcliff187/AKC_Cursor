#!/usr/bin/env python3
"""
Schema Comparison Tool

This script compares the schema in Supabase with the models in the codebase
to identify missing tables and fields that need to be implemented.
"""

import os
import sys
import json
import requests
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

# Get environment variables
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

# Critical business tables to focus on
CRITICAL_TABLES = [
    'invoices',
    'invoice_items',
    'bids',
    'bid_items',
    'payments',
    'expenses',
    'time_entries',
    'materials',
    'subcontractors',
    'equipment',
    'notifications',
    'documents',
    'user_profiles'
]

def check_environment():
    """Check if all required environment variables are set."""
    if not SUPABASE_URL:
        print("Error: SUPABASE_URL environment variable is not set.")
        return False
    
    if not SUPABASE_SERVICE_KEY:
        print("Error: SUPABASE_SERVICE_ROLE_KEY environment variable is not set.")
        return False
    
    return True

def create_supabase_client():
    """Create a Supabase client."""
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        print("Error: Supabase credentials not set.")
        return None
    
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
        print("Supabase client created successfully.")
        return supabase
    except Exception as e:
        print(f"Error creating Supabase client: {str(e)}")
        return None

def get_supabase_schema(supabase):
    """Get the schema from Supabase."""
    try:
        # Query to get all tables
        tables_query = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_type = 'BASE TABLE'
        AND table_name NOT LIKE 'pg_%'
        AND table_name NOT LIKE 'temp_%'
        ORDER BY table_name;
        """
        
        # Execute the query using the exec_sql function if it exists
        try:
            response = supabase.rpc('exec_sql', {'query': tables_query}).execute()
            if hasattr(response, 'data'):
                tables = response.data
            else:
                print("Error: Could not retrieve tables from Supabase.")
                return None
        except Exception as e:
            print(f"Error executing SQL: {str(e)}")
            print("Falling back to direct query...")
            
            # Fallback to direct query if exec_sql doesn't exist
            url = f"{SUPABASE_URL}/rest/v1/rpc/exec_sql"
            headers = {
                "apikey": SUPABASE_SERVICE_KEY,
                "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
                "Content-Type": "application/json"
            }
            data = {"query": tables_query}
            
            response = requests.post(url, headers=headers, json=data)
            if response.status_code == 200:
                tables = response.json()
            else:
                print(f"Error: Could not retrieve tables. Status code: {response.status_code}")
                return None
        
        # Get columns for each table
        schema = {}
        for table in tables:
            table_name = table.get('table_name')
            if not table_name:
                continue
                
            columns_query = f"""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_schema = 'public'
            AND table_name = '{table_name}'
            ORDER BY ordinal_position;
            """
            
            try:
                response = supabase.rpc('exec_sql', {'query': columns_query}).execute()
                if hasattr(response, 'data'):
                    columns = response.data
                    schema[table_name] = columns
                else:
                    print(f"Error: Could not retrieve columns for table {table_name}.")
            except Exception as e:
                print(f"Error getting columns for {table_name}: {str(e)}")
                
                # Fallback to direct query
                url = f"{SUPABASE_URL}/rest/v1/rpc/exec_sql"
                data = {"query": columns_query}
                
                response = requests.post(url, headers=headers, json=data)
                if response.status_code == 200:
                    columns = response.json()
                    schema[table_name] = columns
                else:
                    print(f"Error: Could not retrieve columns for {table_name}. Status code: {response.status_code}")
        
        return schema
    except Exception as e:
        print(f"Error getting Supabase schema: {str(e)}")
        return None

def scan_codebase_models(base_dir='.'):
    """Scan the codebase to find model definitions."""
    model_files = []
    model_definitions = {}
    
    # Find all potential model files
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.py') or file.endswith('.js') or file.endswith('.ts'):
                # Skip node_modules, venv, etc.
                if 'node_modules' in root or 'venv' in root or '.git' in root:
                    continue
                    
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                    # Look for model definitions
                    # This is a simple heuristic and might need refinement
                    if ('class' in content and ('model' in content.lower() or 'schema' in content.lower())) or \
                       ('interface' in content.lower() and 'model' in content.lower()) or \
                       ('type' in content.lower() and 'model' in content.lower()):
                        model_files.append(file_path)
    
    # Parse model files to extract table names and fields
    for file_path in model_files:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
                # Extract model name and fields
                # This is a simple approach and might need to be adapted based on your codebase
                if file_path.endswith('.py'):
                    # Python models
                    for line in content.split('\n'):
                        if 'class' in line and '(' in line:
                            class_def = line.split('class ')[1].split('(')[0].strip()
                            table_name = class_def.lower()
                            if 'model' in table_name:
                                table_name = table_name.replace('model', '').strip()
                            model_definitions[table_name] = {'file': file_path, 'fields': []}
                            
                        if '=' in line and ':' in line and 'class' not in line:
                            field = line.split('=')[0].strip()
                            if field and not field.startswith('_') and field not in ['id', 'created_at', 'updated_at']:
                                if table_name in model_definitions:
                                    model_definitions[table_name]['fields'].append(field)
                
                elif file_path.endswith('.js') or file_path.endswith('.ts'):
                    # JavaScript/TypeScript models
                    for line in content.split('\n'):
                        if 'interface' in line or 'type' in line and '{' in content:
                            interface_def = line.split('interface ')[1].split('{')[0].strip() if 'interface' in line else line.split('type ')[1].split('=')[0].strip()
                            table_name = interface_def.lower()
                            if 'model' in table_name or 'interface' in table_name:
                                table_name = table_name.replace('model', '').replace('interface', '').strip()
                            model_definitions[table_name] = {'file': file_path, 'fields': []}
                            
                        if ':' in line and ';' in line:
                            field = line.split(':')[0].strip()
                            if field and not field.startswith('_') and field not in ['id', 'createdAt', 'updatedAt', 'created_at', 'updated_at']:
                                if table_name in model_definitions:
                                    model_definitions[table_name]['fields'].append(field)
        except Exception as e:
            print(f"Error parsing model file {file_path}: {str(e)}")
    
    return model_definitions

def compare_schemas(supabase_schema, codebase_models):
    """Compare Supabase schema with codebase models to identify gaps."""
    missing_tables = []
    incomplete_tables = []
    
    # Check for missing tables
    for table_name in supabase_schema:
        if table_name.lower() not in codebase_models:
            missing_tables.append({
                'table_name': table_name,
                'columns': supabase_schema[table_name]
            })
    
    # Check for incomplete tables (missing fields)
    for table_name, columns in supabase_schema.items():
        if table_name.lower() in codebase_models:
            model_fields = codebase_models[table_name.lower()]['fields']
            missing_fields = []
            
            for column in columns:
                column_name = column.get('column_name')
                if column_name and column_name not in ['id', 'created_at', 'updated_at'] and column_name not in model_fields:
                    missing_fields.append({
                        'column_name': column_name,
                        'data_type': column.get('data_type'),
                        'is_nullable': column.get('is_nullable'),
                        'column_default': column.get('column_default')
                    })
            
            if missing_fields:
                incomplete_tables.append({
                    'table_name': table_name,
                    'file': codebase_models[table_name.lower()]['file'],
                    'missing_fields': missing_fields
                })
    
    return {
        'missing_tables': missing_tables,
        'incomplete_tables': incomplete_tables
    }

def generate_implementation_plan(comparison_results):
    """Generate an implementation plan based on comparison results."""
    plan = {
        'critical_missing_tables': [],
        'critical_incomplete_tables': [],
        'other_missing_tables': [],
        'other_incomplete_tables': []
    }
    
    # Categorize missing tables
    for table in comparison_results['missing_tables']:
        table_name = table['table_name']
        if table_name in CRITICAL_TABLES:
            plan['critical_missing_tables'].append(table)
        else:
            plan['other_missing_tables'].append(table)
    
    # Categorize incomplete tables
    for table in comparison_results['incomplete_tables']:
        table_name = table['table_name']
        if table_name in CRITICAL_TABLES:
            plan['critical_incomplete_tables'].append(table)
        else:
            plan['other_incomplete_tables'].append(table)
    
    return plan

def output_results(implementation_plan):
    """Output the implementation plan in a readable format."""
    print("\n=== SCHEMA COMPARISON RESULTS ===\n")
    
    # Critical missing tables
    print("\n--- CRITICAL MISSING TABLES ---")
    if implementation_plan['critical_missing_tables']:
        for table in implementation_plan['critical_missing_tables']:
            print(f"\nTable: {table['table_name']}")
            print("Columns:")
            for column in table['columns']:
                print(f"  - {column.get('column_name')} ({column.get('data_type')})")
    else:
        print("None")
    
    # Critical incomplete tables
    print("\n--- CRITICAL INCOMPLETE TABLES ---")
    if implementation_plan['critical_incomplete_tables']:
        for table in implementation_plan['critical_incomplete_tables']:
            print(f"\nTable: {table['table_name']} (File: {table['file']})")
            print("Missing Fields:")
            for field in table['missing_fields']:
                print(f"  - {field['column_name']} ({field['data_type']})")
    else:
        print("None")
    
    # Other missing tables
    print("\n--- OTHER MISSING TABLES ---")
    if implementation_plan['other_missing_tables']:
        for table in implementation_plan['other_missing_tables']:
            print(f"\nTable: {table['table_name']}")
            print("Columns:")
            for column in table['columns']:
                print(f"  - {column.get('column_name')} ({column.get('data_type')})")
    else:
        print("None")
    
    # Other incomplete tables
    print("\n--- OTHER INCOMPLETE TABLES ---")
    if implementation_plan['other_incomplete_tables']:
        for table in implementation_plan['other_incomplete_tables']:
            print(f"\nTable: {table['table_name']} (File: {table['file']})")
            print("Missing Fields:")
            for field in table['missing_fields']:
                print(f"  - {field['column_name']} ({field['data_type']})")
    else:
        print("None")
    
    # Save results to file
    with open('schema_comparison_results.json', 'w') as f:
        json.dump(implementation_plan, f, indent=2)
    
    print("\nResults saved to schema_comparison_results.json")

def main():
    """Main function."""
    print("Starting schema comparison...")
    
    # Check environment
    if not check_environment():
        return False
    
    # Create Supabase client
    supabase = create_supabase_client()
    if not supabase:
        return False
    
    # Get Supabase schema
    print("Retrieving Supabase schema...")
    supabase_schema = get_supabase_schema(supabase)
    if not supabase_schema:
        return False
    
    # Scan codebase for models
    print("Scanning codebase for models...")
    codebase_models = scan_codebase_models()
    
    # Compare schemas
    print("Comparing schemas...")
    comparison_results = compare_schemas(supabase_schema, codebase_models)
    
    # Generate implementation plan
    print("Generating implementation plan...")
    implementation_plan = generate_implementation_plan(comparison_results)
    
    # Output results
    output_results(implementation_plan)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 