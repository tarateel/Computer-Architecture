"""CPU functionality."""

import sys

LDI = 0b10000010  # store value
PRN = 0b01000111  # print value
HLT = 0b00000001  # halt & exit
MUL = 0b10100010  # multiply


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        # Add list properties to the `CPU` class
        # hold 256 bytes of memory
        self.ram = [0] * 256
        # 8 general-purpose registers
        self.reg = [0] * 8
        # program counter
        self.pc = 0

    # accept address to read & return stored value
    def ram_read(self, MAR):  # MAR  <-- Memory Address Register
        return self.ram[MAR]

    # accept a value to write & address to write it to
    def ram_write(self, MDR, MAR):
        self.ram[MAR] = MDR  # MDR  <-- Memory Data Register

    def load(self):
        """Load a program into memory."""

        address = 0

        # For now, we've just hardcoded a program:

        # program = [
        #     # From print8.ls8
        #     0b10000010, # LDI R0,8  <-- opcode
        #     0b00000000, #  <-- operand
        #     0b00001000,  # <-- operand
        #     0b01000111,  # PRN R0  <-- opcode
        #     0b00000000,  # <-- operand
        #     0b00000001,  # HLT  <-- opcode
        # ]

        program = []

        try:
            if len(sys.argv) < 2:
                print(f'Error from {sys.argv[0]}: missing filename argument')
                print(f'Usage: python3 {sys.argv[0]} <somefilename>')
                sys.exit(1)

            with open(sys.argv[1]) as file:
                for line in file:
                    split_line = line.split('#')[0]
                    stripped_split_line = split_line.strip()

                    if stripped_split_line != '':
                        command = int(stripped_split_line, 2)
                        self.ram[address] = command
                        address += 1

        except FileNotFoundError:
            print(f'Error from {sys.argv[0]}: {sys.argv[1]} not found')
            print("(Did you double-check the file name?)")

        # for instruction in program:
        #     self.ram[address] = instruction
        #     address += 1

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""

        running = True

        while running:
            # IR = Instruction Register
            # read the memory address that's stored in register `PC`
            # store that result in `IR`
            IR = self.ram_read(self.pc)  # 'command'
            # read the bytes at `PC+1` and `PC+2` from RAM into variables `operand_a` and `operand_b`
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            # depending on the value of the opcode, perform the actions needed for the instruction per the LS-8 spec
            if IR == HLT:
                running = False
            elif IR == LDI:
                # registers[register_address] = num_to_save
                self.reg[operand_a] = operand_b
                # 3-byte command
                # print(operand_a, operand_b)
                self.pc += 3
            elif IR == PRN:
                print(self.reg[operand_a])
                # 2-byte command
                self.pc += 3
            elif IR == MUL:
                self.alu('MUL', operand_a, operand_b)
                self.pc += 3
            else:
                running = False
            # running code for any particular instruction, the `PC` needs to be updated to point to the next instruction for the next iteration of the loop

            # number of bytes an instruction uses can be determined from the two high bits (bits 6-7) of the instruction opcode
