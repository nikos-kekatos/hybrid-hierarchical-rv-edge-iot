# Hybrid Hierarchical Runtime Verification for Edge-IoT Security: Combining MonPoly and RTLola

Paper, specifications, code and experimental results for a three-layer runtime-verification
architecture for edge-IoT security monitoring, in which the cloud layer runs **two complementary
RV engines**: MonPoly for first-order temporal correlation across devices, and RTLola for
time-triggered properties that must fire when a compromised device *stops* emitting events.

## Publication

**Nikolaos Kekatos**¹ ✉, **Marinelio Chintri**², **Panagiotis Katsaros**³, **Alexios Lekidis**⁴,
**Tom Nianios**¹, **Ioannis Seitoglou**², **Anastasios Temperekidis**¹, **Stylianos Basagiannis**²

1. Clone Systems, Larnaca, Cyprus — `{nkekatos,tnianios,atemperekidis}@clone-systems.com`
2. International Hellenic University, Serres, Greece — `{basagiannis,marchint,ioaseito}@ihu.gr`
3. Aristotle University of Thessaloniki, Greece — `katsaros@csd.auth.gr`
4. University of Thessaly, Larissa, Greece — `alekidis@uth.gr`

✉ Corresponding author.

Accepted at the **IWAPS** workshop of **ARES 2026** (International Conference on Availability,
Reliability and Security), Vienna, 24 August 2026; proceedings published by Springer in **LNCS**.

The accepted manuscript is `paper/paper.pdf`; `paper/paper.tex` is the source that produced it.
The definitive version of record is the Springer-published proceedings version.

## The problem

Security monitoring of edge-IoT fleets faces three structural challenges. A per-node monitor is
cheap but cannot see attacks that coordinate across devices. A cloud monitor sees the whole fleet
but pays for that view in bandwidth. And a cloud monitor built on a single, event-triggered RV
engine can be defeated by an attacker who compromises a device, raises one malicious request and
then goes silent: once the events stop, an event-triggered monitor has nothing left to evaluate.

The architecture answers all three with three layers and two engines at the top.

```
L1 edge        canonicaliser.py       classifies each raw event as it happens
L2 gateway     cloud_monitor.py       aggregates short windows of per-device behaviour
L3 cloud       correlator_monitor.py  MonPoly (P3.1-P3.4) + RTLola (P3.5)
```

## Layout

```
paper/                    accepted manuscript, LaTeX source, bibliography
code/                     the full stack (this is the code that produced the paper's results)
  monpoly_specs/          P3.1 APT, P3.2 botnet, P3.3 escalation, P3.4 persistent + signature
  rtlola_specs/           P3.5 silent-node anomaly
  tessla_specs/           TeSSLa example specification
  evaluation/             orchestration, metrics collection, analysis
  Dockerfile, docker-compose.yml
results/primary-600s/     a 600 s 15-actor run reproduced on 2026-08-03
results/supplementary/
  duration-sweep/         300 s, 600 s and 1200 s runs
  may-snapshot/           an earlier MonPoly-only snapshot, kept for reference
```

## Reproduce

Docker is the only requirement. The image compiles `rtlola-cli` from source, so the first build
takes several minutes.

```sh
cd code
./evaluation/run_experiment.sh 600      # the paper's primary run; 120 for a quick check
cat results/metrics.json
python3 evaluation/analyze_results.py --metrics results/metrics.json
```

`run_experiment.sh` brings the compose stack up, runs for the given duration, tears it down, then
collects metrics into `results/metrics.json` and detection rates into `results/analysis.json`.

## What reproduces

The testbed is a live 15-container emulation whose event generation is timing-dependent, so runs
are **not** bit-identical. What reproduces is the behaviour and the magnitudes. A 600 s run on
2026-08-03 against the paper's Table 5:

| ID | property | engine | paper | rerun |
|---|---|---|---|---|
| P3.1 | apt_indicator | MonPoly | 41 | 39 |
| P3.2 | coordinated_attack | MonPoly | 19 | 20 |
| P3.3 | escalation_pattern | MonPoly | 41 | 39 |
| P3.4 | persistent_threat | MonPoly | 6 | 5 |
| P3.5 | silent_node_anomaly | RTLola | 30 | 35 |
| | **total incidents** | | **137** | **138** |

Table 4 aggregates likewise: 6872 raw events in the paper against 6728 on rerun, with overflow
alerts 93 against 92. Expect every count to land within a few percent of the published figure
rather than on it.

## Citing

```bibtex
@InProceedings{kekatos2027hybrid,
  author    = {Kekatos, Nikolaos and Chintri, Marinelio and Katsaros, Panagiotis
               and Lekidis, Alexios and Nianios, Tom and Seitoglou, Ioannis
               and Temperekidis, Anastasios and Basagiannis, Stylianos},
  editor    = {Kieseberg, Peter and Skopik, Florian and Atli, Buse
               and Asplund, Mikael},
  title     = {Hybrid Hierarchical Runtime Verification for {Edge-IoT} Security:
               Combining {MonPoly} and {RTLola}},
  booktitle = {Availability, Reliability and Security.
               ARES 2026 EU Projects Symposium Workshops},
  series    = {Lecture Notes in Computer Science},
  volume    = {16903},
  pages     = {222--240},
  publisher = {Springer},
  address   = {Cham},
  year      = {2027},
  doi       = {10.1007/978-3-032-37218-5_14}
}
```

Published version: <https://link.springer.com/chapter/10.1007/978-3-032-37218-5_14>

## Licence

Code, specifications and results: MIT (`LICENSE`). The manuscript is the authors' accepted
version; the definitive record is the Springer-published proceedings version.
