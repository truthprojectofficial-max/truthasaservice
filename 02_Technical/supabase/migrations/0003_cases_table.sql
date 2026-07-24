-- OGIR Cases Table Migration (trial board / case management)
-- Adds the `cases` table for the 8-stage kanban flow
-- Created 2026-07-24
--
-- The cases table is the trial board backend. Each case moves through
-- 8 stages: inbox -> triage -> sealed -> running -> draft -> review -> delivered -> archived
--
-- Run in Supabase SQL Editor after 0001 + 0002

CREATE TABLE IF NOT EXISTS cases (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  customer_id UUID REFERENCES customers(id) ON DELETE CASCADE NOT NULL,
  order_id UUID REFERENCES orders(id) ON DELETE CASCADE,
  scan_id UUID REFERENCES scans(id) ON DELETE CASCADE,
  -- the 8-stage flow
  status TEXT NOT NULL DEFAULT 'inbox'
    CHECK (status IN ('inbox', 'triage', 'sealed', 'running', 'draft', 'review', 'delivered', 'archived', 'rejected')),
  -- triage
  triage_decision TEXT,
  triage_reason TEXT,
  triaged_at TIMESTAMPTZ,
  -- client-facing
  client_name TEXT NOT NULL,
  client_contact TEXT NOT NULL,
  document_summary TEXT,
  document_hash TEXT,
  -- chain
  chain_block_index INT,
  chain_block_hash TEXT,
  -- timeline
  created_at TIMESTAMPTZ DEFAULT now(),
  sealed_at TIMESTAMPTZ,
  delivered_at TIMESTAMPTZ,
  archived_at TIMESTAMPTZ,
  -- audit result (denormalized from scan for quick board view)
  final_action TEXT,
  deception_score NUMERIC(4,3),
  pattern_count INT DEFAULT 0
);

CREATE INDEX cases_status_idx ON cases(status);
CREATE INDEX cases_customer_idx ON cases(customer_id, created_at DESC);
CREATE INDEX cases_created_idx ON cases(created_at DESC);

-- RLS
ALTER TABLE cases ENABLE ROW LEVEL SECURITY;

-- Clients see their own cases
CREATE POLICY "clients_see_own_cases" ON cases
  FOR SELECT TO authenticated
  USING (customer_id = auth.uid());

-- Operator (service_role) can manage all cases
CREATE POLICY "operator_all_cases" ON cases
  FOR ALL TO service_role
  USING (true) WITH CHECK (true);

-- Trigger: auto-update case status when a scan completes
CREATE OR REPLACE FUNCTION auto_update_case_on_scan()
RETURNS TRIGGER AS $$
BEGIN
  UPDATE cases
  SET
    scan_id = NEW.id,
    status = 'draft',
    final_action = NEW.report->>'finalAction',
    deception_score = NEW.deception_probability,
    pattern_count = NEW.pattern_count,
    sealed_at = now()
  WHERE order_id = NEW.order_id AND status = 'running';
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_case_on_scan ON scans;
CREATE TRIGGER trigger_case_on_scan
  AFTER UPDATE ON scans
  FOR EACH ROW
  WHEN (NEW.is_deceptive IS NOT NULL)
  EXECUTE FUNCTION auto_update_case_on_scan();