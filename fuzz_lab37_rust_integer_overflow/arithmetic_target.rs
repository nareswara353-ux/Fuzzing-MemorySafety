use std::env;
use std::fs::File;
use std::io::Read;
use std::process;

fn process_transaction(data: &[u8]) {
    if data.len() < 11 {
        return;
    }

    let magic = u32::from_le_bytes([data[0], data[1], data[2], data[3]]);
    if magic != 0x4F56464C {
        return;
    }

    let op_type = data[4];
    let val_a = u32::from_le_bytes([data[5], data[6], data[7], data[8]]);
    let val_b = u16::from_le_bytes([data[9], data[10]]) as u32;

    if op_type == 0x01 {
        let res = val_a.saturating_add(val_b);
        println!("[*] Safe saturated math: {}", res);
    } else if op_type == 0xEE {
        if val_a > 0xFFFFFF00 && val_b > 0x00FF {
            eprintln!("[!] INTEGER OVERFLOW SINK HIT");
            let _res: u32 = val_a + val_b;
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

    process_transaction(&buffer);
}
