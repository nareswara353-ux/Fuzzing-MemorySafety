package main

/*
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

void process_cgo_buffer(const char *data, int len) {
    if (len < 8) return;
    unsigned int magic = *(unsigned int *)data;
    if (magic != 0x43474F21) return;

    unsigned char cmd = (unsigned char)data[4];
    if (cmd == 0xCC) {
        fprintf(stderr, "[!] CGO MEMORY CORRUPTION CRASH HIT\n");
        abort();
    }
}
*/
import "C"
import (
	"fmt"
	"os"
	"unsafe"
)

func main() {
	if len(os.Args) < 2 {
		os.Exit(1)
	}
	data, err := os.ReadFile(os.Args[1])
	if err != nil || len(data) > 4096 {
		os.Exit(1)
	}
	if len(data) >= 8 {
		cPtr := C.CBytes(data)
		defer C.free(cPtr)
		C.process_cgo_buffer((*C.char)(cPtr), C.int(len(data)))
	}
	fmt.Println("[*] Cgo processed safely")
}
