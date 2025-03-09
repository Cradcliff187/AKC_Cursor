-- Basic RLS policies to restrict access to authenticated users
-- You may want to customize these based on your specific requirements

-- Projects table policy
CREATE POLICY "Enable access to authenticated users" ON projects
  FOR ALL USING (auth.role() = 'authenticated');

-- Customers table policy
CREATE POLICY "Enable access to authenticated users" ON customers
  FOR ALL USING (auth.role() = 'authenticated');

-- TimeLogs table policy
CREATE POLICY "Enable access to authenticated users" ON timelogs
  FOR ALL USING (auth.role() = 'authenticated');

-- MaterialsReceipts table policy
CREATE POLICY "Enable access to authenticated users" ON materialsreceipts
  FOR ALL USING (auth.role() = 'authenticated');

-- Subcontractors table policy
CREATE POLICY "Enable access to authenticated users" ON subcontractors
  FOR ALL USING (auth.role() = 'authenticated');

-- SubInvoices table policy
CREATE POLICY "Enable access to authenticated users" ON subinvoices
  FOR ALL USING (auth.role() = 'authenticated');

-- Estimates table policy
CREATE POLICY "Enable access to authenticated users" ON estimates
  FOR ALL USING (auth.role() = 'authenticated');

-- ActivityLog table policy
CREATE POLICY "Enable access to authenticated users" ON activitylog
  FOR ALL USING (auth.role() = 'authenticated');

-- Vendors table policy
CREATE POLICY "Enable access to authenticated users" ON vendors
  FOR ALL USING (auth.role() = 'authenticated'); 