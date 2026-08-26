#!/usr/bin/env python3
import hashlib
import os
import shutil
import struct

class DistributedCorpusCoordinator:
    def __init__(self, shared_pool_dir="/tmp/fuzz_cluster_shared"):
        self.shared_pool_dir = shared_pool_dir
        self.known_hashes = set()
        os.makedirs(self.shared_pool_dir, exist_ok=True)

    def compute_hash(self, data):
        return hashlib.sha256(data).hexdigest()

    def broadcast_seed(self, node_id, raw_bytes):
        """Worker menyiarkan seed baru ke shared pool jika belum pernah ada."""
        h = self.compute_hash(raw_bytes)
        if h not in self.known_hashes:
            self.known_hashes.add(h)
            seed_name = f"seed_node_{node_id}_{h[:10]}.bin"
            target_path = os.path.join(self.shared_pool_dir, seed_name)
            with open(target_path, "wb") as f:
                f.write(raw_bytes)
            return True, target_path
        return False, None

    def sync_worker_inbox(self, worker_in_dir):
        """Menyalin seed unggulan dari shared pool ke inbox input worker."""
        os.makedirs(worker_in_dir, exist_ok=True)
        synced_count = 0
        for f in os.listdir(self.shared_pool_dir):
            src = os.path.join(self.shared_pool_dir, f)
            dst = os.path.join(worker_in_dir, f)
            if os.path.isfile(src) and not os.path.exists(dst):
                shutil.copy2(src, dst)
                synced_count += 1
        return synced_count

def synthesize_cluster_seed(node_id, seq_id, cmd, data_bytes):
    magic = 0x54534944 # 'DIST'
    payload_len = len(data_bytes)
    padded_data = data_bytes.ljust(64, b"\x00")[:64]
    return struct.pack("<IHHBB64s", magic, node_id, seq_id, cmd, payload_len, padded_data)

if __name__ == "__main__":
    coord = DistributedCorpusCoordinator()
    sample = synthesize_cluster_seed(1, 101, 0xCC, b"CLUSTER_SYNC_ALL")
    ok, path = coord.broadcast_seed(1, sample)
    print(f"[+] Broadcast Seed: {ok} -> {path}")
