-- Cleanup Script for AKC Construction CRM
-- This script removes existing configurations before applying new ones

-- 1. Drop existing functions with CASCADE to remove dependent objects
DROP FUNCTION IF EXISTS public.verify_sql_configurations() CASCADE;
DROP FUNCTION IF EXISTS public.update_updated_at_column() CASCADE;

-- 2. Drop existing temporary tables
DROP TABLE IF EXISTS public.temp_config_export;

-- 3. Drop existing triggers (this may not be needed after CASCADE above, but keeping for safety)
DO $$
DECLARE
    t record;
BEGIN
    FOR t IN 
        SELECT trigger_name, event_object_table
        FROM information_schema.triggers
        WHERE trigger_schema = 'public'
        AND trigger_name LIKE 'update_%_updated_at'
    LOOP
        BEGIN
            EXECUTE format('DROP TRIGGER IF EXISTS %s ON public.%s', 
                          t.trigger_name, t.event_object_table);
            RAISE NOTICE 'Dropped trigger: %', t.trigger_name;
        EXCEPTION WHEN OTHERS THEN
            RAISE NOTICE 'Could not drop trigger %: %', t.trigger_name, SQLERRM;
        END;
    END LOOP;
END;
$$;

-- 4. Drop existing policies
DO $$
DECLARE
    pol record;
BEGIN
    FOR pol IN 
        SELECT policyname, tablename
        FROM pg_policies
        WHERE schemaname = 'public'
    LOOP
        BEGIN
            EXECUTE format('DROP POLICY IF EXISTS "%s" ON public.%s', 
                          pol.policyname, pol.tablename);
            RAISE NOTICE 'Dropped policy: %', pol.policyname;
        EXCEPTION WHEN OTHERS THEN
            RAISE NOTICE 'Could not drop policy %: %', pol.policyname, SQLERRM;
        END;
    END LOOP;
END;
$$;

-- 5. Drop existing indexes
DO $$
DECLARE
    idx record;
BEGIN
    FOR idx IN 
        SELECT indexname, tablename
        FROM pg_indexes
        WHERE schemaname = 'public'
        AND indexname LIKE 'idx_%'
    LOOP
        BEGIN
            EXECUTE format('DROP INDEX IF EXISTS public.%s', idx.indexname);
            RAISE NOTICE 'Dropped index: %', idx.indexname;
        EXCEPTION WHEN OTHERS THEN
            RAISE NOTICE 'Could not drop index %: %', idx.indexname, SQLERRM;
        END;
    END LOOP;
END;
$$;

-- 6. Disable Row Level Security on all tables
DO $$
DECLARE
    t record;
BEGIN
    FOR t IN 
        SELECT tablename
        FROM pg_tables
        WHERE schemaname = 'public'
        AND rowsecurity = true
    LOOP
        BEGIN
            EXECUTE format('ALTER TABLE public.%s DISABLE ROW LEVEL SECURITY', t.tablename);
            RAISE NOTICE 'Disabled RLS for table: %', t.tablename;
        EXCEPTION WHEN OTHERS THEN
            RAISE NOTICE 'Could not disable RLS on table %: %', t.tablename, SQLERRM;
        END;
    END LOOP;
END;
$$;

-- Notify completion
DO $$
BEGIN
    RAISE NOTICE 'Cleanup completed. Ready to run the main configuration script.';
END;
$$; 