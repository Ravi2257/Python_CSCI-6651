
    MOV  X0, #100
    MOV  X1, #42
    ADD  X2, X0, X1
    SUB  X3, X0, X1
    MUL  X4, X0, X1
    MOV  W5, #0xFF00FF00
    MOV  W6, #0x00FFFF00
    AND  W7, W5, W6
    EOR  W8, W5, W6
    RET
    