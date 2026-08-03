Σενάριο

MonPoly P3.1 (APT): ένα device που έχει overflow + time_anomaly + fuzzing μέσα σε 60s window → APT indicator
RTLola P3.5 (silent node): ένα device που κάνει overflow και δεν στέλνει safe_tx → silent_node_anomaly

Τι περιμένουμε
Για node-1:

overflow στο t=1779119196 → spawns RTLola watchdog (deadline στο 1779119201)
time_anomaly στο t=1779119197
fuzzing στο t=1779119198
MonPoly P3.1 βλέπει 3 διαφορετικά attack vectors μέσα σε 2s → APT incident 🔥
Στο t=1779119201 (5s μετά το overflow) → RTLola δεν είδε safe_tx για node-1 → silent_node_anomaly 🔥

Για node-2:

Στέλνει safe_tx αλλά δεν έχει κάνει overflow → no incident

```bash
(cat "$(pwd)/examples/apt_and_silent_node/scenario.jsonl"; sleep 10) | \
  docker run --rm -i \
    -v "$(pwd)/rtlola_specs:/app/rtlola_specs" \
    -v "$(pwd)/monpoly_specs:/app/monpoly_specs" \
    hierarchical_rv-monitor python3 correlator_monitor.py
```

expected output:
=== Layer 3 MonPoly Monitor (Online MFOTL + RTLola) ===
    Incremental event-based monitoring

Started online monitor for P3.1
Started online monitor for P3.2
Started online monitor for P3.3
Started online monitor for P3.4
✅ Online MonPoly monitors started

=== Started online monitor for P3.5 (RTLola Time-Triggered) ===
[*] Spawned RTLola monitor (single process, parameterized)
[Layer3] Alert #1: overflow from node-1 @ t=1779119196.0
[Layer3] Alert #2: time_anomaly from node-1 @ t=1779119197.0
[Layer3] Alert #3: fuzzing from node-1 @ t=1779119198.0
[Layer3] Alert #4: safe_tx from node-2 @ t=1779119203.0

🔥🔥🔥 [INCIDENT DETECTED] APT_INDICATOR
    Severity: CRITICAL
    Property: P3.1
    Method: monpoly_online
    Device: node-1
    Details: {
      "type": "apt_indicator",
      "severity": "CRITICAL",
      "device": "node-1",
      "timestamp": 1779119197,
      "property": "P3.1",
      "method": "monpoly_online"
}

[RTLola stdout] [5.000002667][Trigger][#0(node-1)][Value] = "silent_node_anomaly: node-1"
[Layer3] Alert #5: safe_tx from node-2 @ t=1779119205.0

🔥🔥🔥 [INCIDENT DETECTED] SILENT_NODE_ANOMALY
    Severity: CRITICAL
    Property: P3.5
    Method: rtlola_time_triggered
    Device: node-1
    Details: {
      "type": "silent_node_anomaly",
      "severity": "CRITICAL",
      "device": "node-1",
      "timestamp": 1779119201.0,
      "property": "P3.5",
      "method": "rtlola_time_triggered",
      "metadata": {
            "msg": "silent_node_anomaly: node-1",
            "overflow_event_timestamp": 1779119196.0,
            "rtlola_detection_latency_ms": 5011.463642120361
      }
}
