package main

import (
	"encoding/binary"
	"fmt"
	"os"
	"unsafe"
)

type MetadataHeader struct {
	ID    uint32
	Flags uint32
	Tag   [16]byte
}

func processUnsafe(data []byte) {
	if len(data) < 8 {
		return
	}
	magic := binary.LittleEndian.Uint32(data[0:4])
	if magic != 0x554E5346 {
		return
	}
	cmd := data[4]

	if cmd == 0x99 {
		if len(data) >= 9 {
			ptr := unsafe.Pointer(&data[0])
			header := (*MetadataHeader)(ptr)
			fmt.Fprintf(os.Stderr, "[!] UNSAFE POINTER CORRUPTION HIT: ID=%d\n", header.ID)
			panic("UNSAFE_POINTER_MEMORY_CORRUPTION_SINK")
		}
	} else {
		fmt.Println("[*] Safe standard slice processing")
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
	processUnsafe(data)
}
