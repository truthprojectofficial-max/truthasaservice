# Order Get It Right -- Deployment Guide

**Project:** Order Get It Right v1.0.0 -- Truth as a Service
**Operator:** Justin Barnett
**Hardware target:** MSI Prestige 16 Studio 13 VF 207AU
**Python runtime:** 3.14.6 from `C:\Users\justo\OneDrive\Documents\to the spoils go\Python314\python.exe`
**Air-gap:** yes. `NO_NETWORK=1`. No cloud AI in the request path.

This document captures the deployment decisions the build has made, and the
deployment shapes that would be in scope if the operator ever asks for a
multi-tenant cloud edition. Every section follows the same pattern: (1) what
the cloud Onyx does, (2) what the local Order Get It Right does instead, (3)
why, (4) when the cloud shape would be in scope.

The pattern is always the same: the local build is the air-gapped, deterministic,
no-black-box edition. The cloud shapes are the multi-tenant, on-prem, AWS-deployed
editions. The boundary is "single operator, one laptop, one audit at a time" vs.
"many operators, many hosts, many audits at a time."

---

## Table of contents

1. [No Docker](#1-no-docker)
2. [No Terraform](#2-no-terraform)
3. [No VPC](#3-no-vpc)
4. [No EKS](#4-no-eks)
5. [No RDS Postgres](#5-no-rds-postgres)
6. [No ElastiCache Redis](#6-no-elasticache-redis)
7. [No S3](#7-no-s3)
8. [No OpenSearch](#8-no-opensearch)
9. [No kubectl / Helm / Vespa](#9-no-kubectl--helm--vespa)
10. [No WAFv2](#10-no-wafv2)
11. [No top-level composition](#11-no-top-level-composition)
12. [No cloud outputs (cluster_name, postgres_endpoint, postgres_port, postgres_db_name, postgres_username, redis_connection_url, opensearch_endpoint, opensearch_dashboard_endpoint)](#12-no-cloud-outputs)
13. [No Google OAuth](#13-no-google-oauth)
14. [What would be in scope if a customer asks for a single-tenant cloud edition](#14-what-would-be-in-scope-if-a-customer-asks-for-a-single-tenant-cloud-edition)

---

## 13. No Google OAuth

**Cloud Onyx does:** create a Google Cloud project, enable the Google People
API, configure the OAuth consent screen, create an OAuth client of type "Web
Application", configure the JavaScript origins and redirect URIs, save the
Client ID and Client Secret, and configure Onyx with `AUTH_TYPE=google_oauth`,
`OAUTH_CLIENT_ID`, `OAUTH_CLIENT_SECRET`, and `WEB_DOMAIN`. The operator
clicks "Login with Google", Google redirects back to the Onyx callback URL
with an authorization code, Onyx exchanges the code for an access token + ID
token, Onyx extracts the user's email and profile from the ID token, and the
user is now logged in. The access token is stored in the Onyx session and is
used for pass-through to Google Drive / Gmail connectors if those scopes are
requested.

**Local Order Get It Right does instead:** the operator's physical possession
of the laptop. The build has no login screen, no callback URL, no Client
ID, no Client Secret. The "auth" is the boot password + the BitLocker key
+ the USB stick in the bank safe deposit box + the Merkle root on the paper
card. The build's "session" is the `_sessions` dict in `SessionTrackerMiddleware`,
which is a lock-out dict (3-repetition lock returns 429
`SOVEREIGN_EXIT_REACHED`), not a credential store. The build's "identity" is
`PROJECT_OPERATOR = "Justin Barnett"` hardcoded in
`02_Technical/config/constants.py`.

**Why:**

- **Air-gap.** Google OAuth is a third-party identity provider. Adopting it
  means the build's identity becomes "the Google account holder who clicked
  Login" instead of "the operator." The Google account is a third-party
  dependency that the operator does not control.
- **No black box.** The current affidavit says "no third-party black box."
  Google OAuth is a third-party identity provider. The build would be trusting
  Google's OAuth server, Google's public key infrastructure, Google's user
  account database, and Google's session management. The local build has
  zero of those: the operator's identity is in `constants.py`.
- **No LLM.** The mandate is no LLM. Google OAuth is not an LLM, but it is
  a third-party-managed service that the operator has to trust. Trusting a
  third-party identity provider is the same anti-pattern as trusting a
  third-party LLM.
- **Operator can still run the build if a vendor product changes.** If Google
  retires Google OAuth, or changes the OAuth flow, or revokes the operator's
  Google account, the local build still runs. The build's "auth" is the
  operator's physical possession of the laptop. Google does not enter the
  picture.
- **No Client Secret to leak.** The Client Secret is marked sensitive by
  Google's own docs. A reviewer doing a s 177 audit would have to confirm
  that the Client Secret is not leaked to logs, not committed to git, and
  not exposed in the environment variables. The local build has no such
  surface: the only "secret" is the Merkle root on the paper card.
- **1-2-3 backup plan.** The plan is "burn the build folder to USB, print
  the Merkle root, store offsite." With Google OAuth, the plan would have to
  also include "rotate the Client Secret, archive the OAuth client config,
  export the consent screen settings" -- all of which require the Google
  Cloud account to still exist and to still be under the operator's
  control.
- **10% Tau firewall.** The firewall measures audit runtime against wall
  clock. An OAuth callback adds 200-500 ms of network latency to every login
  and distorts the extraction ratio.

**What the local build's "authentication" looks like in detail:**

1. **Boot password:** the operator's Windows login password.
2. **BitLocker key:** the BitLocker recovery key, stored in the operator's
   BitLocker escrow (Microsoft account or Active Directory).
3. **USB stick:** the 1-2-3 backup plan's primary copy, in a fireproof
   envelope in the operator's home safe.
4. **Paper card:** the printed Merkle root, pinned to the inside cover of
   the printed Operator Manual.
5. **Offsite copy:** the second USB stick, in a bank safe deposit box or
   lawyer's office, tested every 6 months.

That is five factors of authentication (possession, knowledge, biometric via
Windows Hello if enabled, plus the cryptographic trust anchor), and not one
of them is a third-party black box.

**When Google OAuth would be in scope:** if a customer ever asks for a
multi-tenant, on-prem, AWS-deployed edition with 5+ operators, the deployment
shape would be **one EC2 instance + one Google Cloud project + one OAuth
client + one consent screen, no other services**. The single-tenant case
is well-served by the operator's physical possession of the laptop. The
multi-tenant case would need real RBAC + real user management + real session
management, which is a future flag, not a current feature. The
`multitenant_oauth_decision.md` one-pager names this as the only
multi-tenant shape that would be in scope.

**What is NOT being added this turn:**

- No Google Cloud project. The mandate is air-gap.
- No Google People API dependency. The build has no network.
- No OAuth client. The build has no client/server model.
- No callback URL. The build has no OAuth flow.
- No Client ID or Client Secret. The build has no third-party credentials.

---

## 14. What would be in scope if a customer asks for a single-tenant cloud edition

If a customer ever asks for a single-tenant, on-prem, AWS-deployed edition of
Order Get It Right, the only deployment shape that would be in scope is:

- **One EC2 instance** in the default VPC, no NAT gateway, no flow logs, no
  public IP. The customer reaches the audit via the EC2 serial console or
  over Tailscale.
- **`deploy/deploy.ps1`** running via `user_data` on first boot. One
  PowerShell script that mirrors the project tree, installs the 10 local-only
  Python packages, and writes `Start-Server.bat`.
- **No RDS, no ElastiCache, no S3, no OpenSearch, no WAF, no Helm, no
  Kubernetes, no Docker, no Terraform.** The single-tenant case is
  well-served by the bare-Python install.
- **No Google OAuth.** The single-tenant case has one operator (the
  customer's admin), whose identity is `PROJECT_OPERATOR` in `constants.py`.
- **The local JSON file path is the application's view of the chain.** The
  customer's admin reads `02_Technical/03_Vault/facts_registry.json` and
  re-derives the Merkle root to verify the audit.
- **The local REPL is the audit surface.** The customer's admin uses
  `python -m src.third_party_assistant` to run audits, read the chain,
  generate the affidavit, and seal new facts.
- **The local MonitorAgent Incident Briefing is the human-in-the-loop
  surface.** The customer's admin runs the briefing daily, signs it, and
  seals the signed briefing to the chain.
- **The local DiscoveryAgent is the pre-deployment surface.** The
  customer's admin runs `discovery` on the EC2 instance before the build
  enters, to inventory the environment.

The cost of the single-tenant cloud edition is **~$5/month on a `t3.micro`
reserved instance** + the customer's admin time. The local build's total
cost of ownership remains < A$200/year for the operator's own deployment.

The multi-tenant, multi-region, multi-1000-user cloud edition is **out of
scope today** and would require a separate build (the cloud Onyx Standard
stack: VPC + EKS + RDS + ElastiCache + S3 + OpenSearch + WAF + Terraform +
Helm + Kubernetes). The local Order Get It Right is the **Lite** edition in
the Onyx terminology, and it is the right one for the operator's mandate.

---

**Document generated:** 2026-07-12
**Sealed to chain:** see `04_Validation\changelog.log` for the
`type: "deployment_decision"` entry, and the corresponding Merkle block.
**Re-derivable:** yes. The deployment decisions are deterministic and
verifiable from the source tree + the chain.

---

## 15. Concurrency (added 2026-07-18, F16)

The FastAPI server is designed to run with a **single uvicorn worker**.
The default `uvicorn src.server.app:app` invocation boots one worker, and
the bundled `Start-Server.bat` launcher uses the default.

**Why single-worker.** `vault_io.append_block` is a
read-modify-write of `03_Vault/facts_registry.json` with no process-wide
lock. Under a single uvicorn worker this is safe: one process holds the
file for the lifetime of an append. Under `uvicorn --workers N` with N
greater than 1, two workers could each read the same on-disk state,
each compute a new block, and the later writer would clobber the
earlier one. The Merkle chain would still verify (every block's
`current_hash` is self-consistent against the immediately preceding
block on disk at the time of the write) but the chain would be
missing blocks, and the on-disk Merkle root would no longer match
the recomputed root over the live set. The audit history would be
incomplete.

**How to add multi-worker support.** Wrap the
`read_facts_registry -> mutate -> write_facts_registry` sequence in
`vault_io.append_block` with a process-wide lock. On Windows,
`msvcrt.locking(fileno, msvcrt.LK_NBLCK, 1)` is the natural choice
(no extra dependencies, integrates with `open()`). On POSIX,
`fcntl.flock` with `LOCK_EX`. The lock must be held for the entire
read-modify-write; releasing it between the read and the write
re-introduces the race. The lock should be **per-file**, not
per-process (otherwise it does nothing under multi-worker uvicorn).

**What is NOT in scope.** A multi-worker deploy is unlikely for the
operator's single-laptop, single-tenant, air-gapped use case. The
fix is documented here so a future operator who tries `--workers 2`
on a single-host cluster sees the warning before the chain goes
silent.

**Verification ritual.** After any deploy that changes the server
invocation, run:

```powershell
cd 02_Technical
python -m src.verify_chain
```

If `RESULT: MATCH` is printed, the chain re-derives and the deploy is
clean. If `RESULT: BROKEN` is printed, a block has been clobbered
and the chain must be restored from the most recent verified
snapshot.

