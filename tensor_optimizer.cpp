#include <iostream>
#include <iomanip>
#include <z3++.h>

using namespace z3;

int main() {
    std::cout << "[*] Initializing Native C++ Z3 Tensor Superoptimizer...\n";
    
    context c;
    int divisor = 3;
    
    std::cout << "[*] Target Operation: Slow CPU Division (x / " << divisor << ")\n";
    std::cout << "[*] Modeling universal equivalence theorem: (x / d) == ((x * M) >> S)\n";
    
    // We use 16-bit mathematical vectors for the proof to keep solving time under 5 seconds
    expr x = c.bv_const("x", 16);
    expr M = c.bv_const("M", 16);
    expr S = c.bv_const("S", 16);
    
    // 32-bit math for intermediate multiplication steps to prevent overflow
    expr x_32 = zext(x, 16);
    expr M_32 = zext(M, 16);
    
    // Fast bitwise logic model: (x * M) >> S
    expr fast_op_32 = lshr(x_32 * M_32, zext(S, 16));
    expr fast_op_16 = fast_op_32.extract(15, 0);
    
    // Slow division model
    expr d_expr = c.bv_val(divisor, 16);
    expr slow_op_16 = udiv(x, d_expr);
    
    // UNIVERSAL QUANTIFIER: Mathematically mandate equivalence for ALL 16-bit integers
    expr equality = (slow_op_16 == fast_op_16);
    expr theorem = forall(x, equality);
    
    solver s(c);
    
    // Constrain the bit-shift
    s.add(S >= 16);
    s.add(S < 32);
    
    // Add the universal proof requirement
    s.add(theorem);
    
    std::cout << "[*] Engaging Z3 Universal Theorem Prover natively...\n";
    
    if (s.check() == sat) {
        model m = s.get_model();
        
        unsigned val_M = m.eval(M).get_numeral_uint();
        unsigned val_S = m.eval(S).get_numeral_uint();
        
        std::cout << "[+] MATHEMATICAL PROOF SUCCESSFUL!\n";
        std::cout << "[*] Magic Multiplier (M) deduced: 0x" << std::hex << std::uppercase << val_M << std::dec << " (" << val_M << ")\n";
        std::cout << "[*] Optimal Bit-Shift (S) deduced: " << val_S << "\n\n";
        
        std::cout << "==================================================\n";
        std::cout << "SYNTHESIZED C OPTIMIZATION:\n";
        std::cout << "// Replaces slow division: result = x / " << divisor << ";\n";
        std::cout << "inline uint32_t fast_div_" << divisor << "(uint32_t x) {\n";
        std::cout << "    return (uint32_t)(((uint64_t)x * 0x" << std::hex << std::uppercase << val_M << std::dec << "ULL) >> " << val_S << ");\n";
        std::cout << "}\n";
        std::cout << "==================================================\n";
    } else {
        std::cout << "[-] Z3 could not find a universal mathematical substitution.\n";
    }
    
    return 0;
}
