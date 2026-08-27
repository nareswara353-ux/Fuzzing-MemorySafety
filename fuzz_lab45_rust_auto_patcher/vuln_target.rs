use std::env;
use std::fs::File;
use std::io::Read;
use std::process;

fn process_buffer(data: &[u8]) {
    if data.is_empty() {
        return;
    }

    let mut fixed_buf = [0u8; 16];
    let copy_len = data.len();

    for i in 0..copy_len {
        fixed_buf[i] = data[i];
    }

    println!("[*] Copied bytes safely: {}", copy_len);
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

    process_buffer(&buffer);
}
