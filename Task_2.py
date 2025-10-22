class ARM64Registers:
    """
    Represents the ARM64 register set and processor state.
    """
    def __init__(self):
        # Initialize 31 general-purpose 64-bit registers (X0-X30)
        # XZR (X31) is handled implicitly as it always reads 0.
        self.x = {f'X{i}': 0 for i in range(31)}
        
        # Initialize Stack Pointer and Program Counter
        self.sp = 0
        self.pc = 0
        
        # Simplified Processor State (PSTATE) flags
        self.n_bit = 0  # Negative flag
        self.z_bit = 0  # Zero flag

    def display(self):
        """
        Prints the current state of all registers in a formatted way.
        """
        print("-------------------------------------------------------------------------------------------------------------------------------")
        print("Registers:")
        print("-------------------------------------------------------------------------------------------------------------------------------")
        # Print registers in three columns
        for i in range(10):
            r1 = f"X{i}"
            r2 = f"X{i+10}"
            r3 = f"X{i+20}"
            # Use f-string formatting to pad hex values to 16 characters with a '0'
            print(f"{r1:<3}: 0x{self.x[r1]:016x}\t{r2:<3}: 0x{self.x[r2]:016x}\t{r3:<3}: 0x{self.x[r3]:016x}")

        # Print SP, PC, and X30 (Link Register)
        print(f"SP : 0x{self.sp:016x}\tPC : 0x{self.pc:016x}\tX30: 0x{self.x['X30']:016x}")
        
        print(f"Processor State N bit: {self.n_bit}")
        print(f"Processor State Z bit: {self.z_bit}")
        print()

# --- Execute Task 2 ---
if __name__ == '__main__':
    print("--- Running Task 2: ARM64 Registers ---")
    registers = ARM64Registers()
    registers.display()