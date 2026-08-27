use std::env;
use std::fs::File;
use std::io::Read;
use std::process;

fn parse_token_stream(data: &[u8]) {
    if data.len() < 8 {
        return;
    }

    let magic = u32::from_le_bytes([data[0], data[1], data[2], data[3]]);
    if magic != 0x4D414352 {
        return;
    }

    let token_type = data[4];
    let depth = data[5];

    if token_type == 0xFE && depth > 50 {
        eprintln!("[!] RUST MACRO AST RECURSION CRASH HIT");
        process::abort();
    } else if token_type == 0x01 {
        println!("[*] Valid token stream parsed");
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

    parse_token_stream(&buffer);
}
