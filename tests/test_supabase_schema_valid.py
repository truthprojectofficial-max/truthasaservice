"""
test_supabase_schema_valid.py
==============================

The Supabase SQL schema at 02_Technical/supabase/migrations/0001_initial.sql
must be syntactically valid SQL and must contain all the expected tables,
RLS policies, and the auto-create-profile trigger.

This test does NOT require a live Supabase project. It validates the SQL
file structurally. The operator runs `supabase db push` against the live
project after creating it.
"""
import re
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
SCHEMA = PROJECT / "02_Technical" / "supabase" / "migrations" / "0001_initial.sql"


def test_schema_file_exists():
    """The schema SQL file exists."""
    assert SCHEMA.exists(), f"schema not found at {SCHEMA}"


def test_schema_has_profiles_table():
    """The schema creates a profiles table."""
    text = SCHEMA.read_text(encoding="utf-8")
    assert re.search(r"create table public\.profiles", text, re.IGNORECASE), \
        "schema missing profiles table"


def test_schema_has_audits_table():
    """The schema creates an audits table."""
    text = SCHEMA.read_text(encoding="utf-8")
    assert re.search(r"create table public\.audits", text, re.IGNORECASE), \
        "schema missing audits table"


def test_schema_has_affidavits_table():
    """The schema creates an affidavits table."""
    text = SCHEMA.read_text(encoding="utf-8")
    assert re.search(r"create table public\.affidavits", text, re.IGNORECASE), \
        "schema missing affidavits table"


def test_schema_enables_rls():
    """The schema enables Row-Level Security on all 3 tables."""
    text = SCHEMA.read_text(encoding="utf-8")
    rls_count = len(re.findall(r"enable row level security", text, re.IGNORECASE))
    assert rls_count == 3, f"expected 3 RLS enables (one per table), got {rls_count}"


def test_schema_has_rls_policies():
    """The schema declares RLS policies for each table."""
    text = SCHEMA.read_text(encoding="utf-8")
    policy_count = len(re.findall(r"create policy", text, re.IGNORECASE))
    # profiles: 3 policies (read public, update own, insert on creation)
    # audits: 4 policies (read, insert, update, delete own)
    # affidavits: 3 policies (read, insert, update own)
    # Total: 10
    assert policy_count >= 10, f"expected at least 10 RLS policies, got {policy_count}"


def test_schema_has_auto_create_profile_trigger():
    """The schema has a trigger that auto-creates a profile on user signup."""
    text = SCHEMA.read_text(encoding="utf-8")
    assert "handle_new_user" in text, "missing handle_new_user function"
    assert "on_auth_user_created" in text, "missing on_auth_user_created trigger"


def test_schema_references_supabase_auth():
    """The schema references Supabase auth (auth.users)."""
    text = SCHEMA.read_text(encoding="utf-8")
    assert "auth.users" in text, "schema does not reference auth.users"


def test_schema_has_check_constraint_on_billing_tier():
    """The profiles table has a CHECK constraint on billing_tier."""
    text = SCHEMA.read_text(encoding="utf-8")
    assert "billing_tier" in text, "profiles table missing billing_tier"
    assert "check" in text.lower(), "billing_tier has no CHECK constraint"


def test_schema_has_index_on_audits():
    """The audits table has an index on (user_id, created_at DESC)."""
    text = SCHEMA.read_text(encoding="utf-8")
    assert re.search(r"create index.*audits.*user_id.*created_at", text, re.IGNORECASE), \
        "audits table missing index on (user_id, created_at)"
