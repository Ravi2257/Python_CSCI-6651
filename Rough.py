#!/usr/bin/env python3
"""
Simple ARM64 emulator for coursework (Tasks 1-6).
Usage:
    python arm64_emulator.py assembly_file.s

Notes:
 - Supports labels (label:)
 - Supports registers X0-X30, W0-W30 (32-bit semantics), XZR (read=0, write ignored), SP, PC
 - Stack: 256 bytes (bytearray). Stack base default 0x0; SP initialized to base + size (stack grows down).
 - PC is byte-addressed, starts at 0x0, each instruction assumed size 4 bytes.
 - Instructions implemented: SUB, EOR, ADD, AND, MUL, MOV, STR, STRB, LDR, LDRB, NOP, B, B.GT, B.LE, CMP, RET
 - Branch conditions use N and Z flags (from CMP).
"""

import sys
import re
import textwrap

# ---------------------------
# Utilities
# ---------------------------

def hexdump(buf: bytes, base_addr: int = 0):
    out_lines = []
    for i in range(0, len(buf), 16):
        chunk = buf[i:i+16]
        hexbytes = ' '.join(f"{b:02x}" for b in chunk)
        ascii_ = ''.join((chr(b) if 32 <= b <= 126 else '.') for b in chunk)
        out_lines.append(f"{base_addr + i:08x} {hexbytes:<47} |{ascii_:16}|")
    out_lines.append(f"{base_addr + len(buf):08x}")
    return '\n'.join(out_lines)

def parse_imm(tok: str):
    tok = tok.strip()
    if tok.startswith('#'):
        tok = tok[1:]
    if tok.startswith('0x') or tok.startswith('0X'):
        return int(tok, 16)
    if re.match(r'^-?\d+$', tok):
        return int(tok, 10)
    # allow bare hex like 0x08 or 08
    try:
        return int(tok, 0)
    except Exception:
        raise ValueError(f"Unable to parse immediate: {tok}")

def reg_normalize(r: str):
    # canonicalize register token (remove commas/spaces)
    r = r.strip().rstrip(',')
    return r.upper()

def is_reg(tok):
    tok = tok.upper()
    return tok.startswith('X') or tok.startswith('W') or tok in ('SP', 'XZR', 'PC')

# ---------------------------
# CPU State
# ---------------------------

class CPU:
    def __init__(self, stack_size=256, stack_base=0x0):
        # Registers stored as 64-bit python ints
        self.regs = {f"X{i}": 0 for i in range(0, 31)}  # X0..X30
        self.regs["XZR"] = 0  # Reads as zero (writes ignored)
        self.regs["SP"] = stack_base + stack_size  # initialize SP at top of stack (stack grows down)
        self.regs["PC"] = 0
        self.stack_base = stack_base
        self.stack_size = stack_size
        self.stack = bytearray(stack_size)
        # Flags
        self.N = 0
        self.Z = 0
        # Instruction storage (list of dicts)
        self.instructions = []  # list of {addr, text, mnemonic, operands}
        self.addr_to_idx = {}   # map address -> instruction index (for quick dispatch)
        # label map
        self.labels = {}
        # running flag
        self.running = True
        # trace
        self.trace = []

    # register read with W vs X handling:
    def read_reg(self, name: str):
        name = name.upper()
        if name.startswith('W'):
            # read lower 32 bits
            xname = 'X' + name[1:]
            v = self.regs.get(xname, 0) & 0xffffffff
            return v
        if name == 'XZR':
            return 0
        return self.regs.get(name, 0)

    def write_reg(self, name: str, value: int):
        name = name.upper()
        # mask to 64 bits
        value = value & ((1 << 64) - 1)
        if name == 'XZR':
            # Writes are ignored to XZR
            return
        if name.startswith('W'):
            # zero-extend 32-bit value to 64-bit
            xname = 'X' + name[1:]
            v32 = value & 0xffffffff
            self.regs[xname] = v32  # upper 32 bits cleared by assign
            return
        # normal X register or SP or PC
        if name in self.regs:
            self.regs[name] = value
        else:
            # fall back to Xn mapping
            if name.startswith('X'):
                self.regs[name] = value
            else:
                raise KeyError(f"Unknown register {name}")

    def set_flags_from_result(self, res: int, width_bits=64):
        # N: MSB of result at width_bits
        mask = (1 << width_bits) - 1
        res_masked = res & mask
        msb = (res_masked >> (width_bits - 1)) & 1
        self.N = 1 if msb else 0
        self.Z = 1 if res_masked == 0 else 0

    # Memory helpers: translate virtual address to stack offset
    def check_addr_in_stack(self, addr):
        if not (self.stack_base <= addr < self.stack_base + self.stack_size):
            raise MemoryError(f"Memory access out of stack bounds: {hex(addr)} (stack {hex(self.stack_base)}..{hex(self.stack_base + self.stack_size)})")

    def read_mem64(self, addr):
        self.check_addr_in_stack(addr)
        # Little-endian 8 bytes
        off = addr - self.stack_base
        v = int.from_bytes(self.stack[off:off+8], 'little')
        return v

    def write_mem64(self, addr, value):
        self.check_addr_in_stack(addr)
        off = addr - self.stack_base
        self.stack[off:off+8] = int(value & ((1<<64)-1)).to_bytes(8, 'little')

    def read_mem8(self, addr):
        self.check_addr_in_stack(addr)
        off = addr - self.stack_base
        return self.stack[off]

    def write_mem8(self, addr, value):
        self.check_addr_in_stack(addr)
        off = addr - self.stack_base
        self.stack[off] = value & 0xff

    # register dump for display
    def dump_registers(self):
        lines = []
        # print 3 columns like example
        for row in range(0, 10):
            a = f"X{row:02d}"
            b = f"X{row+10:02d}"
            c = f"X{row+20:02d}"
            if row == 9:
                # X9, X19, X29 then SP/PC/X30 print later
                pass
            xa = self.regs.get(a, 0)
            xb = self.regs.get(b, 0)
            xc = self.regs.get(c, 0)
            lines.append(f"{a}: 0x{xa:016x} {b}: 0x{xb:016x} {c}: 0x{xc:016x}")
        # append final line with SP, PC, X30
        lines.append(f"SP: 0x{self.regs['SP']:016x} PC: 0x{self.regs['PC']:016x} X30: 0x{self.regs.get('X30',0):016x}")
        lines.append(f"Processor State N bit: {self.N}")
        lines.append(f"Processor State Z bit: {self.Z}")
        return '\n'.join(lines)

    # hexdump stack
    def dump_stack(self):
        return hexdump(bytes(self.stack), self.stack_base)

# ---------------------------
# Parser / Loader
# ---------------------------

def preprocess_lines(lines):
    # strip comments (starting with // or @ or ;)
    out = []
    for raw in lines:
        line = raw.split('//')[0].split('@')[0].split(';')[0].strip()
        if not line:
            continue
        out.append(line)
    return out

def parse_asm_file(path):
    with open(path, 'r') as f:
        raw_lines = f.readlines()
    lines = preprocess_lines(raw_lines)

    # First pass: detect labels and build instruction list
    instructions = []
    labels = {}
    addr = 0
    for ln in lines:
        if ln.endswith(':'):
            label = ln[:-1].strip()
            labels[label] = addr
            continue
        # Inline labels like "label: ADD X0, X1, X2" ?
        if ':' in ln:
            # handle label at start of line
            parts = ln.split(':', 1)
            label = parts[0].strip()
            rest = parts[1].strip()
            labels[label] = addr
            if rest == '':
                continue
            ln = rest
        # store instruction
        instructions.append({'addr': addr, 'text': ln})
        addr += 4
    return instructions, labels

def split_operands(opstr):
    # Split operands by commas, but keep memory bracket as single operand.
    # Simpler: split on comma, then strip.
    parts = [p.strip() for p in opstr.split(',')]
    return parts

def parse_instruction_text(instr_text):
    # returns mnemonic, operand list
    # example: "ADD X1, X2, X3"
    tokens = instr_text.strip().split(None, 1)
    if not tokens:
        return None, []
    mnemonic = tokens[0].upper()
    operands = []
    if len(tokens) > 1:
        operands = split_operands(tokens[1])
    return mnemonic, operands

# ---------------------------
# Instruction Execution
# ---------------------------

class Emulator:
    def __init__(self, cpu: CPU):
        self.cpu = cpu

    def load_instructions(self, instrs, labels):
        # parse each text into mnemonic/operands and index mapping
        self.cpu.instructions = []
        for idx, it in enumerate(instrs):
            mnem, ops = parse_instruction_text(it['text'])
            entry = {'addr': it['addr'], 'text': it['text'], 'mnemonic': mnem, 'operands': ops}
            self.cpu.instructions.append(entry)
            self.cpu.addr_to_idx[it['addr']] = idx
        self.cpu.labels = labels

    def resolve_operand_value(self, op):
        # determine operand value for register or immediate
        op = op.strip()
        if is_reg(op):
            return self.cpu.read_reg(op)
        # memory operand [REG, offset]
        if op.startswith('[') and op.endswith(']'):
            content = op[1:-1].strip()
            parts = [p.strip() for p in content.split(',') if p.strip()!='']
            base = parts[0]
            base_addr = self.cpu.read_reg(base)
            offset = 0
            if len(parts) > 1:
                offset = parse_imm(parts[1])
            addr = (base_addr + offset)
            return addr
        # immediate
        try:
            return parse_imm(op)
        except Exception:
            raise ValueError(f"Unknown operand form: {op}")

    def execute(self):
        cpu = self.cpu
        cpu.running = True
        # run loop
        step = 0
        while cpu.running:
            pc = cpu.regs['PC']
            if pc not in cpu.addr_to_idx:
                print(f"PC {pc} has no instruction mapped. Halting.")
                break
            idx = cpu.addr_to_idx[pc]
            instr = cpu.instructions[idx]
            mnem = instr['mnemonic']
            ops = instr['operands']
            # trace line
            cpu.trace.append(f"{pc:08x}: {instr['text']}")
            # advance PC by default (4 bytes). Branches will override if needed.
            cpu.regs['PC'] = pc + 4

            # dispatch
            try:
                self.exec_instr(mnem, ops)
            except Exception as e:
                print(f"Error executing instruction at {pc:08x} '{instr['text']}': {e}")
                cpu.running = False
                break

            step += 1
            if step > 10000:
                print("Exceeded step limit, halting to avoid infinite loop.")
                break

    def exec_instr(self, mnem, ops):
        cpu = self.cpu
        m = mnem.upper()
        # Helper lambdas
        def get_reg_val(op):
            return cpu.read_reg(op)

        def set_reg(op, val):
            cpu.write_reg(op, val)

        # Arithmetic / logical: three operand form like ADD Xd, Xn, Xm or imm
        if m in ('ADD','SUB','AND','EOR','MUL'):
            if len(ops) != 3:
                raise ValueError(f"{m} requires 3 operands")
            dst, op1, op2 = ops
            dst = reg_normalize(dst)
            op1 = reg_normalize(op1)
            op2 = op2.strip()
            # op2 can be register or immediate
            if is_reg(op2):
                val2 = cpu.read_reg(op2)
            else:
                val2 = parse_imm(op2)
            val1 = cpu.read_reg(op1)
            if m == 'ADD':
                res = (val1 + val2) & ((1<<64)-1)
            elif m == 'SUB':
                res = (val1 - val2) & ((1<<64)-1)
            elif m == 'AND':
                res = val1 & val2
            elif m == 'EOR':
                res = val1 ^ val2
            elif m == 'MUL':
                res = (val1 * val2) & ((1<<64)-1)
            else:
                res = 0
            set_reg(dst, res)
            # update flags? Real ARM arithmetic doesn't automatically set flags unless suffix S — but CMP sets flags.
            # For simplicity we'll not change flags here.
            return

        if m == 'MOV':
            # MOV Xd, Xm  or MOV Xd, #imm
            if len(ops) != 2:
                raise ValueError("MOV requires 2 operands")
            dst = reg_normalize(ops[0])
            src = ops[1].strip()
            if is_reg(src):
                val = cpu.read_reg(src)
            else:
                val = parse_imm(src)
            cpu.write_reg(dst, val)
            return

        if m in ('STR','STRB'):
            # STR Xt, [Xn, imm]
            if len(ops) != 2:
                raise ValueError(f"{m} requires 2 operands")
            src = reg_normalize(ops[0])
            mem = ops[1].strip()
            if not (mem.startswith('[') and mem.endswith(']')):
                raise ValueError("Memory operand expected like [SP, 8]")
            content = mem[1:-1].strip()
            parts = [p.strip() for p in content.split(',') if p.strip()!='']
            base = parts[0]
            offset = 0
            if len(parts) > 1:
                offset = parse_imm(parts[1])
            addr = cpu.read_reg(base) + offset
            if m == 'STR':
                val = cpu.read_reg(src)
                cpu.write_mem64(addr, val)
            else:
                # STRB
                val = cpu.read_reg(src) & 0xff
                cpu.write_mem8(addr, val)
            return

        if m in ('LDR','LDRB'):
            # LDR Xt, [Xn, imm]
            if len(ops) != 2:
                raise ValueError(f"{m} requires 2 operands")
            dst = reg_normalize(ops[0])
            mem = ops[1].strip()
            if not (mem.startswith('[') and mem.endswith(']')):
                raise ValueError("Memory operand expected like [SP, 8]")
            content = mem[1:-1].strip()
            parts = [p.strip() for p in content.split(',') if p.strip()!='']
            base = parts[0]
            offset = 0
            if len(parts) > 1:
                offset = parse_imm(parts[1])
            addr = cpu.read_reg(base) + offset
            if m == 'LDR':
                val = cpu.read_mem64(addr)
                cpu.write_reg(dst, val)
            else:
                # LDRB
                val = cpu.read_mem8(addr)
                cpu.write_reg(dst, val)
            return

        if m == 'NOP':
            return

        if m == 'CMP':
            # CMP Rn, Rm_or_imm -> sets flags, like Rn - Rm
            if len(ops) != 2:
                raise ValueError("CMP requires 2 operands")
            rn = reg_normalize(ops[0])
            op2 = ops[1].strip()
            valn = cpu.read_reg(rn)
            if is_reg(op2):
                val2 = cpu.read_reg(op2)
            else:
                val2 = parse_imm(op2)
            res = (valn - val2) & ((1<<64)-1)
            cpu.set_flags_from_result(res, 64)
            return

        if m == 'B':
            # unconditional branch B label
            if len(ops) != 1:
                raise ValueError("B requires 1 operand (label)")
            target = ops[0].strip()
            # allow numeric immediate too
            if target in cpu.labels:
                addr = cpu.labels[target]
            else:
                # maybe target is immediate address
                try:
                    addr = parse_imm(target)
                except:
                    raise ValueError(f"Unknown branch target: {target}")
            cpu.regs['PC'] = addr
            return

        if m == 'B.GT':
            # Branch if greater than -> (Z==0 and N==V) ; but we don't implement V, so approximate: Z==0 and N==0?
            # Simpler: treat GT as (Z==0 and N==0) for unsigned? We'll implement: GT => Z==0 and N==0 (assumption).
            if len(ops) != 1:
                raise ValueError("B.GT requires 1 operand")
            target = ops[0].strip()
            if cpu.Z == 0 and cpu.N == 0:
                if target in cpu.labels:
                    addr = cpu.labels[target]
                else:
                    addr = parse_imm(target)
                cpu.regs['PC'] = addr
            return

        if m == 'B.LE':
            # Branch if less or equal: Z==1 or N != V. With no V, approximate as Z==1 or N==1
            if len(ops) != 1:
                raise ValueError("B.LE requires 1 operand")
            target = ops[0].strip()
            if cpu.Z == 1 or cpu.N == 1:
                if target in cpu.labels:
                    addr = cpu.labels[target]
                else:
                    addr = parse_imm(target)
                cpu.regs['PC'] = addr
            return

        if m == 'RET':
            # end emulation
            cpu.running = False
            return

        # If we reach here, instruction not implemented
        raise NotImplementedError(f"Instruction '{m}' not implemented")

# ---------------------------
# Main runner
# ---------------------------

def run_file(path):
    instrs, labels = parse_asm_file(path)
    cpu = CPU(stack_size=256, stack_base=0x0)
    emu = Emulator(cpu)
    emu.load_instructions(instrs, labels)
    # set PC start at 0
    cpu.regs['PC'] = 0
    print("Loaded program:")
    for it in emu.cpu.instructions:
        print(f"{it['addr']:08x}: {it['text']}")
    if labels:
        print("\nLabels:")
        for k,v in labels.items():
            print(f"  {k} -> 0x{v:08x}")
    print("\nStarting emulation...\n")
    emu.execute()
    print("=== Trace (first 200 lines) ===")
    for t in emu.trace[:200]:
        print(t)
    print("\n=== Registers ===")
    print(cpu.dump_registers())
    print("\n=== Stack (hexdump) ===")
    print(cpu.dump_stack())


def dump_test_file(path):
    with open(path, 'w') as f:
        f.write(path)

def main():
    if len(sys.argv) < 2:
        # write a temp test file and run it
        path = "test.asm"
        dump_test_file(path)
        print("No input supplied; writing small demo to test.asm")
    else:
        run_file(sys.argv[1])

if __name__ == '__main__':
    main()
