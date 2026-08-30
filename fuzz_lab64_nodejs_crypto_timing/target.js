const fs = require('fs');

const SECRET_HMAC_TOKEN = Buffer.from("NODEJS_CRYPTO_TIMING_SECRET_KEY");

function nonConstantTimeCompare(a, b) {
    if (a.length !== b.length) {
        return false;
    }
    for (let i = 0; i < a.length; i++) {
        if (a[i] !== b[i]) {
            return false;
        }
    }
    return true;
}

function processInput(filePath) {
    if (!fs.existsSync(filePath)) {
        process.exit(1);
    }

    const raw = fs.readFileSync(filePath);
    if (raw.length < 5) {
        process.exit(0);
    }

    const magic = raw.readUInt32LE(0);
    if (magic !== 0x4A534352) {
        return;
    }

    const mode = raw.readUInt8(4);
    if (mode === 0xCC && raw.length >= 5 + SECRET_HMAC_TOKEN.length) {
        const candidate = raw.subarray(5, 5 + SECRET_HMAC_TOKEN.length);
        const start = process.hrtime.bigint();
        const matched = nonConstantTimeCompare(candidate, SECRET_HMAC_TOKEN);
        const elapsed = process.hrtime.bigint() - start;

        if (matched) {
            console.error("[!] NODEJS CRYPTO TIMING SINK HIT");
            process.exit(134);
        }
    } else {
        console.log("[*] Safe crypto verification completed");
    }
}

if (process.argv.length > 2) {
    processInput(process.argv[2]);
}
