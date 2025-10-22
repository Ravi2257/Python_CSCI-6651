# Combining previous concepts. Ensure ARM64Registers class is defined or imported.
# For simplicity, I'll redefine the necessary class here.

from Task_1 import parse_arm64_instruction


import re


class ARM64Registers:
    """Represents the ARM64 register set."""
    def __init__(self):
        self.x = {f'X{i}': 0 for i in range(31)}
        self.sp = 0
        self.pc = 0
        self.n_bit = 0
        self.z_bit = 0
    
    def get_pc(self):
        return self.pc

    def increment_pc(self, value=4):
        """Increments the Program Counter by a fixed value (default 4 bytes)."""
        self.pc += value


def run_parser_with_pc(filename="Assembly.asm"):
    """
    Reads an assembly file, parses each line, and prints the result while tracking the PC.
    """
    # Instantiate the registers
    registers = ARM64Registers()

    print("--- Running Task 4: Parser with PC Integration ---")
    try:
        with open(filename, "r") as f:
            lines = f.readlines() # Read all lines to associate line number with instruction
            
            # While the PC is within the bounds of our "program"
            while (registers.get_pc() // 4) < len(lines):
                current_pc = registers.get_pc()
                line_index = current_pc // 4
                line = lines[line_index]
                
                instruction, operands = parse_arm64_instruction(line)

                # Move PC to the next instruction before processing this one
                registers.increment_pc()
                
                if not instruction:
                    continue

                print("-------------------------------------------------------------------------------------------------------------------------------")
                # Line number is index + 1, PC is the address of this instruction
                print(f"Instruction #{line_index + 1} @ PC=0x{current_pc:04x}:")
                print("-------------------------------------------------------------------------------------------------------------------------------")
                print(f"Instruction: {instruction}")
                for i, operand in enumerate(operands, 1):
                    print(f"Operand #{i}: {operand}")
                print()

    except FileNotFoundError:
        print(f"Error: Input file '{filename}' not found.")
    except IndexError:
        print("Reached end of file.")

# --- Execute Task 4 ---
if __name__ == '__main__':
    # You can comment out the other task executions if you want to run only this one.
    # We assume sample.s was created by the first task's code.
    run_parser_with_pc()