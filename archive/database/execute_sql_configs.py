#!/usr/bin/env python3
"""
Execute SQL Configurations

This script executes SQL configurations for the Supabase database.
It uses the Supabase Python client and REST API to execute SQL statements.
"""

import os
import sys
import json
import time
import requests
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

# Get environment variables
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

print(f"SUPABASE_URL: {SUPABASE_URL}")
print(f"SUPABASE_SERVICE_KEY: {'Set (length: ' + str(len(SUPABASE_SERVICE_KEY)) + ')' if SUPABASE_SERVICE_KEY else 'Not set'}")

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

def execute_sql_statement(sql_statement, retry_count=3):
    """Execute a SQL statement using the Supabase REST API."""
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        print("Error: Supabase credentials not set.")
        return False

    # Endpoint for SQL execution
    url = f"{SUPABASE_URL}/rest/v1/sql"
    
    # Headers
    headers = {
        "apikey": SUPABASE_SERVICE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }
    
    # Data
    data = {
        "query": sql_statement
    }
    
    print(f"Executing SQL: {sql_statement[:100]}...")
    
    for attempt in range(retry_count):
        try:
            response = requests.post(url, headers=headers, json=data)
            
            print(f"Response status code: {response.status_code}")
            
            if response.status_code in [200, 201, 204]:
                print(f"SQL executed successfully.")
                return True
            else:
                print(f"Error executing SQL: {response.status_code}")
                print(f"Response: {response.text}")
                
                if attempt < retry_count - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    print(f"Retrying in {wait_time} seconds... (Attempt {attempt + 1}/{retry_count})")
                    time.sleep(wait_time)
                else:
                    return False
        except Exception as e:
            print(f"Exception executing SQL: {str(e)}")
            
            if attempt < retry_count - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"Retrying in {wait_time} seconds... (Attempt {attempt + 1}/{retry_count})")
                time.sleep(wait_time)
            else:
                return False
    
    return False

def execute_sql_configs():
    """Execute SQL configurations for the Supabase database."""
    # Check environment
    if not check_environment():
        return False
    
    print("Executing SQL configurations...")
    
    # List of SQL configurations to execute
    configs = [
        # Create temporary configuration export table
        """
        CREATE TABLE IF NOT EXISTS public.temp_config_export (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            config_type TEXT NOT NULL,
            config_data JSONB NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            expires_at TIMESTAMP WITH TIME ZONE DEFAULT (NOW() + INTERVAL '7 days')
        );
        """,
        
        # Create automatic timestamp update function
        """
        CREATE OR REPLACE FUNCTION public.update_timestamp()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """,
        
        # Enable Row Level Security on all tables
        """
        ALTER TABLE IF EXISTS public.projects ENABLE ROW LEVEL SECURITY;
        """,
        
        """
        ALTER TABLE IF EXISTS public.tasks ENABLE ROW LEVEL SECURITY;
        """,
        
        """
        ALTER TABLE IF EXISTS public.users ENABLE ROW LEVEL SECURITY;
        """,
        
        """
        ALTER TABLE IF EXISTS public.clients ENABLE ROW LEVEL SECURITY;
        """,
        
        """
        ALTER TABLE IF EXISTS public.documents ENABLE ROW LEVEL SECURITY;
        """,
        
        """
        ALTER TABLE IF EXISTS public.invoices ENABLE ROW LEVEL SECURITY;
        """,
        
        """
        ALTER TABLE IF EXISTS public.payments ENABLE ROW LEVEL SECURITY;
        """,
        
        """
        ALTER TABLE IF EXISTS public.expenses ENABLE ROW LEVEL SECURITY;
        """,
        
        """
        ALTER TABLE IF EXISTS public.materials ENABLE ROW LEVEL SECURITY;
        """,
        
        """
        ALTER TABLE IF EXISTS public.labor_hours ENABLE ROW LEVEL SECURITY;
        """,
        
        """
        ALTER TABLE IF EXISTS public.equipment ENABLE ROW LEVEL SECURITY;
        """,
        
        """
        ALTER TABLE IF EXISTS public.subcontractors ENABLE ROW LEVEL SECURITY;
        """,
        
        # Create RLS policies for user roles
        """
        CREATE POLICY IF NOT EXISTS "Allow full access to admins" 
        ON public.projects 
        FOR ALL 
        TO authenticated 
        USING (auth.jwt() ->> 'role' = 'admin')
        WITH CHECK (auth.jwt() ->> 'role' = 'admin');
        """,
        
        """
        CREATE POLICY IF NOT EXISTS "Allow read access to project managers" 
        ON public.projects 
        FOR SELECT 
        TO authenticated 
        USING (auth.jwt() ->> 'role' = 'project_manager');
        """,
        
        # Create performance indexes
        """
        CREATE INDEX IF NOT EXISTS idx_projects_status ON public.projects (status);
        """,
        
        """
        CREATE INDEX IF NOT EXISTS idx_tasks_project_id ON public.tasks (project_id);
        """,
        
        """
        CREATE INDEX IF NOT EXISTS idx_tasks_status ON public.tasks (status);
        """,
        
        """
        CREATE INDEX IF NOT EXISTS idx_invoices_client_id ON public.invoices (client_id);
        """,
        
        """
        CREATE INDEX IF NOT EXISTS idx_invoices_status ON public.invoices (status);
        """,
        
        """
        CREATE INDEX IF NOT EXISTS idx_payments_invoice_id ON public.payments (invoice_id);
        """,
        
        """
        CREATE INDEX IF NOT EXISTS idx_expenses_project_id ON public.expenses (project_id);
        """,
        
        """
        CREATE INDEX IF NOT EXISTS idx_labor_hours_project_id ON public.labor_hours (project_id);
        """,
        
        """
        CREATE INDEX IF NOT EXISTS idx_materials_project_id ON public.materials (project_id);
        """
    ]
    
    success_count = 0
    error_count = 0
    
    for i, sql in enumerate(configs):
        print(f"\nExecuting SQL configuration {i+1}/{len(configs)}")
        
        if execute_sql_statement(sql):
            success_count += 1
        else:
            error_count += 1
    
    print(f"\nSQL configurations execution completed: {success_count} succeeded, {error_count} failed.")
    return error_count == 0

if __name__ == "__main__":
    success = execute_sql_configs()
    sys.exit(0 if success else 1) 