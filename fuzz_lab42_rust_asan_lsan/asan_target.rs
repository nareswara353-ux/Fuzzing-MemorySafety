use std::env;
use std::fs::File;
use std::io::Read;
use std::process;

fn process_asan_payload(data: &[u8]) {
    if data.len() < 8 {
        return;
    }

    let magic = u32::from_le_bytes([data[0], data[1], data[2], data[3]]);
    if magic != 0x4153414E {
        return;
    }

    let mode = data[4];
    if mode == 0xAA {
        unsafe {
            let layout = std::alloc::Layout::from_size_align(16, 4).unwrap();
            let ptr = std::alloc::alloc(layout);
            if !ptr.is_null() {
                for i in 0..64 {
                    *ptr.add(i) = 0x42;
                }
                std::alloc::dealloc(ptr, layout);
            }
        }
        eprintln!("[!] ASAN HEAP BUFFER OVERFLOW HIT");
        process::abort();
    } else {
        println!("[*] Safe memory operations executed");
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

    process_asan_payload(&buffer);
}
