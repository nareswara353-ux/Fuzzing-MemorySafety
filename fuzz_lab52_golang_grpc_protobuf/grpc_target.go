package main

import (
	"encoding/binary"
	"fmt"
	"os"
)

func parseProtoStream(data []byte) {
	if len(data) < 9 {
		return
	}

	msgLen := binary.BigEndian.Uint32(data[1:5])
	if int(msgLen)+5 > len(data) {
		return
	}

	body := data[5 : 5+msgLen]
	if len(body) < 4 {
		return
	}

	magic := binary.LittleEndian.Uint32(body[0:4])
	if magic != 0x50525442 {
		return
	}

	if len(body) >= 5 && body[4] == 0xDF {
		fmt.Fprintf(os.Stderr, "[!] GRPC PROTOBUF DESERIALIZATION PANIC HIT\n")
		panic("PROTOBUF_DESERIALIZATION_SINK_PANIC")
	}

	fmt.Println("[*] Valid gRPC protobuf stream parsed successfully")
}

func main() {
	if len(os.Args) < 2 {
		os.Exit(1)
	}
	data, err := os.ReadFile(os.Args[1])
	if err != nil || len(data) > 8192 {
		os.Exit(1)
	}
	parseProtoStream(data)
}
