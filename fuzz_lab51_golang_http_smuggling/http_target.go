package main

import (
	"bufio"
	"bytes"
	"fmt"
	"net/http"
	"os"
	"strings"
)

func evaluateHTTPRequest(data []byte) {
	if len(data) < 16 {
		return
	}

	raw := string(data)
	if strings.Contains(raw, "Transfer-Encoding: chunked") && strings.Contains(raw, "Content-Length:") {
		if strings.Contains(raw, "SMUGGLED_ADMIN_ACTION") {
			fmt.Fprintf(os.Stderr, "[!] HTTP REQUEST SMUGGLING DESYNC HIT\n")
			panic("HTTP_REQUEST_SMUGGLING_DETECTED")
		}
	}

	reader := bufio.NewReader(bytes.NewReader(data))
	req, err := http.ReadRequest(reader)
	if err != nil {
		return
	}

	fmt.Printf("[*] Valid HTTP request parsed: Method=%s Path=%s\n", req.Method, req.URL.Path)
}

func main() {
	if len(os.Args) < 2 {
		os.Exit(1)
	}
	data, err := os.ReadFile(os.Args[1])
	if err != nil || len(data) > 8192 {
		os.Exit(1)
	}
	evaluateHTTPRequest(data)
}
