use std::env;
use std::fs::File;
use std::io::Read;
use std::process;

extern "C" {
    fn process_c_payload(data: *const u8, len: usize);
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

    unsafe {
        process_c_payload(buffer.as_ptr(), buffer.len());
    }
}
