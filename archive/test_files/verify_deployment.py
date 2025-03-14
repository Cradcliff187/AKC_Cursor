#!/usr/bin/env python3
"""
Verify Deployment Script

This script verifies that all database tables and SQL configurations
have been successfully deployed to the Supabase database.
"""

import os
import json
import sys
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

# Required tables
REQUIRED_TABLES = [
    "user_profiles",
    "clients",
    "projects",
    "documents",
    "tasks",
    "vendors",
    "subcontractors",
    "customers",
    "estimates"
]

def check_environment_variables():
    """Check if all required environment variables are set."""
    required_vars = ["SUPABASE_URL", "SUPABASE_KEY", "SUPABASE_SERVICE_ROLE_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please set these variables in your .env file or environment.")
        return False
    
    print("✅ All required environment variables are set.")
    return True

def create_supabase_client():
    """Create and return a Supabase client."""
    try:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")  # Use service role key for admin access
        return create_client(url, key)
    except Exception as e:
        print(f"❌ Failed to create Supabase client: {str(e)}")
        return None

def check_tables(supabase: Client):
    """Check if all required tables exist in the database."""
    try:
        # Query information_schema.tables to get all tables
        response = supabase.table("information_schema.tables").select("table_name").eq("table_schema", "public").execute()
        
        if hasattr(response, 'error') and response.error:
            print(f"❌ Error querying tables: {response.error}")
            return False
        
        existing_tables = [table['table_name'] for table in response.data]
        
        # Check if all required tables exist
        missing_tables = [table for table in REQUIRED_TABLES if table not in existing_tables]
        
        if missing_tables:
            print(f"❌ Missing tables: {', '.join(missing_tables)}")
            return False
        
        print(f"✅ All required tables exist ({len(REQUIRED_TABLES)} tables).")
        return True
    except Exception as e:
        print(f"❌ Error checking tables: {str(e)}")
        return False

def check_timestamp_function(supabase: Client):
    """Check if the automatic timestamp update function exists."""
    try:
        # Query information_schema.routines to check for the function
        response = supabase.table("information_schema.routines").select("routine_name").eq("routine_schema", "public").eq("routine_name", "update_timestamp").execute()
        
        if hasattr(response, 'error') and response.error:
            print(f"❌ Error querying functions: {response.error}")
            return False
        
        if not response.data:
            print("❌ Automatic timestamp update function does not exist.")
            return False
        
        print("✅ Automatic timestamp update function exists.")
        return True
    except Exception as e:
        print(f"❌ Error checking timestamp function: {str(e)}")
        return False

def check_rls_enabled(supabase: Client):
    """Check if Row Level Security is enabled on all tables."""
    try:
        # Query pg_tables to get RLS status
        query = """
        SELECT tablename, rowsecurity 
        FROM pg_tables 
        WHERE schemaname = 'public' 
        AND tablename = ANY('{%s}'::text[])
        """ % ','.join(REQUIRED_TABLES)
        
        response = supabase.rpc("execute_sql", {"query": query}).execute()
        
        if hasattr(response, 'error') and response.error:
            print(f"❌ Error querying RLS status: {response.error}")
            return False
        
        tables_without_rls = [table['tablename'] for table in response.data if not table['rowsecurity']]
        
        if tables_without_rls:
            print(f"❌ Tables without RLS enabled: {', '.join(tables_without_rls)}")
            return False
        
        print("✅ Row Level Security is enabled on all required tables.")
        return True
    except Exception as e:
        print(f"❌ Error checking RLS status: {str(e)}")
        return False

def check_temp_config_table(supabase: Client):
    """Check if the temporary configuration export table exists."""
    try:
        response = supabase.table("information_schema.tables").select("table_name").eq("table_schema", "public").eq("table_name", "temp_config_export").execute()
        
        if hasattr(response, 'error') and response.error:
            print(f"❌ Error querying temp config table: {response.error}")
            return False
        
        if not response.data:
            print("❌ Temporary configuration export table does not exist.")
            return False
        
        print("✅ Temporary configuration export table exists.")
        return True
    except Exception as e:
        print(f"❌ Error checking temp config table: {str(e)}")
        return False

def check_rls_policies(supabase: Client):
    """Check if RLS policies exist for tables."""
    try:
        # Query pg_policies to get all policies
        query = """
        SELECT tablename, policyname 
        FROM pg_policies 
        WHERE schemaname = 'public' 
        AND tablename = ANY('{%s}'::text[])
        """ % ','.join(REQUIRED_TABLES)
        
        response = supabase.rpc("execute_sql", {"query": query}).execute()
        
        if hasattr(response, 'error') and response.error:
            print(f"❌ Error querying RLS policies: {response.error}")
            return False
        
        # Group policies by table
        policies_by_table = {}
        for policy in response.data:
            table = policy['tablename']
            if table not in policies_by_table:
                policies_by_table[table] = []
            policies_by_table[table].append(policy['policyname'])
        
        # Check if all tables have policies
        tables_without_policies = [table for table in REQUIRED_TABLES if table not in policies_by_table]
        
        if tables_without_policies:
            print(f"❌ Tables without RLS policies: {', '.join(tables_without_policies)}")
            return False
        
        print(f"✅ RLS policies exist for all required tables.")
        return True
    except Exception as e:
        print(f"❌ Error checking RLS policies: {str(e)}")
        return False

def main():
    """Main function to verify deployment."""
    print("\n=== DEPLOYMENT VERIFICATION ===\n")
    
    # Check environment variables
    if not check_environment_variables():
        return False
    
    # Create Supabase client
    supabase = create_supabase_client()
    if not supabase:
        return False
    
    # Run all checks
    checks = [
        ("Tables", check_tables(supabase)),
        ("Timestamp Function", check_timestamp_function(supabase)),
        ("Row Level Security", check_rls_enabled(supabase)),
        ("Temporary Config Table", check_temp_config_table(supabase)),
        ("RLS Policies", check_rls_policies(supabase))
    ]
    
    # Print summary
    print("\n=== VERIFICATION SUMMARY ===\n")
    all_passed = all(result for _, result in checks)
    
    for check_name, result in checks:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{check_name}: {status}")
    
    print("\n=== FINAL RESULT ===\n")
    if all_passed:
        print("✅ All checks passed! The database is ready for deployment to Google Cloud.")
        return True
    else:
        print("❌ Some checks failed. Please fix the issues before connecting to Google Cloud.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 