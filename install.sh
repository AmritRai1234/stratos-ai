#!/bin/bash

echo "[*] Initializing Stratos OS Global Installer..."

# Define installation directories
STRATOS_OPT="$HOME/.local/opt/stratos"
STRATOS_BIN="$HOME/.local/bin"

mkdir -p "$STRATOS_OPT/bin"
mkdir -p "$STRATOS_OPT/models"
mkdir -p "$STRATOS_BIN"

echo "[-] Copying Vulkan-Accelerated Inference Engine binaries..."
cp -r /tmp/llama-vulkan/llama-b9842/* "$STRATOS_OPT/bin/"

echo "[-] Moving 14-Billion Parameter Brain to Vault..."
mv ~/models/*.gguf "$STRATOS_OPT/models/"

echo "[-] Compiling Stratos Native C++ Router..."
# Update the hardcoded path in router to point to local opt just in case
sed -i "s|/opt/stratos/|$STRATOS_OPT/|g" /home/amrit/apps/reserch/stratos_router.cpp

g++ -O3 /home/amrit/apps/reserch/stratos_router.cpp -o "$STRATOS_BIN/stratos-ai"

echo "======================================================"
echo "[+] INSTALLATION COMPLETE!"
echo "[+] You can now launch the engine anytime by typing: stratos-ai"
echo "======================================================"
