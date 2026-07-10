# AGENTS.md

## What this repo is

Multi-language implementation of the Creeper virus (1971) for educational purposes.
Six independent implementations sharing the same behavior spec, each in `*/creeper/`.

## Repo structure

```
python/creeper/   — Python 3.7+ (interpreted, no build step)
rust/creeper/     — Rust (rustc, no Cargo)
go/creeper/       — Go (go build, no go.mod)
nim/creeper/      — Nim 2.0+
c/creeper/        — C11/C17 (gcc from LLVM MinGW)
cpp/creeper/      — C++17 (g++ from LLVM MinGW)
```

Each `*/creeper/` is self-contained: source, `setup_lab.py`, and 12 test user files.

## Build & run (from within each `*/creeper/` directory)

```bash
# Python (no compilation)
python creeper.py

# Rust (GNU toolchain required — see below)
rustc creeper.rs -o creeper.exe && ./creeper.exe

# Go
go build -o creeper.exe creeper.go && ./creeper.exe

# Nim
nim c -d:release --opt:size creeper.nim && ./creeper.exe

# C
gcc creeper.c -o creeper.exe && ./creeper.exe

# C++
g++ -std=c++17 creeper.cpp -o creeper.exe && ./creeper.exe
```

## Generate test files

```bash
# From any */creeper/ directory:
python ../../python/creeper/setup_lab.py
```

Creates 12 user files (txt, csv, html, md, py, png, jpg, mp3, docx, xlsx, pptx).
Must run before each test execution since infection overwrites some files.

## Critical gotchas

- **Rust toolchain must be GNU, not MSVC.** Set with: `rustup default stable-x86_64-pc-windows-gnu`
- **No Cargo.toml, go.mod, or any package manifests.** All compilers are invoked directly.
- **No build system, no tests, no linting, no CI.** Everything is manual one-liners.
- **LLVM MinGW** (`MartinStorsjo.LLVM-MinGW.UCRT`) is shared by Nim, C, and C++.
- **RTL override characters** (U+202E) in generated filenames — these are intentional, not bugs.
- **`*.exe` and `infection.log` are gitignored** but some were committed before `.gitignore` was added.

## Cleanup after a run

```bash
Remove-Item infection.log, "README*txt.py" -ErrorAction SilentlyContinue
python ../../python/creeper/setup_lab.py   # regenerate clean test files
```

## Language differences (only Go supports Office ZIP injection)

| Feature            | Python | Rust | Go | Nim | C | C++ |
|--------------------|--------|------|----|-----|---|-----|
| ZIP injection      | ✗      | ✗    | ✅  | ✗   | ✗ | ✗   |
| Compiled binary    | ✗      | ✅   | ✅  | ✅  | ✅| ✅  |
| Infects Office     | ✗      | ✗    | ✅  | ✗   | ✗ | ✗   |

## Docs

- `README.md` (root) — full project documentation in Spanish
- `python/creeper/README.md`, `rust/creeper/README.md` — per-language notes
- All documentation is in Spanish; code comments vary per language
