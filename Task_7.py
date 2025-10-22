import re
import struct # Used for packing/unpacking bytes for memory access

from Task_1 import parse_arm64_instruction
from Task_2 import ARM64Registers
from Task_3 import StackMemory
from Task_4 import run_parser_with_pc

class ARM64Emulator:
    """
    A simplified ARM64 emulator that combines registers, memory, and instruction execution.
    """
    def __init__(self, stack_size=256):
        # --- Registers (Task 2 & 6) ---
        self.x = {i: 0 for i in range(31)} # X0-X30 registers
        self.sp = stack_size # Stack Pointer starts at the top of the stack
        self.pc = 0 # Program Counter
        self.pstate = {'N': 0, 'Z': 1, 'C': 0, 'V': 0} # Processor State
        self.labels = {} # To store address of labels like 'loop:'
        self.emulation_finished = False

        # --- Memory (Task 3) ---
        self.stack = bytearray(stack_size)

        # --- Instruction Handlers (Task 5) ---
        self.handlers = {
            'ADD': self._handle_add, 'SUB': self._handle_sub,
            'AND': self._handle_and, 'EOR': self._handle_eor,
            'MUL': self._handle_mul, 'MOV': self._handle_mov,
            'STR': self._handle_str, 'STRB': self._handle_strb,
            'LDR': self._handle_ldr, 'LDRB': self._handle_ldrb,
            'NOP': self._handle_nop, 'B': self._handle_b,
            'B.GT': self._handle_b_gt, 'B.LE': self._handle_b_le,
            'CMP': self._handle_cmp, 'RET': self._handle_ret,
        }

    # --- Register Helper Methods (Task 6) ---
    def _get_reg_idx(self, reg_name):
        """Gets the index from a register name like 'X5' or 'W5'."""
        return int(reg_name[1:])

    def get_register(self, name):
        """Reads a value from a register (X, W, SP)."""
        name = name.upper()
        if name == 'SP':
            return self.sp
        if name.startswith('W'):
            # 32-bit read: return lower 32 bits of the corresponding X register
            return self.x[self._get_reg_idx(name)] & 0xFFFFFFFF
        elif name.startswith('X'):
            idx = self._get_reg_idx(name)
            # XZR (register 31) always reads as 0
            return self.x.get(idx, 0) if idx != 31 else 0
        return 0

    def set_register(self, name, value):
        """Writes a value to a register, handling 32-bit zero-extension."""
        name = name.upper()
        if name == 'SP':
            self.sp = value
            return
        
        idx = self._get_reg_idx(name)
        if idx == 31: return # Cannot write to XZR

        if name.startswith('W'):
            # 32-bit write: Set the lower 32 bits, and ZERO the upper 32 bits.
            self.x[idx] = value & 0xFFFFFFFF
        elif name.startswith('X'):
            # 64-bit write: mask to ensure it's a 64-bit value
            self.x[idx] = value & 0xFFFFFFFFFFFFFFFF

    # --- Operand Parsing Helper ---
    def _parse_operand(self, op):
        """Parses an operand string into its value."""
        op = op.strip()
        if op.startswith('#'): # Immediate value
            return int(op[1:], 0) # Base 0 auto-detects hex (0x) or decimal
        elif op.startswith('[') and op.endswith(']'): # Memory address
            parts = op[1:-1].split(',')
            base_reg_val = self.get_register(parts[0].strip())
            offset = int(parts[1].strip().lstrip('#'), 0) if len(parts) > 1 else 0
            return base_reg_val + offset
        else: # Register
            return self.get_register(op)

    # --- PSTATE Update Helper ---
    def _update_flags(self, result, is_64bit=True):
        """Updates N and Z flags based on a result."""
        mask = 0xFFFFFFFFFFFFFFFF if is_64bit else 0xFFFFFFFF
        result &= mask

        self.pstate['Z'] = 1 if result == 0 else 0
        
        # Check the most significant bit for negativity
        msb_pos = 63 if is_64bit else 31
        self.pstate['N'] = 1 if (result >> msb_pos) & 1 else 0
        
    # --- Instruction Handler Implementations (Task 5 & 6) ---
    def _handle_arithmetic(self, operands, op_func):
        dest, src1, src2_op = operands
        val1 = self.get_register(src1)
        val2 = self._parse_operand(src2_op)
        is_64bit = dest.upper().startswith('X')
        
        result = op_func(val1, val2)
        
        self.set_register(dest, result)
        self._update_flags(result, is_64bit)

    def _handle_add(self, operands): self._handle_arithmetic(operands, lambda a, b: a + b)
    def _handle_sub(self, operands): self._handle_arithmetic(operands, lambda a, b: a - b)
    def _handle_mul(self, operands): self._handle_arithmetic(operands, lambda a, b: a * b)
    def _handle_and(self, operands): self._handle_arithmetic(operands, lambda a, b: a & b)
    def _handle_eor(self, operands): self._handle_arithmetic(operands, lambda a, b: a ^ b)

    def _handle_mov(self, operands):
        dest, src_op = operands
        val = self._parse_operand(src_op)
        self.set_register(dest, val)
        # MOV can optionally set flags, but we'll simplify and not set them.

    def _handle_str(self, operands): # Store 64-bit register
        src_reg, mem_op = operands
        addr = self._parse_operand(mem_op)
        val = self.get_register(src_reg)
        self.stack[addr:addr+8] = struct.pack('<Q', val) # <Q is little-endian 64-bit

    def _handle_strb(self, operands): # Store byte (lower 8 bits of register)
        src_reg, mem_op = operands
        addr = self._parse_operand(mem_op)
        val = self.get_register(src_reg)
        self.stack[addr:addr+1] = struct.pack('<B', val & 0xFF) # <B is 1 byte

    def _handle_ldr(self, operands): # Load 64-bit register
        dest_reg, mem_op = operands
        addr = self._parse_operand(mem_op)
        val_bytes = self.stack[addr:addr+8]
        val = struct.unpack('<Q', val_bytes)[0]
        self.set_register(dest_reg, val)
        
    def _handle_ldrb(self, operands): # Load byte
        dest_reg, mem_op = operands
        addr = self._parse_operand(mem_op)
        val_bytes = self.stack[addr:addr+1]
        val = struct.unpack('<B', val_bytes)[0]
        self.set_register(dest_reg, val)

    def _handle_cmp(self, operands):
        reg1_name, op2 = operands
        val1 = self.get_register(reg1_name)
        val2 = self._parse_operand(op2)
        is_64bit = reg1_name.upper().startswith('X')
        result = val1 - val2 # Perform subtraction but don't store result
        self._update_flags(result, is_64bit)

    def _handle_b(self, operands):
        self.pc = self.labels[operands[0]]

    def _handle_b_gt(self, operands): # Branch if Greater Than (Z=0 and N=V)
        if self.pstate['Z'] == 0 and self.pstate['N'] == self.pstate['V']:
            self.pc = self.labels[operands[0]]

    def _handle_b_le(self, operands): # Branch if Less or Equal (Z=1 or N!=V)
        if self.pstate['Z'] == 1 or self.pstate['N'] != self.pstate['V']:
            self.pc = self.labels[operands[0]]
            
    def _handle_nop(self, operands):
        pass # Do nothing

    def _handle_ret(self, operands):
        # In a real system, this would jump to address in LR (X30)
        # For us, it's a simple way to stop the program.
        self.emulation_finished = True

    # --- Main Emulator Logic ---
    def load_program(self, filepath):
        """Loads a program, parsing lines and finding labels."""
        with open(filepath, 'r') as f:
            lines = f.readlines()
        
        # Pre-scan for labels
        current_addr = 0
        program = []
        for line in lines:
            line = re.sub(r'(//|#).*', '', line).strip() # Clean comments and whitespace
            if not line: continue
            
            if line.endswith(':'):
                self.labels[line[:-1]] = current_addr
            else:
                program.append(line)
                current_addr += 4
        return program

    def run(self, program): 
        """Executes the loaded program instruction by instruction."""
        while not self.emulation_finished and (self.pc // 4) < len(program):
            addr = self.pc
            line = program[addr // 4]
            
            self.pc += 4 # Increment PC before execution
            
            parts = line.split(maxsplit=1)
            instr = parts[0].upper()
            ops_str = parts[1] if len(parts) > 1 else ''
            
            # --- THIS IS THE FIXED LINE ---
            # It now splits only on the first comma, keeping memory operands intact.
            operands = [op.strip() for op in ops_str.split(',', 1)] if ops_str else []

            if instr in self.handlers:
                self.handlers[instr](operands)
            else:
                print(f"Error: Unknown instruction '{instr}' at address 0x{addr:x}")
                break
        print("--- Emulation Finished ---")

    def display_state(self):
        """Prints the final state of registers and stack."""
        print("--- Final Register State ---")
        for i in range(31):
            print(f"X{i:<2}: 0x{self.x[i]:016x}", end='\t' if (i+1) % 3 != 0 else '\n')
        print(f"\nSP : 0x{self.sp:016x}\tPC : 0x{self.pc:016x}")
        print(f"PSTATE: N={self.pstate['N']} Z={self.pstate['Z']}")
        
        print("\n--- Final Stack State ---")
        for i in range(0, len(self.stack), 16):
            chunk = self.stack[i:i+16]
            hex_part = ' '.join(f'{b:02x}' for b in chunk)
            ascii_part = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in chunk)
            print(f"0x{i:04x}: {hex_part:<48} |{ascii_part}|")


import re
import struct

class ARM64Emulator:
    """
    A simplified ARM64 emulator that combines registers, memory, and instruction execution.
    """
    def __init__(self, stack_size=256):
        self.x = {i: 0 for i in range(31)} # X0-X30 registers
        self.sp = stack_size
        self.pc = 0
        self.pstate = {'N': 0, 'Z': 1, 'C': 0, 'V': 0}
        self.labels = {}
        self.emulation_finished = False
        self.stack = bytearray(stack_size)

        self.handlers = {
            'ADD': self._handle_add, 'SUB': self._handle_sub,
            'AND': self._handle_and, 'EOR': self._handle_eor,
            'MUL': self._handle_mul, 'MOV': self._handle_mov,
            'STR': self._handle_str, 'STRB': self._handle_strb,
            'LDR': self._handle_ldr, 'LDRB': self._handle_ldrb,
            'NOP': self._handle_nop, 'B': self._handle_b,
            'B.GT': self._handle_b_gt, 'B.LE': self._handle_b_le,
            'CMP': self._handle_cmp, 'RET': self._handle_ret,
        }

    def _get_reg_idx(self, reg_name):
        return int(reg_name[1:])

    def get_register(self, name):
        name = name.upper()
        if name == 'SP':
            return self.sp
        if name.startswith('W'):
            return self.x[self._get_reg_idx(name)] & 0xFFFFFFFF
        elif name.startswith('X'):
            idx = self._get_reg_idx(name)
            return self.x.get(idx, 0) if idx != 31 else 0
        return 0

    def set_register(self, name, value):
        name = name.upper()
        if name == 'SP':
            self.sp = value
            return
        
        idx = self._get_reg_idx(name)
        if idx == 31: return

        if name.startswith('W'):
            self.x[idx] = value & 0xFFFFFFFF
        elif name.startswith('X'):
            self.x[idx] = value & 0xFFFFFFFFFFFFFFFF

    def _parse_operand(self, op):
        op = op.strip()
        if op.startswith('#'):
            return int(op[1:], 0)
        elif op.startswith('[') and op.endswith(']'):
            parts = op[1:-1].split(',')
            base_reg_val = self.get_register(parts[0].strip())
            offset = int(parts[1].strip().lstrip('#'), 0) if len(parts) > 1 else 0
            return base_reg_val + offset
        else:
            return self.get_register(op)

    def _update_flags(self, result, is_64bit=True):
        mask = 0xFFFFFFFFFFFFFFFF if is_64bit else 0xFFFFFFFF
        result &= mask
        self.pstate['Z'] = 1 if result == 0 else 0
        msb_pos = 63 if is_64bit else 31
        self.pstate['N'] = 1 if (result >> msb_pos) & 1 else 0
        
    def _handle_arithmetic(self, operands, op_func):
        dest, src1, src2_op = operands
        val1 = self.get_register(src1)
        val2 = self._parse_operand(src2_op)
        is_64bit = dest.upper().startswith('X')
        result = op_func(val1, val2)
        self.set_register(dest, result)
        self._update_flags(result, is_64bit)

    def _handle_add(self, operands): self._handle_arithmetic(operands, lambda a, b: a + b)
    def _handle_sub(self, operands): self._handle_arithmetic(operands, lambda a, b: a - b)
    def _handle_mul(self, operands): self._handle_arithmetic(operands, lambda a, b: a * b)
    def _handle_and(self, operands): self._handle_arithmetic(operands, lambda a, b: a & b)
    def _handle_eor(self, operands): self._handle_arithmetic(operands, lambda a, b: a ^ b)

    def _handle_mov(self, operands):
        dest, src_op = operands
        val = self._parse_operand(src_op)
        self.set_register(dest, val)

    def _handle_str(self, operands):
        src_reg, mem_op = operands
        addr = self._parse_operand(mem_op)
        val = self.get_register(src_reg)
        self.stack[addr:addr+8] = struct.pack('<Q', val)

    def _handle_strb(self, operands):
        src_reg, mem_op = operands
        addr = self._parse_operand(mem_op)
        val = self.get_register(src_reg)
        self.stack[addr:addr+1] = struct.pack('<B', val & 0xFF)

    def _handle_ldr(self, operands):
        dest_reg, mem_op = operands
        addr = self._parse_operand(mem_op)
        val_bytes = self.stack[addr:addr+8]
        val = struct.unpack('<Q', val_bytes)[0]
        self.set_register(dest_reg, val)
        
    def _handle_ldrb(self, operands):
        dest_reg, mem_op = operands
        addr = self._parse_operand(mem_op)
        val_bytes = self.stack[addr:addr+1]
        val = struct.unpack('<B', val_bytes)[0]
        self.set_register(dest_reg, val)

    def _handle_cmp(self, operands):
        reg1_name, op2 = operands
        val1 = self.get_register(reg1_name)
        val2 = self._parse_operand(op2)
        is_64bit = reg1_name.upper().startswith('X')
        result = val1 - val2
        self._update_flags(result, is_64bit)

    def _handle_b(self, operands):
        self.pc = self.labels[operands[0]]

    def _handle_b_gt(self, operands):
        if self.pstate['Z'] == 0 and self.pstate['N'] == self.pstate['V']:
            self.pc = self.labels[operands[0]]

    def _handle_b_le(self, operands):
        if self.pstate['Z'] == 1 or self.pstate['N'] != self.pstate['V']:
            self.pc = self.labels[operands[0]]
            
    def _handle_nop(self, operands):
        pass

    def _handle_ret(self, operands):
        self.emulation_finished = True

    def load_program(self, filepath):
        with open(filepath, 'r') as f:
            lines = f.readlines()
        current_addr = 0
        program = []
        for line in lines:
            line = re.sub(r'(//|#).*', '', line).strip()
            if not line: continue
            if line.endswith(':'):
                self.labels[line[:-1]] = current_addr
            else:
                program.append(line)
                current_addr += 4
        return program

    def run(self, program):
        while not self.emulation_finished and (self.pc // 4) < len(program):
            addr = self.pc
            line = program[addr // 4]
            self.pc += 4
            parts = line.split(maxsplit=1)
            instr = parts[0].upper()
            ops_str = parts[1] if len(parts) > 1 else ''
            operands = [op.strip() for op in ops_str.split(',', 1)] if ops_str else []
            if instr in self.handlers:
                self.handlers[instr](operands)
            else:
                print(f"Error: Unknown instruction '{instr}' at address 0x{addr:x}")
                break
        print("--- Emulation Finished ---")

    def display_state(self):
        print("--- Final Register State ---")
        for i in range(31):
            print(f"X{i:<2}: 0x{self.x[i]:016x}", end='\t' if (i+1) % 3 != 0 else '\n')
        print(f"\nSP : 0x{self.sp:016x}\tPC : 0x{self.pc:016x}")
        print(f"PSTATE: N={self.pstate['N']} Z={self.pstate['Z']}")
        print("\n--- Final Stack State ---")
        for i in range(0, len(self.stack), 16):
            chunk = self.stack[i:i+16]
            hex_part = ' '.join(f'{b:02x}' for b in chunk)
            ascii_part = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in chunk)
            print(f"0x{i:04x}: {hex_part:<48} |{ascii_part}|")


def run_single_test(filename, code_to_write, description):
    """A helper function to write a test file, run it, and display the state."""
    print(f"=======================================================================")
    print(f"===== Running: {description}")
    print(f"=======================================================================\n")
    with open(filename, "w") as f:
        f.write(code_to_write)
    emulator = ARM64Emulator()
    program = emulator.load_program(filename)
    print("--- Starting Emulation ---")
    emulator.run(program)
    print("\n")
    emulator.display_state()
    print("\n\n")


# --- Main Execution Block ---
if __name__ == "__main__":
    # --- Test Case 1: Arithmetic Test ---
    arithmetic_code = """
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
    """
    run_single_test("ARTH_TEST.s", arithmetic_code, "Arithmetic and Logic Test")

    # --- Test Case 2: Memory Test ---
    memory_code = """
    SUB  SP, SP, #16
    MOV  X0, #0x11223344AABBCCDD
    STR  X0, [SP, #0]
    MOV  W1, #'A'
    STRB W1, [SP, #15]
    MOV  X0, #0
    MOV  W1, #0
    LDR  X2, [SP, #0]
    LDRB W3, [SP, #15]
    LDRB W4, [SP, #2]
    RET
    """
    run_single_test("MEMORY_TEST.s", memory_code, "Memory and Stack Test")

    # --- Test Case 3: Branching Test ---
    branching_code = """
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
    """
    run_single_test("BRANCH_TEST.s", branching_code, "Branching and Logic Test")