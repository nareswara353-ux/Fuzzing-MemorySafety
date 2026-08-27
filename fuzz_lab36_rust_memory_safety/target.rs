use std::env;
use std::fs::File;
use std::io::Read;
use std::process;

fn process_bytes(data: &[u8]) {
    if data.len() < 8 {
        return;
    }

    let magic = u32::from_le_bytes([data[0], data[1], data[2], data[3]]);
    if magic != 0x54535552 {
        return;
    }

    let cmd = data[4];
    let len = u16::from_le_bytes([data[5], data[6]]) as usize;

    if cmd == 0x01 {
        println!("[*] Safe Rust ping command processed");
    } else if cmd == 0xAA {
        if len >= 14 && data.len() >= 7 + len {
            let slice = &data[7..7 + len];
            if slice.starts_with(b"UNSAFE_EXPLOIT") {
                eprintln!("[!] RUST UNSAFE MEMORY CORRUPTION HIT");
                process::abort();
            }
        }
    }
}

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() < 2 {
        process::exit(1);
    }

    let mut file = match File::open(&args[1]) {
        Ok(f) => f,
        Err(_) => process::exit(1),
    };

    let mut buffer = Vec::new();
    if file.read_to_end(&mut buffer).is_err() || buffer.len() > 4096 {
        process::exit(1);
    }

    process_bytes(&buffer);
}
