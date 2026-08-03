import os
import time
import json
import random
import string

# --- ΑΛΗΘΙΝΗ ΤΥΧΑΙΟΤΗΤΑ ---
random.seed(os.urandom(16))

DEVICE_ID = os.environ.get("DEVICE_ID", "unknown-node")
PROFILE = os.environ.get("PROFILE", "normal") 
LOG_FILE = "/shared_data/events.log"
BUFFER_SIZE = 30 

def emit_raw_event(event_type, attempted_size, actual_sent, fake_time=None, content=None):
    current_time = fake_time if fake_time else int(time.time())

    raw_event = {
        "turn": current_time,
        "actor": DEVICE_ID,
        "kind": "tool_call",
        "tool": event_type,
        "args": {
            "attempted_size": attempted_size,
            "actual_sent": actual_sent,
            "buffer_limit": BUFFER_SIZE,
            "content": content
        }
    }

    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(raw_event) + "\n")

# --- ΠΕΡΙΕΧΟΜΕΝΟ PAYLOAD (content-level fuzzing, option C) ---
def make_valid_content(size):
    """Well-formed payload: printable-ASCII string of the given size."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=max(0, size)))

def make_malformed_content():
    """Malformed payload that violates the printable-ASCII contract.
    Each choice is caught by is_well_formed() in the canonicaliser."""
    return random.choice([
        "\x00\x01\x02\x07",   # control / non-printable bytes
        "ÿÿÿ", # non-ASCII bytes
        "💣💣💣",               # unexpected multibyte encoding
        None,                 # wrong type (no content)
        12345,                # wrong type (number instead of string)
    ])

def perform_safe_tx():
    payload = random.randint(10, 30)
    emit_raw_event("safe_send", payload, payload, content=make_valid_content(payload))

def perform_overflow_attack():
    payload = random.randint(35, 60)
    emit_raw_event("vulnerable_send", payload, payload, content=make_valid_content(30))

def perform_time_spoof_attack():
    payload = random.randint(10, 30)
    offset = random.choice([-600, -300, 300, 600])
    fake_time = int(time.time()) + offset
    emit_raw_event("time_spoof_send", payload, payload, fake_time=fake_time,
                   content=make_valid_content(payload))

# --- ΝΕΕΣ ΕΠΙΘΕΣΕΙΣ ---
def perform_stealth_overflow():
    payload = random.choice([31, 32]) # Οριακό overflow
    emit_raw_event("vulnerable_send", payload, payload, content=make_valid_content(30))

def perform_fuzz_attack():
    payload = random.randint(10, 30)
    emit_raw_event("fuzz_send", payload, payload, content=make_malformed_content())

if __name__ == "__main__":
    startup_delay = random.uniform(1.0, 5.0)
    time.sleep(startup_delay)
    
    print(f"Node {DEVICE_ID} started with profile: [{PROFILE}] after {startup_delay:.2f}s delay", flush=True)
    
    while True:
        if random.random() < 0.15: 
            time.sleep(random.uniform(0.5, 1.5))
            continue

        if PROFILE == "normal":
            perform_safe_tx()
            time.sleep(random.uniform(0.1, 4.0))
            
        elif PROFILE == "overflow":
            if random.random() < 0.8:
                perform_overflow_attack()
            else:
                perform_safe_tx()
            time.sleep(random.uniform(4.0, 10.0)) 
            
        elif PROFILE == "timespoof":
            perform_time_spoof_attack()
            time.sleep(random.uniform(2.0, 6.0))
            
        elif PROFILE == "spam":
            perform_safe_tx()
            time.sleep(random.uniform(0.005, 0.05)) 
            
        elif PROFILE == "stealth":
            if random.random() < 0.90: perform_safe_tx()
            else: perform_stealth_overflow()
            time.sleep(random.uniform(0.5, 3.0))

        elif PROFILE == "fuzzer":
            if random.random() < 0.6: perform_fuzz_attack()
            else: perform_safe_tx()
            time.sleep(random.uniform(0.5, 2.0))

        elif PROFILE == "pulsing":
            time.sleep(random.uniform(20.0, 30.0))
            for _ in range(20): 
                perform_safe_tx()
                time.sleep(0.05)

        elif PROFILE == "mixed":
            action = random.choices(
                [perform_safe_tx, perform_overflow_attack, perform_time_spoof_attack],
                weights=[0.6, 0.2, 0.2]
            )[0]
            action()
            time.sleep(random.uniform(0.2, 3.5))