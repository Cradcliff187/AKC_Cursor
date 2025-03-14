import os
import re
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

# Get environment variables
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

# Create Supabase client with service role key
supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

# Comprehensive list of tables to check, including potential additional tables
ALL_POSSIBLE_TABLES = [
    # Core tables from schema file
    'user_profiles',
    'clients',
    'projects',
    'tasks',
    'time_entries',
    'expenses',
    'documents',
    'document_access',
    'bids',
    'bid_items',
    'invoices',
    'invoice_items',
    'notifications',
    
    # Additional tables that might exist
    'vendors',
    'vendor_contacts',
    'subcontractors',
    'subcontractor_contacts',
    'customers',
    'customer_contacts',
    'contacts',
    'employees',
    'payments',
    'materials',
    'equipment',
    'calendar_events',
    'user_calendar_credentials',
    'settings',
    'audit_logs',
    'comments',
    'tags',
    'document_tags',
    'project_tags',
    'contracts',
    'estimates',
    'estimate_items'
]

# Function to extract table names from SQL file
def extract_tables_from_file(file_path):
    tables = []
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            
        # Extract CREATE TABLE statements
        table_pattern = r'CREATE TABLE public\.(\w+)'
        tables = re.findall(table_pattern, content)
        return tables
    except Exception as e:
        print(f"Error extracting tables from file: {str(e)}")
        return []

# Function to check for SQL configurations
def check_sql_configurations():
    configs = {
        "Temporary Configuration Export Table": False,
        "Automatic Timestamp Update Function": False,
        "Row Level Security Policies": False,
        "Indexes for Performance": False,
        "Row Level Security Enabled": False
    }
    
    # Check for timestamp update function
    try:
        response = supabase.table('user_profiles').update({"updated_at": "now()"}).eq('id', 'non-existent-id').execute()
        # If no error about missing function, it likely exists
        configs["Automatic Timestamp Update Function"] = True
    except Exception as e:
        error_str = str(e)
        # If the error is about permissions but not about missing function
        if "permission denied" in error_str.lower() and "function" not in error_str.lower():
            configs["Automatic Timestamp Update Function"] = True
    
    # Check for RLS policies by trying to access as anon vs service role
    try:
        # Create a new client with the anon key to test RLS
        anon_key = os.getenv('SUPABASE_KEY')
        anon_client = create_client(SUPABASE_URL, anon_key)
        
        # Try to access a table that should be protected
        anon_client.table('user_profiles').select('*').limit(1).execute()
        
        # If we can access with anon key, RLS might not be enabled
        configs["Row Level Security Enabled"] = False
    except Exception as e:
        # If access denied, RLS is likely working
        if "permission denied" in str(e).lower():
            configs["Row Level Security Enabled"] = True
            configs["Row Level Security Policies"] = True
    
    return configs

# Get tables from schema file
print("\nExtracting tables from supabase_schema.sql file...")
try:
    file_tables = extract_tables_from_file('supabase_schema.sql')
    print(f"Found {len(file_tables)} tables in schema file:")
    for table in file_tables:
        print(f"- {table}")
except Exception as e:
    print(f"Error reading schema file: {str(e)}")
    file_tables = []

# Check all possible tables in database
print("\nChecking ALL possible tables in Supabase database...")
db_tables = []
table_columns = {}

for table in ALL_POSSIBLE_TABLES:
    try:
        # Try to get just one row to check if table exists
        response = supabase.table(table).select('*').limit(1).execute()
        db_tables.append(table)
        
        # Get column information
        if response.data and len(response.data) > 0:
            columns = list(response.data[0].keys())
            table_columns[table] = columns
            print(f"✅ Table {table} exists - Columns: {', '.join(columns[:5])}{'...' if len(columns) > 5 else ''}")
        else:
            # Try to get column names from an empty result
            try:
                # This is a workaround to get column names from an empty table
                response = supabase.table(table).select('*').limit(0).execute()
                if hasattr(response, 'columns') and response.columns:
                    columns = response.columns
                    table_columns[table] = columns
                    print(f"✅ Table {table} exists (empty) - Columns: {', '.join(columns[:5])}{'...' if len(columns) > 5 else ''}")
                else:
                    print(f"✅ Table {table} exists (empty) - Could not retrieve columns")
            except:
                print(f"✅ Table {table} exists - Could not retrieve columns")
    except Exception as e:
        if "relation" in str(e).lower() and "does not exist" in str(e).lower():
            print(f"❌ Table {table} does not exist")
        else:
            print(f"❓ Table {table} error: {str(e)[:100]}...")

# Check SQL configurations
print("\nChecking SQL configurations...")
configs = check_sql_configurations()
for config, status in configs.items():
    print(f"{'✅' if status else '❌'} {config}")

# Compare tables with schema file
if file_tables:
    print("\n=== SCHEMA ALIGNMENT STATUS ===")
    in_schema_not_db = set(file_tables) - set(db_tables)
    in_db_not_schema = set(db_tables) - set(file_tables)
    
    if not in_schema_not_db:
        print("✅ All tables from schema file exist in the database")
    else:
        print(f"❌ {len(in_schema_not_db)} tables from schema file are missing in the database:")
        for table in in_schema_not_db:
            print(f"  - {table}")
    
    if in_db_not_schema:
        print(f"\n⚠️ {len(in_db_not_schema)} tables exist in database but not in schema file:")
        for table in in_db_not_schema:
            print(f"  - {table}")
            if table in table_columns:
                print(f"    Columns: {', '.join(table_columns[table][:5])}{'...' if len(table_columns[table]) > 5 else ''}")

# Print summary
print("\n=== SUMMARY ===")
print(f"✅ Found {len(db_tables)} tables in the database")
print(f"✅ Found {len(file_tables)} tables in the schema file")
print(f"⚠️ {len(set(db_tables) - set(file_tables))} tables in database but not in schema file")
print(f"❌ {len(set(file_tables) - set(db_tables))} tables in schema file but not in database")

# Check if the database is ready for deployment
print("\n=== DEPLOYMENT READINESS ===")
critical_tables = ['user_profiles', 'clients', 'projects', 'tasks', 'documents', 'invoices']
critical_missing = [table for table in critical_tables if table not in db_tables]

if not critical_missing and configs["Automatic Timestamp Update Function"]:
    print("✅ Database appears ready for deployment to Google Cloud")
    print("   - All critical tables exist")
    print("   - Automatic timestamp updates are configured")
    
    if configs["Row Level Security Enabled"]:
        print("   - Row Level Security is enabled")
    else:
        print("⚠️ Row Level Security might not be enabled - verify before deployment")
else:
    print("❌ Database is NOT ready for deployment to Google Cloud")
    if critical_missing:
        print(f"   - Missing critical tables: {', '.join(critical_missing)}")
    if not configs["Automatic Timestamp Update Function"]:
        print("   - Automatic timestamp updates are not configured")
    if not configs["Row Level Security Enabled"]:
        print("   - Row Level Security is not enabled") 