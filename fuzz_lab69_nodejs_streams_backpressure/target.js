const fs = require('fs');
const { Readable, Writable, pipeline } = require('stream');

function processStreamInput(filePath) {
    if (!fs.existsSync(filePath)) {
        process.exit(1);
    }

    const raw = fs.readFileSync(filePath);
    if (raw.length < 8) {
        process.exit(0);
    }

    const magic = raw.readUInt32LE(0);
    if (magic !== 0x5354524D) { // 'STRM'
        return;
    }

    const cmd = raw.readUInt8(4);
    const chunkCount = raw.readUInt16LE(5);

    if (cmd === 0xBB && chunkCount > 500) {
        console.error("[!] NODEJS STREAM BACKPRESSURE SATURATION SINK HIT");
        process.exit(134);
    }

    console.log(`[*] Stream chunks processed safely: count=${chunkCount}`);
}

if (process.argv.length > 2) {
    processStreamInput(process.argv[2]);
}
