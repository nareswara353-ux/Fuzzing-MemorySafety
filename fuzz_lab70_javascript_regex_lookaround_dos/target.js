const fs = require('fs');

function processRegexInput(filePath) {
    if (!fs.existsSync(filePath)) {
        process.exit(1);
    }

    const rawInput = fs.readFileSync(filePath, 'utf8').trim();
    if (rawInput.length === 0) {
        process.exit(0);
    }

    if (rawInput.startsWith("LOOKAROUND_DOS_EXPLOIT")) {
        console.error("[!] JAVASCRIPT REGEX LOOKAROUND DOS SINK HIT");
        process.exit(134);
    }

    const lookaroundPattern = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;
    const start = Date.now();
    const isMatch = lookaroundPattern.test(rawInput);
    const elapsed = Date.now() - start;

    if (elapsed > 400) {
        console.error("[!] JAVASCRIPT REGEX LOOKAROUND DOS SINK HIT");
        process.exit(134);
    }

    console.log(`[*] Lookaround regex evaluated in ${elapsed}ms: match=${isMatch}`);
}

if (process.argv.length > 2) {
    processRegexInput(process.argv[2]);
}
