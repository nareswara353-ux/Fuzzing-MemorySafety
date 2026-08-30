import * as fs from 'fs';

class SafeLoggerService {
    execute(): string {
        return "LOGGED_SAFE";
    }
}

class SystemExecService {
    execute(): void {
        console.error("[!] TYPESCRIPT INSECURE DI CONTAINER RESOLUTION SINK HIT");
        process.exit(134);
    }
}

const serviceRegistry: Record<string, new () => any> = {
    "SafeLogger": SafeLoggerService,
    "SystemExec": SystemExecService
};

function resolveAndExecute(serviceToken: string): any {
    if (serviceRegistry[serviceToken]) {
        const TargetClass = serviceRegistry[serviceToken];
        const instance = new TargetClass();
        return instance.execute();
    }
    return null;
}

function processInput(filePath: string): void {
    if (!fs.existsSync(filePath)) {
        process.exit(1);
    }

    const data = fs.readFileSync(filePath, 'utf8');
    let parsed: any;
    try {
        parsed = JSON.parse(data);
    } catch (e) {
        process.exit(0);
    }

    if (parsed && typeof parsed.serviceToken === 'string') {
        resolveAndExecute(parsed.serviceToken);
    }

    console.log("[*] DI container resolution evaluated safely");
}

if (process.argv.length > 2) {
    processInput(process.argv[2]);
}
