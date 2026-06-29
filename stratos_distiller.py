from huggingface_hub import hf_hub_download
from safetensors.numpy import load_file
import numpy as np
from z3 import *

print("[*] Initializing Stratos PyTorch Distiller...")

# 1. Download a Real AI Model (135 Million Parameters)
print("[*] Downloading Real AI Weights from Hugging Face...")
try:
    # We use SmolLM-135M for the proof of concept as it is a real, fast-to-download model.
    model_repo = "HuggingFaceTB/SmolLM-135M"
    file_path = hf_hub_download(repo_id=model_repo, filename="model.safetensors")
except Exception as e:
    print(f"[-] Failed to download weights: {e}")
    exit(1)

# 2. Perform Brain Surgery (Extracting a single real layer)
print("[*] Performing Brain Surgery (Extracting Layer)...")
tensors = load_file(file_path)

# Extract a real Attention Projection Layer
layer_name = "model.layers.0.self_attn.o_proj.weight"
W_real_float = tensors[layer_name]

print(f"[*] Extracted Real Layer '{layer_name}' with shape: {W_real_float.shape}")
print(f"[*] Total Parameters in this layer: {W_real_float.size}")

# 3. Micro-Refinement (Z3 scale restriction)
# Z3 scales exponentially. We isolate a 4x4 sub-block of the real neural layer to prove the formal logic mathematically.
N = 4
W_teacher = W_real_float[:N, :N].astype(np.float32)

print("\n[*] Real PyTorch Sub-Block Weights (Teacher):")
for row in W_teacher:
    print("   ", [round(float(x), 4) for x in row])

# 4. Simulate an Inference Pass
np.random.seed(42)
X_input = np.random.randn(N).astype(np.float32)
Y_target = W_teacher @ X_input

print("\n[*] Teacher Model Output (FP32) for this Activation:")
print("   ", np.round(Y_target, 4))

# 5. Formal Z3 Distillation
print("\n[*] Engaging Z3 Formal Model Distillation on Real Weights...")

alpha_float = np.mean(np.abs(W_teacher))
print(f"[*] Deduced Constant Scale Factor (Alpha): {alpha_float:.4f}")

# Z3 is fastest with Integers. Scale up floats to work with precise Integers.
SCALE = 1000
Y_target_int = (Y_target * SCALE).astype(int)
X_input_int = (X_input * SCALE).astype(int)
alpha_int = int(alpha_float * 1000)

opt = Optimize()
W_student = [[Int(f'w_{i}_{j}') for j in range(N)] for i in range(N)]

# Mathematical Constraint: All weights MUST be exactly -1, 0, or 1
for i in range(N):
    for j in range(N):
        opt.add(Or(W_student[i][j] == -1, W_student[i][j] == 0, W_student[i][j] == 1))

# Minimize Error against the Teacher's real output
errors = []
for i in range(N):
    student_dot = sum([W_student[i][j] * int(X_input_int[j]) for j in range(N)])
    y_student_scaled = (student_dot * alpha_int) / 1000
    
    err = Int(f'err_{i}')
    opt.add(If(y_student_scaled > int(Y_target_int[i]), 
               err == y_student_scaled - int(Y_target_int[i]), 
               err == int(Y_target_int[i]) - y_student_scaled))
    errors.append(err)

total_error = Int('total_error')
opt.add(total_error == sum(errors))
opt.minimize(total_error)

if opt.check() == sat:
    model = opt.model()
    print("\n[+] MATHEMATICAL REFINEMENT SUCCESSFUL!")
    
    print("[*] Synthesized 1.58-bit Ternary Weights (Student):")
    for i in range(N):
        row = [model[W_student[i][j]].as_long() for j in range(N)]
        print("   ", row)
        
    print("\n[*] Student Output vs Teacher Output:")
    for i in range(N):
        student_val = sum([model[W_student[i][j]].as_long() * X_input[j] for j in range(N)]) * alpha_float
        print(f"    Teacher (Real PyTorch): {Y_target[i]:>7.4f}  |  Student (Z3 Ternary): {student_val:>7.4f}")
else:
    print("[-] Z3 could not find a valid refinement.")
