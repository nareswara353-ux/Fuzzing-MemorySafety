const fs = require('fs');

function processBufferInput(filePath) {
    if (!fs.existsSync(filePath)) {
        process.exit(1);
    }

    const raw = fs.readFileSync(filePath);
    if (raw.length < 9) {
        process.exit(0);
    }

    const magic = raw.readUInt32LE(0);
    if (magic !== 0x42554646) {
        return;
    }

    const cmd = raw.readUInt8(4);
    const offset = raw.readInt32LE(5);

    if (cmd === 0xEE) {
        const unsafeBuf = Buffer.allocUnsafe(16);
        if (offset < 0 || offset >= unsafeBuf.length) {
            console.error("[!] NODEJS BUFFER OUT-OF-BOUNDS SINK HIT");
            process.exit(134);
        }
        unsafeBuf[offset] = 0xFF;
    } else {
        const safeBuf = Buffer.alloc(16);
        if (offset >= 0 && offset < safeBuf.length) {
            safeBuf[offset] = 0xAA;
        }
        console.log("[*] Safe buffer write executed");
    }
}

if (process.argv.length > 2) {
    processBufferInput(process.argv[2]);
}
