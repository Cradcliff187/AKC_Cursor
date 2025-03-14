# Supabase Setup Instructions

This document provides instructions for setting up the necessary database tables and functions in Supabase for the AKC Construction CRM.

## Prerequisites

- A Supabase account and project
- Access to the Supabase dashboard

## Setup Steps

### 1. Create the `exec_sql` Function

1. Go to your Supabase project dashboard
2. Navigate to the SQL Editor
3. Create a new query
4. Paste the following SQL code:

```sql
-- Create the exec_sql function for executing dynamic SQL queries
CREATE OR REPLACE FUNCTION public.exec_sql(query text, params jsonb DEFAULT NULL)
RETURNS SETOF json AS $$
BEGIN
    IF params IS NULL THEN
        RETURN QUERY EXECUTE query;
    ELSE
        RETURN QUERY EXECUTE query USING params;
    END IF;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

5. Click "Run" to execute the query

### 2. Fix the `user_profiles` Table Schema

We've detected that the `user_profiles` table exists but may not have the correct schema. To fix this:

1. Go to your Supabase project dashboard
2. Navigate to the SQL Editor
3. Create a new query
4. Open the `create_user_profiles_table.sql` file from this project
5. Copy the contents of the file and paste it into the SQL Editor
6. Click "Run" to execute the query

### 3. Create Missing Database Tables

Based on our checks, the following tables are missing from your Supabase project:
- user_notifications
- project_tasks
- payments

To create these missing tables:

1. Go to your Supabase project dashboard
2. Navigate to the SQL Editor
3. Create a new query
4. Open the `create_missing_tables.sql` file from this project
5. Copy the contents of the file and paste it into the SQL Editor
6. Click "Run" to execute the query

### 4. Verify Setup

1. Go to your Supabase project dashboard
2. Navigate to the "Table Editor" section
3. Verify that all the tables have been created:
   - user_profiles
   - user_notifications
   - clients
   - projects
   - project_tasks
   - invoices
   - invoice_items
   - payments
   - bids
   - bid_items
   - expenses
   - time_entries
   - documents

4. Navigate to the "Functions" section
5. Verify that the `exec_sql` function has been created
6. Verify that the `update_updated_at_column` function has been created

## Environment Variables

Make sure to set the following environment variables in your `.env` file:

```
SUPABASE_URL=your-supabase-url
SUPABASE_SERVICE_ROLE_KEY=your-supabase-service-role-key
```

You can find these values in your Supabase project dashboard under "Settings" > "API".

## Testing the Connection

Run the following command to test the database connection:

```
python test_db_connection.py
```

If the connection is successful, you should see a message indicating that the connection was successful.

## Running the Application

Once the setup is complete, you can run the application with:

```
python run_app.py
```

The API will be available at `http://localhost:8000` and the API documentation will be available at `http://localhost:8000/docs`. 