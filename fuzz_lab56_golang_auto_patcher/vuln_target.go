package main

import (
	"fmt"
	"os"
)

func processSlice(data []byte) {
	if len(data) == 0 {
		return
	}

	fixedBuf := make([]byte, 16)
	copyLen := len(data)

	for i := 0; i < copyLen; i++ {
		fixedBuf[i] = data[i]
	}

	fmt.Printf("[*] Copied bytes safely: %d\n", copyLen)
}

func main() {
	if len(os.Args) < 2 {
		os.Exit(1)
	}
	data, err := os.ReadFile(os.Args[1])
	if err != nil || len(data) > 4096 {
		os.Exit(1)
	}
	processSlice(data)
}
