# Database Deployment Guide

This guide provides instructions for deploying the necessary database updates to ensure the Supabase database is aligned with the schema file and has all required configurations before connecting to the live project in Google Cloud.

## Overview

The deployment process includes:

1. Updating the schema file with missing tables
2. Creating the necessary SQL functions
3. Executing schema updates to add missing tables
4. Applying SQL configurations (Automatic Timestamp Updates, Row Level Security, etc.)
5. Applying Google Cloud alignment updates (Additional tables, columns, etc.)
6. Verifying that all configurations are properly set up

## Prerequisites

- Python 3.6 or higher
- Supabase project with admin access
- Environment variables set up:
  - `SUPABASE_URL`: Your Supabase project URL
  - `SUPABASE_KEY`: Your Supabase anon key
  - `SUPABASE_SERVICE_ROLE_KEY`: Your Supabase service role key (required for admin operations)

## Files

- `schema_updates.sql`: SQL script to add missing tables to the database
- `sql_configurations.sql`: SQL script to set up required SQL configurations
- `google_cloud_alignment.sql`: SQL script to ensure alignment with Google Cloud
- `update_schema_file.py`: Python script to update the schema file with missing tables
- `deploy_database_updates.py`: Main deployment script that orchestrates the entire process
- `verify_deployment.py`: Script to verify that the deployment was successful

## Deployment Steps

### 1. Set Environment Variables

Make sure your environment variables are set correctly:

```bash
# Linux/macOS
export SUPABASE_URL="https://your-project-id.supabase.co"
export SUPABASE_KEY="your-anon-key"
export SUPABASE_SERVICE_ROLE_KEY="your-service-role-key"

# Windows (PowerShell)
$env:SUPABASE_URL="https://your-project-id.supabase.co"
$env:SUPABASE_KEY="your-anon-key"
$env:SUPABASE_SERVICE_ROLE_KEY="your-service-role-key"
```

### 2. Install Required Python Packages

```bash
pip install supabase python-dotenv requests
```

### 3. Run the Deployment Script

```bash
python deploy_database_updates.py
```

This script will:
- Update the schema file with missing tables
- Create the necessary SQL functions
- Execute schema updates
- Apply SQL configurations
- Apply Google Cloud alignment updates
- Verify that all configurations are properly set up

### 4. Verify Deployment

After running the deployment script, verify that all configurations are properly set up by running:

```bash
python verify_deployment.py
```

This script will check:
- If all required tables exist in the database
- If all SQL configurations are properly set up
- If all Google Cloud alignment updates are properly applied
- If the database is ready for deployment to Google Cloud

## SQL Configurations

The deployment process sets up the following SQL configurations:

1. **Temporary Configuration Export Table**: A table for exporting configuration data
2. **Automatic Timestamp Update Function**: A function that automatically updates the `updated_at` column when a record is modified
3. **Row Level Security Policies**: Security policies that control access to data based on the user's role
4. **Indexes for Performance Optimization**: Indexes on foreign keys and commonly queried columns
5. **Row Level Security Enabled**: Enabling Row Level Security on all tables

## Google Cloud Alignment

The deployment process also ensures alignment with Google Cloud by:

1. **Creating Additional Tables**:
   - `subcontractor_invoices`: Stores invoices from subcontractors
   - `purchases`: Stores purchase records from vendors
   - `recurring_invoices`: Stores recurring invoice templates
   - `invoice_templates`: Stores invoice templates
   - `bid_versions`: Stores version history for bids
   - `project_assignments`: Stores subcontractor assignments to projects

2. **Adding Columns to Existing Tables**:
   - Employee-related columns to `user_profiles` table
   - Additional columns to `bids` table
   - Additional columns to `bid_items` table

3. **Configuring New Tables**:
   - Creating indexes for all new tables
   - Applying triggers for `updated_at` columns
   - Creating RLS policies
   - Enabling RLS

## Troubleshooting

### Common Issues

1. **Permission Denied Errors**:
   - Make sure you're using the service role key for admin operations
   - Check that your Supabase project has the necessary permissions

2. **Function Creation Errors**:
   - Some functions may already exist with different signatures
   - Try dropping the function first before creating it

3. **Table Creation Errors**:
   - Tables may already exist with different schemas
   - Use `IF NOT EXISTS` clause to avoid errors

4. **Column Addition Errors**:
   - Columns may already exist with different data types
   - Use `IF NOT EXISTS` clause when adding columns

### Getting Help

If you encounter any issues during the deployment process, please:

1. Check the error messages for specific details
2. Verify that your environment variables are set correctly
3. Make sure you have the necessary permissions in your Supabase project

## After Deployment

After successfully deploying the database updates, you can proceed with connecting to the live project in Google Cloud. The database is now properly aligned with the schema file and has all required configurations.

## Important Notes

- Always back up your database before making significant changes
- Test the deployment process in a development environment before applying it to production
- Monitor the database performance after deployment to ensure everything is working correctly 