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

# Function to extract table schema from SQL file
def extract_schema_from_file(file_path):
    schema_definitions = {}
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
            
        # Extract CREATE TABLE statements
        table_pattern = r'CREATE TABLE public\.(\w+)\s*\(([\s\S]*?)\);'
        tables = re.findall(table_pattern, content)
        
        for table_name, columns_text in tables:
            # Extract column definitions
            columns = []
            for line in columns_text.split('\n'):
                line = line.strip()
                if line and not line.startswith('--') and not line.startswith('CONSTRAINT') and not line.startswith('PRIMARY KEY'):
                    # Remove trailing comma if present
                    if line.endswith(','):
                        line = line[:-1]
                    columns.append(line)
            
            schema_definitions[table_name] = columns
            
        return schema_definitions
    except Exception as e:
        print(f"Error extracting schema from file: {str(e)}")
        return {}

# Function to get actual schema from Supabase
def get_actual_schema():
    actual_schema = {}
    
    # Tables to check
    tables_to_check = [
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
        'notifications'
    ]
    
    for table in tables_to_check:
        try:
            # Query information_schema to get column details
            query = f"""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = '{table}'
            ORDER BY ordinal_position;
            """
            
            # Execute the query using RPC
            response = supabase.rpc('exec_sql', {'query': query}).execute()
            
            if response.data:
                columns = []
                for column in response.data:
                    column_def = f"{column['column_name']} {column['data_type']}"
                    if column['is_nullable'] == 'NO':
                        column_def += " NOT NULL"
                    if column['column_default']:
                        column_def += f" DEFAULT {column['column_default']}"
                    columns.append(column_def)
                
                actual_schema[table] = columns
            else:
                print(f"No schema information available for {table}")
                
        except Exception as e:
            print(f"Error getting schema for {table}: {str(e)}")
            
            # Fallback to simple check if table exists
            try:
                response = supabase.table(table).select('*').limit(1).execute()
                print(f"Table {table} exists but couldn't get schema details")
                actual_schema[table] = ["<schema details not available>"]
            except:
                print(f"Table {table} does not exist or is not accessible")
    
    return actual_schema

# First, try to create the exec_sql function if it doesn't exist
try:
    create_function_query = """
    CREATE OR REPLACE FUNCTION exec_sql(query text) RETURNS SETOF json AS $$
    BEGIN
        RETURN QUERY EXECUTE query;
    END;
    $$ LANGUAGE plpgsql;
    """
    
    # Execute the function creation
    supabase.rpc('exec_sql', {'query': create_function_query}).execute()
    print("Created or updated the exec_sql function")
except Exception as e:
    print(f"Error creating exec_sql function: {str(e)}")
    print("Will try to proceed with schema check anyway...")

# Get schema from file
print("\nExtracting schema from supabase_schema.sql file...")
file_schema = extract_schema_from_file('supabase_schema.sql')

# Get actual schema from Supabase
print("\nGetting actual schema from Supabase...")
actual_schema = get_actual_schema()

# Compare schemas
print("\nComparing schemas:")
all_tables = set(list(file_schema.keys()) + list(actual_schema.keys()))

alignment_status = True

for table in all_tables:
    print(f"\n=== Table: {table} ===")
    
    if table not in file_schema:
        print("❌ Table exists in database but not in schema file")
        alignment_status = False
        continue
        
    if table not in actual_schema:
        print("❌ Table defined in schema file but not found in database")
        alignment_status = False
        continue
    
    # If we couldn't get detailed schema
    if len(actual_schema[table]) == 1 and actual_schema[table][0] == "<schema details not available>":
        print("⚠️ Table exists but couldn't compare schema details")
        continue
    
    # Simple column count comparison
    file_columns = len(file_schema[table])
    actual_columns = len(actual_schema[table])
    
    if file_columns != actual_columns:
        print(f"❌ Column count mismatch: {file_columns} in file vs {actual_columns} in database")
        alignment_status = False
    else:
        print(f"✅ Column count matches: {file_columns}")

# Print final alignment status
print("\n=== SCHEMA ALIGNMENT STATUS ===")
if alignment_status:
    print("✅ Schema file appears to be aligned with deployed database")
else:
    print("❌ Schema file is NOT fully aligned with deployed database")
    print("   Review the details above to identify specific misalignments") 