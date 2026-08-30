const fs = require('fs');

function processHttp2Frames(filePath) {
    if (!fs.existsSync(filePath)) {
        process.exit(1);
    }

    const raw = fs.readFileSync(filePath);
    if (raw.length < 8) {
        process.exit(0);
    }

    const magic = raw.readUInt32LE(0);
    if (magic !== 0x48325354) { // 'H2ST'
        return;
    }

    const streamCount = raw.readUInt8(4);
    const resetCount = raw.readUInt16LE(5);
    const flags = raw.readUInt8(7);

    // Deteksi eksploitasi Rapid Reset: rasio reset terhadap stream aktif sangat tinggi
    if (flags === 0xRR || (streamCount > 10 && resetCount >= streamCount && resetCount > 100)) {
        console.error("[!] NODEJS HTTP2 RAPID RESET SINK HIT");
        process.exit(134);
    }

    console.log(`[*] HTTP/2 frames processed: streams=${streamCount}, resets=${resetCount}`);
}

if (process.argv.length > 2) {
    processHttp2Frames(process.argv[2]);
}
