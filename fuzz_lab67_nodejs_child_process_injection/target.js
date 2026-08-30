const fs = require('fs');

function processCommandInput(filePath) {
    if (!fs.existsSync(filePath)) {
        process.exit(1);
    }

    const rawInput = fs.readFileSync(filePath, 'utf8').trim();
    if (rawInput.length === 0) {
        process.exit(0);
    }

    const dangerousDelimiters = [";", "&&", "||", "|", "`", "$("];
    const hasDelimiter = dangerousDelimiters.some(d => rawInput.includes(d));

    if (hasDelimiter && (rawInput.includes("EXPLOIT_CMD_EXEC") || rawInput.includes("whoami") || rawInput.includes("id"))) {
        console.error("[!] NODEJS CHILD PROCESS COMMAND INJECTION SINK HIT");
        process.exit(134);
    }

    console.log(`[*] Command argument validated safely: ${rawInput}`);
}

if (process.argv.length > 2) {
    processCommandInput(process.argv[2]);
}
