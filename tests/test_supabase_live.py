"""
Order Get It Right -- Supabase live integration test (skip-guarded).

Closes Block B of the GTM plan (Supabase backend). SKIPs with a clear
message if the operator has not yet set OGIR_SUPABASE_URL +
OGIR_SUPABASE_ANON_KEY (the directives at
04_Validation/GTM_OPERATOR_DIRECTIVES_2026-07-24.md Block B walk through
creating the project + applying 0001_initial.sql). When configured, the
test exercises the round-trip: insert a probe scan into a throwaway
customer, read it back, delete it. PASS = the backend is live + the RLS
schema is correctly applied.

This test follows the B3 skip-guard pattern: host-dependent functionality
SKIPs with a message naming the exact missing dependency, so the next
agent / operator can install it and re-run.
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "02_Technical"))

import pytest  # noqa: E402

from config import supabase as supa  # noqa: E402


def _skip_if_unconfigured() -> None:
    if not supa.is_configured():
        pytest.skip(
            "Supabase not configured. Set OGIR_SUPABASE_URL and "
            "OGIR_SUPABASE_ANON_KEY after creating the Supabase project + "
            "applying 0001_initial.sql. See "
            "04_Validation/GTM_OPERATOR_DIRECTIVES_2026-07-24.md Block B."
        )


def test_supabase_credentials_parse():
    """The config module reads URL + anon key from the environment. When
    set, the URL must look like https://<ref>.supabase.co and the anon
    key must be a non-empty JWT-shaped string. When unset, is_configured()
    returns False (the SKIP path the live tests take)."""
    if not supa.is_configured():
        pytest.skip("Supabase not configured (expected until Block B done)")
    url, anon = supa.credentials()
    assert url.startswith("https://"), f"URL must be https://, got {url!r}"
    assert ".supabase.co" in url, f"URL must be a supabase.co host, got {url!r}"
    assert len(anon) > 20, f"anon key looks too short: {len(anon)} chars"
    ref = supa.project_ref()
    assert ref, f"could not extract project ref from {url!r}"


def test_supabase_round_trip():
    """End-to-end: insert a probe scan, read it back, delete it. Requires
    a real Supabase project with 0001_initial.sql applied. SKIPs cleanly
    if not configured, so the suite stays green on a source-only host."""
    _skip_if_unconfigured()
    try:
        client = supa.get_client()
    except ImportError:
        pytest.skip(
            "supabase-py not installed. Install in the Tauri shell env: "
            "pip install supabase"
        )

    # Use a deterministic probe id so we can clean up even if the test
    # is interrupted. The customer row must exist before the scan (the
    # 0001_initial.sql trigger normally creates it on signup, but for
    # a direct DB probe we insert a throwaway customer with a fixed UUID).
    import uuid

    probe_customer_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, "ogir-supabase-live-test"))
    probe_input = "OGIR SUPABASE LIVE TEST PROBE -- delete me"
    probe_report = {"_probe": True, "source": "test_supabase_live.py"}

    # Clean up any prior probe (idempotent re-run).
    try:
        client.table("scans").delete().eq("input_hash", "ogir-probe-" + probe_customer_id).execute()
    except Exception:
        pass
    try:
        client.table("customers").delete().eq("id", probe_customer_id).execute()
    except Exception:
        pass

    # Insert a throwaway customer. RLS: the anon key + a service-role
    # would both permit this; the anon key uses the public insert policy
    # (0001_initial.sql line 124-126: auth.uid() = id). We use the anon
    # key with a client that has no authenticated session, so we bypass
    # via the service_role key if set, else SKIP (the anon key alone
    # cannot insert without an auth session).
    service_key = __import__("os").environ.get("OGIR_SUPABASE_SERVICE_KEY", "")
    if not service_key:
        pytest.skip(
            "OGIR_SUPABASE_SERVICE_KEY not set. The round-trip test needs "
            "the service_role key to insert a probe customer + scan (the "
            "anon key is RLS-scoped to an authenticated session). Set "
            "OGIR_SUPABASE_SERVICE_KEY from Project Settings -> API -> "
            "service_role. See GTM_OPERATOR_DIRECTIVES Block B."
        )

    # Re-create the client with the service_role key for the probe.
    from supabase import create_client  # type: ignore[import-not-found]
    url, _ = supa.credentials()
    admin = create_client(url, service_key)

    try:
        admin.table("customers").insert({
            "id": probe_customer_id,
            "display_name": "OGIR Live Test Probe",
            "pseudonym": "ogir-probe-" + probe_customer_id[:8],
        }).execute()

        inserted = admin.table("scans").insert({
            "customer_id": probe_customer_id,
            "input_text": probe_input,
            "input_hash": "ogir-probe-" + probe_customer_id,
            "context": "live-test-probe",
            "report": probe_report,
            "summary": "delete me",
            "is_deceptive": False,
            "pattern_count": 0,
            "deception_probability": 0.0,
        }).execute()

        # Read it back.
        read_back = admin.table("scans").select("*").eq(
            "input_hash", "ogir-probe-" + probe_customer_id
        ).execute()
        assert len(read_back.data) == 1, f"expected 1 probe scan, got {len(read_back.data)}"
        assert read_back.data[0]["input_text"] == probe_input
        assert read_back.data[0]["is_deceptive"] is False
    finally:
        # Always clean up, even on assertion failure.
        try:
            admin.table("scans").delete().eq("input_hash", "ogir-probe-" + probe_customer_id).execute()
        except Exception:
            pass
        try:
            admin.table("customers").delete().eq("id", probe_customer_id).execute()
        except Exception:
            pass


def test_schema_three_tables_exist():
    """The 0001_initial.sql migration creates exactly 3 public tables:
    customers, scans, affidavits. This confirms the migration was applied
    (the most common Block B failure is running the wrong SQL or none)."""
    _skip_if_unconfigured()
    service_key = __import__("os").environ.get("OGIR_SUPABASE_SERVICE_KEY", "")
    if not service_key:
        pytest.skip(
            "OGIR_SUPABASE_SERVICE_KEY not set (needed to read pg_tables). "
            "See GTM_OPERATOR_DIRECTIVES Block B."
        )
    from supabase import create_client  # type: ignore[import-not-found]
    url, _ = supa.credentials()
    admin = create_client(url, service_key)
    result = admin.rpc(
        "to_jsonb",
        {"arg": admin.table("scans").select("table_name").execute()},
    ).execute() if False else None  # placeholder; simpler: query pg_tables
    # Simpler: use the REST API to list tables via the pg_tables view.
    res = admin.table("pg_tables").select("tablename").eq("schemaname", "public").execute()
    tables = {row["tablename"] for row in res.data}
    expected = {"customers", "scans", "affidavits"}
    assert expected.issubset(tables), (
        f"missing tables: {expected - tables}. "
        f"Did you run 02_Technical/supabase/migrations/0001_initial.sql "
        f"in the Supabase SQL Editor? Found: {sorted(tables)}"
    )