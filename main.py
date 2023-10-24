#!/bin/python3

import argparse

from riscv.register import Registers
from riscv.register import RegisterType
from riscv.register import RegisterSaveType


from riscv.instruction import InstructionSet
from riscv.instruction import InstructionFormat
from riscv.csr import CSRRegisters
from riscv.assembler import Assembler

def tc_01():
    all_registers = Registers()
    reg = all_registers.filter(type=RegisterType.X, saved_by=RegisterSaveType.Caller).pick_register(reserve=True)
    print(reg)

def tc_02():
    # Instantiate the InstructionSet class:
    regs = Registers()
    isa = InstructionSet()
    acc_reg = regs.pick_register(type=RegisterType.X, reserve=True)
    rd = regs.pick_register(type=RegisterType.X)
    for i in range(10):
        rs1 = rd
        rs2 = regs.pick_register(type=RegisterType.X)
        rd = regs.pick_register(type=RegisterType.X)
        print(isa.instructions["ADD"].generate(rd, rs1, rs2))
        print(isa.instructions["XOR"].generate(acc_reg, acc_reg, rd))


def tc_03():
    assembler = Assembler()
    for i in range(100):
        chosen_instr = assembler.isa.pick_random_instruction()        
        operands = [assembler.generate_random_operand(op_type) for op_type in chosen_instr.format.value]
        assembler.add_instruction(chosen_instr.mnemonic, *operands)
    assembler.write_to_file("random_asm_output.asm")

def tc_04():
    assembler = Assembler(seed=0)
    assembler.add_comment("Test 04")
    assembler.add_label("test_04")
    instructions = InstructionSet(instructions=assembler.isa.filter(format=InstructionFormat.R).instructions | assembler.isa.filter(format=InstructionFormat.I).instructions)
    acc_reg = assembler.registers.pick_register(type=RegisterType.X, reserve=True)
    rd = assembler.registers.pick_register(type=RegisterType.X)

    for i in range(100):
        rs1 = rd
        rd = assembler.registers.pick_register(type=RegisterType.X)
        chosen_instr = instructions.pick_random_instruction()
        rs2 = assembler.generate_random_operand(chosen_instr.format.value[2])
        operands = [rd, rs1, rs2]
        assembler.add_instruction(chosen_instr.mnemonic, *operands)
        operands = [acc_reg, acc_reg, rd]
        assembler.add_instruction("XOR", *operands)
    assembler.write_to_file("random_asm_output.asm")
    
def tc_05():
    isa=InstructionSet()
    print(isa.instructions)

def main(args):
    # Compute the sum of the two numbers
    print(f"tc is {args.tc}")
    match args.tc:
        case 1:
            print("First Registers Class Demo")
            tc_01()
        case 2:
            print("First InstructionSet Class Demo")
            tc_02()
        case 3:
            print("First Assembler Class Demo")
            tc_03()
        case 4:
            print("Second Assembler Class Demo")
            tc_04()
        case 5:
            print("Second Assembler Class Demo")
            tc_05()
        case _:
            print("tc not implemented")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Demo For RV GEN")
    # Adding expected arguments
    parser.add_argument("tc", type=int, help="Test case to run")
    # Parsing command line arguments
    args = parser.parse_args()

    main(args)
