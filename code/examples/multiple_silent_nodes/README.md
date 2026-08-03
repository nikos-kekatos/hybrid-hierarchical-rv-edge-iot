Scenario
three silent nodes

```bash
(cat "$(pwd)/examples/multiple_silent_nodes/scenario.jsonl"; sleep 10) | \
  docker run --rm -i \
    -v "$(pwd)/rtlola_specs:/app/rtlola_specs" \
    -v "$(pwd)/monpoly_specs:/app/monpoly_specs" \
    hierarchical_rv-monitor python3 correlator_monitor.py
```

expected output:


(cat "$(pwd)/examples/multiple_silent_nodes/scenario.jsonl"; sleep 7; echo '{"device":"dummy","type":"safe_tx","timestamp":1779119510.0}'; sleep 2) | \
  docker run --rm -i \
    -v "$(pwd)/rtlola_specs:/app/rtlola_specs" \
    -v "$(pwd)/monpoly_specs:/app/monpoly_specs" \
    hierarchical_rv-monitor python3 correlator_monitor.py
=== Layer 3 MonPoly Monitor (Online MFOTL + RTLola) ===
    Incremental event-based monitoring

Started online monitor for P3.1
Started online monitor for P3.2
Started online monitor for P3.3
Started online monitor for P3.4
✅ Online MonPoly monitors started

=== Started online monitor for P3.5 (RTLola Time-Triggered) ===
[*] Spawned RTLola monitor (single process, parameterized)
[Layer3] Alert #1: overflow from node-X @ t=1779119500.0
[Layer3] Alert #2: overflow from node-Y @ t=1779119500.5
[Layer3] Alert #3: overflow from node-Z @ t=1779119501.0
[RTLola stdout] [5.000002000][Trigger][#0(node-X)][Value] = "silent_node_anomaly: node-X"
[RTLola stdout] [5.000063875][Trigger][#0(node-Y)][Value] = "silent_node_anomaly: node-Y"
[RTLola stdout] [5.000080959][Trigger][#0(node-Z)][Value] = "silent_node_anomaly: node-Z"
[Layer3] Alert #4: safe_tx from dummy @ t=1779119510.0

🔥🔥🔥 [INCIDENT DETECTED] SILENT_NODE_ANOMALY
    Severity: CRITICAL
    Property: P3.5
    Method: rtlola_time_triggered
    Device: node-X
    Details: {
      "type": "silent_node_anomaly",
      "severity": "CRITICAL",
      "device": "node-X",
      "timestamp": 1779119505.0,
      "property": "P3.5",
      "method": "rtlola_time_triggered",
      "metadata": {
            "msg": "silent_node_anomaly: node-X",
            "overflow_event_timestamp": 1779119500.0,
            "rtlola_detection_latency_ms": 5012.869119644165
      }
}


🔥🔥🔥 [INCIDENT DETECTED] SILENT_NODE_ANOMALY
    Severity: CRITICAL
    Property: P3.5
    Method: rtlola_time_triggered
    Device: node-Y
    Details: {
      "type": "silent_node_anomaly",
      "severity": "CRITICAL",
      "device": "node-Y",
      "timestamp": 1779119505.5,
      "property": "P3.5",
      "method": "rtlola_time_triggered",
      "metadata": {
            "msg": "silent_node_anomaly: node-Y",
            "overflow_event_timestamp": 1779119500.5,
            "rtlola_detection_latency_ms": 5012.794017791748
      }
}


🔥🔥🔥 [INCIDENT DETECTED] SILENT_NODE_ANOMALY
    Severity: CRITICAL
    Property: P3.5
    Method: rtlola_time_triggered
    Device: node-Z
    Details: {
      "type": "silent_node_anomaly",
      "severity": "CRITICAL",
      "device": "node-Z",
      "timestamp": 1779119506.0,
      "property": "P3.5",
      "method": "rtlola_time_triggered",
      "metadata": {
            "msg": "silent_node_anomaly: node-Z",
            "overflow_event_timestamp": 1779119501.0,
            "rtlola_detection_latency_ms": 5012.776851654053
      }
}

[Layer3] Input closed, draining for 7s...

[Layer3] Shutting down...
⚠️  Monitor P3.1 reader thread ended
⚠️  Monitor P3.2 reader thread ended
⚠️  Monitor P3.3 reader thread ended
⚠️  Monitor P3.4 reader thread ended
