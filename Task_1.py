import re

def parse_arm64_instruction(line):
    """
    Parses a single line of ARM64 assembly into an instruction and its operands.
    """
    # Remove comments (from // or # to end of line) and strip whitespace
    line = re.sub(r'(//|#).*', '', line).strip()
    if not line:
        return None, []

    # Split the instruction mnemonic from the rest of the line
    parts = line.split(maxsplit=1)
    instruction = parts[0].upper()
    
    operands = []
    if len(parts) > 1:
        # Split operands by comma, and strip whitespace from each
        operands = [op.strip() for op in parts[1].split(',')]
        
    return instruction, operands

def run_parser(filename):
    """
    Reads an assembly file, parses each line, and prints the result.
    """

    print("--- Running Task 1: ARM64 Assembly Parser ---")
    try:
        with open(filename, "r") as f:
            for line_num, line in enumerate(f, 1):
                instruction, operands = parse_arm64_instruction(line)
                
                # If the line was empty or just a comment, skip it
                if not instruction:
                    continue

                print("-------------------------------------------------------------------------------------------------------------------------------")
                print(f"Instruction #{line_num}:")
                print("-------------------------------------------------------------------------------------------------------------------------------")
                print(f"Instruction: {instruction}")
                for i, operand in enumerate(operands, 1):
                    # Special formatting for memory operands for clarity
                    if operand.startswith('[') and operand.endswith(']'):
                         mem_parts = operand.strip('[]').split(',')
                         base_reg = mem_parts[0].strip()
                         offset = mem_parts[1].strip().lstrip('#')
                         print(f"Operand #{i}: {operand} --> {base_reg} + {offset}")
                    else:
                        print(f"Operand #{i}: {operand}")
                print() # Add a blank line for readability

    except FileNotFoundError:
        print(f"Error: Input file '{filename}' not found.")

# --- Execute Task 1 ---
if __name__ == '__main__':
    run_parser("Assembly.asm")