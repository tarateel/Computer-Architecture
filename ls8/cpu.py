"""CPU functionality."""

import sys

# OPCODES
LDI = 0b10000010 # store value
PRN = 0b01000111 # print value
HLT = 0b00000001 # halt & exit
MUL = 0b10100010  # multiply

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        # Add list properties to the `CPU` class
        self.ram = [0] * 256  # hold 256 bytes of memory (RAM)
        self.reg = [0] * 8  # 8 general-purpose registers (R0 - R7)
        self.pc = 0  # program counter
        self.sp = 7  # stack pointer
        
        self.branchtable = {  # branch/dispatch table: pointers to functions or methods
            LDI: self.ldi,
            PRN: self.prn,
            MUL: self.mul
        }

    # accept address to read & return stored value
    def ram_read(self, mar):  # MAR  <-- Memory Address Register
        return self.ram[mar]

    # accept a value to write & address to write it to
    def ram_write(self, mdr, mar):
        self.ram[mar] = mdr  # MDR  <-- Memory Data Register

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
    
    def ldi(self, operand_a, operand_b):
        self.reg[operand_a] = operand_b
        self.pc += 3
    
    def prn(self, operand_a, operand_b):
        print(self.reg[operand_a])
        self.pc += 3
    
    def mul(self, operand_a, operand_b):
        self.alu('MUL', operand_a, operand_b)
        self.pc += 3

    def run(self):
        """Run the CPU."""
        running = True
        while running:
            # IR = Instruction Register
            # read the memory address that's stored in register `PC`
            # store that result in `IR`
            ir = self.ram_read(self.pc) # 'command'
            # read the bytes at `PC+1` and `PC+2` from RAM into variables `operand_a` and `operand_b`
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)
            if ir == HLT:
                running = False
            else:
                self.branchtable[ir](operand_a, operand_b)
    
            # running code for any particular instruction, the `PC` needs to be updated to point to the next instruction for the next iteration of the loop
            
            # number of bytes an instruction uses can be determined from the two high bits (bits 6-7) of the instruction opcode
