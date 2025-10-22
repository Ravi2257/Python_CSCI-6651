MOV  W0, #5
MOV  W1, #0
B    check
loop:
    ADD  W1, W1, W0
    SUB  W0, W0, #1
check:
    CMP  W0, #0
    B.GT loop
RET