================================================================================
ORDER GET IT RIGHT -- RUNBOOK: WHEN THE CONVERSATION LAYER IS DOWN
================================================================================

Last updated: 2026-07-22
Chain root at seal: 8bfc95bd9b01f8088ea717d1d73cf83fd92a22f6c3ef2f5f386a7d682e84442b
Blocks at seal: 34,127
Last event: SHUTDOWN (2026-07-21T20:41:50Z)

PURPOSE
-------
This runbook gives you the PowerShell-only path for keeping the
OrderGetItRight system operational when the conversation layer
(the AI agent you talk to via the terminal) is unavailable.

The conversation layer depends on: (1) a working internet link,
(2) the Ollama proxy or cloud API endpoint being reachable,
(3) DNS resolving the endpoint hostname.

If any of those three fail, you lose the conversation layer.
The engine (02_Technical) and the chain (03_Vault) do NOT need
the conversation layer. They are pure-Python, local, air-gapped.

This runbook is a SEALED PROCEDURE. Do not deviate. If you find
a gap, seal a new block with event_type RUNBOOK_AMENDMENT_<DATE>
and update this file. Ritual is religion, procedural is law.

SYMPTOM
-------
You type a message to the agent and get one of:
  - "502 dial tcp: lookup ollama.com: no such host"
  - "Connection refused" / "Connection timed out"
  - The terminal hangs indefinitely after you press Enter
  - "503 Service Unavailable"

STEP 1: CHECK WHICH LINK IS UP
-------------------------------
Open PowerShell (Win+R, type "powershell", Enter). Run:

  ipconfig | Select-String "IPv4|adapter"

You should see one of:
  - "Wireless LAN adapter Wi-Fi" with an IPv4 address -> Starlink is up
  - "Ethernet adapter Ethernet 2" with an IPv4 address -> Vodafone tether is up
  - Neither -> both links are down, go to STEP 6

If Starlink is up but the conversation layer is down, the issue is
DNS or the Ollama endpoint. Go to STEP 2.

If only Vodafone tether is up (Starlink down), go to STEP 3.

STEP 2: CHECK DNS (Starlink up, agent down)
------------------------------------------
Run:

  nslookup ollama.com

If it returns "DNS request timed out" or NXDOMAIN, the Unbound
forwarder may have crashed. Restart it:

  Restart-Service Unbound -Force

Then retry:

  nslookup ollama.com

If Unbound is not running or won't start, bypass it:

  nslookup ollama.com 1.1.1.1

If that works, set your Wi-Fi adapter DNS to 1.1.1.1 temporarily:

  Set-DnsClientServerAddress -InterfaceAlias "Wi-Fi" -ServerAddresses 1.1.1.1

Then retry the conversation layer. If it comes back, the problem
was Unbound. Leave DNS on 1.1.1.1 until you can debug Unbound.

STEP 3: VODAFONE TETHER FALLBACK (Starlink down)
----------------------------------------------
If Starlink is down (no Wi-Fi IP, or ping 8.8.8.8 fails from Wi-Fi),
switch to the Vodafone 5G tether:

  1. Plug the phone into the USB-C port.
  2. On the phone: Settings -> Network -> Hotspot & tethering ->
     USB tethering -> ON.
  3. In PowerShell, check:

       ipconfig | Select-String "IPv4"

     You should see an "Ethernet adapter Ethernet 2" or similar
     with a 10.x.x.x address.
  4. Set DNS for the tether adapter:

       Set-DnsClientServerAddress -InterfaceAlias "Ethernet 2" -ServerAddresses 127.0.0.1

  5. Test: ping 8.8.8.8
  6. Test DNS: nslookup ollama.com

If the C port is doggie (phone enumerates but Status=Unknown),
follow RUNBOOK_C_PORT_RECOVERY.md first.

STEP 4: CHECK OLLAMA ENDPOINT
-----------------------------
If the link is up and DNS resolves but the conversation layer
is still down, the Ollama proxy or cloud API may be unreachable.

  1. Test reachability:

       ping ollama.com

  2. If ping works but the agent still can't connect, the
     service itself may be down. Try the Starlink link if you
     were on tether, or vice versa -- sometimes one path
     routes better to the endpoint.

  3. If neither link can reach the endpoint, wait 5 minutes
     and retry. The endpoint may be cycling.

STEP 5: LOCAL OPERATIONS (no conversation layer needed)
-------------------------------------------------------
The engine does not need the conversation layer. You can run
the full audit pipeline from PowerShell:

  cd "C:\Users\justo\OneDrive\Documents\My Project\OrderGetItRight"

  # Verify the chain (no network needed)
  python -m src.verify_chain

  # Run the test suite (no network needed)
  python -m pytest tests/ -v

  # Run an audit (no network needed)
  python -m src.audit_cli --inbox data/inbox --outbox data/outbox

  # Seal a marker block (no network needed)
  python 04_Validation/scripts/append_marker.py --event CONVERSATION_LAYER_DOWN_<DATE> --note "Starlink down, Vodafone tether up, operator working locally"

  # Push to the D: drive mirror (no network needed)
  git push usb

  # Run hygiene check (no network needed)
  python 04_Validation/scripts/deterministic_hygiene.py --json-only

All of the above work with zero internet. The chain, the vault,
the tests, and the audit engine are fully air-gapped.

STEP 6: TOTAL INTERNET LOSS (both links down)
---------------------------------------------
If both Starlink and Vodafone are down:

  1. Seal a block recording the outage:

       python 04_Validation/scripts/append_marker.py --event TOTAL_INTERNET_OUTAGE_<DATE> --note "Both Starlink and Vodafone down. Working locally."

  2. Continue all local work (audit, tests, chain seals).
  3. Do NOT attempt to push to any remote (there is no remote
     that works without the D: drive, and the D: drive does not
     need internet -- it is a local filesystem path).

  4. When either link comes back, seal a block:

       python 04_Validation/scripts/append_marker.py --event INTERNET_RESTORED_<DATE> --note "Link restored after outage"

  5. Push to the D: drive mirror:

       git push usb

ESCALATION: HF RADIO (last resort, only if internet is down for >48h)
-------------------------------------------------------------------
If both links are down for more than 48 hours, and you need to
send a message out, the only option that does not require
internet is HF amateur radio via Winlink.

PREREQUISITES:
  - Amateur radio license (Foundation, Standard, or Advanced)
  - HF transceiver (e.g. Icom IC-7300, Yaesu FT-991A)
  - Antenna suitable for 40m/80m bands
  - Winlink Express software (free, installed before outage)
  - Computer-to-radio interface (USB or soundcard DRA)

If you do not have these prerequisites, this option is not
available to you. Make a note to acquire them if prolonged
outages are a concern.

The Whyalla Amateur Radio Club can be contacted (when internet
is up) for licensing and equipment guidance.

PAPER BACKUP CARD
-----------------
The Merkle root should be on a paper card in a fireproof safe.
This runbook should be printed and stored next to it.

Current Merkle root: 8bfc95bd9b01f8088ea717d1d73cf83fd92a22f6c3ef2f5f386a7d682e84442b
Current block count: 34,127
Sealed at: 2026-07-22

If you can read this paper card and the root matches what
`python -m src.verify_chain` outputs, the chain is intact.
If the root does NOT match, the chain has been tampered with
or is stale. Seal a CHAIN_ROOT_MISMATCH_<DATE> block immediately.