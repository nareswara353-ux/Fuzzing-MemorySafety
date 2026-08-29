const fs = require('fs');

function recursiveMerge(target, source) {
    for (const key in source) {
        if (typeof source[key] === 'object' && source[key] !== null && !Array.isArray(source[key])) {
            if (!target[key]) target[key] = {};
            recursiveMerge(target[key], source[key]);
        } else {
            target[key] = source[key];
        }
    }
    return target;
}

function processInput(filePath) {
    if (!fs.existsSync(filePath)) {
        process.exit(1);
    }

    const data = fs.readFileSync(filePath, 'utf8');
    let parsed;
    try {
        parsed = JSON.parse(data);
    } catch (e) {
        process.exit(0);
    }

    const baseObj = {};
    recursiveMerge(baseObj, parsed);

    const testObj = {};
    if (testObj.polluted === "CRITICAL_POLLUTION_HIT" || testObj.isAdmin === true) {
        console.error("[!] PROTOTYPE POLLUTION EXPLOIT SINK HIT");
        process.exit(134);
    }

    console.log("[*] Safe object merge completed");
}

if (process.argv.length > 2) {
    processInput(process.argv[2]);
}
