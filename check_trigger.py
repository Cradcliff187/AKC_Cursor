import psycopg2
from dotenv import load_dotenv
import os

def check_trigger_function():
    load_dotenv()
    
    # Construct the connection string
    db_url = 'postgresql://postgres:' + os.getenv('SUPABASE_DB_PASSWORD') + '@db.' + os.getenv('SUPABASE_URL').split('//')[1].split('.')[0] + '.supabase.co:5432/postgres'
    
    try:
        # Connect to the database
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        # Check trigger function
        cur.execute("SELECT prosrc FROM pg_proc WHERE proname = 'update_updated_at_column'")
        result = cur.fetchone()
        print('Trigger function definition:', result[0] if result else 'Not found')
        
        # Check triggers on tables
        tables = ['user_profiles', 'clients', 'projects', 'tasks', 'time_entries', 
                 'expenses', 'documents', 'bids', 'bid_items', 'invoices', 'invoice_items']
        
        print('\nChecking triggers on tables:')
        for table in tables:
            cur.execute("""
                SELECT t.tgname, pg_get_triggerdef(t.oid) 
                FROM pg_trigger t
                JOIN pg_class c ON t.tgrelid = c.oid
                JOIN pg_namespace n ON c.relnamespace = n.oid
                WHERE n.nspname = 'public'
                AND c.relname = %s
                AND t.tgname LIKE 'update_%%_updated_at'
            """, (table,))
            triggers = cur.fetchall()
            print(f'\n{table}:')
            if triggers:
                for trigger in triggers:
                    print(f'- {trigger[0]}: {trigger[1]}')
            else:
                print('No update_at trigger found')
        
    except Exception as e:
        print('Error:', str(e))
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    check_trigger_function() 