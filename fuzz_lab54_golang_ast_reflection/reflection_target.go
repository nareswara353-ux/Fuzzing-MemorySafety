package main

import (
	"encoding/binary"
	"fmt"
	"os"
	"reflect"
	"strings"
)

type AdminService struct{}

func (a *AdminService) SafeOp() string {
	return "SAFE_OP_SUCCESS"
}

func (a *AdminService) DangerousSink() string {
	panic("INSECURE_REFLECTION_EXECUTION_SINK")
}

func processReflection(data []byte) {
	if len(data) < 6 {
		return
	}
	magic := binary.LittleEndian.Uint32(data[0:4])
	if magic != 0x5245464C {
		return
	}
	methodLen := int(data[4])
	if len(data) < 5+methodLen {
		return
	}
	methodName := string(data[5 : 5+methodLen])

	service := &AdminService{}
	val := reflect.ValueOf(service)
	method := val.MethodByName(methodName)

	if !method.IsValid() {
		return
	}

	if strings.Contains(methodName, "Dangerous") {
		fmt.Fprintf(os.Stderr, "[!] INSECURE REFLECTION METHOD INVOKED: %s\n", methodName)
	}
	_ = method.Call(nil)
}

func main() {
	if len(os.Args) < 2 {
		os.Exit(1)
	}
	data, err := os.ReadFile(os.Args[1])
	if err != nil || len(data) > 4096 {
		os.Exit(1)
	}
	processReflection(data)
}
