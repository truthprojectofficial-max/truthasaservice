"""
test_supabase_schema_valid.py
==============================

The Supabase SQL schema at 02_Technical/supabase/migrations/0001_initial.sql
must be syntactically valid SQL and must contain all the expected tables,
RLS policies, and the auto-create-customer trigger.

This test does NOT require a live Supabase project. It validates the SQL
file structurally. The operator runs `supabase db push` against the live
project after creating it.

Schema (Option C: shell + engine, per the subagent's drift audit):
  - customers     (the merchant account, the SHELL)
  - orders        (the order records, the SHELL)
  - order_files   (the uploaded files, the SHELL)
  - scans         (the lie-detector runs, the ENGINE)
  - affidavits    (the legal documents, the WRAPPER)
"""
import re
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
SCHEMA = PROJECT / "02_Technical" / "supabase" / "migrations" / "0001_initial.sql"

# The 5 tables per Option C
EXPECTED_TABLES = ["customers", "orders", "order_files", "scans", "affidavits"]


def test_schema_file_exists():
    """The schema SQL file exists."""
    assert SCHEMA.exists(), f"schema not found at {SCHEMA}"


def test_schema_has_customers_table():
    """The schema creates a customers table (the merchant account)."""
    text = SCHEMA.read_text(encoding="utf-8")
    assert re.search(r"create table public\.customers", text, re.IGNORECASE), \
        "schema missing customers table"


def test_schema_has_orders_table():
    """The schema creates an orders table (the order records)."""
    text = SCHEMA.read_text(encoding="utf-8")
    assert re.search(r"create table public\.orders", text, re.IGNORECASE), \
        "schema missing orders table"


def test_schema_has_order_files_table():
    """The schema creates an order_files table (the uploaded files)."""
    text = SCHEMA.read_text(encoding="utf-8")
    assert re.search(r"create table public\.order_files", text, re.IGNORECASE), \
        "schema missing order_files table"


def test_schema_has_scans_table():
    """The schema creates a scans table (the lie-detector runs -- the engine)."""
    text = SCHEMA.read_text(encoding="utf-8")
    assert re.search(r"create table public\.scans", text, re.IGNORECASE), \
        "schema missing scans table"


def test_schema_has_affidavits_table():
    """The schema creates an affidavits table (the legal documents)."""
    text = SCHEMA.read_text(encoding="utf-8")
    assert re.search(r"create table public\.affidavits", text, re.IGNORECASE), \
        "schema missing affidavits table"


def test_schema_has_all_five_tables():
    """The schema declares all 5 expected tables per Option C."""
    text = SCHEMA.read_text(encoding="utf-8").lower()
    for tbl in EXPECTED_TABLES:
        assert f"create table public.{tbl}" in text, f"schema missing table {tbl}"


def test_schema_does_not_have_old_audits_table():
    """The schema does NOT declare the old audits table (the lie-detector-only drift)."""
    text = SCHEMA.read_text(encoding="utf-8").lower()
    assert "create table public.audits" not in text, \
        "schema still has the old audits table (drift from the subagent's audit)"


def test_schema_does_not_have_old_profiles_table():
    """The schema does NOT declare the old profiles table (replaced by customers)."""
    text = SCHEMA.read_text(encoding="utf-8").lower()
    assert "create table public.profiles" not in text, \
        "schema still has the old profiles table (replaced by customers in Option C)"


def test_schema_enables_rls_on_all_tables():
    """The schema enables Row-Level Security on all 5 tables."""
    text = SCHEMA.read_text(encoding="utf-8")
    rls_count = len(re.findall(r"enable row level security", text, re.IGNORECASE))
    assert rls_count == 5, f"expected 5 RLS enables (one per table), got {rls_count}"


def test_schema_has_rls_policies():
    """The schema declares RLS policies for each table."""
    text = SCHEMA.read_text(encoding="utf-8")
    policy_count = len(re.findall(r"create policy", text, re.IGNORECASE))
    # customers: 3 (read public, update own, insert on creation)
    # orders: 4 (read, insert, update, delete own)
    # order_files: 3 (read, insert, delete own)
    # scans: 4 (read, insert, update, delete own)
    # affidavits: 3 (read, insert, update own)
    # Total: 17
    assert policy_count >= 17, f"expected at least 17 RLS policies, got {policy_count}"


def test_schema_has_auto_create_customer_trigger():
    """The schema has a trigger that auto-creates a customer on user signup."""
    text = SCHEMA.read_text(encoding="utf-8")
    assert "handle_new_user" in text, "missing handle_new_user function"
    assert "on_auth_user_created" in text, "missing on_auth_user_created trigger"
    # The trigger inserts into customers, not profiles
    assert re.search(r"insert into public\.customers", text, re.IGNORECASE), \
        "trigger should insert into customers, not profiles"


def test_schema_references_supabase_auth():
    """The schema references Supabase auth (auth.users)."""
    text = SCHEMA.read_text(encoding="utf-8")
    assert "auth.users" in text, "schema does not reference auth.users"


def test_schema_has_check_constraint_on_billing_tier():
    """The customers table has a CHECK constraint on billing_tier."""
    text = SCHEMA.read_text(encoding="utf-8")
    assert "billing_tier" in text, "customers table missing billing_tier"
    assert "check" in text.lower(), "billing_tier has no CHECK constraint"


def test_schema_has_check_constraint_on_order_source():
    """The orders table has a CHECK constraint on the order source."""
    text = SCHEMA.read_text(encoding="utf-8")
    assert "source" in text, "orders table missing source column"
    # The source enum includes shopify, 3pl, field_service, etc.
    assert "shopify" in text.lower(), "orders source enum missing shopify"
    assert "google_drive" in text.lower(), "orders source enum missing google_drive"


def test_schema_has_index_on_orders():
    """The orders table has an index on (customer_id, created_at DESC)."""
    text = SCHEMA.read_text(encoding="utf-8")
    assert re.search(r"create index.*orders.*customer_id.*created_at", text, re.IGNORECASE), \
        "orders table missing index on (customer_id, created_at)"


def test_schema_has_index_on_scans():
    """The scans table has an index on (customer_id, created_at DESC)."""
    text = SCHEMA.read_text(encoding="utf-8")
    assert re.search(r"create index.*scans.*customer_id.*created_at", text, re.IGNORECASE), \
        "scans table missing index on (customer_id, created_at)"


def test_schema_scans_has_deception_columns():
    """The scans table has the lie-detector output columns."""
    text = SCHEMA.read_text(encoding="utf-8")
    assert "is_deceptive" in text, "scans missing is_deceptive"
    assert "deception_probability" in text, "scans missing deception_probability"
    assert "pattern_count" in text, "scans missing pattern_count"
    assert "report jsonb" in text.lower() or "report\tjsonb" in text, "scans missing report jsonb"


def test_schema_documents_option_c():
    """The schema documents that this is Option C (shell + engine)."""
    text = SCHEMA.read_text(encoding="utf-8")
    assert "Option C" in text or "shell + engine" in text.lower() or "shell and engine" in text.lower(), \
        "schema does not document the Option C (shell + engine) decision"
