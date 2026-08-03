Property. Device Λόγος 
P3.1 APTnode-Aoverflow + time_anomaly + fuzzing
P3.2 Coordinated(3) node-B, C, D με overflow σε 30s
P3.3 Escalation node-A safe_tx παλιό + overflow + time_anomaly
P3.5 Silent node-A overflow @ t=20 χωρίς safe_tx ως t=25
P3.5 Silent node-B overflow χωρίς safe_tx
P3.5 Silent node-C overflow χωρίς safe_tx
P3.5 Silent node-D overflow χωρίς safe_tx

```bash
(cat examples/coordinated_attack_with_silent_nodes/scenario.jsonl; sleep 10) | \
  docker run --rm -i \
    -v "$(pwd)/rtlola_specs:/app/rtlola_specs" \
    -v "$(pwd)/monpoly_specs:/app/monpoly_specs" \
    -v "$(pwd)/shared_data:/shared_data" \
    hierarchical_rv-monitor python3 correlator_monitor.py
```