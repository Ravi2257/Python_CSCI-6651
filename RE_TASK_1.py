# Here I am creating a Python script to read an ARM64 assembly file and 
# parse each line to extract the instruction and its operands.

# Here I am defining a function to parse each line of the assembly file.


def parse_arm64_line(line, line_number):

    line = line.strip()
    if not line:
        return

    # We are using split to separate the instruction from the operands.
    parts = line.split(maxsplit=1)
    instruction = parts[0]
    operands = []

    if len(parts) > 1:
        # Split operands by comma, but keep brackets intact
        raw_operands = parts[1].split(",")
        # Clean spaces
        operands = [op.strip() for op in raw_operands]

    # We are going to Print the result

    print("-" * 80)
    print(f"Instruction #{line_number}:")
    print("-" * 80)
    print(f"Instruction: {instruction}")

    for i, op in enumerate(operands, start=1):
        if op.startswith("[") and op.endswith("]"):
            # Here we are handling memory access operands
            inner = op[1:-1].strip()
            # For Example: SP, 0x08 → "SP + 0x08"
            formatted = inner.replace(",", " +")
            print(f"Operand #{i}: {op} --> {formatted}")
        elif op.startswith("#"):
            # Here we are handling immediate values
            print(f"Operand #{i}: {op} --> Immediate value {op[1:]}")
        else:
            print(f"Operand #{i}: {op}")
    print()


# Here I am defining a function to read the assembly file and parse each line using the above function.

def parse_file(filename):
    # Open and read file line by line
    with open(filename, "r") as f:
        for line_number, line in enumerate(f, start=1):
            parse_arm64_line(line, line_number)


# Here I am calling the parse_file function with the path of the assembly file.

if __name__ == "__main__":
    parse_file("Assembly.asm")



