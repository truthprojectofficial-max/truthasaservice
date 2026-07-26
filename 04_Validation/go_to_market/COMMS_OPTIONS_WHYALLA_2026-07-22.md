# Comms Options -- Whyalla Norrie SA 5608

Date: 2026-07-22 (updated)
Location: 20 Loveday St, Whyalla Norrie SA 5608

## Current Position (Verified 2026-07-22)

### Active Links
| Link | Status | Latency | Notes |
|------|--------|---------|-------|
| Starlink Wi-Fi | UP | 46-111ms | 0% packet loss, IPv6 native |
| Vodafone 5G tether | Available (phone not connected) | ~50ms | USB-C, MAC AA-D0-75-05-D8-D8 |
| Bluetooth PAN | Adapter present, disconnected | | ~1-2 Mbps, emergency only |

### DNS
| Layer | Config | Status |
|-------|--------|--------|
| Local resolver | Unbound 1.25.1 at 127.0.0.1:53 | HEALTHY |
| Forwarders | Cloudflare 1.1.1.1 + Quad9 9.9.9.9 | Both reachable |
| NXDOMAIN timing | 0.22ms via aggressive NSEC | No stale cache |

## All Comms Options Available at This Location

### Layer 1: Satellite (Primary)
1. **Starlink (active)**
   - LEO constellation, 46-111ms latency, unlimited data
   - Dish is already installed and working
   - Failure mode: weather obstruction, dish misalignment, power loss
   - Backup: Starlink Mini (portable, 12V, could be a second dish)

2. **NBN Sky Muster II (available, not active)**
   - Geostationary, ~500ms latency, data-capped (50-300GB/month)
   - Would require an NBN plan + satellite dish installation
   - Fallback if Starlink fails for an extended period

3. **Inmarsat BGAN (emergency)**
   - Global, portable, ~400-700ms latency, very expensive ($5-15/MB)
   - Requires a BGAN terminal (~$1000-2000) and a service plan
   - Last-resort emergency internet for sending a message out

### Layer 2: Mobile (Backup)
4. **Vodafone 5G (active as USB tether)**
   - Currently the backup link. Phone tethers via USB-C (NCM)
   - C-port flapping fixed (Default USB config = tethering)
   - Vodafone regional SA: improving but weakest of the three carriers

5. **Telstra 4GX/5G (available, not active)**
   - Best coverage in regional SA by far
   - Would need a Telstra SIM or a Telstra mobile broadband plan
   - If Vodafone coverage is unreliable at the new address, consider switching
   - A Telstra prepaid mobile broadband dongle (~$50-99) + SIM (~$30-50/month)
     would give a completely independent backup link

6. **Optus 4G (available, not active)**
   - Moderate coverage in Whyalla
   - Could add as a third backup if needed

### Layer 2.5: Private Fixed-Wireless ISPs
7a. **WideNet (widenet.com.au) -- INQUIRY DRAFTED**
   - Private fixed-wireless ISP serving regional SA
   - Operator has drafted a formal technical feasibility inquiry
     requesting: Fresnel Zone clearance, signal integrity (dBm),
     SFOA/SLA documentation, fault rectification timeframes, uptime
     objectives, service credits
   - Property has no legacy copper or NBN lead-in, so standard
     online checkers are useless -- needs a physical site survey
   - Email: support@widenet.com.au
   - Status: READY TO SEND (draft is in PROJECT TROUBLE COMMS.txt)

7b. **Field Solutions Group (fsg.com.au)**
   - Regional Australia fixed-wireless specialist
   - May have infrastructure near Whyalla
   - Worth a parallel inquiry if WideNet does not cover the address

7c. **Uniti Wireless (unitiwireless.com.au)**
   - Adelaide-focused but expanding into regional SA
   - Lower probability of coverage at Whyalla but worth checking

### Layer 3: Fixed Line (NBN)
7. **NBN Fixed Wireless**
   - Whyalla is in the NBN Fixed Wireless footprint
   - Would require a plan + modem + antenna installation
   - Latency: ~30-50ms, data: typically 250GB-metre plans available
   - Speed: 75/25 Mbps typical (Fixed Wireless Plus)
   - This is a viable primary/backup if Starlink is unreliable long-term

8. **NBN FTTC (Fibre to the Curb)**
   - Some parts of Whyalla have FTTC
   - Would need to check specific address at nbnco.com.au
   - Better than Fixed Wireless (100/40 Mbps, lower latency)
   - Not yet checked for 20 Loveday St

### Layer 4: Radio (Emergency, No Internet)
9. **HF Amateur Radio + Winlink**
   - Can send/receive email over HF radio (no internet needed)
   - Requires: amateur license + HF radio + antenna + Winlink software
   - Whyalla Amateur Radio Club exists for licensing support
   - This is the ONLY option for sending data when all internet is down

10. **CB Radio (UHF 477 MHz)**
    - No license needed, 5W handheld (~$50-100)
    - Range: 5-10km line-of-sight
    - Voice only, no data
    - Useful for contacting neighbours or emergency services

11. **Marine VHF (Spencer Gulf)**
    - Channel 16 monitored by coast guard
    - Range: 20-30km over water
    - Requires Marine Radio Operators Certificate of Proficiency
    - For emergencies only, not for project work

### Layer 5: Physical (Sneaker Net)
12. **D: microSD 64GB (local mirror)**
    - Never removed, stays in the laptop
    - Git remote `usb` points here
    - 33% used (20GB used, 41GB free)

13. **USB sticks (offsite backup)**
    - Not yet done. Need to set up a mirror + rotation schedule.

14. **Paper Merkle root card (fireproof safe)**
    - Not yet done. The root is:
      8bfc95bd9b01f8088ea717d1d73cf83fd92a22f6c3ef2f5f386a7d682e84442b
    - Print this + block count (34,127) + date on a card, store in fireproof safe

15. **Australia Post (physical mail)**
    - For offline correspondence, legal documents, physical backups

## Gap Analysis

| Need | Status | Action Required |
|------|--------|-----------------|
| Primary internet | Starlink UP | None |
| Backup internet | Vodafone tether (available) | None, but phone must be plugged in |
| Third internet | Nothing | Consider Telstra mobile broadband dongle |
| DNS resilience | Unbound local forwarder | Done (2026-07-22) |
| Local mirror | D: microSD (git push usb works) | Done |
| Offsite backup | NOTHING DONE | Buy USB stick, mirror, store offsite |
| Paper root | NOTHING DONE | Print root, store in fireproof safe |
| Emergency radio | NOTHING IN PLACE | Not needed unless outage >48h is a real risk |
| Decouple runbook | Written | See RUNBOOK_CONVERSATION_LAYER_DOWN.md |

## Recommendations (Priority Order)

1. **IMMEDIATE: Paper Merkle root card.** Print the root hash and
   block count on a card. Put it in a fireproof safe. This is the
   1-2-3 backup plan item #3. It has never been done.

2. **IMMEDIATE: Offsite USB backup.** Buy a USB stick, run the
   existing mirror scripts (amendments_mirror_to_sdxc.bat), and
   store the stick somewhere offsite (not in the same building).

3. **SHORT-TERM: Telstra mobile broadband.** A prepaid Telstra
   dongle is the cheapest way to get a completely independent
   backup link. Vodafone is the current backup but it is the
   weakest carrier in regional SA.

4. **MEDIUM-TERM: NBN Fixed Wireless or FTTC.** If the address
   has FTTC, it would give a reliable fixed-line primary that
   does not depend on weather or satellite obstructions. Check
   at nbnco.com.au for the specific address.

5. **LONG-TERM: HF radio + Winlink.** Only if prolonged internet
   outages become a real risk. Requires a license and equipment.
   Not urgent for Whyalla (two independent internet paths exist).
