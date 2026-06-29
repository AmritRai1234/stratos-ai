#!/bin/bash

echo "[*] Initializing Stratos OS Intelligent Memory Launcher..."

# 1. Hardware Probe
TOTAL_RAM_MB=$(free -m | awk '/^Mem:/{print $2}')
echo "[+] Detected Physical RAM: ${TOTAL_RAM_MB} MB"

# 2. Define Core LLM Arguments
MODEL_PATH="/home/amrit/models/qwen2.5-14b-instruct-q2_k-00001-of-00002.gguf"
INFERENCE_BIN="/home/amrit/apps/stratos_inference/build/bin/llama-cli"
CONTEXT_SIZE=1024

# Base flags: Conversational mode, fixed context size
FLAGS="-m $MODEL_PATH -cnv -c $CONTEXT_SIZE"

# 3. Dynamic Optimization Logic
if [ "$TOTAL_RAM_MB" -lt 10000 ]; then
    echo "[!] HARDWARE PROFILE: CONSTRAINED (< 10GB RAM)"
    echo "[-] Activating Extreme Memory Optimizations..."
    # Warning: Flash Attention (-fa) is currently unstable when combined with KV Quantization on CPU. Disabled to prevent segfaults.
    # FLAGS="$FLAGS -fa on"
    
    # Crush KV Cache to 8-bit (from 16-bit float)
    FLAGS="$FLAGS -ctk q8_0 -ctv q8_0"
    echo "    -> Crushed KV-Cache to 8-bit Integer (-ctk q8_0 -ctv q8_0)"
    
    # Ensure memory mapping is enabled for zero-copy paging
    FLAGS="$FLAGS --mmap"
    echo "    -> Forced MMAP Storage to bypass RAM bottlenecks"
else
    echo "[!] HARDWARE PROFILE: HIGH-END"
    echo "[-] Activating Standard Optimizations..."
    FLAGS="$FLAGS -fa"
fi

echo "======================================================"
echo "[+] LAUNCHING STRATOS INFERENCE ENGINE"
echo "======================================================"

# Execute the engine
$INFERENCE_BIN $FLAGS
