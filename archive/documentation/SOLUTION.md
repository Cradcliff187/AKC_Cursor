# Database Schema Issues and Solutions

## Issues Identified

After running our diagnostic scripts, we've identified the following issues with the Supabase database:

1. **Missing `auth_id` Column in `user_profiles` Table**:
   - The `user_profiles` table exists but doesn't have the required `auth_id` column.
   - Error: `Could not find the 'auth_id' column of 'user_profiles' in the schema cache`

2. **Missing Tables**:
   - `user_notifications` - For storing user notifications
   - `project_tasks` - For storing tasks associated with projects
   - `payments` - For storing payment records

3. **Missing PostgreSQL Functions**:
   - `exec_sql` - Used for executing dynamic SQL queries
   - `update_updated_at_column` - Used for automatically updating the `updated_at` column

## Solutions

We've created the following SQL scripts to fix these issues:

1. **`create_user_profiles_table.sql`**:
   - Drops and recreates the `user_profiles` table with the correct schema
   - Creates the `update_updated_at_column` function
   - Sets up Row Level Security (RLS) policies for the table
   - Creates necessary indexes for performance

2. **`create_missing_tables.sql`**:
   - Creates the missing tables (`user_notifications`, `project_tasks`, `payments`)
   - Creates the `exec_sql` function
   - Sets up triggers for updating the `updated_at` column
   - Sets up Row Level Security (RLS) policies for the tables
   - Creates necessary indexes for performance

## Implementation Steps

Follow these steps to fix the database schema:

1. **Create the `exec_sql` Function**:
   - Execute the SQL code in the Supabase SQL Editor to create the function

2. **Fix the `user_profiles` Table Schema**:
   - Execute the `create_user_profiles_table.sql` script in the Supabase SQL Editor

3. **Create the Missing Tables**:
   - Execute the `create_missing_tables.sql` script in the Supabase SQL Editor

4. **Verify the Setup**:
   - Run `python test_db_connection.py` to verify that all tables exist and have the correct schema

## Expected Results

After implementing these solutions:

1. The `user_profiles` table will have the correct schema, including the `auth_id` column.
2. All missing tables will be created with the correct schema.
3. The required PostgreSQL functions will be available.
4. The application will be able to connect to the database and perform CRUD operations.

## Additional Notes

- The `auth_id` column in the `user_profiles` table is used to link the user profile to the Supabase Auth user.
- The `exec_sql` function is used for executing dynamic SQL queries, which is useful for complex queries that can't be expressed using the Supabase client's API.
- The `update_updated_at_column` function is used to automatically update the `updated_at` column when a record is modified, ensuring that we always know when a record was last updated.

Detailed setup instructions can be found in the `supabase_setup_instructions.md` file. 