"""
Order Get It Right -- Supabase client configuration.

The Supabase backend is the persistence layer for the Tauri desktop
shell: scan history + affidavit storage, per-customer, with row-level
security. This is NOT part of the audit runtime -- the no-network audit
(04_Validation/scripts/audit_no_network.py) scans 02_Technical/src/
only; this file lives in 02_Technical/config/ alongside constants.py
and is used by the Tauri shell + the live tests, not by the engines.

The credentials are read from environment variables, NOT hardcoded.
The operator sets them after creating the Supabase project (Block B of
the GTM plan, see 04_Validation/GTM_OPERATOR_DIRECTIVES_2026-07-24.md):

    set OGIR_SUPABASE_URL=https://<ref>.supabase.co
    set OGIR_SUPABASE_ANON_KEY=eyJ...

For local dev, put them in a .env (gitignored) or set them in the
shell before running the Tauri app / the live tests.

This module does NOT import the supabase Python client at import time
(the runtime is stdlib-only; the 10 third-party packages in
requirements.txt are pure-Python and vendorable, but the supabase-py
client is NOT in that list -- it is a shell-layer dependency only). The
client is imported lazily inside get_client() so the audit runtime is
never forced to load it.
"""
from __future__ import annotations

import os
from typing import Optional, Tuple


SUPABASE_URL: str = os.environ.get("OGIR_SUPABASE_URL", "")
SUPABASE_ANON_KEY: str = os.environ.get("OGIR_SUPABASE_ANON_KEY", "")


def is_configured() -> bool:
    """Return True iff both the URL and anon key are set in the environment.

    Used by the live test (tests/test_supabase_live.py) to decide whether
    to SKIP (operator has not configured Supabase yet) or run.
    """
    return bool(SUPABASE_URL) and bool(SUPABASE_ANON_KEY)


def credentials() -> Tuple[str, str]:
    """Return (url, anon_key). Raises if not configured."""
    if not is_configured():
        raise RuntimeError(
            "Supabase not configured. Set OGIR_SUPABASE_URL and "
            "OGIR_SUPABASE_ANON_KEY environment variables after creating "
            "the Supabase project (Block B of the GTM plan)."
        )
    return SUPABASE_URL, SUPABASE_ANON_KEY


def get_client():  # type: ignore[no-untyped-def]
    """Return a configured supabase-py client.

    Lazily imports supabase-py so the audit runtime (which is stdlib-only)
    is never forced to load the shell-layer dependency. Callers should
    install supabase-py only in the Tauri shell environment.
    """
    url, anon_key = credentials()
    from supabase import create_client  # type: ignore[import-not-found]

    return create_client(url, anon_key)


def project_ref() -> Optional[str]:
    """Extract the project ref from the URL (the <ref> in <ref>.supabase.co).

    Returns None if not configured or the URL does not match the expected
    shape. Useful for diagnostics + the live test.
    """
    if not SUPABASE_URL:
        return None
    # https://<ref>.supabase.co
    host = SUPABASE_URL.removeprefix("https://").removeprefix("http://")
    ref = host.split(".")[0]
    return ref or None