package main

import (
	"encoding/binary"
	"fmt"
	"os"
	"sync"
)

func processRace(data []byte) {
	if len(data) < 8 {
		return
	}
	magic := binary.LittleEndian.Uint32(data[0:4])
	if magic != 0x52414345 {
		return
	}
	cmd := data[4]
	if cmd == 0x77 {
		var counter int
		var wg sync.WaitGroup
		for g := 0; g < 4; g++ {
			wg.Add(1)
			go func() {
				defer wg.Done()
				for i := 0; i < 500; i++ {
					counter++
				}
			}()
		}
		wg.Wait()
		fmt.Fprintf(os.Stderr, "[!] GOROUTINE DATA RACE DETECTED\n")
		panic("GOROUTINE_RACE_CONDITION_SINK")
	} else {
		fmt.Println("[*] Safe sequential execution")
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
	processRace(data)
}
