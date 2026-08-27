package main

import (
	"encoding/binary"
	"fmt"
	"os"
)

type Worker interface {
	Execute() string
}

type HeavyTask struct {
	Tag string
}

func (h *HeavyTask) Execute() string {
	return h.Tag
}

func evaluateInterface(data []byte) {
	if len(data) < 8 {
		return
	}
	magic := binary.LittleEndian.Uint32(data[0:4])
	if magic != 0x4E494C50 {
		return
	}
	typeTag := data[4]

	var worker Worker
	if typeTag == 0x01 {
		worker = &HeavyTask{Tag: "HEALTHY_TASK"}
		fmt.Println("[*] Safe worker executed:", worker.Execute())
	} else if typeTag == 0xEE {
		var nilTask *HeavyTask = nil
		worker = nilTask
		fmt.Fprintf(os.Stderr, "[!] NIL POINTER DEREFERENCE SINK HIT\n")
		_ = worker.Execute()
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
	evaluateInterface(data)
}
