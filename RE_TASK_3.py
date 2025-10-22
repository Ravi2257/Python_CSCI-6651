class StackMemory:
    def __init__(reg, size=256, base_address=0x0):
        reg.size = size
        reg.base_address = base_address
        # Initialize stack with zeros
        reg.memory = bytearray([0x00] * size)

    def write(reg, offset, data):
        """Write bytes to stack starting at offset."""
        for i, byte in enumerate(data):
            if offset + i < reg.size:
                reg.memory[offset + i] = byte
            else:
                raise IndexError("Stack write out of bounds")

    def read(reg, offset, length):
        """Read bytes from stack starting at offset."""
        if offset + length <= reg.size:
            return reg.memory[offset:offset + length]
        else:
            raise IndexError("Stack read out of bounds")

    def display_stack(reg):
        """Pretty print stack in hexdump format."""
        print("-------------------------------------------------------------------------------------------------------------------------------")
        print("Stack:")
        print("-------------------------------------------------------------------------------------------------------------------------------")

        # Print 16 bytes per line
        for i in range(0, reg.size, 16):
            chunk = reg.memory[i:i+16]

            # Hex values
            hex_bytes = " ".join(f"{b:02x}" for b in chunk)

            # ASCII representation ('.' for non-printables)
            ascii_repr = "".join(chr(b) if 32 <= b <= 126 else "." for b in chunk)

            print(f"{reg.base_address + i:08x} {hex_bytes:<47} |{ascii_repr}|")

        # Print end address
        print(f"{reg.base_address + reg.size:08x}")


# Example usage
if __name__ == "__main__":
    stack = StackMemory(size=256, base_address=0x0)
    stack.display_stack()

    print("\n--- Filling some stack with random data ---\n")
    import os
    stack.memory = bytearray(os.urandom(256))  # fill with random bytes
    stack.display_stack()
