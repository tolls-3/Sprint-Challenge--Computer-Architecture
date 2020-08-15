"""CPU functionality."""

import sys


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc = 0
        self.running = True
        self.fl = 0
        self.sp = 7

        self.branch_table = {
            0b00000001: self.op_HLT,
            0b10000010: self.op_LDI,
            0b01000111: self.op_PRN,
            0b10100010: self.op_MUL,
            0b01000101: self.op_PUSH,
            0b01000110: self.op_POP
        }

    def ram_read(self, MAR):
        MDR = self.ram[MAR]
        return MDR

    def ram_write(self, MAR, MDR):
        self.ram[MAR] = MDR

    def load(self):
        """Load a program into memory."""

        # address = 0

        # # # For now, we've just hardcoded a program:

        # program = [
        #     0b10000010,  # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b10000010,  # LDI R1,9
        #     0b00000001,
        #     0b00001001,
        #     0b10100010,  # MUL R0,R1
        #     0b00000000,
        #     0b00000001,
        #     0b01000111,  # PRN R0
        #     0b00000000,
        #     0b00000001,  # HLT
        # ]

        # program = [
        #     # From print8.ls8
        #     0b10000010,  # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111,  # PRN R0
        #     0b00000000,
        #     0b00000001,  # HLT
        # ]

        # for instruction in program:
        #     self.ram[address] = instruction
        #     address += 1

        filename = sys.argv[1]
        try:
            address = 0
            with open(filename) as f:
                for line in f:
                    line = line.split('#')[0]
                    command = line.strip()
                    if command == '':
                        continue
                    instruction = int(command, 2)
                    self.ram_write(address, instruction)

                    address += 1
        except FileNotFoundError:
            print(f'{sys.argv[0]}: {sys.argv[1]} file was not found')
            sys.exit()

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        # elif op == "SUB": etc
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
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def ldi(self, operand_a, operand_b):
        self.reg[operand_a] = operand_b

    def prn(self, operand_a):
        print(operand_a)

    def return_operands(self):
        operand_a = self.ram_read(self.pc + 1)
        operand_b = self.ram_read(self.pc + 2)
        return operand_a, operand_b

    def op_LDI(self):
        operand_a, operand_b = self.return_operands()
        self.ldi(operand_a, operand_b)
        self.pc += 3

    def op_PRN(self):
        operand_a, _ = self.return_operands()
        self.prn(self.reg[operand_a])
        self.pc += 2

    def op_MUL(self):
        operand_a, operand_b = self.return_operands()
        self.alu('MUL', operand_a, operand_b)
        self.pc += 3

    def op_HLT(self):
        self.running = False

    def op_PUSH(self):
        self.reg[self.sp] -= 1
        stack_address = self.reg[self.sp]
        register_number = self.ram_read(self.pc + 1)
        register_number_value = self.reg[register_number]
        self.ram_write(stack_address, register_number_value)
        self.pc += 2

    def op_POP(self):
        stack_value = self.ram_read(self.reg[self.sp])
        register_number = self.ram_read(self.pc + 1)
        self.reg[register_number] = stack_value
        self.reg[self.sp] += 1
        self.pc += 2

    def run(self):
        """Run the CPU."""
        while self.running:
            IR = self.ram_read(self.pc)

            if IR in self.branch_table:
                self.branch_table[IR]()
            else:
                print('Error or something like that!')
                self.op_HLT()
