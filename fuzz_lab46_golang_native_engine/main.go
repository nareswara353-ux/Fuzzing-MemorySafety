package main

import (
	"fmt"
	"os"
)

func main() {
	if len(os.Args) < 2 {
		os.Exit(1)
	}
	data, err := os.ReadFile(os.Args[1])
	if err != nil || len(data) > 4096 {
		os.Exit(1)
	}
	if err := ParsePayload(data); err != nil {
		os.Exit(0)
	}
	fmt.Println("[*] Go payload processed safely")
}
