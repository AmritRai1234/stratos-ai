from z3 import *
import subprocess

def main():
    print("[*] Initializing Mathematical Symbolic Execution Engine (Z3)")
    print("[*] Target: ./vault binary")
    print("[*] Mapping C state constraints to algebraic symbols...")
    
    # Define our abstract mathematical symbols (32-bit unsigned integers)
    k1 = BitVec('k1', 32)
    k2 = BitVec('k2', 32)
    k3 = BitVec('k3', 32)
    
    # Initialize the Theorem Prover
    solver = Solver()
    
    # We copy the C code logic directly into Z3 constraints
    # Stage 1: Algebraic constraint
    solver.add((k1 * 3 + k2) == 9380)
    
    # Stage 2: Bitwise shifts and XOR operations
    solver.add(((k2 << 4) ^ k3) == 82388)
    
    # Stage 3: Inter-variable XOR dependencies
    solver.add((k1 ^ k3) + k2 == 15892)
    
    # Stage 4: Modulo arithmetic
    solver.add(k3 % 1337 == 990)
    
    print("[*] Constraints mathematically modeled. Engaging Z3 Prover...")
    
    # Ask the mathematical prover to solve the algebraic system
    if solver.check() == sat:
        model = solver.model()
        print("[+] MATHEMATICAL PROOF SUCCESSFUL!")
        
        # Extract the exact integer values
        val_k1 = model[k1].as_long()
        val_k2 = model[k2].as_long()
        val_k3 = model[k3].as_long()
        
        print(f"[*] Deduced Sequence: {val_k1} {val_k2} {val_k3}")
        print("[*] Verifying against the actual compiled C binary...")
        print("--------------------------------------------------")
        
        res = subprocess.run(["./vault", str(val_k1), str(val_k2), str(val_k3)], capture_output=True, text=True)
        print(res.stdout.strip())
        print("--------------------------------------------------")
    else:
        print("[-] The Z3 Prover determined that no mathematical solution exists.")

if __name__ == "__main__":
    main()
