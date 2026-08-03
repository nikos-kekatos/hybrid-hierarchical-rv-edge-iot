import sys
import re
import json
import time
from collections import defaultdict, deque

PULSING_WINDOW, PULSING_THRESHOLD = 2, 15
OVERFLOW_WINDOW, OVERFLOW_THRESHOLD = 30, 3
SPAM_WINDOW, SPAM_THRESHOLD = 5, 30
ALERTS_LOG = "/shared_data/alerts.log"

pulsing_history = defaultdict(deque)
overflow_history = defaultdict(deque)
spam_history = defaultdict(deque)

def emit_alert(alert_type, device_id, timestamp, metadata=None):
    """Emit structured alert for Layer 3 monitoring"""
    alert = {
        "timestamp": timestamp,
        "type": alert_type,
        "device": device_id,
        "metadata": metadata or {}
    }

    # Print to stdout for pipeline (Layer 3)
    print(json.dumps(alert), flush=True)

    # Also write to log file for persistence
    try:
        with open(ALERTS_LOG, "a") as f:
            f.write(json.dumps(alert) + "\n")
    except Exception:
        pass

# --- Per-event timing (Table 7) + consumed counter (L1->L2 loss) ---
_timing = []
_consumed = 0
_TIMING_OUT = "/shared_data/l2_timing.json"

def _pct(sorted_xs, p):
    n = len(sorted_xs)
    return sorted_xs[min(n - 1, int(p / 100.0 * n))]

def _dump_timing():
    if not _timing:
        return
    xs = sorted(_timing)                      # nanoseconds
    n = len(xs)
    stats = {
        "tier": "L2",
        "n_events": n,
        "n_consumed": _consumed,              # matched canonical events from L1
        "mean_us": (sum(xs) / n) / 1000.0,
        "p50_us":  _pct(xs, 50) / 1000.0,
        "p95_us":  _pct(xs, 95) / 1000.0,
        "p99_us":  _pct(xs, 99) / 1000.0,
        "max_us":  xs[-1] / 1000.0,
    }
    try:
        with open(_TIMING_OUT, "w") as f:
            json.dump(stats, f, indent=2)
    except Exception:
        pass

def _handle_event(timestamp, event_type, device_id):
    """Per-event body (alert-emitting logic is byte-identical to before)."""
    if event_type == "time_anomaly":
        emit_alert("time_anomaly", device_id, timestamp)
        return
    if event_type == "logic_fuzz_anomaly":
        emit_alert("fuzzing", device_id, timestamp)
        return
    if event_type == "buffer_overflow":
        hist = overflow_history[device_id]
        hist.append(timestamp)
        while hist and hist[0] < timestamp - OVERFLOW_WINDOW: hist.popleft()
        if len(hist) >= OVERFLOW_THRESHOLD:
            emit_alert("overflow", device_id, timestamp,
                       {"count": len(hist), "window_sec": OVERFLOW_WINDOW})
            hist.clear()
        return
    if event_type == "safe_tx":
        emit_alert("safe_tx", device_id, timestamp)   # forward for P3.3
        hist = spam_history[device_id]
        hist.append(timestamp)
        while hist and hist[0] < timestamp - SPAM_WINDOW: hist.popleft()
        if len(hist) >= SPAM_THRESHOLD:
            emit_alert("dos_spam", device_id, timestamp,
                       {"count": len(hist), "window_sec": SPAM_WINDOW})
            hist.clear()
        p_q = pulsing_history[device_id]
        p_q.append(timestamp)
        while p_q and p_q[0] < timestamp - PULSING_WINDOW: p_q.popleft()
        if len(p_q) >= PULSING_THRESHOLD:
            emit_alert("dos_spam", device_id, timestamp)
            p_q.clear()
        return

def process_cloud_stream():
    global _consumed
    print("=== Cloud Monitor Active: Multi-Threat Detection ===", file=sys.stderr, flush=True)

    log_pattern = re.compile(r'@(\d+)\s+(buffer_overflow|time_anomaly|logic_fuzz_anomaly|safe_tx)\("(.*?)",\s+(-?\d+)\)')

    for line in sys.stdin:
        line = line.strip()
        match = log_pattern.search(line)
        if not match:
            continue
        _consumed += 1
        timestamp = int(match.group(1))
        event_type = match.group(2)
        device_id = match.group(3)

        t0 = time.perf_counter_ns()           # time the per-event body
        _handle_event(timestamp, event_type, device_id)
        _timing.append(time.perf_counter_ns() - t0)
        if len(_timing) % 200 == 0:
            _dump_timing()

    _dump_timing()                            # final dump on stdin EOF


if __name__ == "__main__":
    process_cloud_stream()