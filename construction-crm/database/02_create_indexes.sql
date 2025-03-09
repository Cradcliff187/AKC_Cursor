-- Add indexes to improve query performance

-- Projects table indexes
CREATE INDEX IF NOT EXISTS idx_projects_customerid ON projects(customerid);
CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);
CREATE INDEX IF NOT EXISTS idx_projects_created_at ON projects(created_at);

-- TimeLogs table indexes
CREATE INDEX IF NOT EXISTS idx_timelogs_projectid ON timelogs(projectid);
CREATE INDEX IF NOT EXISTS idx_timelogs_dateworked ON timelogs(dateworked);

-- MaterialsReceipts table indexes
CREATE INDEX IF NOT EXISTS idx_materialsreceipts_projectid ON materialsreceipts(projectid);
CREATE INDEX IF NOT EXISTS idx_materialsreceipts_vendorid ON materialsreceipts(vendorid);

-- SubInvoices table indexes
CREATE INDEX IF NOT EXISTS idx_subinvoices_projectid ON subinvoices(projectid);
CREATE INDEX IF NOT EXISTS idx_subinvoices_subid ON subinvoices(subid);

-- Estimates table indexes
CREATE INDEX IF NOT EXISTS idx_estimates_projectid ON estimates(projectid);
CREATE INDEX IF NOT EXISTS idx_estimates_customerid ON estimates(customerid);
CREATE INDEX IF NOT EXISTS idx_estimates_status ON estimates(status);

-- ActivityLog table indexes
CREATE INDEX IF NOT EXISTS idx_activitylog_referenceid ON activitylog(referenceid);
CREATE INDEX IF NOT EXISTS idx_activitylog_moduletype ON activitylog(moduletype);
CREATE INDEX IF NOT EXISTS idx_activitylog_timestamp ON activitylog(timestamp); 