from riscv.instruction import InstructionSet
from riscv.instruction import OperandType
from riscv.register import Registers, RegisterType
from riscv.label import Label
from riscv.csr import CSRRegisters

import random

class Assembler:
    def __init__(self, seed=None):
        self.random_engine = random.Random(seed)
        self.isa = InstructionSet(random_engine=self.random_engine)
        self.registers = Registers(random_engine=self.random_engine)
        self.csrs = CSRRegisters(random_engine=self.random_engine)
        self.code = []
        self.labels = {}  # To keep track of defined labels

    def add_instruction(self, instruction, *operands):
        try:
            instr_str = self.isa.instructions[instruction.upper()].generate(*operands)
            print(instr_str)
            self.code.append(instr_str)
        except Exception as e:
            raise ValueError(f"Error adding instruction {instruction} with operands {operands}. {str(e)}")

    def define_label(self, label_name):
        if label_name not in self.labels:
            self.labels[label_name] = Label(label_name)
            return self.labels[label_name]
        else:
            raise ValueError(f"Label {label_name} already exists.")
        
    def add_label(self, label_name):
        if label_name not in self.labels:
            self.define_label(label_name)
        self.code.append(f"{self.labels[label_name]}:")
        return self.labels[label_name]

        
    def generate_random_operand(self, operand_type):
        if operand_type == OperandType.REGISTER:
            return self.registers.pick_register(type=RegisterType.X)
        elif operand_type == OperandType.FREGISTER:
            return self.registers.pick_register(type=RegisterType.F)
        elif operand_type == OperandType.CSR:
            return self.csrs.pick_random_csr()
        elif operand_type == OperandType.IMMEDIATE:
            return self.random_engine.randint(0x0, 0xFFFFFFFF)  # Example range
        elif operand_type == OperandType.LABEL:
            return self.define_label(f"label_{random.randint(0, 1000)}")
        elif operand_type == OperandType.BASE_OFFSET:
            return (self.registers.pick_register(type=RegisterType.X), self.random_engine.randint(0x0, 0xFFFFFFFF))
        # Add more operand types if necessary

    def add_comment(self, comment):
        self.code.append(f"# {comment}")

    def write_to_file(self, filename):
        with open(filename, 'w') as file:
            for line in self.code:
                file.write(line + "\n")