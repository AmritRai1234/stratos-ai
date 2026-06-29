#include <iostream>
#include <sys/sysinfo.h>
#include <cstdlib>
#include <string>

using namespace std;

int main() {
    cout << "[*] Stratos Native Hardware Router Initialized.\n";

    // 1. Probe RAM
    struct sysinfo memInfo;
    sysinfo(&memInfo);
    long long totalPhysMem = memInfo.totalram;
    totalPhysMem *= memInfo.mem_unit;
    double ram_gb = (double)totalPhysMem / (1024 * 1024 * 1024);

    cout << "[+] Physical RAM Detected: " << ram_gb << " GB\n";

    // 2. Define Paths (Global Installation)
    string model_path = "/home/amrit/.local/home/amrit/.local/opt/stratos/models/gemma-4-E4B-it-Q4_K_M.gguf";
    string engine_bin = "/home/amrit/.local/home/amrit/.local/opt/stratos/bin/llama-cli";

    // 3. Dynamic Optimization Logic
    string flags = "-m " + model_path + " -cnv -c 4096";

    if (ram_gb < 10.0) {
        cout << "[!] HARDWARE PROFILE: CONSTRAINED\n";
        cout << "[-] Injecting 8-bit KV-Cache Quantization...\n";
        flags += " -ctk q8_0 -ctv q8_0 --mmap";
    }

    // 4. Vulkan GPU Offloading
    // We assume the binary was compiled with GGML_VULKAN=1
    // -ngl 99 forces all layers to the GPU if available.
    cout << "[-] Engaging Vulkan API Engine...\n";
    flags += " -ngl 99";

    cout << "======================================================\n";
    cout << "[+] LAUNCHING STRATOS INFERENCE ENGINE (VULKAN EDITION)\n";
    cout << "======================================================\n";

    string command = engine_bin + " " + flags;
    int status = system(command.c_str());

    return status;
}
