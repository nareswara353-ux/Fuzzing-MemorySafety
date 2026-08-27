package main

import "testing"

func FuzzParsePayload(f *testing.F) {
	f.Add([]byte{0x47, 0x4F, 0x4C, 0x47, 0x01, 0x00, 0x00, 0x00})
	f.Fuzz(func(t *testing.T, data []byte) {
		_ = ParsePayload(data)
	})
}
