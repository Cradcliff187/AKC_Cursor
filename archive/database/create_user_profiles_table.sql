-- Drop and recreate the user_profiles table with the correct schema
DROP TABLE IF EXISTS public.user_profiles CASCADE;

CREATE TABLE IF NOT EXISTS public.user_profiles (
    id UUID PRIMARY KEY,
    auth_id TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    first_name TEXT,
    last_name TEXT,
    display_name TEXT,
    role TEXT NOT NULL DEFAULT 'employee',
    status TEXT NOT NULL DEFAULT 'active',
    phone TEXT,
    avatar_url TEXT,
    title TEXT,
    department TEXT,
    hire_date TIMESTAMP WITH TIME ZONE,
    last_login TIMESTAMP WITH TIME ZONE,
    preferences JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create the update_updated_at_column function if it doesn't exist
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for user_profiles to update updated_at column
CREATE TRIGGER update_user_profiles_updated_at
BEFORE UPDATE ON public.user_profiles
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Enable Row Level Security (RLS) on user_profiles
ALTER TABLE public.user_profiles ENABLE ROW LEVEL SECURITY;

-- Create RLS policies for user_profiles
CREATE POLICY user_profiles_select ON public.user_profiles
    FOR SELECT USING (auth_id = auth.uid()::text OR auth.role() = 'service_role');

CREATE POLICY user_profiles_insert ON public.user_profiles
    FOR INSERT WITH CHECK (auth_id = auth.uid()::text OR auth.role() = 'service_role');

CREATE POLICY user_profiles_update ON public.user_profiles
    FOR UPDATE USING (auth_id = auth.uid()::text OR auth.role() = 'service_role');

CREATE POLICY user_profiles_delete ON public.user_profiles
    FOR DELETE USING (auth_id = auth.uid()::text OR auth.role() = 'service_role');

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_user_profiles_auth_id ON public.user_profiles(auth_id);
CREATE INDEX IF NOT EXISTS idx_user_profiles_email ON public.user_profiles(email);
CREATE INDEX IF NOT EXISTS idx_user_profiles_role ON public.user_profiles(role);
CREATE INDEX IF NOT EXISTS idx_user_profiles_status ON public.user_profiles(status); 