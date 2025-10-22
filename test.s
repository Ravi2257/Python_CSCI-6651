// factorial.s: Calculates the factorial of 5
// Result will be in W0

start:
    MOV  W0, #1      // W0 is our result, initialize to 1
    MOV  W1, #5      // W1 is our counter, N=5

loop:
    CMP  W1, #1      // Compare counter with 1
    B.LE end_loop   // If counter <= 1, we are done

    MUL  W0, W0, W1  // result = result * counter
    SUB  W1, W1, #1  // counter = counter - 1
    B    loop        // Go to the start of the loop

end_loop:
    NOP              // Do nothing, just a place to land
    RET              // End emulation