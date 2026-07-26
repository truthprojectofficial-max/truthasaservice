# Anomaly Detection Techniques — Thread Analysis

> Created 2026-07-24. Sealed to chain.
> Source: Core TechniquesIsolation Forests Is.txt (93KB)
> A web-scrape about anomaly detection techniques from an FinOps
> company (Octo/Alphaus). This file opens several threads that
> connect directly to OGIR's engine architecture.
> Sealed to chain: `ANOMALY_DETECTION_THREAD_ANALYSIS_2026_07_24`

---

## WHAT THE FILE CONTAINS

A comprehensive overview of anomaly detection techniques:
- **Isolation Forests** — isolates observations by randomly splitting feature values, making rare patterns stand out
- **Local Outlier Factor (LOF)** — calculates local data density to spot isolated points
- **Autoencoders** — neural networks that compress normal data and flag high reconstruction errors
- **Statistical methods** — Z-Score, IQR, Time Series Decomposition
- **Three anomaly types** — Point, Contextual, Collective
- **Implementation challenges** — false positives, data quality, dynamic environments, feedback loops

---

## THREADS THIS OPENS FOR OGIR

### Thread 1: OGIR's Shannon Entropy IS a statistical anomaly detector

The engine already uses Shannon entropy as an anomaly detector. The
file describes Z-Score analysis as "assessing how far a data point
is from the average." OGIR's entropy gate does the same thing:
text with entropy outside the normal band (SHANNON_ANOMALY_THRESHOLD
= 4.5 bits/char, SHANNON_LOW_THRESHOLD) is flagged as anomalous.

**OGIR already has:** statistical anomaly detection (entropy).
**The file validates:** this is the oldest, most established approach.
**Thread to pull:** could add Z-Score and IQR as secondary statistical
gates alongside entropy for more robust anomaly detection.

### Thread 2: OGIR's 55 patterns are CONTEXTUAL anomalies

The file defines contextual anomalies: "data points that appear
normal in isolation but become anomalous when viewed within a
specific context." This is exactly what OGIR's deception patterns
do. "Clearly" is normal English. "Clearly" in a contract clause
without evidence is a contextual anomaly (DD-001 Clarity Shield).

**OGIR already has:** contextual anomaly detection (the 55 patterns).
**The file validates:** this is "much more sophisticated" than point
anomaly detection.
**Thread to pull:** the R1-R6 structural co-text gates ARE the
context engine. They could be described as "contextual anomaly
detection with domain expertise" — exactly what the file recommends.

### Thread 3: The 12 structural mechanics are COLLECTIVE anomalies

The file defines collective anomalies: "individual data points may
seem normal, but together they form an unusual pattern." This is
exactly what the 12 structural mechanics (DD-056 to DD-067) detect.
A single "shall I continue?" is normal. Six "shall I continue?" in
a row is a collective anomaly (DD-064 Re-Engagement Bait).

**OGIR doesn't have yet:** collective anomaly detection (sequence
analysis across turns in a session).
**The file recommends:** "graph-based methods, sequence analysis,
and deep learning" for collective anomalies.
**Thread to pull:** add a session-level detector that counts the
12 mechanics across a conversation and flags when the collective
pattern crosses a threshold. SQUEAL is the alarm; the collective
anomaly detector would be the sensor.

### Thread 4: Isolation Forests could detect the "insistence" pattern

Isolation Forests "isolate observations by randomly splitting
feature values, making rare or hidden patterns stand out quickly."
The insistence-after-being-called-out pattern is a rare pattern
(a few turns in a long session) that stands out when isolated.

**OGIR doesn't have:** Isolation Forest detection.
**Thread to pull:** not for the current pure-stdlib engine (Isolation
Forests need numpy/scikit-learn, which violates the no-dependencies
rule). But the CONCEPT could be implemented as a pure-stdlib
approximation: count the frequency of concede-then-repeat sequences
(DD-065) and isolation-score them. Rare sequences that match the
insistence pattern get flagged.

### Thread 5: The Correction Tax (DD-067) is a feedback loop metric

The file says: "Implement feedback loops. Systems should learn from
false positives and missed anomalies." The Correction Tax IS the
feedback loop metric — it measures how much the operator is
correcting the AI. If the Correction Tax exceeds 40%, the session
is net-negative.

**OGIR already has:** TAU_EXTRACTION_CEILING (0.10) — if the
operator spends >10% of runtime tolerances correcting the agent,
the cycle aborts.
**The file validates:** feedback loops improve detection over time.
**Thread to pull:** the Correction Tax should be measured per-session
and sealed to the chain as a metric. Over time, the engine learns
which AI systems produce the highest Correction Tax and flags them
before the operator starts a session.

### Thread 6: False positives are the implementation challenge

The file says: "Many systems generate too many alerts for non-issues,
leading to alert fatigue." OGIR's engine has the same risk — if
the 55 patterns fire too often on honest text, the operator stops
trusting the alerts.

**OGIR already has:** the R1-R6 structural co-text gates to reduce
false positives (e.g., "clearly" with a citation nearby doesn't
fire DD-001).
**The file validates:** this is the correct approach — "layer multiple
detection methods" and "reduce false alarms."
**Thread to pull:** measure the false-positive rate across the 139
eval cases and surface it as a per-pattern metric. Patterns with
high false-positive rates get tightened gates.

### Thread 7: The file itself is an example of the "AI speak" it describes

The file is a marketing piece from Octo/Alphaus. It uses:
- "Silent guardians" (authority mimicry)
- "Force multiplier" (capability-pledge tell — DD-058)
- "Step-Up Your Anomaly Detection with Octo!" (re-engagement bait — DD-064)
- "Ready to step up? Book a demo today" (re-engagement bait)
- "Projected to reach over $12 billion by 2029" (confidence inflation — DD-061)

The file about anomaly detection ITSELF contains detectable deception
patterns. The engine should be run on it.

---

## WHAT I CAN DO NOW

1. **Run the engine on this file** — see which of the 55 patterns fire on marketing copy that's trying to sell anomaly detection
2. **Add the 3 anomaly types** (Point, Contextual, Collective) to the OGIR methodology docs — the engine already implements the first two; the third is the structural mechanics tier
3. **Add the feedback loop concept** to the harvesting policy — the Correction Tax IS the feedback metric the file describes
4. **Note the Isolation Forest concept** for future research — not implementable in pure stdlib, but the concept (rare patterns stand out when isolated) could be approximated

---

## THE VERDICT

This file opens 7 threads. 3 of them are already implemented in OGIR
(entropy as statistical anomaly, patterns as contextual anomalies,
Tau ceiling as feedback loop). 3 are new threads to pull (collective
anomaly detection for the 12 mechanics, Isolation Forest concept for
the insistence pattern, false-positive rate as a per-pattern metric).
1 is meta: the file itself contains the patterns it describes.

The file validates OGIR's architecture. The engine is doing what
the anomaly detection field recommends — just with pure-stdlib
Python and deception patterns instead of neural networks.