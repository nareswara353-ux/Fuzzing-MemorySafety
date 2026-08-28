package main

/*
#include <stdlib.h>
#include <stdio.h>

void trigger_uninit_leak(int should_crash) {
    if (should_crash) {
        fprintf(stderr, "[!] MSAN UNINITIALIZED MEMORY READ SINK HIT\n");
        abort();
    }
}
*/
import "C"
import (
	"encoding/binary"
	"fmt"
	"os"
)

func processMSan(data []byte) {
	if len(data) < 8 {
		return
	}
	magic := binary.LittleEndian.Uint32(data[0:4])
	if magic != 0x4D53414E {
		return
	}
	cmd := data[4]
	if cmd == 0x77 {
		C.trigger_uninit_leak(C.int(1))
	} else {
		fmt.Println("[*] Safe initialized memory read")
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
	processMSan(data)
}
