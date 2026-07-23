-- Order Get It Right -- Initial database schema (2026-07-24)
--
-- Per the operator's architectural research at
--   .hermes/plans/OPERATOR_ARCHITECTURAL_RESEARCH_2026-07-24.txt
-- The schema is designed for:
--   - Order management (regional e-commerce merchants, 3PL, field service)
--   - Audit history (each text the user runs through the lie detector)
--   - Legal affidavit generation (per-pattern justification)
--   - Row-Level Security (users can only read their own data)
--   - Supabase Auth (GoTrue) for sign-up, sign-in, password reset
--
-- Operator runs:  supabase db push
-- (after creating the Supabase project, see Block B of the GTM plan)

-- =====================================================================
-- 1. PROFILES (extends Supabase auth.users)
-- =====================================================================

-- Create the profiles table. Each user has one profile.
-- auth.users is Supabase-managed; profiles stores app-specific fields.
create table public.profiles (
    id uuid references auth.users on delete cascade primary key,
    updated_at timestamp with time zone default timezone('utc'::text, now()) not null,
    full_name text,
    -- billing_tier: 'free' (default), 'pro' ($25/mo), 'enterprise'
    billing_tier text default 'free'::text check (billing_tier in ('free', 'pro', 'enterprise')),
    -- opt-in flags
    analytics_opt_in boolean default false not null,
    -- the user's chosen pseudonym (APP 2 compliance: anonymity/pseudonymity)
    pseudonym text unique
);

-- Index on pseudonym for fast lookups (e.g., "is this name taken?")
create index profiles_pseudonym_idx on public.profiles (pseudonym);

-- =====================================================================
-- 2. AUDITS (each text the user runs through the lie detector)
-- =====================================================================

-- An audit is one run of audit_text() on user-supplied text.
-- The full DeceptionReport is stored as JSONB.
create table public.audits (
    id uuid primary key default gen_random_uuid(),
    user_id uuid references auth.users on delete cascade not null,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null,
    -- the input text (or a hash if the user opts to redact)
    input_text text not null,
    input_hash text,  -- sha256 of input_text for de-duplication
    context text,     -- optional context (e.g., "contract clause")
    -- the lie-detector verdict: a DeceptionReport as JSONB
    -- (entropy, pattern matches, deception probability, forensic reasoning)
    report jsonb not null,
    -- the human-readable summary
    summary text,
    -- flags for filtering
    is_deceptive boolean not null,
    pattern_count integer not null default 0,
    deception_probability numeric(4,3) not null  -- 0.000 to 1.000
);

-- Indexes for the dashboard: most recent audits first, filtered by user
create index audits_user_id_created_at_idx on public.audits (user_id, created_at desc);
create index audits_is_deceptive_idx on public.audits (user_id, is_deceptive);
create index audits_input_hash_idx on public.audits (user_id, input_hash);

-- =====================================================================
-- 3. AFFIDAVITS (legal-grade documents for the legal_affidavit_generator)
-- =====================================================================

-- An affidavit is a generated document, signed and dated, that an
-- audit's findings can be relied upon in a court or compliance setting.
create table public.affidavits (
    id uuid primary key default gen_random_uuid(),
    user_id uuid references auth.users on delete cascade not null,
    audit_id uuid references public.audits on delete cascade not null,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null,
    -- the affidavit number (e.g., "OGIR-2026-0001")
    affidavit_number text unique not null,
    -- the operator (Justin Barnett, the OGIR Operator)
    operator_name text not null default 'Justin Barnett'::text,
    -- the affidavit body (Markdown with full DeceptionReport + ISO dates)
    body text not null,
    -- the chain witness: a block reference for non-repudiation
    chain_block_index bigint,
    -- status: 'draft', 'signed', 'served'
    status text default 'draft'::text check (status in ('draft', 'signed', 'served'))
);

create index affidavits_user_id_idx on public.affidavits (user_id, created_at desc);
create index affidavits_audit_id_idx on public.affidavits (audit_id);

-- =====================================================================
-- 4. ROW-LEVEL SECURITY (the heart of the Supabase contract)
-- =====================================================================

-- Enable RLS on every table. NO row is readable without a policy.
alter table public.profiles enable row level security;
alter table public.audits enable row level security;
alter table public.affidavits enable row level security;

-- profiles: users can read any profile (for collaboration features
-- like "show me my peer's pseudonym" if opt-in), but only update their own.
create policy "Allow public read access to profiles"
    on public.profiles for select
    using (true);

create policy "Allow individual update access to own profile"
    on public.profiles for update
    using (auth.uid() = id);

create policy "Allow individual insert on profile creation"
    on public.profiles for insert
    with check (auth.uid() = id);

-- audits: STRICT per-user. Users can only read/write their own audits.
create policy "Allow individual read access to own audits"
    on public.audits for select
    using (auth.uid() = user_id);

create policy "Allow individual insert access to own audits"
    on public.audits for insert
    with check (auth.uid() = user_id);

create policy "Allow individual update access to own audits"
    on public.audits for update
    using (auth.uid() = user_id);

create policy "Allow individual delete access to own audits"
    on public.audits for delete
    using (auth.uid() = user_id);

-- affidavits: same as audits, per-user only.
create policy "Allow individual read access to own affidavits"
    on public.affidavits for select
    using (auth.uid() = user_id);

create policy "Allow individual insert access to own affidavits"
    on public.affidavits for insert
    with check (auth.uid() = user_id);

create policy "Allow individual update access to own affidavits"
    on public.affidavits for update
    using (auth.uid() = user_id);

-- =====================================================================
-- 5. UTILITY: auto-create a profile when a user signs up
-- =====================================================================

-- When a new user signs up via Supabase Auth, automatically create
-- a corresponding row in public.profiles. This is a Supabase-recommended
-- pattern: a trigger on auth.users -> insert into public.profiles.
create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
begin
    insert into public.profiles (id, full_name, pseudonym)
    values (
        new.id,
        new.raw_user_meta_data->>'full_name',
        -- Default pseudonym: 'user-' || first 8 chars of the UUID
        'user-' || substring(new.id::text, 1, 8)
    );
    return new;
end;
$$;

-- Trigger fires on every new user creation
create trigger on_auth_user_created
    after insert on auth.users
    for each row execute function public.handle_new_user();

-- =====================================================================
-- 6. STORAGE: the optional Google Drive picker integration
-- =====================================================================

-- The research says we use Supabase Storage for user-uploaded files
-- that the user wants the lie-detector to scan. The Google Picker
-- only gives us a stream; we save the user's chosen file here.
-- (Operator may skip this bucket if they prefer local-only mode.)
--
-- create bucket 'user-files' with size limit 50 MB per file.
-- This is created via the Supabase dashboard, not via SQL.

-- =====================================================================
-- 7. INITIAL DATA: nothing. The schema starts empty.
-- =====================================================================

-- The first user signs up, a profile is auto-created, and the user
-- runs audits. The schema does not seed any default data.
