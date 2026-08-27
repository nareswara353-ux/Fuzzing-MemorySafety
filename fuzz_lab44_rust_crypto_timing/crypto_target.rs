use std::env;
use std::fs::File;
use std::io::Read;
use std::process;
use std::time::Instant;

const SECRET_KEY: &[u8; 16] = b"SECRET_HMAC_KEY!";

fn non_constant_time_compare(a: &[u8], b: &[u8]) -> bool {
    if a.len() != b.len() {
        return false;
    }
    for i in 0..a.len() {
        if a[i] != b[i] {
            return false;
        }
    }
    true
}

fn process_crypto(data: &[u8]) {
    if data.len() < 8 {
        return;
    }

    let magic = u32::from_le_bytes([data[0], data[1], data[2], data[3]]);
    if magic != 0x43525950 {
        return;
    }

    let mode = data[4];
    if mode == 0xCC {
        if data.len() >= 21 {
            let candidate = &data[5..21];
            let start = Instant::now();
            let is_match = non_constant_time_compare(candidate, SECRET_KEY);
            let _elapsed = start.elapsed();
            if is_match {
                eprintln!("[!] CRYPTO SIDE CHANNEL SINK HIT");
                process::abort();
            }
        }
    } else {
        println!("[*] Safe crypto operation executed");
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

    process_crypto(&buffer);
}
