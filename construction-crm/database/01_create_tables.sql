-- Enable RLS (Row Level Security)
ALTER TABLE IF EXISTS projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS customers ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS timelogs ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS materialsreceipts ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS subcontractors ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS subinvoices ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS estimates ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS activitylog ENABLE ROW LEVEL SECURITY;
ALTER TABLE IF EXISTS vendors ENABLE ROW LEVEL SECURITY;

-- Create or replace customers table
CREATE TABLE IF NOT EXISTS customers (
  customerid TEXT PRIMARY KEY,
  customername TEXT,
  address TEXT,
  city TEXT,
  state TEXT,
  zip TEXT,
  contactemail TEXT,
  phone TEXT,
  createdon TIMESTAMPTZ,
  createdby TEXT,
  status TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Create or replace vendors table
CREATE TABLE IF NOT EXISTS vendors (
  vendorid TEXT PRIMARY KEY,
  vendorname TEXT,
  address TEXT,
  city TEXT,
  state TEXT,
  zip TEXT,
  email TEXT,
  phone TEXT,
  createdon TIMESTAMPTZ,
  createdby TEXT,
  status TEXT,
  qbvendortype TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Create or replace projects table
CREATE TABLE IF NOT EXISTS projects (
  projectid TEXT PRIMARY KEY,
  customerid TEXT REFERENCES customers(customerid),
  projectname TEXT,
  status TEXT,
  folderid TEXT,
  createdon TIMESTAMPTZ,
  createdby TEXT,
  jobid TEXT,
  lastmodified TEXT,
  lastmodifiedby TEXT,
  estimatesfolderid TEXT,
  materialsfolderid TEXT,
  subinvoicesfolderid TEXT,
  docurl TEXT,
  customername TEXT,
  jobdescription TEXT,
  sitelocationaddress TEXT,
  sitelocationcity TEXT,
  sitelocationstate TEXT,
  sitelocationzip TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Create or replace timelogs table
CREATE TABLE IF NOT EXISTS timelogs (
  timelogid TEXT PRIMARY KEY,
  projectid TEXT REFERENCES projects(projectid),
  dateworked TIMESTAMPTZ,
  starttime TEXT,
  endtime TEXT,
  totalhours TEXT,
  submittinguser TEXT,
  foruseremail TEXT,
  createdon TIMESTAMPTZ,
  "employee hourly rate" TEXT,
  "job id" TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Create or replace materialsreceipts table
CREATE TABLE IF NOT EXISTS materialsreceipts (
  receiptid TEXT PRIMARY KEY,
  projectid TEXT REFERENCES projects(projectid),
  vendorid TEXT REFERENCES vendors(vendorid),
  vendorname TEXT,
  amount DECIMAL(10,2),
  receiptdocurl TEXT,
  submittinguser TEXT,
  foruseremail TEXT,
  createdon TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Create or replace subcontractors table
CREATE TABLE IF NOT EXISTS subcontractors (
  subid TEXT PRIMARY KEY,
  subname TEXT,
  address TEXT,
  city TEXT,
  state TEXT,
  zip TEXT,
  contactemail TEXT,
  phone TEXT,
  qbvendortype TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Create or replace subinvoices table
CREATE TABLE IF NOT EXISTS subinvoices (
  subinvoiceid TEXT PRIMARY KEY,
  projectid TEXT REFERENCES projects(projectid),
  projectname TEXT,
  subid TEXT REFERENCES subcontractors(subid),
  subname TEXT,
  invoiceamount DECIMAL(10,2),
  invoicedocurl TEXT,
  submittinguser TEXT,
  createdon TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Create or replace estimates table
CREATE TABLE IF NOT EXISTS estimates (
  estimateid TEXT PRIMARY KEY,
  projectid TEXT REFERENCES projects(projectid),
  datecreated TIMESTAMPTZ,
  customerid TEXT REFERENCES customers(customerid),
  estimateamount DECIMAL(10,2),
  contingencyamount DECIMAL(10,2),
  createdby TEXT,
  docurl TEXT,
  docid TEXT,
  status TEXT,
  sentdate TIMESTAMPTZ,
  isactive BOOLEAN,
  approveddate TIMESTAMPTZ,
  sitelocationaddress TEXT,
  sitelocationcity TEXT,
  sitelocationstate TEXT,
  sitelocationzip TEXT,
  "po#" TEXT,
  "job description" TEXT,
  customername TEXT,
  projectname TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Create or replace activitylog table
CREATE TABLE IF NOT EXISTS activitylog (
  logid TEXT PRIMARY KEY,
  timestamp TIMESTAMPTZ,
  action TEXT,
  useremail TEXT,
  moduletype TEXT,
  referenceid TEXT,
  detailsjson TEXT,
  status TEXT,
  previousstatus TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
); 