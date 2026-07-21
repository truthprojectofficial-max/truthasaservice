================================================================================
ORDER GET IT RIGHT -- RUNBOOK: WHEN THE C PORT GOES DOGGIE
================================================================================

Last updated: 2026-07-22

SYMPTOM
-------
The phone is plugged in via USB. Windows sees the device enumerated
(USB Composite Device, UsbNcm Host Device, ADB Interface all visible
in Device Manager) but their Status is "Unknown" rather than "OK".
ADB sees nothing. The phone's USB tether drops out, the laptop falls
back to Wi-Fi (Starlink), DNS goes flaky, and any in-flight DNS query
returns NXDOMAIN because the now-detached tethered resolver answered
from a stale negative cache.

DIAGNOSIS (one PowerShell command)
----------------------------------
Run from the laptop:

  Get-PnpDevice | Where-Object { ($_.InstanceId -like 'USB*VID_18D1*') } |
    Select-Object Status, FriendlyName | Format-List

If the Status column says "Unknown" for all four Google interfaces
(UsbNcm Host Device, USB Composite Device, ADB Interface, MIDI
function), the device is electrically connected but data handshake
is failing. The C port is the suspect.

FIVE-STEP RECOVERY
------------------
1. UNPLUG the phone's USB cable from the laptop's C port. Wait 5
   seconds. (Power off the data lines.)

2. CLEAN the C port. Use:
   - Compressed air (3-second burst, hold can upright)
   - Or a wooden/plastic pick (NOT metal -- risk of short)
   The most common cause of intermittent USB-C connectivity is
   pocket lint compacted in the port. It's a real, physical,
   non-software problem.

3. INSPECT the cable. USB-C cables fail at the strain relief. A
   cable that charges but doesn't data is usually an internal
   wire break. Try a different cable if cleaning the port
   doesn't fix it.

4. Reseat the cable firmly. The connector should "click" into
   place. If it wiggles, the port is mechanically worn.

5. After reseat, check:
   - The phone's notification shade should show "Charging this
     device via USB" or "USB for file transfer". If it says
     "Charging only", the phone's USB configuration is set to
     charging-only -- go to Settings -> System -> Developer
     options -> Default USB configuration and change it.
   - On the laptop, re-run the PowerShell command above. All
     four Google interfaces should now show Status = "OK".
   - Run `adb devices` from a bash shell. The phone should
     appear as `<serial>   device` (not `offline`, not blank).
   - If the phone appears but says "unauthorized", tap "Allow
     USB debugging?" on the phone.

NETWORK IMPLICATION
-------------------
While the C port is doggie, the laptop's network is degraded:

  - USB tether: dropped
  - DNS: laptop falls back to Starlink (Wi-Fi gateway 10.35.87.222)
  - Starlink DNS: slow for non-cached hostnames, occasionally
    times out
  - Cellular: phone still has its own Vodafone 5G, but laptop
    isn't routing through it

If the conversation layer (Hermes) starts returning
"502 dial tcp: lookup <hostname>: no such host" or timing out,
this is the cause. Fix the C port first, then retry.

SEAL
----
When you have to recover from this in the middle of a session,
seal a `C_PORT_RECOVERY_<date>` block to the chain so the
audit trail records the disruption. Use:

  python 04_Validation/scripts/append_marker.py \\
    --event-type C_PORT_RECOVERY_<YYYY_MM_DD> \\
    --note "USB-C port flapped; cleaned and reseated; ADB re-established"

(The append_marker.py may not exist yet; if it doesn't, the
fallback is to use the same append_block pattern that
handover_drift_check.py uses, with a manual payload.)

WHY THIS MATTERS
----------------
The 2026-07-22 move from Broadway to Loveday was the event that
exposed this class of failure. The 502 dial tcp: lookup ollama.com:
no such host that killed the conversation was caused by the USB
tether flapping during transport, not by phone-hotspot DNS
mangling as initially suspected. The phone's cellular was fine.
The laptop's Wi-Fi was fine. The USB tether between them was the
single point of failure, and it failed.

The fix is mechanical, not procedural: clean the C port.

END OF RUNBOOK
================================================================================
