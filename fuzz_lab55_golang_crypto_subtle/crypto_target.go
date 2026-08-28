package main

import (
	"encoding/binary"
	"fmt"
	"os"
	"time"
)

var secretMasterKey = []byte("GO_MASTER_KEY_32B_SECRET_TOKEN!")

func nonConstantTimeEqual(a, b []byte) bool {
	if len(a) != len(b) {
		return false
	}
	for i := 0; i < len(a); i++ {
		if a[i] != b[i] {
			return false
		}
	}
	return true
}

func processCrypto(data []byte) {
	if len(data) < 8 {
		return
	}
	magic := binary.LittleEndian.Uint32(data[0:4])
	if magic != 0x474F5342 {
		return
	}
	mode := data[4]

	if mode == 0xCC && len(data) >= 5+len(secretMasterKey) {
		candidate := data[5 : 5+len(secretMasterKey)]
		start := time.Now()
		matched := nonConstantTimeEqual(candidate, secretMasterKey)
		_ = time.Since(start)

		if matched {
			fmt.Fprintf(os.Stderr, "[!] CRYPTO TIMING LEAK SINK HIT\n")
			panic("CRYPTO_SUBTLE_TIMING_LEAK_SINK")
		}
	} else {
		fmt.Println("[*] Safe crypto hash verification executed")
	}
}

func main() {
	if len(os.Args) < 2 {
		os.Exit(1)
	}
	data, err := os.ReadFile(os.Args[1])
	if err != nil || len(data) > 4096 {
		os.Exit(1)
	}
	processCrypto(data)
}
