import os
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

# Get environment variables
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

# Create Supabase client with service role key
supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

# Key tables to check
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

print('Checking tables in Supabase:')
for table in tables_to_check:
    try:
        # Try to get just one row to check if table exists
        response = supabase.table(table).select('*').limit(1).execute()
        print(f'✅ Table {table} exists')
        
        # Try to insert a dummy record to test permissions
        try:
            # For testing only - we'll immediately delete this
            dummy_data = {'test_column': 'test_value'}
            insert_response = supabase.table(table).insert(dummy_data).execute()
            print(f'  ✅ Insert permission OK')
            
            # If insert succeeded, try to delete it
            if insert_response.data and len(insert_response.data) > 0:
                record_id = insert_response.data[0].get('id')
                if record_id:
                    supabase.table(table).delete().eq('id', record_id).execute()
                    print(f'  ✅ Delete permission OK')
        except Exception as e:
            print(f'  ❌ Write permission issue: {str(e)[:100]}...')
            
    except Exception as e:
        print(f'❌ Table {table} does not exist or is not accessible')
        print(f'   Error: {str(e)[:100]}...') 