const fs = require('fs');

function processWasmInput(filePath) {
    if (!fs.existsSync(filePath)) {
        process.exit(1);
    }

    const raw = fs.readFileSync(filePath);
    if (raw.length < 9) {
        process.exit(0);
    }

    const magic = raw.readUInt32LE(0);
    if (magic !== 0x5741534D) { // 'WASM'
        return;
    }

    const cmd = raw.readUInt8(4);
    const offset = raw.readInt32LE(5);

    // Alokasi 1 halaman WebAssembly Linear Memory (64 KiB = 65,536 bytes)
    const memory = new WebAssembly.Memory({ initial: 1, maximum: 2 });
    const memView = new DataView(memory.buffer);

    if (cmd === 0xAA) {
        if (offset < 0 || offset >= memView.byteLength) {
            console.error("[!] NODEJS WASM LINEAR MEMORY OUT-OF-BOUNDS HIT");
            process.exit(134);
        }
        memView.setUint8(offset, 0xFF);
    } else {
        if (offset >= 0 && offset < memView.byteLength) {
            memView.setUint8(offset, 0x42);
        }
        console.log("[*] Safe WASM linear memory write executed");
    }
}

if (process.argv.length > 2) {
    processWasmInput(process.argv[2]);
}
