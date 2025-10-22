class ARM64Registers:
    def __init__(reg): 
        # Here we are creating general purpose registers X0 - X30
        reg.registers = {f"X{i}": 0 for i in range(31)}

        # Here we are creating special registers
        reg.registers["XZR"] = 0  # The Zero register which always reads as 0, writes are ignored
        reg.registers["SP"] = 0   # Here we are equalling Stack pointer to 0
        reg.registers["PC"] = 0   # Here we are equalling Program counter to 0

        # Here we are creating Processor State Register - N, Z flags
        reg.state = {
            "N": 0,  # This is a Negative flag
            "Z": 0   # This is a Zero flag
        }

    def wrt_register(reg, name, value):
        # Write to a register (XZR always remains 0).
        if name == "XZR":
            return  # Ignore writes to XZR as it is always 0
        if name in reg.registers:
            reg.registers[name] = value & 0xFFFFFFFFFFFFFFFF  # We are enforcing 64-bit
        else:
            raise ValueError(f"Unknown register {name}") 

    def rd_register(reg, name):
        # Read register value (XZR always 0).
        if name == "XZR":
            return 0
        return reg.registers.get(name, None) # Here we are using get to avoid KeyError

    def dis_registers(reg):
        # Here we are printing all registers and processor state.
        print("-" * 120)
        print("Registers:")
        print("-" * 120)
 
        # Print X0 - X29 in groups of 3
        for i in range(0, 30, 3):
            print(
                f"X{i}: {reg.registers[f'X{i}']:>#018x}      "
                f"X{i+1}: {reg.registers[f'X{i+1}']:>#018x}   "
                f"X{i+2}: {reg.registers[f'X{i+2}']:>#018x}  "
            )

        # Print all special registers - SP, PC, X30
        print(
            f"SP: {reg.registers['SP']:>#018x}      "
            f"PC: {reg.registers['PC']:>#018x}      "
            f"X30: {reg.registers['X30']:>#018x}"
        )

        # Print the Processor State
        print(f"\nProcessor State N bit: {reg.state['N']}")
        print(f"Processor State Z bit: {reg.state['Z']}")


# Here we are creating an instance of the ARM64Registers class and displaying the registers.

if __name__ == "__main__":
    cpu = ARM64Registers()
    cpu.dis_registers()
