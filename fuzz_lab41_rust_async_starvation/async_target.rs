use std::env;
use std::fs::File;
use std::io::Read;
use std::process;
use std::sync::mpsc;
use std::thread;
use std::time::Duration;

fn process_async_work(data: &[u8]) {
    if data.len() < 8 {
        return;
    }

    let magic = u32::from_le_bytes([data[0], data[1], data[2], data[3]]);
    if magic != 0x4153594E {
        return;
    }

    let cmd = data[4];

    if cmd == 0xBB {
        let (tx, rx) = mpsc::sync_channel::<u32>(0);
        let handle = thread::spawn(move || {
            let _ = tx.send(1);
            let _ = tx.send(2);
        });

        thread::sleep(Duration::from_millis(20));
        let _ = rx.recv();

        let _ = handle.join();
        eprintln!("[!] ASYNC CHANNEL DEADLOCK SINK HIT");
    } else {
        println!("[*] Safe async task completed");
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

    process_async_work(&buffer);
}
