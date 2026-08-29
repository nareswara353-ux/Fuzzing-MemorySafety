const fs = require('fs');
const path = require('path');

function processInput(filePath) {
    if (!fs.existsSync(filePath)) {
        process.exit(1);
    }

    const inputData = fs.readFileSync(filePath, 'utf8').trim();
    if (inputData.length === 0) {
        process.exit(0);
    }

    const addonPath = path.join(__dirname, 'addon.node');
    if (!fs.existsSync(addonPath)) {
        console.error("addon.node missing");
        process.exit(1);
    }

    const addon = require(addonPath);
    addon.processNativeBuffer(inputData);

    console.log("[*] Native N-API addon call executed safely");
}

if (process.argv.length > 2) {
    processInput(process.argv[2]);
}
