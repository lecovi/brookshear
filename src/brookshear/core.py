from pathlib import Path


class BrookshearMachine:
    def __init__(self):
        self.registers = [0] * 16  # 16 general-purpose registers
        self.memory = [0] * 256  # 256 bytes of main memory
        self.pc = 0  # Program counter
        self.ir = 0  # Instruction register
        self.debug = False
        self._program = []

    def open_program(self, filename: str):
        """Opens a machine code program file and loads it into memory."""
        filename = Path(filename)
        with filename.open() as file:
            for line in file:
                # Remove comments and leading/trailing whitespace
                line = line.split('#')[0].strip()
                if line:
                    # Convert the instruction to an integer
                    instruction = int(line, 16)
                    self._program.append(instruction)
            self.load_program(self._program)

    def load_program(self, program):
        """Loads a machine code program into memory."""
        for i, instruction in enumerate(program):
            self.memory[i * 2] = (instruction >> 8) & 0xFF  # High byte
            self.memory[i * 2 + 1] = instruction & 0xFF  # Low byte
        self.clean_registers()
        self.ir = 0
        self.pc = 0

    def clean_registers(self):
        """Resets all registers to zero."""
        self.registers = [0] * 16

    def fetch(self):
        """Fetches the next instruction from memory."""
        high_byte, low_byte = self.memory[self.pc], self.memory[self.pc + 1]
        self.pc += 2
        self.ir = (high_byte << 8) | low_byte
        return self.ir

    def decode_and_execute(self, instruction):
        """Decodes and executes a single instruction using match-case for all opcodes."""
        match instruction >> 12:
            case 1:  # LOAD from memory
                r, x = (instruction >> 8) & 0xF, instruction & 0xFF
                self.registers[r] = self.memory[x]

                if self.debug:
                    print(f"MOV R{r:X}, [{x:02X}] => R{r:X}={self.memory[x]:02X}")

            case 2:  # LOAD immediate
                r, x = (instruction >> 8) & 0xF, instruction & 0xFF
                self.registers[r] = x

                if self.debug:
                    print(f"MOV R{r:X}, {x:02X} => R{r:X}={x:02X}")

            case 3:  # STORE to memory
                r, x = (instruction >> 8) & 0xF, instruction & 0xFF
                self.memory[x] = self.registers[r]

                if self.debug:
                    print(f"MOV [{x:02X}], R{r:X} => [{x:02X}]={self.registers[r]:02X}")

            case 4:  # MOVE
                r, s, t = (instruction >> 8) & 0xF, (instruction >> 4) & 0xF, instruction & 0xF
                if r != 0:
                    raise ValueError("MOV instruction with opcode 4 must followed with 0, then origin register and target register as operands 40RS")
                self.registers[s] = self.registers[r]

                if self.debug:
                    print(f"MOV R{s:X}, R{r:X} => R{s:X}={self.registers[r]:02X}")

            case 5:  # ADD (two's complement)
                r, s, t = (instruction >> 8) & 0xF, (instruction >> 4) & 0xF, instruction & 0xF
                self.registers[r] = (self.registers[s] + self.registers[t]) & 0xFF

                if self.debug:
                    print(f"ADDI R{r:X}, R{s:X}, R{t:X} => R{r:X}={self.registers[s]:02X}+{self.registers[t]:02X} = {self.registers[r]:02X}")

            case 6:  # ADD (floating-point)
                r, s, t = (instruction >> 8) & 0xF, (instruction >> 4) & 0xF, instruction & 0xF
                result = self.float_add(self.registers[s], self.registers[t])
                self.registers[r] = result

                if self.debug:
                    print(f"ADDF R{r:X}, R{s:X}, R{t:X} => R{r:X}={self.registers[s]:02X}+{self.registers[t]:02X} = {result:02X}")

            case 7:  # OR
                r, s, t = (instruction >> 8) & 0xF, (instruction >> 4) & 0xF, instruction & 0xF
                self.registers[r] = self.registers[s] | self.registers[t]

                if self.debug:
                    print(f"OR R{r:X}, R{s:X}, R{t:X} => R{r:X}={self.registers[s]:02X}|{self.registers[t]:02X} = {self.registers[r]:02X}")

            case 8:  # AND
                r, s, t = (instruction >> 8) & 0xF, (instruction >> 4) & 0xF, instruction & 0xF
                self.registers[r] = self.registers[s] & self.registers[t]

                if self.debug:
                    print(f"AND R{r:X}, R{s:X}, R{t:X} => R{r:X}={self.registers[s]:02X}&{self.registers[t]:02X} = {self.registers[r]:02X}")

            case 9:  # EXCLUSIVE OR
                r, s, t = (instruction >> 8) & 0xF, (instruction >> 4) & 0xF, instruction & 0xF
                self.registers[r] = self.registers[s] ^ self.registers[t]

                if self.debug:
                    print(f"XOR R{r:X}, R{s:X}, R{t:X} => R{r:X}={self.registers[s]:02X}^{self.registers[t]:02X} = {self.registers[r]:02X}")

            case 10:  # ROTATE right
                r, s, x = (instruction >> 8) & 0xF, (instruction >> 4) & 0xF, instruction & 0xF

                if s != 0:
                    raise ValueError("ROR instruction with opcode A must followed with 0 after target register, X means how many times register is rotated AR0X")
            
                self.registers[r] = (self.registers[r] >> x) | ((self.registers[r] & ((1 << x) - 1)) << (8 - x))

                if self.debug:
                    print(f"ROR R{r:X}, {x:X} => R{r:X}={self.registers[r]:02X}")

            case 11:  # JUMP if equal
                r, xy = (instruction >> 8) & 0xF, instruction & 0xFF
                if self.registers[r] == self.registers[0]:
                    self.pc = xy

                if self.debug:
                    print(f"JEQ R{r:X}, {xy:02X} => PC={xy:02X} if R{r:X}==R0")

            case 12:  # HALT
                if instruction == 0xC000:
                    if self.debug:
                        print("HALT")
                    return  # Exit the run loop
                else:
                    raise ValueError(f"Invalid HALT instruction: {instruction}")
            case _:
                raise ValueError(f"Invalid opcode: {instruction >> 12}")

    def float_add(self, a, b):
        """Performs floating-point addition (implementation required)."""
        # Convert integers to floating-point numbers
        float_a = float(a)
        float_b = float(b)
        
        # Add the floating-point numbers
        result = float_a + float_b
        
        # Convert the result back to an 8-bit integer
        result_8bit = int(result) & 0xFF
        
        return result_8bit

    def show_registers(self):
        """Prints the current register values."""
        print("Registers:")
        print("      R0 R1 R2 R3 R4 R5 R6 R7 R8 R9 RA RB RC RD RE RF")
        print("  RX: ", end="")
        for val in self.registers:
            print(f"{val:02X} ", end="")
        print()

    def show_memory(self):
        """Prints the current memory contents."""
        print("Memory:")
        for i in range(0, 256, 16):
            print(f"  {i:02X}: ", end="")
            for j in range(16):
                print(f"{self.memory[i + j]:02X} ", end="")
            print()

    def run(self, step_by_step=False):
        """Runs the loaded program."""
        while True:
            instruction = self.fetch()
            self.decode_and_execute(instruction)

            if self.debug or step_by_step:
                print(f"Executed instruction: {instruction:04X}", end="")
                print(f"  IR: {self.ir:04X}", end="")
                print(f"  PC: {self.pc:02X}")
                self.show_registers()
                self.show_memory()
                input("Press Enter to continue...")

            if instruction == 0xC000:  # HALT
                break

