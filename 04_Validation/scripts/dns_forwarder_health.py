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
import socket
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
    """Send a single A query via UDP and measure elapsed time.
    Returns a dict with: ok (bool), ip (str|None), elapsed_ms (float),
    error (str|None)."""
    import time
    import struct
    # Build DNS query: standard query, recursion desired, 1 question.
    qid = 0x1234
    flags = 0x0100  # standard query, RD=1
    header = struct.pack(">HHHHHH", qid, flags, 1, 0, 0, 0)
    # Encode name: ollama.com -> \x06ollama\x03com\x00
    parts = name.split(".")
    qname = b""
    for p in parts:
        qname += bytes([len(p)]) + p.encode("ascii")
    qname += b"\x00"
    # Type A (1), Class IN (1)
    question = qname + struct.pack(">HH", 1, 1)
    packet = header + question
    start = time.perf_counter()
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(timeout)
        s.sendto(packet, (server, port))
        resp, _ = s.recvfrom(512)
        s.close()
    except (socket.timeout, OSError) as e:
        elapsed_ms = (time.perf_counter() - start) * 1000
        return {"ok": False, "ip": None, "elapsed_ms": elapsed_ms, "error": str(e)}
    elapsed_ms = (time.perf_counter() - start) * 1000
    # Parse response: skip header (12 bytes), parse question section to
    # find the answer section start.
    if len(resp) < 12:
        return {"ok": False, "ip": None, "elapsed_ms": elapsed_ms, "error": "short response"}
    ancount = struct.unpack(">H", resp[6:8])[0]
    rcode = resp[3] & 0x0F
    if rcode == 3:
        return {"ok": True, "ip": None, "elapsed_ms": elapsed_ms, "error": None, "nxdomain": True}
    if ancount == 0:
        return {"ok": False, "ip": None, "elapsed_ms": elapsed_ms, "error": "no answer records"}
    # Skip question section: header is 12 bytes, then the qname.
    pos = 12
    while resp[pos] != 0:
        if resp[pos] & 0xC0:  # pointer
            pos += 2
            break
        pos += 1 + resp[pos]
    else:
        pos += 1
    pos += 4  # qtype + qclass
    # Now in answer section. Find an A record.
    for _ in range(ancount):
        # Name: may be pointer (starts with 0xC0).
        if resp[pos] & 0xC0:
            pos += 2
        else:
            while resp[pos] != 0:
                pos += 1 + resp[pos]
            pos += 1
        rtype, rclass, ttl, rdlen = struct.unpack(">HHLH", resp[pos:pos + 10])
        pos += 10
        if rtype == 1 and rdlen == 4:
            ip = ".".join(str(b) for b in resp[pos:pos + 4])
            return {"ok": True, "ip": ip, "elapsed_ms": elapsed_ms, "error": None}
        pos += rdlen
    return {"ok": False, "ip": None, "elapsed_ms": elapsed_ms, "error": "no A record in answers"}


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
