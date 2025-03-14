-- SQL Configurations for AKC Construction CRM
-- This script sets up all the required SQL configurations shown in the screenshot

-- 1. Temporary Configuration Export Table
CREATE TABLE IF NOT EXISTS public.temp_config_export (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    config_type TEXT NOT NULL,
    config_data JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL DEFAULT (NOW() + INTERVAL '24 hours')
);

COMMENT ON TABLE public.temp_config_export IS 'Temporary table for exporting configuration data';

-- Create an index on expires_at for cleanup
CREATE INDEX idx_temp_config_export_expires_at ON public.temp_config_export(expires_at);

-- 2. Automatic Timestamp Update Function
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION public.update_updated_at_column() IS 'Automatically updates the updated_at column on record modification';

-- Apply the timestamp update trigger to all tables
DO $$
DECLARE
    t record;
BEGIN
    FOR t IN 
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_type = 'BASE TABLE'
        AND table_name NOT LIKE 'pg_%'
        AND table_name NOT LIKE 'temp_%'
    LOOP
        -- Check if the table has an updated_at column
        IF EXISTS (
            SELECT 1 
            FROM information_schema.columns 
            WHERE table_schema = 'public' 
            AND table_name = t.table_name 
            AND column_name = 'updated_at'
        ) THEN
            -- Create trigger name
            EXECUTE format('DROP TRIGGER IF EXISTS update_%s_updated_at ON public.%s', 
                          t.table_name, t.table_name);
            
            EXECUTE format('CREATE TRIGGER update_%s_updated_at
                           BEFORE UPDATE ON public.%s
                           FOR EACH ROW
                           EXECUTE FUNCTION public.update_updated_at_column()', 
                          t.table_name, t.table_name);
                          
            RAISE NOTICE 'Created updated_at trigger for table: %', t.table_name;
        END IF;
    END LOOP;
END;
$$;

-- 3. Row Level Security Policies for Authenticated Users

-- First, enable RLS on all tables
DO $$
DECLARE
    t record;
BEGIN
    FOR t IN 
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_type = 'BASE TABLE'
        AND table_name NOT LIKE 'pg_%'
        AND table_name NOT LIKE 'temp_%'
    LOOP
        EXECUTE format('ALTER TABLE public.%s ENABLE ROW LEVEL SECURITY', t.table_name);
        RAISE NOTICE 'Enabled RLS for table: %', t.table_name;
    END LOOP;
END;
$$;

-- Create basic RLS policies for all tables
-- User Profiles Policies
-- First drop existing policies to avoid conflicts
DO $$
BEGIN
    -- Check if user_profiles table exists
    IF EXISTS (
        SELECT 1 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name = 'user_profiles'
    ) THEN
        -- Drop policies if they exist
        BEGIN
            EXECUTE 'DROP POLICY IF EXISTS "Users can view their own profile" ON public.user_profiles';
        EXCEPTION WHEN OTHERS THEN
            RAISE NOTICE 'Policy "Users can view their own profile" does not exist or cannot be dropped';
        END;
        
        BEGIN
            EXECUTE 'DROP POLICY IF EXISTS "Admins can view all profiles" ON public.user_profiles';
        EXCEPTION WHEN OTHERS THEN
            RAISE NOTICE 'Policy "Admins can view all profiles" does not exist or cannot be dropped';
        END;
        
        BEGIN
            EXECUTE 'DROP POLICY IF EXISTS "Admins can update profiles" ON public.user_profiles';
        EXCEPTION WHEN OTHERS THEN
            RAISE NOTICE 'Policy "Admins can update profiles" does not exist or cannot be dropped';
        END;
        
        -- Create policies
        EXECUTE '
        CREATE POLICY "Users can view their own profile"
            ON public.user_profiles FOR SELECT
            USING (auth.uid() = id)
        ';
        
        EXECUTE '
        CREATE POLICY "Admins can view all profiles"
            ON public.user_profiles FOR SELECT
            USING (EXISTS (
                SELECT 1 FROM public.user_profiles
                WHERE user_profiles.id = auth.uid()
                AND user_profiles.role = ''admin''
            ))
        ';
        
        EXECUTE '
        CREATE POLICY "Admins can update profiles"
            ON public.user_profiles FOR UPDATE
            USING (EXISTS (
                SELECT 1 FROM public.user_profiles
                WHERE user_profiles.id = auth.uid()
                AND user_profiles.role = ''admin''
            ))
        ';
        
        RAISE NOTICE 'Created policies for user_profiles table';
    ELSE
        RAISE NOTICE 'Table user_profiles does not exist, skipping policies';
    END IF;
END;
$$;

-- Clients Policies
DO $$
BEGIN
    -- Check if clients table exists
    IF EXISTS (
        SELECT 1 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name = 'clients'
    ) THEN
        -- Drop policies if they exist
        BEGIN
            EXECUTE 'DROP POLICY IF EXISTS "Employees and admins can view clients" ON public.clients';
        EXCEPTION WHEN OTHERS THEN
            RAISE NOTICE 'Policy "Employees and admins can view clients" does not exist or cannot be dropped';
        END;
        
        BEGIN
            EXECUTE 'DROP POLICY IF EXISTS "Admins can insert clients" ON public.clients';
        EXCEPTION WHEN OTHERS THEN
            RAISE NOTICE 'Policy "Admins can insert clients" does not exist or cannot be dropped';
        END;
        
        BEGIN
            EXECUTE 'DROP POLICY IF EXISTS "Admins can update clients" ON public.clients';
        EXCEPTION WHEN OTHERS THEN
            RAISE NOTICE 'Policy "Admins can update clients" does not exist or cannot be dropped';
        END;
        
        -- Create policies
        EXECUTE '
        CREATE POLICY "Employees and admins can view clients"
            ON public.clients FOR SELECT
            USING (EXISTS (
                SELECT 1 FROM public.user_profiles
                WHERE user_profiles.id = auth.uid()
                AND user_profiles.role IN (''admin'', ''employee'')
            ))
        ';
        
        EXECUTE '
        CREATE POLICY "Admins can insert clients"
            ON public.clients FOR INSERT
            WITH CHECK (EXISTS (
                SELECT 1 FROM public.user_profiles
                WHERE user_profiles.id = auth.uid()
                AND user_profiles.role = ''admin''
            ))
        ';
        
        EXECUTE '
        CREATE POLICY "Admins can update clients"
            ON public.clients FOR UPDATE
            USING (EXISTS (
                SELECT 1 FROM public.user_profiles
                WHERE user_profiles.id = auth.uid()
                AND user_profiles.role = ''admin''
            ))
        ';
        
        RAISE NOTICE 'Created policies for clients table';
    ELSE
        RAISE NOTICE 'Table clients does not exist, skipping policies';
    END IF;
END;
$$;

-- Projects Policies
DO $$
BEGIN
    -- Check if projects table exists
    IF EXISTS (
        SELECT 1 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name = 'projects'
    ) THEN
        -- Drop policies if they exist
        BEGIN
            EXECUTE 'DROP POLICY IF EXISTS "Employees and admins can view projects" ON public.projects';
        EXCEPTION WHEN OTHERS THEN
            RAISE NOTICE 'Policy "Employees and admins can view projects" does not exist or cannot be dropped';
        END;
        
        BEGIN
            EXECUTE 'DROP POLICY IF EXISTS "Admins can insert projects" ON public.projects';
        EXCEPTION WHEN OTHERS THEN
            RAISE NOTICE 'Policy "Admins can insert projects" does not exist or cannot be dropped';
        END;
        
        BEGIN
            EXECUTE 'DROP POLICY IF EXISTS "Admins can update projects" ON public.projects';
        EXCEPTION WHEN OTHERS THEN
            RAISE NOTICE 'Policy "Admins can update projects" does not exist or cannot be dropped';
        END;
        
        -- Create policies
        EXECUTE '
        CREATE POLICY "Employees and admins can view projects"
            ON public.projects FOR SELECT
            USING (EXISTS (
                SELECT 1 FROM public.user_profiles
                WHERE user_profiles.id = auth.uid()
                AND user_profiles.role IN (''admin'', ''employee'')
            ))
        ';
        
        EXECUTE '
        CREATE POLICY "Admins can insert projects"
            ON public.projects FOR INSERT
            WITH CHECK (EXISTS (
                SELECT 1 FROM public.user_profiles
                WHERE user_profiles.id = auth.uid()
                AND user_profiles.role = ''admin''
            ))
        ';
        
        EXECUTE '
        CREATE POLICY "Admins can update projects"
            ON public.projects FOR UPDATE
            USING (EXISTS (
                SELECT 1 FROM public.user_profiles
                WHERE user_profiles.id = auth.uid()
                AND user_profiles.role = ''admin''
            ))
        ';
        
        RAISE NOTICE 'Created policies for projects table';
    ELSE
        RAISE NOTICE 'Table projects does not exist, skipping policies';
    END IF;
END;
$$;

-- Create a default policy for all other tables
DO $$
DECLARE
    t record;
BEGIN
    FOR t IN 
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_type = 'BASE TABLE'
        AND table_name NOT LIKE 'pg_%'
        AND table_name NOT LIKE 'temp_%'
        AND table_name NOT IN ('user_profiles', 'clients', 'projects')
    LOOP
        -- First drop existing policies
        BEGIN
            EXECUTE format('DROP POLICY IF EXISTS "Admins have full access to %1$s" ON public.%1$s', t.table_name);
        EXCEPTION WHEN OTHERS THEN
            RAISE NOTICE 'Policy "Admins have full access to %1$s" does not exist or cannot be dropped', t.table_name;
        END;
        
        BEGIN
            EXECUTE format('DROP POLICY IF EXISTS "Employees can view %1$s" ON public.%1$s', t.table_name);
        EXCEPTION WHEN OTHERS THEN
            RAISE NOTICE 'Policy "Employees can view %1$s" does not exist or cannot be dropped', t.table_name;
        END;
        
        -- Create a default admin access policy
        EXECUTE format('
            CREATE POLICY "Admins have full access to %1$s"
            ON public.%1$s FOR ALL
            USING (EXISTS (
                SELECT 1 FROM public.user_profiles
                WHERE user_profiles.id = auth.uid()
                AND user_profiles.role = ''admin''
            ));
        ', t.table_name);
        
        -- Create a default employee read access policy
        EXECUTE format('
            CREATE POLICY "Employees can view %1$s"
            ON public.%1$s FOR SELECT
            USING (EXISTS (
                SELECT 1 FROM public.user_profiles
                WHERE user_profiles.id = auth.uid()
                AND user_profiles.role = ''employee''
            ));
        ', t.table_name);
        
        RAISE NOTICE 'Created default RLS policies for table: %', t.table_name;
    END LOOP;
END;
$$;

-- 4. Add Indexes for Performance Optimization

-- Create indexes on foreign keys
DO $$
DECLARE
    fk record;
BEGIN
    FOR fk IN 
        SELECT
            tc.table_schema, 
            tc.table_name, 
            kcu.column_name, 
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name
        FROM 
            information_schema.table_constraints AS tc 
            JOIN information_schema.key_column_usage AS kcu
              ON tc.constraint_name = kcu.constraint_name
              AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
              ON ccu.constraint_name = tc.constraint_name
              AND ccu.table_schema = tc.table_schema
        WHERE tc.constraint_type = 'FOREIGN KEY'
        AND tc.table_schema = 'public'
    LOOP
        -- Create index name
        BEGIN
            EXECUTE format('CREATE INDEX idx_%s_%s ON public.%s(%s)', 
                          fk.table_name, fk.column_name, fk.table_name, fk.column_name);
            RAISE NOTICE 'Created index on foreign key: %.%', fk.table_name, fk.column_name;
        EXCEPTION WHEN OTHERS THEN
            RAISE NOTICE 'Could not create index on %.%: %', fk.table_name, fk.column_name, SQLERRM;
        END;
    END LOOP;
END;
$$;

-- Create additional indexes on commonly queried columns
DO $$
BEGIN
    -- Projects status index
    IF EXISTS (
        SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'projects'
    ) AND EXISTS (
        SELECT 1 FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'projects' AND column_name = 'status'
    ) THEN
        BEGIN
            EXECUTE 'CREATE INDEX idx_projects_status ON public.projects(status)';
            RAISE NOTICE 'Created index on projects.status';
        EXCEPTION WHEN OTHERS THEN
            RAISE NOTICE 'Could not create index on projects.status: %', SQLERRM;
        END;
    END IF;
    
    -- Tasks indexes
    IF EXISTS (
        SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'tasks'
    ) THEN
        -- Status index
        IF EXISTS (
            SELECT 1 FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'tasks' AND column_name = 'status'
        ) THEN
            BEGIN
                EXECUTE 'CREATE INDEX idx_tasks_status ON public.tasks(status)';
                RAISE NOTICE 'Created index on tasks.status';
            EXCEPTION WHEN OTHERS THEN
                RAISE NOTICE 'Could not create index on tasks.status: %', SQLERRM;
            END;
        END IF;
        
        -- Priority index
        IF EXISTS (
            SELECT 1 FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'tasks' AND column_name = 'priority'
        ) THEN
            BEGIN
                EXECUTE 'CREATE INDEX idx_tasks_priority ON public.tasks(priority)';
                RAISE NOTICE 'Created index on tasks.priority';
            EXCEPTION WHEN OTHERS THEN
                RAISE NOTICE 'Could not create index on tasks.priority: %', SQLERRM;
            END;
        END IF;
        
        -- Due date index
        IF EXISTS (
            SELECT 1 FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'tasks' AND column_name = 'due_date'
        ) THEN
            BEGIN
                EXECUTE 'CREATE INDEX idx_tasks_due_date ON public.tasks(due_date)';
                RAISE NOTICE 'Created index on tasks.due_date';
            EXCEPTION WHEN OTHERS THEN
                RAISE NOTICE 'Could not create index on tasks.due_date: %', SQLERRM;
            END;
        END IF;
    END IF;
    
    -- Invoices indexes
    IF EXISTS (
        SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'invoices'
    ) THEN
        -- Status index
        IF EXISTS (
            SELECT 1 FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'invoices' AND column_name = 'status'
        ) THEN
            BEGIN
                EXECUTE 'CREATE INDEX idx_invoices_status ON public.invoices(status)';
                RAISE NOTICE 'Created index on invoices.status';
            EXCEPTION WHEN OTHERS THEN
                RAISE NOTICE 'Could not create index on invoices.status: %', SQLERRM;
            END;
        END IF;
        
        -- Due date index
        IF EXISTS (
            SELECT 1 FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'invoices' AND column_name = 'due_date'
        ) THEN
            BEGIN
                EXECUTE 'CREATE INDEX idx_invoices_due_date ON public.invoices(due_date)';
                RAISE NOTICE 'Created index on invoices.due_date';
            EXCEPTION WHEN OTHERS THEN
                RAISE NOTICE 'Could not create index on invoices.due_date: %', SQLERRM;
            END;
        END IF;
    END IF;
    
    -- Documents entity_type and entity_id index
    IF EXISTS (
        SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'documents'
    ) AND EXISTS (
        SELECT 1 FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'documents' AND column_name = 'entity_type'
    ) AND EXISTS (
        SELECT 1 FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'documents' AND column_name = 'entity_id'
    ) THEN
        BEGIN
            EXECUTE 'CREATE INDEX idx_documents_entity_type_entity_id ON public.documents(entity_type, entity_id)';
            RAISE NOTICE 'Created index on documents.entity_type, documents.entity_id';
        EXCEPTION WHEN OTHERS THEN
            RAISE NOTICE 'Could not create index on documents.entity_type, documents.entity_id: %', SQLERRM;
        END;
    END IF;
    
    -- Time entries date index
    IF EXISTS (
        SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'time_entries'
    ) AND EXISTS (
        SELECT 1 FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'time_entries' AND column_name = 'date'
    ) THEN
        BEGIN
            EXECUTE 'CREATE INDEX idx_time_entries_date ON public.time_entries(date)';
            RAISE NOTICE 'Created index on time_entries.date';
        EXCEPTION WHEN OTHERS THEN
            RAISE NOTICE 'Could not create index on time_entries.date: %', SQLERRM;
        END;
    END IF;
    
    -- Expenses date index
    IF EXISTS (
        SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'expenses'
    ) AND EXISTS (
        SELECT 1 FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'expenses' AND column_name = 'date'
    ) THEN
        BEGIN
            EXECUTE 'CREATE INDEX idx_expenses_date ON public.expenses(date)';
            RAISE NOTICE 'Created index on expenses.date';
        EXCEPTION WHEN OTHERS THEN
            RAISE NOTICE 'Could not create index on expenses.date: %', SQLERRM;
        END;
    END IF;
    
    -- Notifications read index
    IF EXISTS (
        SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'notifications'
    ) AND EXISTS (
        SELECT 1 FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'notifications' AND column_name = 'read'
    ) THEN
        BEGIN
            EXECUTE 'CREATE INDEX idx_notifications_read ON public.notifications(read)';
            RAISE NOTICE 'Created index on notifications.read';
        EXCEPTION WHEN OTHERS THEN
            RAISE NOTICE 'Could not create index on notifications.read: %', SQLERRM;
        END;
    END IF;
    
    -- Notifications user_id index
    IF EXISTS (
        SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'notifications'
    ) AND EXISTS (
        SELECT 1 FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'notifications' AND column_name = 'user_id'
    ) THEN
        BEGIN
            EXECUTE 'CREATE INDEX idx_notifications_user_id ON public.notifications(user_id)';
            RAISE NOTICE 'Created index on notifications.user_id';
        EXCEPTION WHEN OTHERS THEN
            RAISE NOTICE 'Could not create index on notifications.user_id: %', SQLERRM;
        END;
    END IF;
END;
$$;

-- 5. Enable Row Level Security (already done in step 3)

-- Create a function to verify the configuration
CREATE OR REPLACE FUNCTION public.verify_sql_configurations()
RETURNS TABLE (
    configuration_name TEXT,
    status BOOLEAN,
    details TEXT
) AS $$
BEGIN
    -- Check Temporary Configuration Export Table
    RETURN QUERY
    SELECT 
        'Temporary Configuration Export Table' AS configuration_name,
        EXISTS (
            SELECT 1 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'temp_config_export'
        ) AS status,
        CASE 
            WHEN EXISTS (
                SELECT 1 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'temp_config_export'
            ) THEN 'Table exists'
            ELSE 'Table does not exist'
        END AS details;

    -- Check Automatic Timestamp Update Function
    RETURN QUERY
    SELECT 
        'Automatic Timestamp Update Function' AS configuration_name,
        EXISTS (
            SELECT 1 
            FROM pg_proc 
            WHERE proname = 'update_updated_at_column'
            AND pronamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public')
        ) AS status,
        CASE 
            WHEN EXISTS (
                SELECT 1 
                FROM pg_proc 
                WHERE proname = 'update_updated_at_column'
                AND pronamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public')
            ) THEN 'Function exists'
            ELSE 'Function does not exist'
        END AS details;

    -- Check Row Level Security Policies
    RETURN QUERY
    SELECT 
        'Row Level Security Policies' AS configuration_name,
        EXISTS (
            SELECT 1 
            FROM pg_policies
            WHERE schemaname = 'public'
        ) AS status,
        (SELECT COUNT(*)::TEXT || ' policies found' FROM pg_policies WHERE schemaname = 'public') AS details;

    -- Check Indexes for Performance
    RETURN QUERY
    SELECT 
        'Indexes for Performance' AS configuration_name,
        EXISTS (
            SELECT 1 
            FROM pg_indexes
            WHERE schemaname = 'public'
            AND indexname LIKE 'idx_%'
        ) AS status,
        (SELECT COUNT(*)::TEXT || ' indexes found' FROM pg_indexes WHERE schemaname = 'public' AND indexname LIKE 'idx_%') AS details;

    -- Check Row Level Security Enabled
    RETURN QUERY
    SELECT 
        'Row Level Security Enabled' AS configuration_name,
        EXISTS (
            SELECT 1 
            FROM pg_tables
            WHERE schemaname = 'public'
            AND rowsecurity = true
        ) AS status,
        (SELECT COUNT(*)::TEXT || ' tables with RLS enabled' FROM pg_tables WHERE schemaname = 'public' AND rowsecurity = true) AS details;
END;
$$ LANGUAGE plpgsql;

-- Run the verification function
SELECT * FROM public.verify_sql_configurations(); 