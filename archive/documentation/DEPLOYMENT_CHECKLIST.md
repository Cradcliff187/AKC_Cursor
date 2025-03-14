# Database Deployment Checklist

Use this checklist to ensure all necessary steps are completed before connecting to Google Cloud.

## Pre-Deployment Checks

- [ ] Database backup has been created
- [ ] Environment variables are properly set:
  - [ ] SUPABASE_URL
  - [ ] SUPABASE_KEY
  - [ ] SUPABASE_SERVICE_ROLE_KEY
- [ ] Required Python packages are installed:
  - [ ] supabase
  - [ ] python-dotenv
  - [ ] requests

## Deployment Steps

- [ ] Run `update_schema_file.py` to update the schema file with missing tables
- [ ] Run `deploy_database_updates.py` to execute all database updates
- [ ] Run `check_comprehensive.py` to verify all configurations are properly set up

## Post-Deployment Verification

### Schema Verification
- [ ] All required tables exist in the database:
  - [ ] user_profiles
  - [ ] clients
  - [ ] projects
  - [ ] documents
  - [ ] tasks
  - [ ] vendors
  - [ ] subcontractors
  - [ ] customers
  - [ ] estimates
  - [ ] (and all other tables defined in the schema file)

### Google Cloud Alignment Verification
- [ ] Additional tables required by service files exist:
  - [ ] subcontractor_invoices
  - [ ] purchases
  - [ ] recurring_invoices
  - [ ] invoice_templates
  - [ ] bid_versions
  - [ ] project_assignments
- [ ] Additional columns have been added to existing tables:
  - [ ] Employee-related columns in user_profiles
  - [ ] Additional columns in bids table
  - [ ] Additional columns in bid_items table
- [ ] Indexes have been created for all new tables
- [ ] Triggers have been applied to all new tables
- [ ] RLS policies have been created for all new tables
- [ ] RLS has been enabled on all new tables

### SQL Configuration Verification
- [ ] Temporary Configuration Export Table is created
- [ ] Automatic Timestamp Update Function is created and applied to all tables
- [ ] Row Level Security Policies are created for all tables
- [ ] Performance Indexes are created on all necessary columns
- [ ] Row Level Security is enabled on all tables

### Functional Verification
- [ ] Test inserting a record into a table with RLS policies
- [ ] Test updating a record to verify automatic timestamp update
- [ ] Test querying data with different user roles to verify RLS policies
- [ ] Test service files with the database to ensure they can access all required tables and columns

## Google Cloud Connection

- [ ] Supabase connection string is configured in Google Cloud
- [ ] Application environment variables are updated with Supabase credentials
- [ ] Initial connection test is successful
- [ ] Test service files with Google Cloud connection to ensure they work correctly

## Final Approval

- [ ] All checklist items are completed
- [ ] Database deployment is approved by project manager
- [ ] Application is ready to be connected to the live database

## Notes

* Complete each item in the checklist before proceeding to the next step
* If any verification step fails, resolve the issue before continuing
* Document any issues encountered during deployment for future reference 