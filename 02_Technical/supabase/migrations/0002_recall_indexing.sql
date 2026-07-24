-- OGIR Recall + Indexing System Migration
-- Adds documents + document_requests tables for document retrieval
-- + full-text search index for recall/indexing
-- Created 2026-07-24
--
-- Run in Supabase SQL Editor or via: supabase db push
--
-- This migration adds:
-- 1. documents table (stores audit reports, affidavits, evidence, explanations)
-- 2. document_requests table (tracks who requested what and when)
-- 3. Full-text search index on documents.content_text
-- 4. RLS policies (authenticated users see their own documents only)

-- ============================================================================
-- 1. DOCUMENTS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS documents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  scan_id UUID REFERENCES scans(id) ON DELETE CASCADE,
  customer_id UUID REFERENCES customers(id) ON DELETE CASCADE,
  document_type TEXT NOT NULL DEFAULT 'audit_report',
  -- Types: audit_report, affidavit, evidence, client_explanation, acl_demand
  content_text TEXT,
  content_hash TEXT NOT NULL,
  chain_block_index INT,
  chain_block_hash TEXT,
  created_at TIMESTAMPTZ DEFAULT now(),
  -- Full-text search vector (auto-generated from content_text)
  searchable tsvector GENERATED ALWAYS AS (to_tsvector('english', content_text)) STORED
);

-- GIN index for fast full-text search
CREATE INDEX IF NOT EXISTS documents_search_idx ON documents USING GIN(searchable);

-- Index for filtering by customer
CREATE INDEX IF NOT EXISTS documents_customer_idx ON documents(customer_id);

-- Index for filtering by scan
CREATE INDEX IF NOT EXISTS documents_scan_idx ON documents(scan_id);

-- ============================================================================
-- 2. DOCUMENT_REQUESTS TABLE (recall tracking)
-- ============================================================================
CREATE TABLE IF NOT EXISTS document_requests (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  requester_name TEXT NOT NULL,
  requester_contact TEXT NOT NULL,
  requester_type TEXT NOT NULL DEFAULT 'client',
  -- Types: client, court, regulator, oaic, operator
  document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
  request_reason TEXT,
  request_date TIMESTAMPTZ DEFAULT now(),
  delivered_at TIMESTAMPTZ,
  delivery_hash TEXT,
  delivery_method TEXT,
  -- Methods: email, portal_download, paper, usb
  status TEXT NOT NULL DEFAULT 'pending'
  -- Statuses: pending, fulfilled, refused, expired
);

CREATE INDEX IF NOT EXISTS document_requests_status_idx ON document_requests(status);
CREATE INDEX IF NOT EXISTS document_requests_requester_idx ON document_requests(requester_name);

-- ============================================================================
-- 3. ROW LEVEL SECURITY
-- ============================================================================
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE document_requests ENABLE ROW LEVEL SECURITY;

-- Documents: authenticated users see their own (via customer_id → auth.uid())
CREATE POLICY "users_see_own_documents" ON documents
  FOR SELECT TO authenticated
  USING (customer_id IN (
    SELECT id FROM customers WHERE auth_uid = auth.uid()
  ));

-- Operators (service_role) can see all documents
CREATE POLICY "operator_all_documents" ON documents
  FOR ALL TO service_role
  USING (true) WITH CHECK (true);

-- Document requests: authenticated users see their own requests
CREATE POLICY "users_see_own_requests" ON document_requests
  FOR SELECT TO authenticated
  USING (requester_contact IN (
    SELECT email FROM customers WHERE auth_uid = auth.uid()
  ));

-- Operators (service_role) can manage all requests
CREATE POLICY "operator_all_requests" ON document_requests
  FOR ALL TO service_role
  USING (true) WITH CHECK (true);

-- ============================================================================
-- 4. TRIGGER: auto-create a document record when a scan completes
-- ============================================================================
CREATE OR REPLACE FUNCTION auto_create_document_on_scan()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO documents (
    scan_id,
    customer_id,
    document_type,
    content_text,
    content_hash,
    chain_block_index,
    chain_block_hash
  ) VALUES (
    NEW.id,
    NEW.customer_id,
    'audit_report',
    COALESCE(NEW.result, ''),
    'pending_hash',
    NULL,
    NULL
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_auto_document ON scans;
CREATE TRIGGER trigger_auto_document
  AFTER INSERT ON scans
  FOR EACH ROW
  EXECUTE FUNCTION auto_create_document_on_scan();

-- ============================================================================
-- 5. HELPER: search documents by keyword (for the recall UI)
-- ============================================================================
CREATE OR REPLACE FUNCTION search_documents(
  query TEXT,
  filter_customer_id UUID DEFAULT NULL
)
RETURNS TABLE (
  id UUID,
  document_type TEXT,
  content_text TEXT,
  created_at TIMESTAMPTZ,
  rank REAL
)
LANGUAGE sql
SECURITY DEFINER
AS $$
  SELECT
    d.id,
    d.document_type,
    LEFT(d.content_text, 500) AS content_text,
    d.created_at,
    ts_rank(d.searchable, to_tsquery('english', query)) AS rank
  FROM documents d
  WHERE d.searchable @@ to_tsquery('english', query)
    AND (filter_customer_id IS NULL OR d.customer_id = filter_customer_id)
  ORDER BY rank DESC
  LIMIT 50;
$$;

-- ============================================================================
-- NOTES
-- ============================================================================
-- After running this migration:
-- 1. Verify in Table Editor: documents + document_requests tables appear
-- 2. Verify RLS: Dashboard → Database → Policies
-- 3. Test search: SELECT * FROM search_documents('invoice warranty');
-- 4. Every retrieval must seal a DOCUMENT_RETRIEVED block to the OGIR chain
-- 5. The content_hash should be the SHA-256 of the document content
--    (computed by the OGIR runtime, not by Postgres)