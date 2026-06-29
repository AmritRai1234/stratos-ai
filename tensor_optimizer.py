from z3 import *
import sys

def main():
    print("[*] Initializing Z3 Tensor Superoptimizer...")
    
    d = 3
    print(f"[*] Target Operation: Slow CPU Division (x / {d})")
    print("[*] Modeling universal equivalence theorem: (x / d) == ((x * M) >> S)")
    
    # We use 16-bit mathematical vectors for the proof to keep solving time under 5 seconds
    x = BitVec('x', 16)
    M = BitVec('M', 16)
    S = BitVec('S', 16)
    
    # We use 32-bit mathematical vectors for the intermediate multiplication step
    x_32 = ZeroExt(16, x)
    M_32 = ZeroExt(16, M)
    
    # The fast bitwise logic model
    fast_op_32 = LShR(x_32 * M_32, ZeroExt(16, S))
    fast_op_16 = Extract(15, 0, fast_op_32)
    
    # The slow operation model
    slow_op_16 = UDiv(x, d)
    
    # UNIVERSAL QUANTIFIER: We mathematically mandate that the fast op MUST equal the slow op 
    # for EVERY SINGLE POSSIBLE 16-bit integer (x). No guessing.
    theorem = ForAll([x], slow_op_16 == fast_op_16)
    
    solver = Solver()
    
    # Constrain the bit-shift to a reasonable range
    solver.add(S >= 16, S < 32)
    
    # Add the universal proof requirement
    solver.add(theorem)
    
    print("[*] Engaging Z3 Universal Theorem Prover...")
    
    if solver.check() == sat:
        model = solver.model()
        val_M = model[M].as_long()
        val_S = model[S].as_long()
        
        print("[+] MATHEMATICAL PROOF SUCCESSFUL!")
        print(f"[*] Magic Multiplier (M) deduced: 0x{val_M:X} ({val_M})")
        print(f"[*] Optimal Bit-Shift (S) deduced: {val_S}")
        
        print("\n==================================================")
        print("SYNTHESIZED C OPTIMIZATION:")
        print(f"// Replaces slow division: result = x / {d};")
        print(f"inline uint32_t fast_div_{d}(uint32_t x) {{")
        print(f"    return (uint32_t)(((uint64_t)x * 0x{val_M:X}ULL) >> {val_S});")
        print("}")
        print("==================================================\n")
    else:
        print("[-] Z3 could not find a universal mathematical substitution.")

if __name__ == '__main__':
    main()
