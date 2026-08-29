const vm = require('vm');
const fs = require('fs');

function evaluateSandboxedCode(filePath) {
    if (!fs.existsSync(filePath)) {
        process.exit(1);
    }

    const userScript = fs.readFileSync(filePath, 'utf8').trim();
    if (userScript.length === 0) {
        process.exit(0);
    }

    const sandbox = {
        console: { log: () => {} },
        data: { value: 42 }
    };

    const context = vm.createContext(sandbox);

    try {
        const script = new vm.Script(userScript);
        const result = script.runInContext(context, { timeout: 1000 });

        if (userScript.includes("CRITICAL_VM_ESCAPE") || (result && typeof result === 'object' && result.isHostProcess)) {
            console.error("[!] NODEJS VM CONTEXT SANDBOX ESCAPE HIT");
            process.exit(134);
        }

        console.log("[*] Sandbox script executed safely:", result);
    } catch (err) {
        if (err.message && err.message.includes("ESCAPE_TRIGGERED")) {
            console.error("[!] NODEJS VM CONTEXT SANDBOX ESCAPE HIT");
            process.exit(134);
        }
        process.exit(0);
    }
}

if (process.argv.length > 2) {
    evaluateSandboxedCode(process.argv[2]);
}
