import asyncio
import json
import os
import sys
import time

async def worker_task(task_id, duration_ms, is_blocking):
    if is_blocking:
        # VULNERABILITY: Eksekusi sinkronus pemblokir di dalam event loop thread
        time.sleep(duration_ms / 1000.0)
        if duration_ms > 400:
            sys.stderr.write("[!] PYTHON ASYNCIO EVENT LOOP STARVATION SINK HIT\n")
            sys.stderr.flush()
            sys.exit(134)
    else:
        await asyncio.sleep(duration_ms / 1000.0)

async def run_event_loop(payload):
    tasks = []
    for item in payload.get("tasks", []):
        t_id = item.get("id", 0)
        dur = item.get("duration_ms", 10)
        block = item.get("blocking", False)
        tasks.append(worker_task(t_id, dur, block))

    if tasks:
        await asyncio.gather(*tasks)

def main():
    if len(sys.argv) < 2:
        return

    input_file = sys.argv[1]
    if not os.path.exists(input_file):
        return

    try:
        with open(input_file, "r", errors="ignore") as f:
            data = json.load(f)
    except Exception:
        return

    asyncio.run(run_event_loop(data))
    print("[*] Asyncio event loop completed safely")

if __name__ == "__main__":
    main()
