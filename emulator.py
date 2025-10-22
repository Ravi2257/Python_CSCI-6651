import re
import sys

class ARM64Emulator:
    """
    A simplified ARM64 emulator that handles a subset of instructions,
    registers, and a small stack memory.
    """
    def __init__(self, stack_size=256):
        # Task 2: Create ARM64 registers
        self.regs = {f'X{i}': 0 for i in range(31)}
        self.regs['XZR'] = 0 # Zero register
        self.pc = 0
        
        # Processor state register bits
        self.n_flag = 0  # Negative flag
        self.z_flag = 1  # Zero flag (initialized to 1 as regs are 0)
        
        # Task 3: Prepare stack memory
        self.stack_base_addr = 0x7FFF_FFFF_E00  # Arbitrary high memory address
        self.stack_size = stack_size
        self.memory = bytearray(stack_size)
        self.regs['SP'] = self.stack_base_addr + self.stack_size

        # For mapping instruction mnemonics to handler functions
        self.handlers = self._get_handlers()
        self.labels = {}
        self.running = False
        self.instruction_count = 0

    # =========================================================================
    # NEW METHOD TO PRINT INITIAL SETUP FOR TASKS 1, 2, AND 3
    # =========================================================================
    def print_initial_setup(self, program):
        """Prints the parsed program and initial state of the emulator."""
        
        # --- Task 1: Print Parsed Instructions ---
        print("\n" + "="*120)
        print("TASK 1: PARSED INSTRUCTIONS".center(120))
        print("="*120)
        clean_program = [line for line in program if line.strip() and not line.strip().endswith(':')]
        for line_num, line in enumerate(clean_program):
            mnemonic, operands = self._parse_line(line)
            if not mnemonic: continue
            
            print("-" * 120)
            print(f"Instruction #{line_num}:")
            print("-" * 120)
            print(f"Instruction: {mnemonic}")
            for i, op in enumerate(operands):
                # Add special formatting for LDR/STR to match the original example
                if mnemonic in ('LDR', 'STR', 'LDRB', 'STRB') and '[' in op:
                    try:
                        base_reg, offset = self._parse_mem_operand(op)
                        print(f"Operand #{i+1}: {op} --> {base_reg} + {offset:#x}")
                    except ValueError:
                        print(f"Operand #{i+1}: {op}") # Fallback for invalid format
                else:
                    print(f"Operand #{i+1}: {op}")
            print() # Add a blank line for readability

        # --- Task 2 & 3: Print Initial Register and Stack State ---
        print("\n" + "="*120)
        print("TASKS 2 & 3: INITIAL EMULATOR STATE".center(120))
        print("="*120)
        self.print_registers()
        self.print_stack()

    def _get_handlers(self):
        # Task 5: Map instructions to their implementation
        return {
            'ADD': self._handle_add, 'SUB': self._handle_sub,
            'EOR': self._handle_eor, 'AND': self._handle_and,
            'MUL': self._handle_mul, 'MOV': self._handle_mov,
            'STR': self._handle_str, 'STRB': self._handle_strb,
            'LDR': self._handle_ldr, 'LDRB': self._handle_ldrb,
            'NOP': self._handle_nop, 'B': self._handle_b,
            'B.GT': self._handle_b_gt, 'B.LE': self._handle_b_le,
            'CMP': self._handle_cmp, 'RET': self._handle_ret,
        }

    # --- Register and Flag Helpers (Task 2 & 6) ---
    def _is_w_reg(self, reg_name):
        return reg_name.startswith('W')

    def _to_x_reg(self, reg_name):
        if self._is_w_reg(reg_name):
            if reg_name == 'WSP': return 'SP'
            if reg_name == 'WZR': return 'XZR'
            return 'X' + reg_name[1:]
        return reg_name

    def _get_reg(self, name):
        if name == 'XZR' or name == 'WZR':
            return 0
        
        x_reg = self._to_x_reg(name)
        val = self.regs.get(x_reg)
        if val is None:
            raise ValueError(f"Unknown register: {name}")

        # Task 6: For 32-bit registers, only return the lower 32 bits
        if self._is_w_reg(name):
            return val & 0xFFFFFFFF
        return val

    def _set_reg(self, name, value):
        if name == 'XZR' or name == 'WZR':
            return # Cannot write to the zero register

        x_reg = self._to_x_reg(name)
        if x_reg not in self.regs:
            raise ValueError(f"Unknown register: {name}")

        # Task 6: For 32-bit registers, zero-extend to 64 bits
        if self._is_w_reg(name):
            self.regs[x_reg] = value & 0xFFFFFFFF
        else:
            self.regs[x_reg] = value & 0xFFFFFFFFFFFFFFFF

    def _update_flags(self, result):
        result_64 = result & 0xFFFFFFFFFFFFFFFF
        self.z_flag = 1 if result_64 == 0 else 0
        self.n_flag = (result_64 >> 63) & 1

    # --- Memory Helpers (Task 3) ---
    def _mem_op(self, address, num_bytes, value=None, write=False):
        if not (self.stack_base_addr <= address < self.stack_base_addr + self.stack_size):
            raise MemoryError(f"Memory access violation at address {address:#x}")
        
        offset = address - self.stack_base_addr
        if offset + num_bytes > self.stack_size:
             raise MemoryError(f"Memory access out of bounds at address {address:#x}")

        if write:
            for i in range(num_bytes):
                self.memory[offset + i] = (value >> (i * 8)) & 0xFF
        else:
            read_val = 0
            for i in range(num_bytes):
                read_val |= self.memory[offset + i] << (i * 8)
            return read_val
            
    # --- Parser and Operand Helpers (Task 1) ---
    def _parse_mem_operand(self, op_str):
        match = re.match(r'\[(X\d+|SP|XZR),\s*#?(-?0x[0-9a-fA-F]+|-?\d+)\]', op_str.strip())
        if not match:
            raise ValueError(f"Invalid memory operand: {op_str}")
        base_reg, offset_str = match.groups()
        return base_reg, int(offset_str, 0)
    
    def _parse_operand(self, op_str):
        op_str = op_str.strip()
        if op_str.startswith('#'):
            return int(op_str[1:], 0)
        return op_str # It's a register name

    def _parse_line(self, line):
        line = line.split('//')[0].split(';')[0].strip()
        if not line:
            return None, None
        
        parts = line.split(maxsplit=1)
        mnemonic = parts[0].upper()
        
        if len(parts) == 1:
            return mnemonic, []
            
        # Regex to split operands by comma, but ignore commas inside brackets
        operands_str = parts[1]
        operands = [op.strip() for op in re.split(r',\s*(?![^[]*\])', operands_str)]
        return mnemonic, operands

    # --- Instruction Handlers (Task 5) ---
    def _handle_arithmetic(self, operands, op_func):
        dest_reg, src_reg1, op2_str = operands
        val1 = self._get_reg(src_reg1)
        op2 = self._parse_operand(op2_str)
        val2 = self._get_reg(op2) if isinstance(op2, str) else op2
        
        result = op_func(val1, val2)
        self._set_reg(dest_reg, result)
        self._update_flags(result)

    def _handle_add(self, operands): self._handle_arithmetic(operands, lambda a, b: a + b)
    def _handle_sub(self, operands): self._handle_arithmetic(operands, lambda a, b: a - b)
    def _handle_eor(self, operands): self._handle_arithmetic(operands, lambda a, b: a ^ b)
    def _handle_and(self, operands): self._handle_arithmetic(operands, lambda a, b: a & b)
    def _handle_mul(self, operands): self._handle_arithmetic(operands, lambda a, b: a * b)
    
    def _handle_mov(self, operands):
        dest_reg, op2_str = operands
        op2 = self._parse_operand(op2_str)
        val2 = self._get_reg(op2) if isinstance(op2, str) else op2
        self._set_reg(dest_reg, val2)

    def _handle_cmp(self, operands):
        src_reg1, op2_str = operands
        val1 = self._get_reg(src_reg1)
        op2 = self._parse_operand(op2_str)
        val2 = self._get_reg(op2) if isinstance(op2, str) else op2
        result = val1 - val2
        self._update_flags(result)
        
    def _handle_mem_access(self, operands, is_store, is_byte):
        reg, mem_op_str = operands
        base_reg, offset = self._parse_mem_operand(mem_op_str)
        address = self._get_reg(base_reg) + offset
        num_bytes = 1 if is_byte else 8
        
        if is_store:
            value = self._get_reg(reg)
            self._mem_op(address, num_bytes, value, write=True)
        else: # Load
            value = self._mem_op(address, num_bytes, write=False)
            self._set_reg(reg, value)
            
    def _handle_ldr(self, operands): self._handle_mem_access(operands, is_store=False, is_byte=False)
    def _handle_ldrb(self, operands): self._handle_mem_access(operands, is_store=False, is_byte=True)
    def _handle_str(self, operands): self._handle_mem_access(operands, is_store=True, is_byte=False)
    def _handle_strb(self, operands): self._handle_mem_access(operands, is_store=True, is_byte=True)

    def _handle_nop(self, operands): pass
    def _handle_ret(self, operands): self.running = False
    
    def _handle_b(self, operands):
        label = operands[0]
        if label in self.labels:
            self.pc = self.labels[label] - 4
        else:
            raise ValueError(f"Undefined label: {label}")

    def _handle_b_gt(self, operands):
        if self.z_flag == 0 and self.n_flag == 0:
            self._handle_b(operands)
            
    def _handle_b_le(self, operands):
        if self.z_flag == 1 or self.n_flag == 1:
            self._handle_b(operands)

    # --- Main Execution Loop (Task 4 & 7) ---
    def _pre_scan_for_labels(self, program):
        for i, line in enumerate(program):
            line = line.strip()
            if line.endswith(':'):
                label = line[:-1]
                self.labels[label] = i * 4

    def run(self, program):
        clean_program = [line for line in program if line.strip() and not line.strip().endswith(':')]
        self._pre_scan_for_labels(program)
        
        self.pc = 0
        self.running = True

        print("\n" + "="*120)
        print("STARTING EMULATION RUN".center(120))
        print("="*120 + "\n")

        while self.running:
            if not (0 <= self.pc < len(clean_program) * 4):
                print("\nPC out of bounds. Halting.")
                break
                
            line_idx = self.pc // 4
            line = clean_program[line_idx]
            
            mnemonic, operands = self._parse_line(line)
            if not mnemonic:
                self.pc += 4
                continue

            print(f"--- Instruction #{line_idx} ({line.strip()}) ---")

            handler = self.handlers.get(mnemonic)
            if handler:
                pc_before = self.pc
                handler(operands)
                if self.pc == pc_before:
                    self.pc += 4
                else:
                    self.pc += 4
            else:
                raise NotImplementedError(f"Instruction '{mnemonic}' not implemented.")
            
            self.instruction_count += 1
            if self.instruction_count > 1000:
                print("Instruction limit reached. Halting.")
                break

            self.print_state()

        print("\n--- Emulation Finished ---")
        self.print_state()

    # --- Output Formatting ---
    def print_state(self):
        self.print_registers()
        self.print_stack()

    def print_registers(self):
        print("-" * 120)
        print("Registers:")
        print("-" * 120)
        for i in range(10):
            print(f"X{i:<2}: {self._get_reg(f'X{i}'):#018x}\t"
                  f"X{i+10:<2}: {self._get_reg(f'X{i+10}'):#018x}\t"
                  f"X{i+20:<2}: {self._get_reg(f'X{i+20}'):#018x}")
        print(f"X30: {self._get_reg('X30'):#018x}\t"
              f"SP: {self._get_reg('SP'):#018x}\tPC: {self.pc:#018x}")
        print(f"Processor State N bit: {self.n_flag}\tProcessor State Z bit: {self.z_flag}")

    def print_stack(self):
        print("-" * 120)
        print("Stack:")
        print("-" * 120)
        for i in range(0, self.stack_size, 16):
            addr = self.stack_base_addr + i
            chunk = self.memory[i:i+16]
            hex_part = ' '.join(f'{b:02x}' for b in chunk)
            ascii_part = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in chunk)
            print(f"{addr:08x}  {hex_part:<48} |{ascii_part}|")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: python {sys.argv[0]} <assembly_file.s>")
        sys.exit(1)

    filepath = "test.s"
    try:
        with open(filepath, 'r') as f:
            program_lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: File not found at '{filepath}'")
        sys.exit(1)

    emulator = ARM64Emulator()
    
    # ====================================================
    # =====================
    # MODIFIED: Call the new setup function first
    # ====================================================
 
    emulator.print_initial_setup(program_lines)
    
    # Original call to run the full emulation

    emulator.run(program_lines)