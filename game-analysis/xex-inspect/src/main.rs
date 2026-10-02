#![forbid(unsafe_code)]
use std::fs::File;
use std::io::{self, Write};

fn run() -> Result<(), String> {
    let args: Vec<_> = std::env::args_os().collect();
    if args.len() != 2 {
        return Err("usage: obsidian-xex-inspect FILE (read-only metadata)".into());
    }
    let meta = std::fs::metadata(&args[1]).map_err(|_| "cannot stat input")?;
    if !meta.is_file() {
        return Err("input must be a regular file".into());
    }
    let mut file = File::open(&args[1]).map_err(|_| "cannot open input")?;
    let meta = file.metadata().map_err(|_| "cannot stat opened input")?;
    if !meta.is_file() {
        return Err("opened input must be a regular file".into());
    }
    let report = obsidian_xex_inspect::inspect(&mut file, meta.len()).map_err(|e| e.0)?;
    writeln!(io::stdout().lock(), "{}", report.json()).map_err(|_| "cannot write output")?;
    Ok(())
}

fn main() {
    if let Err(e) = run() {
        eprintln!("xex-inspect: {e}");
        std::process::exit(2);
    }
}
