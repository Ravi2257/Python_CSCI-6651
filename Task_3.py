class StackMemory:
    """
    Represents a simple, contiguous block of memory for the stack.
    """
    def __init__(self, size_bytes=256):
        # Create a mutable array of bytes, initialized to zero
        self.memory = bytearray(size_bytes)
        self.size = size_bytes

    def display(self):
        """
        Prints the memory content in a classic hexdump format.
        """
        print("-------------------------------------------------------------------------------------------------------------------------------")
        print("Stack:")
        print("-------------------------------------------------------------------------------------------------------------------------------")
        
        # Iterate through memory in 16-byte chunks
        for i in range(0, self.size, 16):
            chunk = self.memory[i:i+16]
            
            # 1. Print Address
            # Format address as an 8-digit hex string
            print(f"{i:08x}  ", end="")
            
            # 2. Print Hex Representation
            hex_part = ""
            for j, byte in enumerate(chunk):
                hex_part += f"{byte:02x} "
                if j == 7: # Add extra space in the middle
                    hex_part += " "
            # Pad with spaces if the chunk is smaller than 16 bytes (last line)
            print(f"{hex_part:<49}", end="")

            # 3. Print ASCII Representation
            ascii_part = ""
            for byte in chunk:
                # Use a dot for non-printable characters
                if 32 <= byte <= 126:
                    ascii_part += chr(byte)
                else:
                    ascii_part += "."
            print(f"|{ascii_part}|")
        print()
            
# --- Execute Task 3 ---
if __name__ == '__main__':
    print("--- Running Task 3: Stack Memory ---")
    stack = StackMemory(size_bytes=256)

    # Display the initial zeroed-out stack
    print("Initial (Zeroed) Stack:")
    stack.display()
    
    # Let's write some random bytes to show a non-empty stack
    import os
    random_bytes = os.urandom(128)
    stack.memory[0:128] = random_bytes
    
    print("\nStack with some random data:")
    stack.display()