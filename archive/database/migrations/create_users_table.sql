-- Create users table in public schema
create table public.users (
    id uuid not null references auth.users on delete cascade,
    email text unique not null,
    first_name text,
    last_name text,
    role text default 'user',
    created_at timestamptz default now(),
    updated_at timestamptz default now(),
    primary key (id)
);

-- Enable row level security
alter table public.users enable row level security;

-- Create policy to allow users to read their own data
create policy "Users can read their own data"
    on public.users
    for select
    using (auth.uid() = id);

-- Create policy to allow users to update their own data
create policy "Users can update their own data"
    on public.users
    for update
    using (auth.uid() = id);

-- Function to handle new user creation
create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer set search_path = public
as $$
begin
    insert into public.users (id, email)
    values (
        new.id,
        new.email
    );
    return new;
end;
$$;

-- Trigger to automatically create user profile
create trigger on_auth_user_created
    after insert on auth.users
    for each row execute procedure public.handle_new_user(); 