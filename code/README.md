# Hierarchical Runtime Verification for IoT Security

Formal runtime verification system με 3-layer hierarchical architecture για detection of security attacks σε IoT networks.

---

## System Architecture

```
Layer 1: Canonicaliser     - Immediate event classification
Layer 2: Cloud Monitor     - Temporal pattern detection (5-30s windows)
Layer 3: Correlator        - Formal MFOTL monitoring (MonPoly) + TeSSLA
```

**Pipeline:**
```
15 IoT Devices → Canonicaliser → Cloud Monitor → Correlator
  (iot_app.py)      (Layer 1)       (Layer 2)     (Layer 3/MonPoly)
                                        ↓              ↓
                                   alerts.log    incidents.log
```

---

## Quick Start

### Build & Run System
```bash
docker-compose up --build
```

### Run Evaluation Experiment
```bash
# 2-minute test
./evaluation/run_experiment.sh 120

# 10-minute paper evaluation
./evaluation/run_experiment.sh 600
```

### View Results
```bash
cat results/metrics.json
python3 evaluation/analyze_results.py --metrics results/metrics.json
```

---

## Properties Monitored

### Layer 1 (Immediate)
- **P1.1:** Buffer Overflow Detection
- **P1.2:** Time Spoofing Detection (>15s)
- **P1.3:** Input Fuzzing Detection
- **P1.4:** Safe Transaction Classification

### Layer 2 (Temporal)
- **P2.1:** Repeated Buffer Overflow (3 in 30s)
- **P2.2:** DoS/Spam Attack (30 in 5s)
- **P2.3:** Immediate Time Anomaly Alert
- **P2.4:** Immediate Fuzzing Alert

### Layer 3 (MFOTL - Formal Correlation)
- **P3.1:** Multi-Vector APT Detection (2+ attack types in 60s)
- **P3.2:** Coordinated Botnet Attack (3+ devices in 30s)
- **P3.3:** Attack Escalation Pattern (normal → malicious)
- **P3.4:** Persistent Campaign (5+ attacks in 1 hour)

See [PROPERTIES.md](PROPERTIES.md) for formal specifications.

---

## Files

### Core System
- `iot_app.py` - Event generator με 8 attack profiles
- `canonicaliser.py` - Layer 1 (immediate detection)
- `cloud_monitor.py` - Layer 2 (temporal patterns)
- `correlator_monitor.py` - Layer 3 (MFOTL/MonPoly)
- `docker-compose.yml` - 15-device test environment

### Evaluation
- `evaluation/collect_metrics.py` - Parse logs → metrics
- `evaluation/analyze_results.py` - Detection rates & paper stats
- `evaluation/run_experiment.sh` - Full experiment orchestration

### Specifications
- `PROPERTIES.md` - Formal property specifications
- `monpoly_specs/*.mfotl` - MFOTL formulas για MonPoly

### Additional
- `benchmark_layer3.py` - Performance benchmarking
- `LAYER3_GUIDE.md` - Layer 3 implementation details

---

## Device Profiles

| Profile | Count | Behavior | Detected By |
|---------|-------|----------|-------------|
| normal | 5 | Safe traffic | Baseline |
| overflow | 1 | Buffer overflow attacks | P2.1, P3.2, P3.4 |
| timespoof | 1 | Time spoofing | P2.3 |
| spam | 1 | DoS spam | P2.2 |
| stealth | 1 | Low-and-slow overflow | P2.1, P3.2, P3.4 |
| fuzzer | 1 | Fuzzing attacks | P2.4 |
| pulsing | 1 | Pulsing DoS | P2.2 |
| mixed | 4 | Multi-vector APT | P3.1, P3.2, P3.3, P3.4 |

**Total: 15 devices** (5 benign + 10 attack)

---

## Requirements

- Docker & docker-compose
- Python 3.9+
- MonPoly (installed via Dockerfile with OPAM)

---

## Paper Evaluation

### Run Evaluation
```bash
./evaluation/run_experiment.sh 600  # 10 minutes
```

### Collect Metrics
- Detection rates per property (P3.1-P3.4)
- Latency (alert → incident)
- Throughput (events/alerts/incidents)
- False positive estimates

### LaTeX Table Output
```bash
python3 evaluation/analyze_results.py --metrics results/metrics.json
```

Copy the LaTeX table from stdout to your paper.

---

## Academic Defensibility

- ✅ **Formal Specifications**: MFOTL (Metric First-Order Temporal Logic)
- ✅ **Verified Tool**: MonPoly from ETH Zurich
- ✅ **Peer-Reviewed**: Research-grade runtime verification
- ✅ **Mathematically Rigorous**: Temporal logic semantics

---

## Architecture Highlights

### Hierarchical Design
- **Layer 1**: O(1) per-event checks
- **Layer 2**: O(n) sliding windows (bounded memory)
- **Layer 3**: MFOTL & Stream formal monitoring (online/incremental)

### Scalability
- Event-driven architecture
- Bounded memory (no unbounded state)
- Real-time processing (no batch delays)

### Correctness

Check MonPoly specifications:
```bash
monpoly -sig /app/monpoly_specs/signature.sig -formula /app/monpoly_specs/p3_4_persistent.mfotl    -check
```

Check RTLola:
```bash
docker run --rm -i -v "$(pwd)/rtlola_specs:/specs" hierarchical_rv-monitor:latest bash -c '
  (echo "overflow,safe_tx,time"; echo "node-1,#,0.0"; sleep 7) | \
  rtlola-cli monitor --online --stdin /specs/silent_node.lola
```

Check TeSSLA specification:
```bash
docker build -t hierarchical_rv-monitor .
docker run --rm -v "$(pwd)/tessla_specs:/specs" \
  hierarchical_rv-monitor:latest \
  tessla compile-core /specs/p3_5_silent_node.tessla
```
