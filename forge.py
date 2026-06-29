from safetensors.numpy import load_file
import numpy as np
import os

print("[*] Initializing Stratos Forge (Python -> C++ Distiller)...")

from huggingface_hub import hf_hub_download

model_repo = "HuggingFaceTB/SmolLM-135M"
model_path = hf_hub_download(repo_id=model_repo, filename="model.safetensors")

print("[*] Loading Real AI Weights from Disk...")
tensors = load_file(model_path)

# Extract a real Attention Projection Layer
layer_name = "model.layers.0.self_attn.o_proj.weight"
W_real = tensors[layer_name].astype(np.float32)

print(f"[*] Extracted Real Layer '{layer_name}' with shape: {W_real.shape}")
N_rows, N_cols = W_real.shape

# 1. Mathematical Quantization (1.58-bit Ternary) based on Z3 logic
print("[*] Applying Mathematical Ternary Quantization (-1, 0, 1)...")
alpha = np.mean(np.abs(W_real))
threshold = alpha * 0.5 # Standard 1.58-bit constraint threshold

# Vectorized quantization for massive speed
W_ternary = np.zeros_like(W_real, dtype=np.int8)
W_ternary[W_real > threshold] = 1
W_ternary[W_real < -threshold] = -1

print(f"[*] Scale Factor (Alpha): {alpha:.4f}")
nonzero_count = np.count_nonzero(W_ternary)
sparsity = 100.0 * (1.0 - (nonzero_count / float(W_ternary.size)))
print(f"[*] Sparsity Achieved: {sparsity:.2f}% of weights mathematically eliminated (0)! ")

# 2. Binary Export for C++ AVX2 Engine
bin_path = "weights.bin"
print(f"[*] Packing {W_ternary.size} Ternary Weights to raw C++ Binary: {bin_path}")
W_ternary.tofile(bin_path)

print("[+] FORGE COMPLETE! Ready for C++ Execution.")
