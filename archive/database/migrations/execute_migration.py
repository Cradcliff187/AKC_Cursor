import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Supabase credentials
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

# Read the SQL file
with open('migrations/create_users_table.sql', 'r') as f:
    sql = f.read()

# Set up headers
headers = {
    'apikey': key,
    'Authorization': f'Bearer {key}',
    'Content-Type': 'application/json',
    'Prefer': 'return=minimal'
}

# Execute the SQL
try:
    response = requests.post(
        f"{url}/rest/v1/",
        headers=headers,
        json={'query': sql}
    )
    
    if response.status_code == 200:
        print("Migration completed successfully!")
    else:
        print(f"Error executing migration: {response.text}")
except Exception as e:
    print(f"Error executing migration: {e}") 