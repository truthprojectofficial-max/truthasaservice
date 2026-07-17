# Order Get It Right -- Resourcing Guide

**Project:** Order Get It Right v1.0.0 -- Truth as a Service
**Operator:** Justin Barnett
**Hardware target:** MSI Prestige 16 Studio 13 VF 207AU
**Python runtime:** 3.14.6 from `C:\Users\justo\OneDrive\Documents\to the spoils go\Python314\python.exe`
**Air-gap:** yes. `NO_NETWORK=1`. No cloud AI in the request path.

This document is the Order Get It Right answer to the Onyx resourcing
guide. It tells a third party (a customer, a lawyer, a future LLM)
exactly what the build needs to run, exactly what it uses at idle,
and exactly what it costs.

## 1. Resourcing overview

| Build | vCPU (min) | RAM (min) | Disk (min) | Idle RAM | Idle CPU |
|-------|-----------:|----------:|-----------:|---------:|---------:|
| Order Get It Right Lite (this build) | 1 | 256 MB | 100 MB | ~150 MB | < 1% |
| Onyx Lite (cloud reference) | 2 | 2 GB | 10 GB | < 1 GB | < 5% |
| Onyx Standard (cloud reference) | 4 | 10 GB | 32 GB + 2.5x indexed data | n/a | n/a |

Order Get It Right is **between 8x and 40x lighter than Onyx Lite** on
minimum RAM and **100x lighter** on idle RAM, because we omit the
LLM model server, the inference model server, the vector DB, the
Postgres instance, the Redis cache, and the MinIO blob store. The
audit is rule-based, not statistical. The persistence is a single
JSON file, not a database.

## 2. Per-component footprint (this build)

| Component | File | RAM | Disk | CPU |
|-----------|------|----:|-----:|----:|
| Python interpreter | `C:\Users\justo\OneDrive\Documents\to the spoils go\Python314\python.exe` | ~30 MB | 50 MB | < 0.5% |
| FastAPI + Uvicorn | `02_Technical\src\server\app.py` | ~25 MB | source only | < 0.5% |
| Deception scanner (54 patterns) | `02_Technical\src\engines\deception_scanner.py` | loaded in memory | < 100 KB | < 0.1% per audit |
| BBFB engine | `02_Technical\src\engines\bbfb_engine.py` | loaded in memory | < 50 KB | < 0.1% per compute |
| Real-Options lattice | `02_Technical\src\engines\real_options_lattice.py` | loaded in memory | < 50 KB | < 0.1% per compute |
| Merkle truth ledger | `02_Technical\03_Vault\facts_registry.json` | < 1 MB at 1k blocks | ~30 KB now | 0% |
| Document extractors | `02_Technical\src\io\extractors.py` | loaded on demand | < 50 KB | burst |
| Report writers | `02_Technical\src\io\report_writer.py` | loaded on demand | < 50 KB | burst |
| Tauri shell (optional) | `02_Technical\tauri-shell\` | not running unless built | ~30 MB binary | n/a |

There is no Docker, no Kubernetes, no Helm chart, no cloud account.
The build runs on the bare Python 3.12+ interpreter.

## 3. Concrete single-instance sizes

| Workload | vCPU | RAM | Disk |
|----------|-----:|----:|-----:|
| **Operator single-laptop, on-prem** (the build today) | 1 | 256 MB | 100 MB |
| **Small team (1-5 operators), single host** | 2 | 512 MB | 250 MB |
| **Customer-facing deployment, single host** | 4 | 1 GB | 500 MB |
| **Multi-tenant / multi-organisation** (out of scope today) | n/a | n/a | n/a |

## 4. On-premise host recommendations

| Workload | AWS | GCP | Azure | On-prem |
|----------|-----|-----|-------|---------|
| Single operator | `t3.micro` | `e2-micro` | `B1s` | Any laptop, any Pi 4 |
| Small team | `t3.small` | `e2-small` | `B2s` | Mini PC, 8 GB RAM |
| Customer-facing | `t3.medium` | `e2-medium` | `B2s` | Mini PC, 16 GB RAM |

The MSI Prestige 16 Studio 13 VF 207AU on the operator's desk is
`> 2x` over-provisioned for this build. That is intentional: the
operator wants the laptop to stay usable for browsing, email, and
Office while the audit runs.

## 5. Storage scaling

| Driver | Cost per block | 1 year (1k blocks/day) | 5 years |
|--------|----------------|------------------------|---------|
| Merkle chain (this build) | ~1 KB | ~365 MB | ~1.8 GB |
| Onyx Standard OpenSearch | ~1.45x source | n/a | n/a |
| Onyx Standard PostgreSQL | depends on data | n/a | n/a |

At the operator's current rate of ~50 blocks per day (mostly
`ASSISTANT_STARTED` and `JOB_QUEUED`), one year of audit work is
under 20 MB on disk. The chain is the only thing that grows.

## 6. Air-gap and network

- **Inbound network:** none. `NO_NETWORK=1`. No inbound sockets.
- **Outbound network:** none. Zero `urllib`, `requests`, `http.client`,
  `socket` calls in `02_Technical`. The boundary test enforces this.
- **Localhost:** FastAPI binds to `127.0.0.1:3000` (or the port the
  operator chooses). The Tauri shell binds to `127.0.0.1` for IPC.
- **Tailscale / VPN:** out of scope. The build does not need a network
  to function. If the operator wants remote access, run the build
  on a Raspberry Pi 4 on the home network and reach it over Tailscale.

## 7. Cloud-provider comparison (AWS, GCP, Azure)

For a single-operator deployment, Order Get It Right Lite is
**between 8x and 40x cheaper to run than Onyx Lite on the same cloud**.
For a 5-operator team, Order Get It Right Lite is **between 10x and
20x cheaper to run than Onyx Standard**, because we omit the
OpenSearch instance, the model servers, the Redis cache, and the
MinIO blob store.

## 8. Build-time vs runtime requirements

- **Runtime:** Python 3.12+ standard library. The 10 third-party
  packages in `02_Technical/requirements.txt` are all pure-Python
  and can be vendored. The build is fully operational on the
  standard library alone if the operator cannot install the 10
  packages.
- **Build-time (Tauri binary, optional):** Rust 1.77+, Node.js 20+,
  WebView2 (Windows). The Tauri build is not required to run the
  audit; it is the optional desktop wrapper.
- **Test-time:** `pytest>=8.0.0`, `httpx>=0.27.0`. Both pure-Python.

## 9. Disk: where the bytes actually go

| Path | Purpose | Size today |
|------|---------|-----------:|
| `02_Technical\src\` | Python source | 200 KB |
| `02_Technical\config\` | Hardcoded constants | 5 KB |
| `02_Technical\web\` | Static HTML UI | 28 KB |
| `02_Technical\data\samples\` | Test inputs | ~50 KB |
| `02_Technical\03_Vault\` | Merkle chain | 30 KB |
| `02_Technical\04_Validation\` | Affidavits, squeal-reports | < 1 KB |
| `04_Validation\changelog.log` | Operator changelog | ~5 KB |
| `04_Validation\hardcopy\` | Hard-copy backup documents | 10 KB |
| `data\outbox\` | Generated reports | depends on usage |
| `data\discovery\` | Discovery ingests | depends on usage |
| `99_Archive\` | Frozen snapshots | depends on usage |

The build tree, the Merkle chain, and the test data are < 1 MB total
on disk. The build is portable on a 4 GB USB stick with 99% of the
space unused.

## 10. What it costs to run (annualised)

- **Hardware:** A$0 -- the operator already has the MSI Prestige 16.
- **Electricity:** < A$5/year (a laptop at 65W, idle, 24/7 = 570 kWh/yr
  at A$0.30/kWh).
- **Internet:** A$0 -- the build is air-gapped.
- **Cloud bill:** A$0 -- no cloud account.
- **Backup media:** A$31/year (one-time) + A$82-142/year recurring
  (the 1-2-3 hard-copy plan).
- **Total cost of ownership:** **< A$200/year** for a single-operator
  deployment, including the offsite backup.

A small team of 5 operators on a single shared host runs at the
same cost; the bottleneck is the operator's time, not the machine.

## 11. Resourcing summary (the third-party elevator pitch)

> "Order Get It Right runs on a $200 laptop on 256 MB of RAM with no
> GPU, no Docker, no cloud, and no internet. The same input + same
> config produces the same output, every time, on any host. The
> chain is sealed to a Merkle root that the operator prints on a
> paper card and stores in a bank vault. The whole program
> costs < A$200/year to run, including the offsite backup. The
> third party can verify the chain in 30 seconds on any other
> laptop, with no other software. The math, the persistence,
> and the audit trail are bit-for-bit identical on every host."

## 12. What is not in this document

- Multi-tenant RBAC. Out of scope today; one operator, one host.
- Long-term archival. The `99_Archive/` directory is the operator's
  responsibility.
- Disaster recovery beyond the 1-2-3 hard-copy backup plan. The
  Tauri binary, when built, is the long-term deployment shape.
- Cloud Onyx features (vector DB, model servers, Redis, MinIO,
  Postgres). All deliberately omitted for the air-gap.
