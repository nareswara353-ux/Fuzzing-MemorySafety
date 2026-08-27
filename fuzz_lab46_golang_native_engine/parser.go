package main

import (
	"encoding/binary"
	"errors"
)

var (
	ErrTooShort     = errors.New("input too short")
	ErrInvalidMagic = errors.New("invalid magic")
)

func ParsePayload(data []byte) error {
	if len(data) < 8 {
		return ErrTooShort
	}
	magic := binary.LittleEndian.Uint32(data[0:4])
	if magic != 0x474F4C47 {
		return ErrInvalidMagic
	}
	cmd := data[4]
	if cmd == 0xAA && len(data) >= 12 && string(data[5:12]) == "PANICGO" {
		panic("GOLANG_NATIVE_FUZZ_SINK_PANIC")
	}
	return nil
}
