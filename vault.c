#include <stdio.h>
#include <stdlib.h>

// A highly complex mathematical state machine (The Vault)
// It takes 3 unsigned 32-bit integers as the key.
int check_vault_key(unsigned int k1, unsigned int k2, unsigned int k3) {
    // Stage 1: Algebraic constraint
    if ((k1 * 3 + k2) != 9380) return 0;
    
    // Stage 2: Bitwise shifts and XOR operations
    if (((k2 << 4) ^ k3) != 82388) return 0;
    
    // Stage 3: Inter-variable XOR dependencies
    if ((k1 ^ k3) + k2 != 15892) return 0;
    
    // Stage 4: Modulo arithmetic
    if (k3 % 1337 != 990) return 0;

    return 1; // ACCESS GRANTED
}

int main(int argc, char** argv) {
    if (argc < 4) {
        printf("Usage: ./vault <key1> <key2> <key3>\n");
        return 1;
    }
    
    unsigned int k1 = (unsigned int)strtoul(argv[1], NULL, 10);
    unsigned int k2 = (unsigned int)strtoul(argv[2], NULL, 10);
    unsigned int k3 = (unsigned int)strtoul(argv[3], NULL, 10);
    
    printf("[*] Checking keys: %u, %u, %u...\n", k1, k2, k3);
    
    if (check_vault_key(k1, k2, k3)) {
        printf("[+] ACCESS GRANTED. Welcome to the Vault.\n");
    } else {
        printf("[-] ACCESS DENIED. Invalid mathematical sequence.\n");
    }
    
    return 0;
}
