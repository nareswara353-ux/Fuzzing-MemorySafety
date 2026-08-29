import * as fs from 'fs';

interface FinancialRecord {
    userId: number;
    transactions: number[]; // TS static type assumption
}

function processFinancialData(record: FinancialRecord) {
    // Type Erasure Vulnerability: No runtime validation that 'transactions' is actually an array
    let total = 0;
    
    // If transactions is a string or null at runtime, .forEach or .reduce will throw TypeError
    record.transactions.forEach(amount => {
        total += amount;
    });

    if (total > 100000) {
        console.error("[!] HIGH VALUE TRANSACTION DETECTED");
    }

    console.log(`[*] Processed financial record safely. Total: ${total}`);
}

function processInput(filePath: string) {
    if (!fs.existsSync(filePath)) {
        process.exit(1);
    }

    const data = fs.readFileSync(filePath, 'utf8');
    let parsed: any;
    try {
        parsed = JSON.parse(data);
    } catch (e) {
        process.exit(0); // Ignore valid syntax errors from fuzzer
    }

    // Cast bypassing static check
    const record = parsed as FinancialRecord;

    try {
        processFinancialData(record);
    } catch (err: any) {
        if (err instanceof TypeError) {
            console.error("[!] TYPESCRIPT RUNTIME TYPE CONFUSION SINK HIT");
            console.error(err.message);
            process.exit(134);
        }
        process.exit(1);
    }
}

if (process.argv.length > 2) {
    processInput(process.argv[2]);
}
