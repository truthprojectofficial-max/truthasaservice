-- Order Get It Right -- Initial database schema (2026-07-24, Option C: SHELL + ENGINE)
--
-- This schema is the merge of two product visions:
--   1. SHELL: the order-management platform from the operator's 893-line research
--      (Shopify/3PL/field service merchants who upload order files to be audited)
--   2. ENGINE: the forensic lie-detector (the actual product in 02_Technical/src/engines/)
--
-- The product is BOTH. The shell wraps the engine. A customer uploads an order
-- file via Google Drive, the engine runs the lie-detector on it, the result
-- is an affidavit the customer can rely on.
--
-- Per the subagent's drift audit (block 40713), the previous schema
-- (profiles/audits/affidavits) conflated the shell and the engine. The
-- corrected schema is: customers + orders + order_files + scans + affidavits.
--
-- Operator runs:  supabase db push
-- (after creating the Supabase project, see Block B of the GTM plan)

-- =====================================================================
-- 1. CUSTOMERS (the merchant account: Shopify, 3PL, field service)
-- =====================================================================

-- Customers are the merchants. They sign up via Supabase Auth (GoTrue).
-- Each customer has one profile (extends Supabase auth.users).
create table public.customers (
    id uuid references auth.users on delete cascade primary key,
    updated_at timestamp with time zone default timezone('utc'::text, now()) not null,
    -- business identity
    business_name text not null,
    abn text,  -- Australian Business Number (for invoicing)
    contact_email text not null,
    -- billing_tier: 'free' (default), 'pro' ($25/mo), 'enterprise' ($99/mo)
    billing_tier text default 'free'::text check (billing_tier in ('free', 'pro', 'enterprise')),
    -- opt-in flags
    analytics_opt_in boolean default false not null,
    -- the customer's chosen pseudonym (APP 2 compliance: anonymity/pseudonymity)
    pseudonym text unique
);

create index customers_business_name_idx on public.customers (business_name);
create index customers_pseudonym_idx on public.customers (pseudonym);

-- =====================================================================
-- 2. ORDERS (the order records: Shopify orders, 3PL shipments, etc.)
-- =====================================================================

-- An order is one transaction the customer wants audited.
-- The customer's intake channel (Shopify, CSV upload, Google Drive) is captured.
create table public.orders (
    id uuid primary key default gen_random_uuid(),
    customer_id uuid references public.customers on delete cascade not null,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null,
    -- external order id (Shopify order_id, 3PL tracking_number, etc.)
    external_order_id text not null,
    source text not null check (source in ('shopify', '3pl', 'field_service', 'csv_upload', 'google_drive', 'manual')),
    -- the merchant's description of the order
    description text,
    -- the value of the order (for invoicing + risk scoring)
    value_aud numeric(12,2),  -- Australian Dollars
    -- the merchant's contact for this order (e.g., customer name, vendor name)
    counterparty text,
    -- status: 'received', 'scanning', 'scanned', 'affidavit_ready', 'closed'
    status text default 'received'::text check (status in ('received', 'scanning', 'scanned', 'affidavit_ready', 'closed')),
    -- the latest scan's deception_probability (denormalized for dashboard)
    risk_score numeric(4,3),
    unique (customer_id, source, external_order_id)
);

create index orders_customer_id_created_at_idx on public.orders (customer_id, created_at desc);
create index orders_source_idx on public.orders (customer_id, source);
create index orders_status_idx on public.orders (customer_id, status);
create index orders_risk_score_idx on public.orders (customer_id, risk_score);

-- =====================================================================
-- 3. ORDER_FILES (the raw files the customer uploaded for scanning)
-- =====================================================================

-- An order can have multiple files (PDF contract, email thread, invoice image).
-- Files are stored in Supabase Storage; this table holds the metadata + pointer.
create table public.order_files (
    id uuid primary key default gen_random_uuid(),
    order_id uuid references public.orders on delete cascade not null,
    customer_id uuid references public.customers on delete cascade not null,  -- denormalized for RLS
    created_at timestamp with time zone default timezone('utc'::text, now()) not null,
    -- the file as uploaded
    file_name text not null,
    file_size_bytes bigint not null check (file_size_bytes > 0),
    mime_type text not null,
    -- the storage bucket path (e.g., 'customer-uuid/order-uuid/filename.pdf')
    storage_path text not null,
    -- optional sha256 for de-duplication
    file_hash text,
    -- if the file came from Google Drive, the drive file id
    google_drive_file_id text,
    unique (customer_id, storage_path)
);

create index order_files_order_id_idx on public.order_files (order_id);
create index order_files_customer_id_idx on public.order_files (customer_id);

-- =====================================================================
-- 4. SCANS (the lie-detector runs -- the ENGINE output)
-- =====================================================================

-- A scan is one run of the lie-detector engine on one order_file.
-- This is where the forensic output lives.
create table public.scans (
    id uuid primary key default gen_random_uuid(),
    customer_id uuid references public.customers on delete cascade not null,  -- denormalized for RLS
    order_id uuid references public.orders on delete cascade not null,
    order_file_id uuid references public.order_files on delete cascade not null,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null,
    -- the input text the engine analyzed (or a hash if the user opts to redact)
    input_text text not null,
    input_hash text,  -- sha256 of input_text for de-duplication
    -- the full DeceptionReport as JSONB (entropy, pattern matches, deception prob)
    report jsonb not null,
    -- the human-readable summary
    summary text,
    -- the engine version (so we can re-run old scans when the engine improves)
    engine_version text not null default '0.1.0'::text,
    -- flags for filtering
    is_deceptive boolean not null,
    pattern_count integer not null default 0,
    deception_probability numeric(4,3) not null check (deception_probability >= 0 and deception_probability <= 1)
);

create index scans_customer_id_created_at_idx on public.scans (customer_id, created_at desc);
create index scans_order_id_idx on public.scans (order_id);
create index scans_order_file_id_idx on public.scans (order_file_id);
create index scans_is_deceptive_idx on public.scans (customer_id, is_deceptive);
create index scans_input_hash_idx on public.scans (customer_id, input_hash);
create index scans_deception_probability_idx on public.scans (customer_id, deception_probability);

-- =====================================================================
-- 5. AFFIDAVITS (legal-grade documents for the legal_affidavit_generator)
-- =====================================================================

-- An affidavit is a generated document, signed and dated, that an
-- order's scans can be relied upon in a court or compliance setting.
create table public.affidavits (
    id uuid primary key default gen_random_uuid(),
    customer_id uuid references public.customers on delete cascade not null,  -- denormalized for RLS
    order_id uuid references public.orders on delete cascade not null,
    scan_id uuid references public.scans on delete cascade not null,
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

create index affidavits_customer_id_idx on public.affidavits (customer_id, created_at desc);
create index affidavits_order_id_idx on public.affidavits (order_id);
create index affidavits_scan_id_idx on public.affidavits (scan_id);

-- =====================================================================
-- 6. ROW-LEVEL SECURITY (per the research)
-- =====================================================================

alter table public.customers enable row level security;
alter table public.orders enable row level security;
alter table public.order_files enable row level security;
alter table public.scans enable row level security;
alter table public.affidavits enable row level security;

-- customers: read any customer (for collaboration features), update only own.
create policy "Allow public read access to customers"
    on public.customers for select
    using (true);

create policy "Allow individual update access to own customer"
    on public.customers for update
    using (auth.uid() = id);

create policy "Allow individual insert on customer creation"
    on public.customers for insert
    with check (auth.uid() = id);

-- orders: STRICT per-customer.
create policy "Allow individual read access to own orders"
    on public.orders for select
    using (auth.uid() = customer_id);

create policy "Allow individual insert access to own orders"
    on public.orders for insert
    with check (auth.uid() = customer_id);

create policy "Allow individual update access to own orders"
    on public.orders for update
    using (auth.uid() = customer_id);

create policy "Allow individual delete access to own orders"
    on public.orders for delete
    using (auth.uid() = customer_id);

-- order_files: STRICT per-customer.
create policy "Allow individual read access to own order_files"
    on public.order_files for select
    using (auth.uid() = customer_id);

create policy "Allow individual insert access to own order_files"
    on public.order_files for insert
    with check (auth.uid() = customer_id);

create policy "Allow individual delete access to own order_files"
    on public.order_files for delete
    using (auth.uid() = customer_id);

-- scans: STRICT per-customer.
create policy "Allow individual read access to own scans"
    on public.scans for select
    using (auth.uid() = customer_id);

create policy "Allow individual insert access to own scans"
    on public.scans for insert
    with check (auth.uid() = customer_id);

create policy "Allow individual update access to own scans"
    on public.scans for update
    using (auth.uid() = customer_id);

create policy "Allow individual delete access to own scans"
    on public.scans for delete
    using (auth.uid() = customer_id);

-- affidavits: STRICT per-customer.
create policy "Allow individual read access to own affidavits"
    on public.affidavits for select
    using (auth.uid() = customer_id);

create policy "Allow individual insert access to own affidavits"
    on public.affidavits for insert
    with check (auth.uid() = customer_id);

create policy "Allow individual update access to own affidavits"
    on public.affidavits for update
    using (auth.uid() = customer_id);

-- =====================================================================
-- 7. UTILITY: auto-create a customer when a user signs up
-- =====================================================================

create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
begin
    insert into public.customers (id, business_name, contact_email, pseudonym)
    values (
        new.id,
        coalesce(new.raw_user_meta_data->>'business_name', 'New Business'),
        new.email,
        'cust-' || substring(new.id::text, 1, 8)
    );
    return new;
end;
$$;

create trigger on_auth_user_created
    after insert on auth.users
    for each row execute function public.handle_new_user();

-- =====================================================================
-- 8. STORAGE BUCKETS
-- =====================================================================

-- Per the research, the order files go to a Supabase Storage bucket
-- 'order-files' (size limit 50 MB per file).
-- This is created via the Supabase dashboard, not via SQL.

-- =====================================================================
-- 9. SCHEMA CHANGE LOG
-- =====================================================================

-- 2026-07-24  v0.1.0  Option C: customers + orders + order_files + scans + affidavits
--                     (replaces the previous profiles/audits/affidavits schema)
--                     per the subagent's drift audit (chain block 40713).
