-- Drop existing policies first
DO $$ 
DECLARE
    pol record;
BEGIN
    FOR pol IN SELECT policyname, tablename FROM pg_policies WHERE schemaname = 'public'
    LOOP
        EXECUTE format('DROP POLICY IF EXISTS %I ON public.%I', pol.policyname, pol.tablename);
    END LOOP;
END $$;

-- RLS Policies for AKC Construction CRM

-- User Profiles Policies
CREATE POLICY "Users can view their own profile"
    ON public.user_profiles FOR SELECT
    USING (auth.uid() = id);

CREATE POLICY "Admins can view all profiles"
    ON public.user_profiles FOR SELECT
    USING (EXISTS (
        SELECT 1 FROM public.user_profiles
        WHERE user_profiles.id = auth.uid()
        AND user_profiles.role = 'admin'
    ));

CREATE POLICY "Admins can update profiles"
    ON public.user_profiles FOR UPDATE
    USING (EXISTS (
        SELECT 1 FROM public.user_profiles
        WHERE user_profiles.id = auth.uid()
        AND user_profiles.role = 'admin'
    ));

-- Clients Policies
CREATE POLICY "Employees and admins can view clients"
    ON public.clients FOR SELECT
    USING (EXISTS (
        SELECT 1 FROM public.user_profiles
        WHERE user_profiles.id = auth.uid()
        AND user_profiles.role IN ('admin', 'employee')
    ));

CREATE POLICY "Admins can insert clients"
    ON public.clients FOR INSERT
    WITH CHECK (EXISTS (
        SELECT 1 FROM public.user_profiles
        WHERE user_profiles.id = auth.uid()
        AND user_profiles.role = 'admin'
    ));

CREATE POLICY "Admins can update clients"
    ON public.clients FOR UPDATE
    USING (EXISTS (
        SELECT 1 FROM public.user_profiles
        WHERE user_profiles.id = auth.uid()
        AND user_profiles.role = 'admin'
    ));

CREATE POLICY "Admins can delete clients"
    ON public.clients FOR DELETE
    USING (EXISTS (
        SELECT 1 FROM public.user_profiles
        WHERE user_profiles.id = auth.uid()
        AND user_profiles.role = 'admin'
    ));

-- Projects Policies
CREATE POLICY "Employees and admins can view projects"
    ON public.projects FOR SELECT
    USING (EXISTS (
        SELECT 1 FROM public.user_profiles
        WHERE user_profiles.id = auth.uid()
        AND user_profiles.role IN ('admin', 'employee')
    ));

CREATE POLICY "Admins can manage projects"
    ON public.projects FOR ALL
    USING (EXISTS (
        SELECT 1 FROM public.user_profiles
        WHERE user_profiles.id = auth.uid()
        AND user_profiles.role = 'admin'
    ));

-- Tasks Policies
CREATE POLICY "Employees can view assigned tasks"
    ON public.tasks FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.user_profiles
            WHERE user_profiles.id = auth.uid()
            AND (user_profiles.role IN ('admin', 'employee'))
        )
        AND (
            assigned_to_id = auth.uid()
            OR created_by_id = auth.uid()
            OR EXISTS (
                SELECT 1 FROM public.user_profiles
                WHERE user_profiles.id = auth.uid()
                AND user_profiles.role = 'admin'
            )
        )
    );

CREATE POLICY "Employees can create tasks"
    ON public.tasks FOR INSERT
    WITH CHECK (EXISTS (
        SELECT 1 FROM public.user_profiles
        WHERE user_profiles.id = auth.uid()
        AND user_profiles.role IN ('admin', 'employee')
    ));

CREATE POLICY "Task owners and admins can update tasks"
    ON public.tasks FOR UPDATE
    USING (
        assigned_to_id = auth.uid()
        OR created_by_id = auth.uid()
        OR EXISTS (
            SELECT 1 FROM public.user_profiles
            WHERE user_profiles.id = auth.uid()
            AND user_profiles.role = 'admin'
        )
    );

-- Time Entries Policies
CREATE POLICY "Users can view their own time entries"
    ON public.time_entries FOR SELECT
    USING (user_id = auth.uid());

CREATE POLICY "Admins can view all time entries"
    ON public.time_entries FOR SELECT
    USING (EXISTS (
        SELECT 1 FROM public.user_profiles
        WHERE user_profiles.id = auth.uid()
        AND user_profiles.role = 'admin'
    ));

CREATE POLICY "Users can manage their own time entries"
    ON public.time_entries FOR ALL
    USING (user_id = auth.uid());

-- Expenses Policies
CREATE POLICY "Users can view their own expenses"
    ON public.expenses FOR SELECT
    USING (user_id = auth.uid());

CREATE POLICY "Admins can view all expenses"
    ON public.expenses FOR SELECT
    USING (EXISTS (
        SELECT 1 FROM public.user_profiles
        WHERE user_profiles.id = auth.uid()
        AND user_profiles.role = 'admin'
    ));

CREATE POLICY "Users can manage their own expenses"
    ON public.expenses FOR ALL
    USING (user_id = auth.uid());

-- Documents Policies
CREATE POLICY "Users can view accessible documents"
    ON public.documents FOR SELECT
    USING (EXISTS (
        SELECT 1 FROM public.document_access
        WHERE document_access.document_id = documents.id
        AND document_access.user_id = auth.uid()
    ));

CREATE POLICY "Admins can manage all documents"
    ON public.documents FOR ALL
    USING (EXISTS (
        SELECT 1 FROM public.user_profiles
        WHERE user_profiles.id = auth.uid()
        AND user_profiles.role = 'admin'
    ));

-- Document Access Policies
CREATE POLICY "Users can view their own access rights"
    ON public.document_access FOR SELECT
    USING (user_id = auth.uid());

CREATE POLICY "Admins can manage document access"
    ON public.document_access FOR ALL
    USING (EXISTS (
        SELECT 1 FROM public.user_profiles
        WHERE user_profiles.id = auth.uid()
        AND user_profiles.role = 'admin'
    ));

-- Bids Policies
CREATE POLICY "Employees can view bids"
    ON public.bids FOR SELECT
    USING (EXISTS (
        SELECT 1 FROM public.user_profiles
        WHERE user_profiles.id = auth.uid()
        AND user_profiles.role IN ('admin', 'employee')
    ));

CREATE POLICY "Admins can manage bids"
    ON public.bids FOR ALL
    USING (EXISTS (
        SELECT 1 FROM public.user_profiles
        WHERE user_profiles.id = auth.uid()
        AND user_profiles.role = 'admin'
    ));

-- Bid Items Policies
CREATE POLICY "Employees can view bid items"
    ON public.bid_items FOR SELECT
    USING (EXISTS (
        SELECT 1 FROM public.user_profiles
        WHERE user_profiles.id = auth.uid()
        AND user_profiles.role IN ('admin', 'employee')
    ));

CREATE POLICY "Admins can manage bid items"
    ON public.bid_items FOR ALL
    USING (EXISTS (
        SELECT 1 FROM public.user_profiles
        WHERE user_profiles.id = auth.uid()
        AND user_profiles.role = 'admin'
    ));

-- Notifications Policies
CREATE POLICY "Users can view their own notifications"
    ON public.notifications FOR SELECT
    USING (user_id = auth.uid());

CREATE POLICY "Users can update their own notifications"
    ON public.notifications FOR UPDATE
    USING (user_id = auth.uid());

-- Invoices Policies
CREATE POLICY "Employees can view invoices"
    ON public.invoices FOR SELECT
    USING (EXISTS (
        SELECT 1 FROM public.user_profiles
        WHERE user_profiles.id = auth.uid()
        AND user_profiles.role IN ('admin', 'employee')
    ));

CREATE POLICY "Admins can manage invoices"
    ON public.invoices FOR ALL
    USING (EXISTS (
        SELECT 1 FROM public.user_profiles
        WHERE user_profiles.id = auth.uid()
        AND user_profiles.role = 'admin'
    ));

-- Invoice Items Policies
CREATE POLICY "Employees can view invoice items"
    ON public.invoice_items FOR SELECT
    USING (EXISTS (
        SELECT 1 FROM public.user_profiles
        WHERE user_profiles.id = auth.uid()
        AND user_profiles.role IN ('admin', 'employee')
    ));

CREATE POLICY "Admins can manage invoice items"
    ON public.invoice_items FOR ALL
    USING (EXISTS (
        SELECT 1 FROM public.user_profiles
        WHERE user_profiles.id = auth.uid()
        AND user_profiles.role = 'admin'
    )); 