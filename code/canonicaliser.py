import sys
import json
import time

# --- Per-event timing instrumentation (Table 7) ---
_timing = []
_TIMING_OUT = "/shared_data/l1_timing.json"

def _pct(sorted_xs, p):
    n = len(sorted_xs)
    return sorted_xs[min(n - 1, int(p / 100.0 * n))]

def _dump_timing():
    if not _timing:
        return
    xs = sorted(_timing)                      # nanoseconds
    n = len(xs)
    stats = {
        "tier": "L1",
        "n_events": n,
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

def is_well_formed(content):
    """Payload contract (option C): a printable-ASCII string.
    Anything else (non-ASCII, control chars, wrong type, missing) is malformed."""
    if not isinstance(content, str):
        return False
    try:
        content.encode("ascii")
    except UnicodeEncodeError:
        return False
    return all(31 < ord(c) < 127 for c in content)

def process_stream():
    for line in sys.stdin:
        line = line.strip()
        if not line.startswith('{'):
            continue

        t0 = time.perf_counter_ns()           # start timing the per-event body
        try:
            event = json.loads(line)
            t, actor, tool, args = event["turn"], event["actor"], event["tool"], event["args"]

            is_overflow = args["actual_sent"] > args["buffer_limit"]          # μέγεθος (P1.1)
            is_fuzzed   = not is_well_formed(args.get("content", ""))         # περιεχόμενο (P1.3)

            curr = int(time.time())
            is_time_spoofed = abs(curr - t) > 15


            if is_overflow and tool == "vulnerable_send":
                print(f"@{t} buffer_overflow(\"{actor}\", {args['actual_sent']})", flush=True)
            elif is_time_spoofed:
                print(f"@{curr} time_anomaly(\"{actor}\", {t})", flush=True)
            elif is_fuzzed:
                print(f"@{t} logic_fuzz_anomaly(\"{actor}\", {args['actual_sent']})", flush=True)
            else:
                print(f"@{t} safe_tx(\"{actor}\", {args['actual_sent']})", flush=True)

        except (json.JSONDecodeError, KeyError):
            continue

        _timing.append(time.perf_counter_ns() - t0)
        if len(_timing) % 200 == 0:           # periodic dump in case of kill
            _dump_timing()

    _dump_timing()                            # final dump on stdin EOF

if __name__ == "__main__":
    process_stream()