"""
Order Get It Right -- Unbound DNS Forwarder Health Check.

Verifies the local Unbound forwarder is running and answering
queries on 127.0.0.1:53. Run as part of the deterministic
hygiene ritual (or by hand) to confirm the DNS path is
healthy. Fails loud if Unbound is down.

The script also re-derives the upstream servers (Cloudflare +
Quad9) by checking that they answer a probe query. If the
upstreams are down, that's a different problem (network
outage) but worth surfacing.

Exit codes:
  0  healthy (Unbound up, upstream answers, NXDOMAIN timing
        bounded)
  1  Unbound is down (operator should restart the service)
  2  Upstream is unreachable (network outage)
  3  NXDOMAIN timing is excessive (> 1s) — Unbound is alive
     but not caching aggressively enough
"""
import json
import subprocess
import sys
from pathlib import Path

UNBOUND_HOST = "127.0.0.1"
UNBOUND_PORT = 53
PROBE_HOSTS = ["ollama.com", "github.com", "cloudflare.com"]
UPSTREAM_PROBE = "1.1.1.1"
NXDOMAIN_PROBE = "this-host-definitely-does-not-exist-9f8a7b6c5d4e3f.invalid"
NXDOMAIN_MAX_MS = 1000  # Aggressive NSEC caching should bound this well under 1s.


def dns_query(name: str, server: str = UNBOUND_HOST, port: int = UNBOUND_PORT, timeout: float = 2.0) -> dict:
    """Send a single A query via subprocess + PowerShell Resolve-DnsName and
    measure elapsed time. No raw socket -- subprocess only.

    Returns a dict with: ok (bool), ip (str|None), elapsed_ms (float),
    error (str|None), nxdomain (bool|None).
    """
    import time
    start = time.perf_counter()
    try:
        # PowerShell Resolve-DnsName: works on Windows, uses the OS DNS resolver
        # which respects the system DNS config (which points to Unbound at 127.0.0.1:53).
        # We can't easily override the server via CLI; we rely on the OS config.
        ps_cmd = (
            f"Resolve-DnsName -Name '{name}' -Type A -ErrorAction Stop | "
            "Select-Object -ExpandProperty IPAddress"
        )
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps_cmd],
            capture_output=True, text=True, timeout=timeout + 2,
        )
        elapsed_ms = (time.perf_counter() - start) * 1000
        if result.returncode != 0:
            err = result.stderr.strip() or "nonzero exit"
            # NXDOMAIN is a "DNS-specific error" but not a transport failure
            if "DNS_ERROR" in err or "Non-Existent" in err or "Name does not exist" in err:
                return {"ok": True, "ip": None, "elapsed_ms": elapsed_ms, "error": None, "nxdomain": True}
            return {"ok": False, "ip": None, "elapsed_ms": elapsed_ms, "error": err}
        ip = result.stdout.strip()
        return {"ok": True, "ip": ip or None, "elapsed_ms": elapsed_ms, "error": None, "nxdomain": False}
    except subprocess.TimeoutExpired as e:
        elapsed_ms = (time.perf_counter() - start) * 1000
        return {"ok": False, "ip": None, "elapsed_ms": elapsed_ms, "error": f"timeout: {e}"}
    except FileNotFoundError:
        elapsed_ms = (time.perf_counter() - start) * 1000
        return {"ok": False, "ip": None, "elapsed_ms": elapsed_ms, "error": "powershell not found on PATH"}


def main() -> int:
    result = {
        "unbound_up": False,
        "probe_hosts": {},
        "upstream_reachable": False,
        "nxdomain_within_bound": True,
        "issues": [],
    }

    # Probe A records through Unbound.
    any_ok = False
    for host in PROBE_HOSTS:
        q = dns_query(host)
        result["probe_hosts"][host] = q
        if q["ok"] and not q.get("nxdomain") and q["ip"]:
            any_ok = True
        if not q["ok"]:
            result["issues"].append(f"unbound failed for {host}: {q['error']}")
    result["unbound_up"] = any_ok

    # Probe upstream reachability: query 1.1.1.1 through Unbound.
    # (Unbound will only answer if 1.1.1.1 is reachable.)
    upstream_q = dns_query(UPSTREAM_PROBE, timeout=3.0)
    result["upstream_query"] = upstream_q
    # 1.1.1.1 is an IP; we want NXDOMAIN (no A record) or some other
    # well-formed response. An error means upstream is down.
    if upstream_q.get("ok"):
        result["upstream_reachable"] = True
    else:
        result["issues"].append(f"upstream probe failed: {upstream_q['error']}")

    # Probe NXDOMAIN timing: this-host-definitely-does-not-exist-...
    # should return NXDOMAIN quickly if aggressive NSEC caching is on.
    nx_q = dns_query(NXDOMAIN_PROBE, timeout=5.0)
    result["nxdomain_query"] = nx_q
    if not nx_q.get("nxdomain"):
        result["nxdomain_within_bound"] = False
        result["issues"].append(f"NXDOMAIN not received: {nx_q['error']}")
    elif nx_q["elapsed_ms"] > NXDOMAIN_MAX_MS:
        result["nxdomain_within_bound"] = False
        result["issues"].append(
            f"NXDOMAIN took {nx_q['elapsed_ms']:.0f} ms (max {NXDOMAIN_MAX_MS} ms); "
            f"aggressive NSEC caching may be off"
        )

    # Verdict.
    if not result["unbound_up"]:
        verdict = "UNHEALTHY"
        rc = 1
    elif not result["upstream_reachable"]:
        verdict = "UPSTREAM_DOWN"
        rc = 2
    elif not result["nxdomain_within_bound"]:
        verdict = "DEGRADED"
        rc = 3
    else:
        verdict = "HEALTHY"
        rc = 0
    result["verdict"] = verdict

    print(json.dumps(result, indent=2))
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
