#!/usr/bin/env python3
import struct
import subprocess
import os
import sys

class FirmwareMicroEmulator:
    def __init__(self, target_bin):
        self.target_bin = target_bin
        self.flash_base = 0x08000000
        self.sram_base = 0x20000000
        self.mmio_base = 0x40000000
        self.mock_peripherals = {
            self.mmio_base: 0x00000001,      # Status Register (READY)
            self.mmio_base + 0x04: 0x00000000 # Data Register
        }

    def read_mmio(self, addr):
        return self.mock_peripherals.get(addr, 0x00000000)

    def write_mmio(self, addr, val):
        self.mock_peripherals[addr] = val

    def execute_packet(self, packet_bytes):
        temp_pkt = "/tmp/fw_payload.bin"
        with open(temp_pkt, "wb") as f:
            f.write(packet_bytes)

        proc = subprocess.run([self.target_bin, temp_pkt], capture_output=True)
        crashed = proc.returncode != 0
        output = proc.stdout.decode(errors="ignore") + proc.stderr.decode(errors="ignore")

        if os.path.exists(temp_pkt):
            os.remove(temp_pkt)

        return {
            "crashed": crashed,
            "returncode": proc.returncode,
            "output": output
        }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 firmware_emulator.py <target_binary>")
        sys.exit(1)
    
    emu = FirmwareMicroEmulator(sys.argv[1])
    # Buat packet uji
    test_pkt = struct.pack("<4sIBH64s", b"FIRM", 0x00010002, 0xEE, 32, b"X" * 64)
    res = emu.execute_packet(test_pkt)
    print(f"Emulation Result: {res}")
