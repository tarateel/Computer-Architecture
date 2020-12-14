"""CPU functionality."""

import sys

LDI = 0b10000010  # store value (3-byte)
PRN = 0b01000111  # print value (2-byte)
HLT = 0b00000001  # halt & exit
PUSH = 0b01000101  # (2-byte)
POP = 0b01000110  # (2-byte)
CALL = 0b01010000  # (2-byte)
RET = 0b00010001

MUL = 0b10100010  # multiply (3-byte) alu operation
CMP = 0b10100111 # (3-byte) alu operation
JMP = 0b01010100 # (2-byte)
JEQ = 0b01010101 # (2-byte)
JNE = 0b01010110 # (2-byte)
ADD = 0b10100000

SP = 7

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        # Add list properties to the `CPU` class
        self.ram = [0] * 256  # hold 256 bytes of memory (RAM)
        self.reg = [0] * 8  # 8 general-purpose registers (R0 - R7)
        self.pc = 0  # program counter
        self.reg[SP] = 0xF4  # stack pointer: top of stack or `F4` if stack is empty
        self.fl = 0b00000000 # 'equal' flag set to zero

    # accept address to read & return stored value
    def ram_read(self, address):  # mar  <-- Memory Address Register
        return self.ram[address]

    # accept a value to write & address to write it to
    def ram_write(self, value, address):
        self.ram[address] = value  # mdr  <-- Memory Data Register

    def load(self):
        """Load a program into memory."""
        address = 0
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
                        self.ram[address] = command
                        address += 1

        # # print error message if filename is incorrect
        except FileNotFoundError:
            print(f'Error from {sys.argv[0]}: {sys.argv[1]} not found')
            print("(Did you double-check the file name?)")

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == ADD:
            self.reg[reg_a] += self.reg[reg_b]
        elif op == MUL:
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == CMP:
            # `FL` bits: `00000LGE`
            # * `L` Less-than: during a `CMP`, set to 1 if registerA is less than registerB,
            # zero otherwise.
            # * `G` Greater-than: during a `CMP`, set to 1 if registerA is greater than
            # registerB, zero otherwise.
            # * `E` Equal: during a `CMP`, set to 1 if registerA is equal to registerB, zero
            # otherwise.
            if self.reg[reg_a] == self.reg[reg_b]:
                self.fl = 0b00000001  # E flag
            elif self.reg[reg_a] > self.reg[reg_b]:
                self.fl = 0b0000010  # G flag
            elif self.reg[reg_a] < self.reg[reg_b]:
                self.fl = 0b00000100  # L flag
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            self.fl,
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
            IR = self.ram_read(self.pc)
            # `operand_a` and `operand_b` renamed reg_a and reg_b
            reg_a = self.ram_read(self.pc + 1)
            reg_b = self.ram_read(self.pc + 2)
            
            if IR == HLT:
                running = False
            
            elif IR == LDI:
                self.reg[reg_a] = reg_b
                
            elif IR == PRN:
                print(self.reg[reg_a])
                
            elif IR == MUL:
                self.alu(IR, reg_a, reg_b)
                
            elif IR == PUSH:
                self.reg[SP] -= 1
                self.ram[self.reg[SP]] = self.reg[reg_a]
                
            elif IR == POP:
                self.reg[reg_a] = self.ram[self.reg[self.sp]]
                self.reg[SP] += 1
                
            elif IR == CALL:
                self.reg[SP] -= 1
                shift_to = self.pc + (IR >> 6) + 1
                self.ram[self.reg[SP]] = shift_to
                self.pc = self.reg[reg_a]
                continue
                
            elif IR == RET:
                ret_value = self.ram[self.reg[SP]]
                self.pc = ret_value
                self.reg[SP] += 1
                continue
                
            elif IR ==CMP:
                self.alu(IR, reg_a, reg_b)
            
            elif IR == JMP:
                self.pc = self.reg[reg_a]
                continue
            
            elif IR == JEQ:
                if self.fl == 1:
                    self.pc = self.reg[reg_a]
                    continue
                    
            elif IR == JNE:
                if self.fl != 1:
                    self.pc = self.reg[reg_a]
                    continue
                    
            else:
                print(f'Error: Unknown command')
                running = False

            self.pc += (IR >> 6) + 1
