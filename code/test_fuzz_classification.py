#!/usr/bin/env python3
"""
Self-test for the content-level fuzzing change (option C).
Feeds one sample event per profile through the REAL canonicaliser.py
and checks that each is classified into the expected L1 predicate.

Run from this directory:   python3 test_fuzz_classification.py
No Docker required.
"""
import json, subprocess, sys, time, os

HERE = os.path.dirname(os.path.abspath(__file__))
now = int(time.time())

def ev(tool, size, content, turn=None):
    return {
        "turn": turn or now,
        "actor": "node-x",
        "kind": "tool_call",
        "tool": tool,
        "args": {"attempted_size": size, "actual_sent": size,
                 "buffer_limit": 30, "content": content},
    }

# (tool, size, content, turn, expected_predicate)
cases = [
    ("safe_send",        20, "Abc123xyz",      None,      "safe_tx"),
    ("vulnerable_send",  50, "Abcdefghij",     None,      "buffer_overflow"),  # overflow node
    ("vulnerable_send",  31, "Abcdefghij",     None,      "buffer_overflow"),  # stealth (borderline)
    ("time_spoof_send",  20, "Abcdefghij",     now + 600, "time_anomaly"),
    ("fuzz_send",        20, "\x00\x01\x02",   None,      "logic_fuzz_anomaly"),  # control bytes
    ("fuzz_send",        20, "ÿÿ",   None,      "logic_fuzz_anomaly"),  # non-ASCII
    ("fuzz_send",        20, "\U0001F4A3",     None,      "logic_fuzz_anomaly"),  # emoji / multibyte
    ("fuzz_send",        20, None,             None,      "logic_fuzz_anomaly"),  # wrong type (None)
    ("fuzz_send",        20, 12345,            None,      "logic_fuzz_anomaly"),  # wrong type (int)
]

payload = "\n".join(json.dumps(ev(t, s, c, turn)) for t, s, c, turn, _ in cases) + "\n"

res = subprocess.run([sys.executable, os.path.join(HERE, "canonicaliser.py")],
                     input=payload, capture_output=True, text=True)
out_lines = [l for l in res.stdout.strip().split("\n") if l]

if len(out_lines) != len(cases):
    print(f"!! expected {len(cases)} output lines, got {len(out_lines)}")
    print("STDOUT:", res.stdout)
    print("STDERR:", res.stderr)
    sys.exit(1)

all_ok = True
for (tool, size, content, turn, expected), line in zip(cases, out_lines):
    got = line.split()[1].split("(")[0]
    ok = got == expected
    all_ok &= ok
    print(f"[{'OK' if ok else 'FAIL'}] {tool:16} content={str(content)[:10]:12} -> {got:18} (expected {expected})")

print("\n✅ ALL PASS" if all_ok else "\n❌ SOME FAILED")
sys.exit(0 if all_ok else 1)
