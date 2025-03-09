# Database Setup Instructions

These SQL scripts will set up the database schema for the Construction CRM application in Supabase.

## How to Run These Scripts

1. **Log in to Supabase**
   - Go to [https://app.supabase.com/](https://app.supabase.com/)
   - Select your project (with URL: https://olfbvahswnkpxlnhbwds.supabase.co)

2. **Navigate to the SQL Editor**
   - Click on "SQL Editor" in the left sidebar

3. **Run the Scripts in Order**
   - Create a new query
   - Copy and paste the contents of each script
   - Run them in sequence:
     1. `01_create_tables.sql` - Creates all the database tables
     2. `02_create_indexes.sql` - Adds indexes for performance
     3. `03_create_rls_policies.sql` - Sets up Row Level Security
     4. `04_create_triggers.sql` - Adds automatic timestamp updates

## Script Descriptions

- **01_create_tables.sql**: Creates the main database tables including projects, customers, timelogs, etc.
- **02_create_indexes.sql**: Adds indexes to improve query performance
- **03_create_rls_policies.sql**: Sets up Row Level Security policies to restrict access to authenticated users
- **04_create_triggers.sql**: Creates triggers to automatically update the `updated_at` timestamp when records change

## Troubleshooting

- If you encounter errors about references to tables that don't exist, make sure to run the scripts in order
- Some warnings about enabling RLS on non-existent tables can be safely ignored
- If you need to start over, you can drop all tables with: `DROP TABLE IF EXISTS projects, customers, timelogs, materialsreceipts, subcontractors, subinvoices, estimates, activitylog, vendors CASCADE;` 