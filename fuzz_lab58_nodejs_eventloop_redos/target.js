const fs = require('fs');

function processInput(filePath) {
    if (!fs.existsSync(filePath)) {
        process.exit(1);
    }

    const input = fs.readFileSync(filePath, 'utf8').trim();
    if (input.length === 0) {
        process.exit(0);
    }

    if (input.startsWith("CRITICAL_EVENTLOOP_BLOCK")) {
        console.error("[!] EVENT LOOP MICROTASK / REDOS BLOCK HIT");
        process.exit(134);
    }

    const vulnerablePattern = /^(a+)+$/;
    const start = Date.now();
    const isMatch = vulnerablePattern.test(input);
    const elapsed = Date.now() - start;

    if (elapsed > 400) {
        console.error("[!] EVENT LOOP MICROTASK / REDOS BLOCK HIT");
        process.exit(134);
    }

    console.log(`[*] Regex evaluation completed in ${elapsed}ms: match=${isMatch}`);
}

if (process.argv.length > 2) {
    processInput(process.argv[2]);
}
