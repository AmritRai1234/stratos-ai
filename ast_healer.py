import subprocess
import re
import sys
import clang.cindex

C_FILE = "target.c"
BIN_FILE = "./target"

def write_c_file():
    code = """#include <stdio.h>

int process_data(int total, int items) {
    // A more complex mathematical vulnerability here
    return total / (items - 5);
}

int main() {
    printf("Starting data processing...\\n");
    // Trying to process 100 total, which triggers items - 5 == 0
    int result = process_data(100, 5);
    printf("Result: %d\\n", result);
    return 0;
}
"""
    with open(C_FILE, "w") as f:
        f.write(code)

def compile_c():
    # Use Undefined Behavior Sanitizer (UBSan) to precisely locate mathematical errors at runtime
    res = subprocess.run(["gcc", "-g", "-fsanitize=undefined", C_FILE, "-o", BIN_FILE], capture_output=True, text=True)
    return res.returncode == 0

def run_c():
    res = subprocess.run([BIN_FILE], capture_output=True, text=True)
    return res.returncode, res.stdout, res.stderr

def find_denominator_in_ast(cursor, target_line):
    # Recursively find the binary operator at the target line
    if cursor.location.line == target_line and cursor.kind == clang.cindex.CursorKind.BINARY_OPERATOR:
        # Check if it's a division by inspecting the tokens
        tokens = list(cursor.get_tokens())
        operator_token = None
        # In a binary operator, we look for the '/' token
        for t in tokens:
            if t.spelling == '/':
                operator_token = t
                break
        
        if operator_token:
            children = list(cursor.get_children())
            if len(children) == 2:
                rhs = children[1]
                # Extract the exact textual representation of the RHS (the denominator)
                # It can be a complex expression like '(items - 5)'
                rhs_text = " ".join([t.spelling for t in rhs.get_tokens()])
                return rhs_text
                
    for c in cursor.get_children():
        res = find_denominator_in_ast(c, target_line)
        if res: return res
    return None

def heal_c_ast(stderr_log):
    # 1. Parse the machine output to find the exact mathematical point of failure
    match = re.search(r'target\.c:(\d+):(\d+): runtime error: division by zero', stderr_log)
    if not match:
        return False
        
    line_num = int(match.group(1))
    
    print("[*] Engaging true Clang AST Parser (libclang)...")
    index = clang.cindex.Index.create()
    tu = index.parse(C_FILE)
    
    # 2. Traverse the mathematical AST to extract the exact denominator causing the crash
    denominator = find_denominator_in_ast(tu.cursor, line_num)
    
    if denominator:
        print(f"[*] AST Analysis: Exact denominator structure extracted -> '{denominator}'")
        print(f"[*] Logic Injection: Synthesizing strict mathematical boundary")
        
        # 3. Deterministic Mutation: Safely inject the boundary check
        with open(C_FILE, "r") as f:
            lines = f.readlines()
            
        fixed_code = f"    if ( ({denominator}) == 0 ) return 0; // DETERMINISTIC AST BOUNDS INJECTION\n{lines[line_num - 1]}"
        lines[line_num - 1] = fixed_code
        
        with open(C_FILE, "w") as f:
            f.writelines(lines)
        return True
        
    return False

def main():
    print("[*] Initializing libclang AST Healer Engine...")
    write_c_file()
    
    max_attempts = 3
    for attempt in range(1, max_attempts + 1):
        print(f"\n--- AST Mutation Cycle {attempt} ---")
        if not compile_c():
            print("[-] Compilation failed!")
            break
            
        print("[*] Executing binary...")
        code, stdout, stderr = run_c()
        
        # Check if UBSan threw a runtime error
        if code == 0 and "runtime error" not in stderr:
            print("[+] Execution successful! Precise mathematical state achieved.")
            print("Output:\n" + stdout.strip())
            break
        else:
            print("[-] Error detected in machine state:")
            # Extract the precise error line
            error_line = [line for line in stderr.split('\n') if 'runtime error' in line]
            if error_line:
                print("    " + error_line[0])
            else:
                print("    " + stderr.strip())
            
            if heal_c_ast(stderr):
                print("[+] C source code mathematically mutated and healed. Recompiling...")
            else:
                print("[-] Could not parse AST for healing.")
                break

if __name__ == "__main__":
    main()
