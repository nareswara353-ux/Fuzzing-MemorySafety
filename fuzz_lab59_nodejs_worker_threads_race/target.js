const { Worker, isMainThread, parentPort, workerData } = require('worker_threads');
const fs = require('fs');

if (isMainThread) {
    function processInput(filePath) {
        if (!fs.existsSync(filePath)) {
            process.exit(1);
        }

        const raw = fs.readFileSync(filePath, 'utf8');
        let parsed;
        try {
            parsed = JSON.parse(raw);
        } catch (e) {
            process.exit(0);
        }

        if (parsed.mode === "RACE_TRIGGER") {
            const sharedBuffer = new SharedArrayBuffer(4);
            const sharedArray = new Int32Array(sharedBuffer);

            const w1 = new Worker(__filename, { workerData: { sharedBuffer, increments: 500 } });
            const w2 = new Worker(__filename, { workerData: { sharedBuffer, increments: 500 } });

            let completed = 0;
            const onExit = () => {
                completed++;
                if (completed === 2) {
                    console.error("[!] WORKER THREAD SHARED MEMORY DATA RACE HIT");
                    process.exit(134);
                }
            };

            w1.on('exit', onExit);
            w2.on('exit', onExit);
        } else {
            console.log("[*] Safe single-threaded worker processing completed");
        }
    }

    if (process.argv.length > 2) {
        processInput(process.argv[2]);
    }
} else {
    const { sharedBuffer, increments } = workerData;
    const array = new Int32Array(sharedBuffer);
    for (let i = 0; i < increments; i++) {
        array[0]++;
    }
}
