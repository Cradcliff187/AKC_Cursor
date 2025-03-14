#!/usr/bin/env python3
"""
Test Supabase Connection

This script tests the connection to Supabase and performs a simple query.
"""

import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client
import json
from datetime import datetime

# Load environment variables
load_dotenv()

def test_supabase_connection():
    """Test the connection to Supabase."""
    # Get environment variables
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not supabase_url or not supabase_key or not service_key:
        print("Error: SUPABASE_URL, SUPABASE_KEY, and SUPABASE_SERVICE_ROLE_KEY must be set in environment variables.")
        return False
    
    print(f"Supabase URL: {supabase_url}")
    print(f"Supabase key length: {len(supabase_key)}")
    print(f"Supabase service key length: {len(service_key)}")
    
    try:
        # Create Supabase client with anonymous key
        print("\nCreating Supabase client with anonymous key...")
        supabase = create_client(supabase_url, supabase_key)
        
        # Test a simple query - get the first 5 user profiles
        print("Testing query: Get first 5 user profiles...")
        response = supabase.table("user_profiles").select("*").limit(5).execute()
        
        # Print the result
        print(f"Query successful! Found {len(response.data)} user profiles.")
        
        if len(response.data) > 0:
            print("\nFirst user profile:")
            print(json.dumps(response.data[0], indent=2, default=str))
        else:
            print("No user profiles found in the database yet.")
        
        # Create Supabase client with service role key
        print("\nCreating Supabase client with service role key...")
        admin_supabase = create_client(supabase_url, service_key)
        
        # Test a simple query with service role key
        print("Testing query with service role key: Get first 5 user profiles...")
        admin_response = admin_supabase.table("user_profiles").select("*").limit(5).execute()
        
        # Print the result
        print(f"Query with service role key successful! Found {len(admin_response.data)} user profiles.")
        
        # Save the results to a JSON file
        results = {
            "timestamp": str(datetime.now()),
            "anonymous_query": {
                "success": True,
                "count": len(response.data)
            },
            "service_role_query": {
                "success": True,
                "count": len(admin_response.data)
            }
        }
        
        with open("supabase_connection_test_results.json", "w") as f:
            json.dump(results, f, indent=2)
        
        print(f"\nResults saved to supabase_connection_test_results.json")
        
        return True
    except Exception as e:
        print(f"Error testing Supabase connection: {str(e)}")
        
        # Save the error to a JSON file
        results = {
            "timestamp": str(datetime.now()),
            "success": False,
            "error": str(e)
        }
        
        with open("supabase_connection_test_results.json", "w") as f:
            json.dump(results, f, indent=2)
        
        print(f"\nError results saved to supabase_connection_test_results.json")
        
        return False

if __name__ == "__main__":
    print("=" * 80)
    print("Testing Supabase Connection")
    print("=" * 80)
    
    success = test_supabase_connection()
    
    if success:
        print("\n✅ Supabase connection test successful!")
        sys.exit(0)
    else:
        print("\n❌ Supabase connection test failed.")
        sys.exit(1) 