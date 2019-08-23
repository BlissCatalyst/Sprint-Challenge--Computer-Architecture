"""CPU functionality."""

import sys

HLT = 0b00000001
LDI = 0b10000010
PRN = 0b01000111
MUL = 0b10100010
PUSH = 0b01000101
POP = 0b01000110
CALL = 0b01010000
RET = 0b00010001
CMP = 0b10100111
JMP = 0b01010100
JEQ = 0b01010101
JNE = 0b01010110

if len(sys.argv) != 2:
    print("usage: file.py <filename>", file=sys.stderr)
    sys.exit(1)

filepath = sys.argv[1]


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.reg = [0] * 8
        self.reg[7] = 0xF4
        self.ram = [0] * 256
        self.pc = 0
        self.fl = 0b00000000
        self.branchtable = {}
        self.branchtable[MUL] = self.alu

    def load(self):
        """Load a program into memory."""
        if len(sys.argv) != 2:
            print("usage: file.py <filename>", file=sys.stderr)
            sys.exit(1)

        filepath = sys.argv[1]

        try:
            address = 0

            with open(filepath) as f:
                for line in f:
                    # print(f'line: {line}')
                    # Split before and after any comment symbols
                    comment_split = line.split("#")
                    # print(f'comment_split: {comment_split}')

                    num = comment_split[0].strip()
                    # print(f'num: {num}')
                    # Ignore blanks
                    if num == "":
                        continue

                    value = int(num, 2)

                    self.ram[address] = value

                    address += 1

        except FileNotFoundError:
            print(f"{sys.argv[0]}: {sys.argv[1]} not found")
            sys.exit(2)

    def push(self, register):
        self.reg[7] -= 1
        self.ram_write(self.reg[register], self.reg[7])

    def pop(self, register):
        self.reg[register] = self.ram_read(self.reg[7])
        self.reg[7] += 1

    def ram_read(self, read_address):
        return self.ram[read_address]

    def ram_write(self, write_value, write_address):
        self.ram[write_address] = write_value

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        # elif op == "SUB": etc
        elif op == "MUL":
            self.reg[reg_a] = self.reg[reg_a] * self.reg[reg_b]
        elif op == "CMP":
            if self.reg[reg_a] == self.reg[reg_b]:
                self.fl = self.fl | 0b00000001
            elif self.reg[reg_a] < self.reg[reg_b]:
                self.fl = self.fl | 0b00000100
            elif self.reg[reg_a] > self.reg[reg_b]:
                self.fl = self.fl | 0b00000010
            else:
                self.fl = 0b0
                print("Not Compared")
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        self.load()
        while True:
            instrReg = self.ram_read(self.pc)
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            # COMMANDS
            if instrReg == HLT:
                print("HLT")
                exit()
            elif instrReg == LDI:
                print("LDI")
                self.reg[operand_a] = operand_b
                print(f"REGISTER: {self.reg}")
            elif instrReg == PRN:
                print("PRN")
                print(f"Register: {operand_a}, Value: {self.reg[operand_a]}")
            elif instrReg == MUL:
                print("MUL")
                self.alu("MUL", operand_a, operand_b)
            elif instrReg == PUSH:
                print("PUSH")
                self.push(operand_a)
            elif instrReg == POP:
                print("POP")
                self.pop(operand_a)
            elif instrReg == CALL:
                print("CALL")
                pass
            elif instrReg == RET:
                print("RET")
                pass
            elif instrReg == CMP:
                print("CMP")
                self.alu("CMP", operand_a, operand_b)
            elif instrReg == JMP:
                print("JMP")
                self.pc = self.reg[operand_a]
                continue
            elif instrReg == JEQ:
                print("JEQ")
                shifter = self.fl
                shifter = shifter << 7
                if shifter == 0b10000000:
                    self.pc = operand_a
                    self.fl = 0
                    continue
            elif instrReg == JNE:
                print("JNE")
                shifter = self.fl
                shifter = shifter << 7
                if shifter == 0b0:
                    self.pc = operand_a
                    self.fl = 0
                    continue

            change_pc = instrReg
            change_pc = change_pc >> 6
            if change_pc == 0b01:
                self.pc += 2
            elif change_pc == 0b10:
                self.pc += 3
            elif change_pc == 0b00:
                self.pc += 1
            else:
                print("There should not be 3 operands!")
