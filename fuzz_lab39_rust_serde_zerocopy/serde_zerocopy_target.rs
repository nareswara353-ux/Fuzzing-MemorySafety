use std::env;
use std::fs::File;
use std::io::Read;
use std::process;

struct ZeroCopyView<'a> {
    tag: u8,
    name: &'a str,
    payload: &'a [u8],
}

fn parse_zerocopy<'a>(data: &'a [u8]) -> Result<ZeroCopyView<'a>, &'static str> {
    if data.len() < 8 {
        return Err("too short");
    }
    let magic = u32::from_le_bytes([data[0], data[1], data[2], data[3]]);
    if magic != 0x5A435059 {
        return Err("invalid magic");
    }
    let tag = data[4];
    let name_len = data[5] as usize;
    let payload_len = u16::from_le_bytes([data[6], data[7]]) as usize;

    if data.len() < 8 + name_len + payload_len {
        return Err("out of bounds");
    }

    let name_bytes = &data[8..8 + name_len];
    let name_str = match std::str::from_utf8(name_bytes) {
        Ok(s) => s,
        Err(_) => return Err("invalid utf8"),
    };

    let payload_bytes = &data[8 + name_len..8 + name_len + payload_len];

    Ok(ZeroCopyView {
        tag,
        name: name_str,
        payload: payload_bytes,
    })
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

    match parse_zerocopy(&buffer) {
        Ok(view) => {
            if view.tag == 0x7E && view.name == "admin_zero" {
                eprintln!("[!] RUST ZERO-COPY DESERIALIZATION PANIC HIT");
                process::abort();
            }
            println!("[*] Valid zero-copy view: name={}, len={}", view.name, view.payload.len());
        }
        Err(_) => {}
    }
}
