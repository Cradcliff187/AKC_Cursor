-- Google Cloud Alignment SQL Script
-- This script ensures that the database in Google Cloud is aligned with the codebase

-- 1. Additional Tables Required by Service Files

-- Subcontractor Invoices table (referenced in subcontractors.py)
CREATE TABLE IF NOT EXISTS public.subcontractor_invoices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    subcontractor_id UUID NOT NULL REFERENCES public.subcontractors(id),
    project_id UUID REFERENCES public.projects(id),
    invoice_number TEXT NOT NULL,
    amount DECIMAL(12,2) NOT NULL,
    date DATE NOT NULL,
    due_date DATE NOT NULL,
    status TEXT DEFAULT 'Pending',
    description TEXT,
    created_by_id UUID,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Purchases table (referenced in vendors.py)
CREATE TABLE IF NOT EXISTS public.purchases (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    vendor_id UUID NOT NULL REFERENCES public.vendors(id),
    project_id UUID REFERENCES public.projects(id),
    description TEXT NOT NULL,
    amount DECIMAL(12,2) NOT NULL,
    date DATE NOT NULL,
    receipt_url TEXT,
    created_by_id UUID,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Recurring Invoices table (referenced in create_invoice_tables.sql)
CREATE TABLE IF NOT EXISTS public.recurring_invoices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    client_id UUID NOT NULL REFERENCES public.clients(id),
    project_id UUID REFERENCES public.projects(id),
    frequency TEXT NOT NULL, -- 'weekly', 'monthly', 'quarterly', 'yearly'
    start_date DATE NOT NULL,
    end_date DATE,
    next_issue_date DATE NOT NULL,
    last_issued_date DATE,
    total_amount DECIMAL(12,2) DEFAULT 0,
    active BOOLEAN DEFAULT TRUE,
    auto_send BOOLEAN DEFAULT FALSE,
    template_data JSONB, -- JSON serialized invoice template
    created_by_id UUID,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Invoice Templates table (referenced in create_invoice_tables.sql)
CREATE TABLE IF NOT EXISTS public.invoice_templates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    content JSONB NOT NULL, -- JSON serialized template data
    is_default BOOLEAN DEFAULT FALSE,
    created_by_id UUID,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Bid Versions table (referenced in create_bids_tables.sql)
CREATE TABLE IF NOT EXISTS public.bid_versions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    bid_id UUID NOT NULL REFERENCES public.bids(id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL,
    data JSONB NOT NULL, -- JSON serialized bid data
    created_by_id UUID,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Project Assignments table (referenced in subcontractors.py)
CREATE TABLE IF NOT EXISTS public.project_assignments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    subcontractor_id UUID NOT NULL REFERENCES public.subcontractors(id),
    project_id UUID NOT NULL REFERENCES public.projects(id),
    status TEXT DEFAULT 'In Progress',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(subcontractor_id, project_id)
);

-- 2. Add missing columns to existing tables

-- Add columns to user_profiles table for employee data
ALTER TABLE public.user_profiles ADD COLUMN IF NOT EXISTS position TEXT;
ALTER TABLE public.user_profiles ADD COLUMN IF NOT EXISTS department TEXT;
ALTER TABLE public.user_profiles ADD COLUMN IF NOT EXISTS payment_type TEXT DEFAULT 'hourly';
ALTER TABLE public.user_profiles ADD COLUMN IF NOT EXISTS hourly_rate DECIMAL(10,2) DEFAULT 0;
ALTER TABLE public.user_profiles ADD COLUMN IF NOT EXISTS annual_salary DECIMAL(12,2) DEFAULT 0;
ALTER TABLE public.user_profiles ADD COLUMN IF NOT EXISTS hours_per_week INTEGER DEFAULT 40;
ALTER TABLE public.user_profiles ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;
ALTER TABLE public.user_profiles ADD COLUMN IF NOT EXISTS avatar_color TEXT;
ALTER TABLE public.user_profiles ADD COLUMN IF NOT EXISTS notes TEXT;

-- Add columns to bids table
ALTER TABLE public.bids ADD COLUMN IF NOT EXISTS version INTEGER DEFAULT 1;
ALTER TABLE public.bids ADD COLUMN IF NOT EXISTS bid_number TEXT;
ALTER TABLE public.bids ADD COLUMN IF NOT EXISTS proposal_date DATE;
ALTER TABLE public.bids ADD COLUMN IF NOT EXISTS valid_until DATE;
ALTER TABLE public.bids ADD COLUMN IF NOT EXISTS overhead_cost DECIMAL(12,2) DEFAULT 0;
ALTER TABLE public.bids ADD COLUMN IF NOT EXISTS profit_margin DECIMAL(12,2) DEFAULT 0;
ALTER TABLE public.bids ADD COLUMN IF NOT EXISTS terms_and_conditions TEXT;
ALTER TABLE public.bids ADD COLUMN IF NOT EXISTS client_message TEXT;
ALTER TABLE public.bids ADD COLUMN IF NOT EXISTS client_response TEXT;
ALTER TABLE public.bids ADD COLUMN IF NOT EXISTS client_response_date DATE;
ALTER TABLE public.bids ADD COLUMN IF NOT EXISTS file_path TEXT;
ALTER TABLE public.bids ADD COLUMN IF NOT EXISTS original_filename TEXT;

-- Add columns to bid_items table
ALTER TABLE public.bid_items ADD COLUMN IF NOT EXISTS item_type TEXT DEFAULT 'Labor';
ALTER TABLE public.bid_items ADD COLUMN IF NOT EXISTS category TEXT;
ALTER TABLE public.bid_items ADD COLUMN IF NOT EXISTS unit TEXT DEFAULT 'Hours';
ALTER TABLE public.bid_items ADD COLUMN IF NOT EXISTS unit_cost DECIMAL(12,2) DEFAULT 0;
ALTER TABLE public.bid_items ADD COLUMN IF NOT EXISTS markup_percentage DECIMAL(5,2) DEFAULT 0;
ALTER TABLE public.bid_items ADD COLUMN IF NOT EXISTS markup_amount DECIMAL(12,2) DEFAULT 0;
ALTER TABLE public.bid_items ADD COLUMN IF NOT EXISTS notes TEXT;

-- 3. Create indexes for performance

-- Indexes for subcontractor_invoices
CREATE INDEX IF NOT EXISTS idx_subcontractor_invoices_subcontractor_id ON public.subcontractor_invoices(subcontractor_id);
CREATE INDEX IF NOT EXISTS idx_subcontractor_invoices_project_id ON public.subcontractor_invoices(project_id);
CREATE INDEX IF NOT EXISTS idx_subcontractor_invoices_status ON public.subcontractor_invoices(status);

-- Indexes for purchases
CREATE INDEX IF NOT EXISTS idx_purchases_vendor_id ON public.purchases(vendor_id);
CREATE INDEX IF NOT EXISTS idx_purchases_project_id ON public.purchases(project_id);
CREATE INDEX IF NOT EXISTS idx_purchases_date ON public.purchases(date);

-- Indexes for recurring_invoices
CREATE INDEX IF NOT EXISTS idx_recurring_invoices_client_id ON public.recurring_invoices(client_id);
CREATE INDEX IF NOT EXISTS idx_recurring_invoices_project_id ON public.recurring_invoices(project_id);
CREATE INDEX IF NOT EXISTS idx_recurring_invoices_next_issue_date ON public.recurring_invoices(next_issue_date);

-- Indexes for bid_versions
CREATE INDEX IF NOT EXISTS idx_bid_versions_bid_id ON public.bid_versions(bid_id);

-- Indexes for project_assignments
CREATE INDEX IF NOT EXISTS idx_project_assignments_subcontractor_id ON public.project_assignments(subcontractor_id);
CREATE INDEX IF NOT EXISTS idx_project_assignments_project_id ON public.project_assignments(project_id);

-- 4. Apply triggers for updated_at columns

-- Create trigger for subcontractor_invoices
CREATE TRIGGER update_subcontractor_invoices_updated_at
    BEFORE UPDATE ON public.subcontractor_invoices
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create trigger for purchases
CREATE TRIGGER update_purchases_updated_at
    BEFORE UPDATE ON public.purchases
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create trigger for recurring_invoices
CREATE TRIGGER update_recurring_invoices_updated_at
    BEFORE UPDATE ON public.recurring_invoices
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create trigger for invoice_templates
CREATE TRIGGER update_invoice_templates_updated_at
    BEFORE UPDATE ON public.invoice_templates
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create trigger for project_assignments
CREATE TRIGGER update_project_assignments_updated_at
    BEFORE UPDATE ON public.project_assignments
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 5. Apply RLS policies

-- RLS for subcontractor_invoices
CREATE POLICY "Employees can view subcontractor invoices"
    ON public.subcontractor_invoices FOR SELECT
    USING (EXISTS (
        SELECT 1 FROM public.user_profiles
        WHERE user_profiles.id = auth.uid()
        AND user_profiles.role IN ('admin', 'employee')
    ));

CREATE POLICY "Admins can manage subcontractor invoices"
    ON public.subcontractor_invoices FOR ALL
    USING (EXISTS (
        SELECT 1 FROM public.user_profiles
        WHERE user_profiles.id = auth.uid()
        AND user_profiles.role = 'admin'
    ));

-- RLS for purchases
CREATE POLICY "Employees can view purchases"
    ON public.purchases FOR SELECT
    USING (EXISTS (
        SELECT 1 FROM public.user_profiles
        WHERE user_profiles.id = auth.uid()
        AND user_profiles.role IN ('admin', 'employee')
    ));

CREATE POLICY "Admins can manage purchases"
    ON public.purchases FOR ALL
    USING (EXISTS (
        SELECT 1 FROM public.user_profiles
        WHERE user_profiles.id = auth.uid()
        AND user_profiles.role = 'admin'
    ));

-- RLS for recurring_invoices
CREATE POLICY "Employees can view recurring invoices"
    ON public.recurring_invoices FOR SELECT
    USING (EXISTS (
        SELECT 1 FROM public.user_profiles
        WHERE user_profiles.id = auth.uid()
        AND user_profiles.role IN ('admin', 'employee')
    ));

CREATE POLICY "Admins can manage recurring invoices"
    ON public.recurring_invoices FOR ALL
    USING (EXISTS (
        SELECT 1 FROM public.user_profiles
        WHERE user_profiles.id = auth.uid()
        AND user_profiles.role = 'admin'
    ));

-- RLS for invoice_templates
CREATE POLICY "Employees can view invoice templates"
    ON public.invoice_templates FOR SELECT
    USING (EXISTS (
        SELECT 1 FROM public.user_profiles
        WHERE user_profiles.id = auth.uid()
        AND user_profiles.role IN ('admin', 'employee')
    ));

CREATE POLICY "Admins can manage invoice templates"
    ON public.invoice_templates FOR ALL
    USING (EXISTS (
        SELECT 1 FROM public.user_profiles
        WHERE user_profiles.id = auth.uid()
        AND user_profiles.role = 'admin'
    ));

-- RLS for bid_versions
CREATE POLICY "Employees can view bid versions"
    ON public.bid_versions FOR SELECT
    USING (EXISTS (
        SELECT 1 FROM public.user_profiles
        WHERE user_profiles.id = auth.uid()
        AND user_profiles.role IN ('admin', 'employee')
    ));

CREATE POLICY "Admins can manage bid versions"
    ON public.bid_versions FOR ALL
    USING (EXISTS (
        SELECT 1 FROM public.user_profiles
        WHERE user_profiles.id = auth.uid()
        AND user_profiles.role = 'admin'
    ));

-- RLS for project_assignments
CREATE POLICY "Employees can view project assignments"
    ON public.project_assignments FOR SELECT
    USING (EXISTS (
        SELECT 1 FROM public.user_profiles
        WHERE user_profiles.id = auth.uid()
        AND user_profiles.role IN ('admin', 'employee')
    ));

CREATE POLICY "Admins can manage project assignments"
    ON public.project_assignments FOR ALL
    USING (EXISTS (
        SELECT 1 FROM public.user_profiles
        WHERE user_profiles.id = auth.uid()
        AND user_profiles.role = 'admin'
    ));

-- 6. Enable RLS on all new tables
ALTER TABLE public.subcontractor_invoices ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.purchases ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.recurring_invoices ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.invoice_templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.bid_versions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.project_assignments ENABLE ROW LEVEL SECURITY; 