"""CPU functionality."""

import sys

LDI = 0b10000010  # store value
PRN = 0b01000111  # print value
HLT = 0b00000001  # halt & exit
MUL = 0b10100010  # multiply
PUSH = 0b01000101
POP = 0b01000110
CALL = 0b01010000
RET = 0b00010001


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        # Add list properties to the `CPU` class
        self.ram = [0] * 256  # hold 256 bytes of memory (RAM)
        self.reg = [0] * 8  # 8 general-purpose registers (R0 - R7)
        self.pc = 0  # program counter
        self.sp = 7  # stack pointer
        self.reg[7] = 0xF4  # top of stack or `F4` if stack is empty
        self.ir = 0 # instruction register
        self.mar = 0 # memory address register
        self.mdr = 0 # memory data register
        self.hlt = False

    # accept address to read & return stored value
    def ram_read(self, mar):  # mar  <-- Memory Address Register
        return self.ram[mar]

    # accept a value to write & address to write it to
    def ram_write(self, mdr, mar):
        self.ram[mar] = mdr  # mdr  <-- Memory Data Register

    def load(self):
        """Load a program into memory."""
        mar = 0
        # print error message & exit if filename not in command line
        try:
            if len(sys.argv) < 2:
                print(f'Error from {sys.argv[0]}: missing filename argument')
                print(f'Usage: python3 {sys.argv[0]} <somefilename>')
                sys.exit(1)
        # open file, remove comments & empty lines
            with open(sys.argv[1]) as file:
                for line in file:
                    split_line = line.split('#')[0]
                    num = split_line.strip()

                    if num != '':
                        command = int(num, 2)
                        self.ram[mar] = command
                        mar += 1

        # # print error message if filename is incorrect
        except FileNotFoundError:
            print(f'Error from {sys.argv[0]}: {sys.argv[1]} not found')
            print("(Did you double-check the file name?)")

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
        while not self.hlt:
            # IR = Instruction Register
            ir = self.ram_read(self.pc)
            # `operand_a` and `operand_b` renamed reg_a and reg_b
            reg_a = self.ram_read(self.pc + 1)
            reg_b = self.ram_read(self.pc + 2)
            self.commands(ir, reg_a, reg_b)
    
    def commands(self, ir, reg_a, reg_b):
        if ir == HLT:
            self.hlt = True
        elif ir == LDI:
            # registers[register_address] = num_to_save
            self.reg[reg_a] = reg_b
            # 3-byte command
            # print(reg_a, reg_b)
            self.pc += 3
        elif ir == PRN:
            print(self.reg[reg_a])
            # 2-byte command
            self.pc += 2
        elif ir == MUL:
            self.alu('MUL', reg_a, reg_b)
            self.pc += 3
        elif ir == PUSH:
            self.reg[self.sp] -= 1
            reg_value = self.ram[self.pc + 1]
            mdr = self.reg[reg_value]
            mar = self.reg[self.sp]
            self.ram[mar] = mdr
            self.pc += 2
        elif ir == POP:
            reg_value = self.ram[self.pc + 1]
            mar = self.reg[self.sp]
            mdr = self.ram[mar]
            self.reg[reg_value] = mdr
            self.reg[self.sp] += 1
            self.pc += 2
        else:
            print(f'Error: Unknown {(ir)}')
            self.pc += 1
