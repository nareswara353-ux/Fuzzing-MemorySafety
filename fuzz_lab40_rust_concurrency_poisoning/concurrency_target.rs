use std::env;
use std::fs::File;
use std::io::Read;
use std::process;
use std::sync::{Arc, Mutex};
use std::thread;

fn process_concurrency(data: &[u8]) {
    if data.len() < 8 {
        return;
    }

    let magic = u32::from_le_bytes([data[0], data[1], data[2], data[3]]);
    if magic != 0x504F4953 {
        return;
    }

    let mode = data[4];
    let lock_data = Arc::new(Mutex::new(0u32));

    if mode == 0xDD {
        let lock_clone = Arc::clone(&lock_data);
        let handle = thread::spawn(move || {
            let _guard = lock_clone.lock().unwrap();
            panic!("Worker thread panic holding mutex lock");
        });

        let _ = handle.join();

        eprintln!("[!] MUTEX POISONING SINK HIT");
        let _res = lock_data.lock().unwrap();
    } else {
        let mut guard = lock_data.lock().unwrap();
        *guard += 1;
        println!("[*] Safe mutex lock executed: {}", *guard);
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

    process_concurrency(&buffer);
}
