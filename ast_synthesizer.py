import random
import subprocess
import copy
import sys

# --- Mathematical AST Structure ---

class Node:
    pass

class Const(Node):
    def __init__(self, val):
        self.val = val
    def __str__(self):
        return str(self.val)

class Var(Node):
    def __init__(self, name):
        self.name = name
    def __str__(self):
        return self.name

class BinOp(Node):
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right
    def __str__(self):
        return f"({self.left} {self.op} {self.right})"

OPS = ['+', '-', '*']
CONSTS = [1, 2, 3, 4, 5]
VARS = ['x']

def generate_random_ast(depth=0):
    if depth > 2 or (depth > 0 and random.random() < 0.4):
        if random.random() < 0.5:
            return Const(random.choice(CONSTS))
        else:
            return Var(random.choice(VARS))
    
    op = random.choice(OPS)
    left = generate_random_ast(depth + 1)
    right = generate_random_ast(depth + 1)
    return BinOp(op, left, right)

def mutate_ast(node):
    new_node = copy.deepcopy(node)
    
    if isinstance(new_node, BinOp):
        # 30% chance to swap the operator
        if random.random() < 0.3:
            new_node.op = random.choice(OPS)
        
        # Randomly descend into left or right child to mutate
        if random.random() < 0.5:
            new_node.left = mutate_ast(new_node.left)
        else:
            new_node.right = mutate_ast(new_node.right)
        return new_node
    else:
        # 20% chance to completely replace a leaf node
        if random.random() < 0.2:
            return generate_random_ast(depth=2)
        
        # 50% chance to swap variables and constants
        if random.random() < 0.5:
            if isinstance(new_node, Const):
                return Const(random.choice(CONSTS))
            else:
                return Const(random.choice(CONSTS)) # Swap var for const sometimes
        return new_node


# --- The Compiler & Monitor Engine ---

def build_c_code(expr_str):
    return f"""#include <stdio.h>
#include <stdlib.h>

// SYNTHESIZED TARGET FUNCTION
int target_function(int x) {{
    return {expr_str};
}}

int main(int argc, char** argv) {{
    if (argc < 2) return 1;
    int x = atoi(argv[1]);
    printf("%d\\n", target_function(x));
    return 0;
}}
"""

def compile_and_run(expr_str, x_val):
    c_code = build_c_code(expr_str)
    with open("synth_target.c", "w") as f:
        f.write(c_code)
    
    # Compile
    res = subprocess.run(["gcc", "synth_target.c", "-o", "synth_target"], capture_output=True)
    if res.returncode != 0:
        return None # Compilation failed
        
    # Run binary
    res = subprocess.run(["./synth_target", str(x_val)], capture_output=True, text=True)
    try:
        return int(res.stdout.strip())
    except:
        return None


# --- The Formal Specification (Goal) ---
# We want the engine to write: f(x) = x * 2 + 5
TEST_CASES = [
    (10, 25), 
    (3, 11),  
    (0, 5)    
]

def evaluate_fitness(ast_node):
    expr_str = str(ast_node)
    total_distance = 0
    for x_val, target_val in TEST_CASES:
        output = compile_and_run(expr_str, x_val)
        if output is None:
            return 999999 # Invalid code penalty
        
        # Mathematical distance from perfection
        distance = abs(output - target_val)
        total_distance += distance
        
    return total_distance


# --- The Evolutionary Loop ---

def main():
    print("[*] Initializing Deterministic AST Synthesizer...")
    print("[*] Target Specification: f(10)=25, f(3)=11, f(0)=5")
    
    population_size = 50
    generations = 500
    
    # Generate initial random sequences
    population = [generate_random_ast() for _ in range(population_size)]
    
    for gen in range(generations):
        # Score the population
        scored_population = []
        for ast in population:
            score = evaluate_fitness(ast)
            scored_population.append((score, ast))
            
        # Sort by distance to target (0 is perfect)
        scored_population.sort(key=lambda x: x[0])
        best_score, best_ast = scored_population[0]
        
        if gen % 10 == 0 or best_score == 0:
            print(f"Gen {gen:03d} | Best Distance: {best_score:04d} | Current Best C Code: return {best_ast};")
            
        # Mathematical Perfection Achieved
        if best_score == 0:
            print("\n[+] SYNTHESIS COMPLETE. PERFECT C SEQUENCE FOUND.")
            print("==================================================")
            print(build_c_code(str(best_ast)))
            print("==================================================")
            break
            
        # Evolution: Keep top 20%, mutate the rest
        next_population = [ast for score, ast in scored_population[:10]]
        
        while len(next_population) < population_size:
            parent = random.choice(scored_population[:10])[1]
            child = mutate_ast(parent)
            next_population.append(child)
            
        population = next_population
        
    if best_score != 0:
        print("[-] Synthesis failed to find perfect mathematical sequence in given generations.")

if __name__ == "__main__":
    main()
