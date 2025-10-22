
    // Simple program to calculate 10 - 5 and store result on stack
    // Also demonstrates 32-bit operations and branching.
    
    MOV  W0, #10          // Set W0 = 10 (X0 becomes 0x0...00A)
    MOV  W1, #5           // Set W1 = 5
    SUB  SP, SP, #16      // Allocate 16 bytes on the stack
    
    // --- Comparison and Branching ---
    CMP  W0, W1           // Compare W0 and W1 (10 > 5)
    B.GT greater_than     // Branch if W0 > W1 (should be taken)
    
    // This code block should be skipped
    MOV  X2, #999         // This should not execute
    B    continue         // Unconditional branch
    
greater_than:
    SUB  X2, X0, X1       // X2 = X0 - X1 = 5
    STR  X2, [SP, #8]     // Store the result on the stack at SP+8

continue:
    LDRB W3, [SP, #11]    // Load one byte from stack into W3
                          // (This will be the 4th byte of the 64-bit value 5)
    
    RET                   // End of program
    