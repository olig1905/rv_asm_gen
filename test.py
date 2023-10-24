#!/bin/python3

import unittest
from riscv.register import RegisterType, RegisterSaveType, Register, Registers
from riscv.csr import CSRRegister, CSRRegisters
from riscv.label import Label
from riscv.instruction import OperandType, InstructionFormat, InstructionDefinition, InstructionSet
from riscv.assembler import Assembler, OperandType

class TestAssembler(unittest.TestCase):

    def setUp(self):
        self.assembler = Assembler(seed=42)

    def test_add_instruction(self):
        # Test a simple addition instruction with registers.
        # Assuming that you have an instruction ADD in your ISA that takes two registers as operands.
        self.assembler.add_instruction('ADD', self.assembler.registers.get_register('x1'), self.assembler.registers.get_register('x2'), self.assembler.registers.get_register('x2'))
        self.assertEqual(self.assembler.code[-1], "add ra, sp, sp")

    def test_define_label(self):
        label = self.assembler.define_label('test_label')
        self.assertEqual(label.name, 'test_label')
        self.assertTrue('test_label' in self.assembler.labels)

    def test_add_label(self):
        self.assembler.add_label('label1')
        self.assertEqual(self.assembler.code[-1], "label1:")

    def test_generate_random_operand(self):
        random_operand = self.assembler.generate_random_operand(OperandType.REGISTER)
        self.assertTrue(str(random_operand.name).startswith('x'))

        random_operand = self.assembler.generate_random_operand(OperandType.IMMEDIATE)
        self.assertTrue(isinstance(random_operand, int))

        # Add more operand types if necessary

    def test_add_comment(self):
        self.assembler.add_comment('This is a test comment')
        self.assertEqual(self.assembler.code[-1], "# This is a test comment")

    def test_write_to_file(self):
        # Test that the code can be written to a file without any error.
        self.assembler.add_instruction('ADD', self.assembler.registers.get_register('x1'), self.assembler.registers.get_register('x2'), self.assembler.registers.get_register('x2'))
        self.assembler.write_to_file('test_file.asm')
        with open('test_file.asm', 'r') as f:
            content = f.readlines()
            self.assertEqual(content[0].strip(), "add ra, sp, sp")


class TestInstructionDefinition(unittest.TestCase):

    def setUp(self):
        self.add_instr = InstructionDefinition("ADD", InstructionFormat.R, "I")
        self.addi_instr = InstructionDefinition("ADDI", InstructionFormat.I, "I")
        self.register_x10 = Register("x10", type = RegisterType.X)
        self.register_x11 = Register("x11", type = RegisterType.X)
        self.label_test = Label("test_label")

    def test_generate_add_instruction(self):
        assembly = self.add_instr.generate(self.register_x10, self.register_x11, self.register_x10)
        self.assertEqual(assembly, "add x10, x11, x10")

    def test_generate_addi_instruction(self):
        assembly = self.addi_instr.generate(self.register_x10, self.register_x11, 5)
        self.assertEqual(assembly, "addi x10, x11, 0x5")

    def test_generate_instruction_with_invalid_operand(self):
        with self.assertRaises(ValueError):
            self.add_instr.generate(self.register_x10, self.register_x11, 5)  # Immediate value not expected
            
    def test_get_extension(self):
        self.assertEqual(self.add_instr.get_extension(), "I")


class TestInstructionSet(unittest.TestCase):

    def setUp(self):
        self.instruction_set = InstructionSet()

    def test_filter_by_extension(self):
        filtered_set = self.instruction_set.filter(extension="I")
        self.assertIn("ADD", filtered_set.instructions)
        self.assertIn("ADDI", filtered_set.instructions)

    def test_filter_by_mnemonic(self):
        filtered_set = self.instruction_set.filter(mnemonic="ADD")
        self.assertIn("ADD", filtered_set.instructions)
        self.assertNotIn("ADDI", filtered_set.instructions)

    def test_pick_random_instruction(self):
        random_instruction = self.instruction_set.pick_random_instruction()
        self.assertIsInstance(random_instruction, InstructionDefinition)

class TestCSRRegister(unittest.TestCase):

    def test_init(self):
        csr = CSRRegister("test", "Test CSR register", 0x400)
        self.assertEqual(csr.name, "test")
        self.assertEqual(csr.description, "Test CSR register")
        self.assertEqual(csr.address, 0x400)

    def test_str(self):
        csr = CSRRegister("test", "Test CSR register", 0x400)
        self.assertEqual(str(csr), "test (0x400): Test CSR register")


class TestCSRRegisters(unittest.TestCase):

    def setUp(self):
        self.csrs = CSRRegisters()

    def test_add_and_get_csr(self):
        self.csrs.add_csr("NEWCSR", "A new example CSR", 0x500)
        csr = self.csrs.get_csr("NEWCSR")
        self.assertEqual(csr.name, "NEWCSR")
        self.assertEqual(csr.description, "A new example CSR")
        self.assertEqual(csr.address, 0x500)

    def test_remove_csr(self):
        self.csrs.add_csr("NEWCSR", "A new example CSR", 0x500)
        self.csrs.remove_csr("NEWCSR")
        with self.assertRaises(ValueError):
            self.csrs.get_csr("NEWCSR")

    def test_load_csrs_from_list(self):
        csrs_list = [("CSR1", "Description 1", 0x501), ("CSR2", "Description 2", 0x502)]
        self.csrs.load_csrs_from_list(csrs_list)
        csr1 = self.csrs.get_csr("CSR1")
        csr2 = self.csrs.get_csr("CSR2")
        self.assertEqual(csr1.name, "CSR1")
        self.assertEqual(csr2.name, "CSR2")
        self.assertEqual(csr1.address, 0x501)
        self.assertEqual(csr2.address, 0x502)

    def test_pick_random_csr(self):
        # Initial CSRRegisters should already be there, so just pick one and check if it's a CSRRegister instance
        csr = self.csrs.pick_random_csr()
        self.assertIsInstance(csr, CSRRegister)

    def test_empty_csrs(self):
        self.csrs.registers.clear()
        with self.assertRaises(ValueError):
            self.csrs.pick_random_csr()

class TestRegisterClass(unittest.TestCase):
    
    def test_register_creation(self):
        reg = Register("x5")
        self.assertEqual(reg.name, "x5")
        self.assertEqual(reg.abi_name, "x5")
        self.assertEqual(reg.type, RegisterType.X)
        self.assertEqual(reg.saved_by, RegisterSaveType.Caller)
        self.assertFalse(reg.is_reserved)
        self.assertFalse(reg.is_in_use)

    def test_invalid_register_creation(self):
        with self.assertRaises(ValueError):
            reg = Register("y5")

    def test_register_in_use_property(self):
        reg = Register("x5")
        self.assertFalse(reg.is_in_use)
        reg.is_in_use = True
        self.assertTrue(reg.is_in_use)
        
    def test_register_reserved_property(self):
        reg = Register("x5")
        self.assertFalse(reg.is_reserved)
        reg.is_reserved = True
        self.assertTrue(reg.is_reserved)

    def test_register_string_representation(self):
        reg = Register("x5", "t0")
        expected_str = "X: x5(t0)\nSaved By: Caller\nReserved: No\nIn Use: No\n"
        self.assertEqual(str(reg), expected_str)

class TestRegistersClass(unittest.TestCase):

    def test_registers_creation(self):
        regs = Registers()
        self.assertIn("x0", regs.registers)
        self.assertIn("f5", regs.registers)

    def test_reset_usage(self):
        regs = Registers()
        reg = regs.pick_register()
        self.assertTrue(reg.is_in_use)
        regs.reset_usage()
        self.assertFalse(reg.is_in_use)

    def test_reserve_register(self):
        regs = Registers()
        reg = regs.reserve_register("x1")
        self.assertTrue(reg.is_reserved)

    def test_pick_register(self):
        regs = Registers()
        reg = regs.pick_register(type=RegisterType.X)
        self.assertTrue(reg.is_in_use)
        self.assertEqual(reg.type, RegisterType.X)

    def test_filter_registers(self):
        regs = Registers()
        filtered = regs.filter(type=RegisterType.X, saved_by=RegisterSaveType.Caller)
        for reg in filtered.registers.values():
            self.assertEqual(reg.type, RegisterType.X)
            self.assertEqual(reg.saved_by, RegisterSaveType.Caller)

    def test_get_register(self):
        regs = Registers()
        reg = regs.get_register("x1")
        self.assertEqual(reg.name, "x1")

    def test_get_register_by_abi_name(self):
        regs = Registers()
        reg = regs.get_register("ra")
        self.assertEqual(reg.name, "x1")

    def test_invalid_get_register(self):
        regs = Registers()
        reg = regs.get_register("nonexistent")
        self.assertIsNone(reg)

    def test_registers_string_representation(self):
        regs = Registers()
        self.assertIn("x0", str(regs))
        self.assertIn("f5", str(regs))

class TestLabel(unittest.TestCase):

    def test_valid_label_name(self):
        label = Label("start")
        self.assertEqual(label.name, "start")

    def test_invalid_label_name(self):
        with self.assertRaises(ValueError):
            label = Label("123start")

    def test_label_with_address(self):
        label = Label("loop", address=0x100)
        self.assertEqual(label.address, 0x100)

    def test_label_with_comment(self):
        label = Label("end", comment="This is the end label")
        self.assertEqual(label.comment, "This is the end label")

    def test_label_str_representation(self):
        label = Label("func")
        self.assertEqual(str(label), "func")

    def test_label_repr_representation(self):
        label = Label("func", address=0x200, comment="Function start")
        expected_repr = "<Label(name=func, address=0x200, comment=Function start)>"
        self.assertEqual(repr(label), expected_repr)

    def test_label_equality(self):
        label1 = Label("main")
        label2 = Label("main")
        label3 = Label("start")
        self.assertEqual(label1, label2)
        self.assertNotEqual(label1, label3)

    def test_label_is_valid_name_static_method(self):
        self.assertTrue(Label.is_valid_name("main"))
        self.assertFalse(Label.is_valid_name("123main"))

if __name__ == "__main__":
    unittest.main()