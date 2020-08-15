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
        self.sp = 7
        self.FLG = 0b00000000

        self.branch_table = {
            0b00000001: self.op_HLT,
            0b10000010: self.op_LDI,
            0b01000111: self.op_PRN,
            0b10100010: self.op_MUL,
            0b01000101: self.op_PUSH,
            0b01000110: self.op_POP,
            0b10100111: self.op_CMP,
            0b01010100: self.op_JMP,
            0b01010101: self.op_JEQ,
            0b01010110: self.op_JNE
        }

    def ram_read(self, MAR):
        MDR = self.ram[MAR]
        return MDR

    def ram_write(self, MAR, MDR):
        self.ram[MAR] = MDR

    def load(self):
        """Load a program into memory."""
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

        elif op == "CMP":
            if self.reg[reg_a] > self.reg[reg_b]:
                # modify sevent bit if a > b
                self.FLG = 0b00000010
            if self.reg[reg_a] < self.reg[reg_b]:
                # modify sixth bit if b < a
                self.FLG = 0b00000100
            else:
                # modfy 8th bit if equal
                self.FLG = 0b00000001
        else:
            raise Exception("Unsupported ALU operation")

    def op_CMP(self):
        operand_a, operand_b = self.return_operands()
        self.alu('CMP',  operand_a, operand_b)
        self.pc += 3

    def op_JMP(self):
        operand_a, _ = self.return_operands()
        self.pc = self.reg[operand_a]

    def op_JEQ(self):
        if self.FLG == 0b00000001:
            self.op_JMP()
        else:
            self.pc += 2

    def op_JNE(self):
        if self.FLG != 0b00000001:
            self.op_JMP()
        else:
            self.pc += 2

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
                print('Error Instruction!')
                sys.exit(1)
