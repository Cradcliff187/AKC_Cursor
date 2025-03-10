-- Users Table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    role VARCHAR(20) DEFAULT 'user',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Clients Table
CREATE TABLE IF NOT EXISTS clients (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    company_name VARCHAR(100),
    email VARCHAR(120),
    phone VARCHAR(20),
    address TEXT,
    city VARCHAR(50),
    state VARCHAR(50),
    zip_code VARCHAR(20),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE
);

-- Projects Table
CREATE TABLE IF NOT EXISTS projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    client_id UUID REFERENCES clients(id) ON DELETE SET NULL,
    client VARCHAR(100),
    status VARCHAR(20) DEFAULT 'Planning',
    start_date TIMESTAMP WITH TIME ZONE,
    end_date TIMESTAMP WITH TIME ZONE,
    budget DECIMAL(12, 2),
    budget_spent DECIMAL(12, 2) DEFAULT 0.0,
    location VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE
);

-- Add Supabase RLS (Row Level Security) Policies
-- Users Table Policies
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

CREATE POLICY users_select_policy ON users 
  FOR SELECT USING (auth.uid() = id OR 
                   EXISTS (SELECT 1 FROM users WHERE id = auth.uid() AND role = 'admin'));

CREATE POLICY users_insert_policy ON users 
  FOR INSERT WITH CHECK (auth.uid() = id OR 
                        EXISTS (SELECT 1 FROM users WHERE id = auth.uid() AND role = 'admin'));

CREATE POLICY users_update_policy ON users 
  FOR UPDATE USING (auth.uid() = id OR 
                   EXISTS (SELECT 1 FROM users WHERE id = auth.uid() AND role = 'admin'));

CREATE POLICY users_delete_policy ON users 
  FOR DELETE USING (auth.uid() = id OR 
                   EXISTS (SELECT 1 FROM users WHERE id = auth.uid() AND role = 'admin'));

-- Clients Table Policies
ALTER TABLE clients ENABLE ROW LEVEL SECURITY;

CREATE POLICY clients_select_policy ON clients 
  FOR SELECT USING (auth.uid() = user_id OR 
                   EXISTS (SELECT 1 FROM users WHERE id = auth.uid() AND role = 'admin'));

CREATE POLICY clients_insert_policy ON clients 
  FOR INSERT WITH CHECK (auth.uid() = user_id OR 
                        EXISTS (SELECT 1 FROM users WHERE id = auth.uid() AND role = 'admin'));

CREATE POLICY clients_update_policy ON clients 
  FOR UPDATE USING (auth.uid() = user_id OR 
                   EXISTS (SELECT 1 FROM users WHERE id = auth.uid() AND role = 'admin'));

CREATE POLICY clients_delete_policy ON clients 
  FOR DELETE USING (auth.uid() = user_id OR 
                   EXISTS (SELECT 1 FROM users WHERE id = auth.uid() AND role = 'admin'));

-- Projects Table Policies
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;

CREATE POLICY projects_select_policy ON projects 
  FOR SELECT USING (auth.uid() = user_id OR 
                   EXISTS (SELECT 1 FROM users WHERE id = auth.uid() AND role = 'admin'));

CREATE POLICY projects_insert_policy ON projects 
  FOR INSERT WITH CHECK (auth.uid() = user_id OR 
                        EXISTS (SELECT 1 FROM users WHERE id = auth.uid() AND role = 'admin'));

CREATE POLICY projects_update_policy ON projects 
  FOR UPDATE USING (auth.uid() = user_id OR 
                   EXISTS (SELECT 1 FROM users WHERE id = auth.uid() AND role = 'admin'));

CREATE POLICY projects_delete_policy ON projects 
  FOR DELETE USING (auth.uid() = user_id OR 
                   EXISTS (SELECT 1 FROM users WHERE id = auth.uid() AND role = 'admin')); 