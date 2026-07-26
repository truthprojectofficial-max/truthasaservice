================================================================================
ORDER GET IT RIGHT -- OPERATOR NOTE: PHONE USB CONFIG (30s FIX)
================================================================================

Last updated: 2026-07-22

SYMPTOM
-------
USB tether flaps; phone enumerates as 4-12 different USB devices
in Windows Device Manager, only 1-2 of them Status=OK at a time.
ADB shows phone-online, then offline, then (no serial), then online.
The conversation layer survives (tether is up intermittently) but
ADB protocol layer is unreliable. C port looks fine mechanically.

DIAGNOSIS
---------
On the phone, the USB function set is renegotiating each time the
cable wiggles or the laptop's USB stack hiccups. Each renegotiation
creates a new enumeration. ADB sees a different serial (or none) per
enumeration. The phone's `sys.usb.config` flips between function
sets, with ADB as the only stable anchor.

ONE-TIME FIX (30 SECONDS, ON THE PHONE)
----------------------------------------
1. Settings -> System -> Developer Options
   (If Developer Options is hidden: Settings -> About phone -> tap
    "Build number" 7 times. Then go back; Developer Options appears
    at the bottom of System.)
2. Scroll to "Default USB configuration" (or "USB default mode")
3. Tap it. Choose: USB tethering
4. Done.

WHY "USB TETHERING" AND NOT OTHER OPTIONS
------------------------------------------
- "Charging only": exposes no data functions. ADB will not work.
- "MTP (Media Transfer Protocol)": exposes file transfer but
  no networking. Tether dies.
- "PTP (Picture Transfer Protocol)": photo-only. Tether dies.
- "RNDIS": legacy Windows tethering. May work but the Pixel 7a
  uses NCM (modern), and RNDIS is slower.
- "Audio source": no networking.
- "MIDI": no networking.
- "No data transfer": no networking, no ADB. Bad.
- "USB tethering": exposes NCM (USB Ethernet). The tether
  works AND ADB coexists because USB tethering mode allows
  ADB to remain enabled. This is the right default.

WHAT CHANGES ON THE LAPTOP
--------------------------
After the operator changes the default:
- The phone will always start in NCM+ADB mode when plugged in.
- sys.usb.config will read something like "adb,usbnet" instead
  of just "adb".
- The USB device tree will show ONE UsbNcm Host Device + ONE
  ADB Interface, not 4-12 ghosts of past enumerations.
- The C port flap mode changes from "tether drops" to "tether
  recovers in 1-2 seconds."

HOW TO VERIFY THE FIX WORKED
----------------------------
On the laptop, after the operator changes the default and
re-plugs the phone:

  adb devices          # should show ONE serial, status "device"
  Get-NetAdapter | Where-Object InterfaceDescription -match NCM
                      # should show ONE UsbNcm adapter, Status=Up
  Get-PnpDevice | Where-Object InstanceId -like 'USB*VID_18D1*'
  | Where-Object Status -ne 'OK'
  | Measure-Object       # should be 0 or very few (1 is OK)

The 11-12 ghost devices from past flapping will remain in
Device Manager as "Unknown" until you right-click each and
"Uninstall device" + "Attempt to remove the driver for this
device" + reboot. After the fix, they won't accumulate.

CHAIN SEAL
----------
After the operator confirms the fix is in place, seal a
PHONE_USB_DEFAULT_PINNED_2026_07_22 marker block to the chain
via:

  python 04_Validation/scripts/append_marker.py \\
    --event-type PHONE_USB_DEFAULT_PINNED_2026_07_22 \\
    --note "Phone default USB configuration changed to 'USB
            tethering' (NCM). sys.usb.config now reads adb+usbnet.
            Tether flap frequency reduced from multiple-per-minute
            to once-per-replug."

WHY THIS WASN'T A HARDWARE ISSUE
--------------------------------
The C port on the laptop is mechanically fine (clean, no bent
pins). The phone's USB-C receptacle is mechanically fine. The
flapping was caused by the phone's USB function set
renegotiating on every C-port micro-disconnect. Pinning the
default to USB tethering means the phone always comes back as
NCM, which is the only configuration the conversation layer
needs to survive a port wiggle.

END OF NOTE
================================================================================
