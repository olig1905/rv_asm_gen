import random
from enum import Enum
from riscv.register import Register, RegisterType
from riscv.csr import CSRRegister
from riscv.label import Label


class OperandType(Enum):
    REGISTER = 1
    IMMEDIATE = 2
    LABEL = 3
    FREGISTER = 4
    BASE_OFFSET = 5
    CSR = 6    
    def __str__(self):
        return self.name
    
class InstructionFormat(Enum):
    """Pre-defined instruction formats."""
    R = [OperandType.REGISTER, OperandType.REGISTER, OperandType.REGISTER]
    I = [OperandType.REGISTER, OperandType.REGISTER, OperandType.IMMEDIATE]
    B = [OperandType.REGISTER, OperandType.REGISTER, OperandType.LABEL]
    U = [OperandType.REGISTER, OperandType.IMMEDIATE]
    J = [OperandType.REGISTER, OperandType.LABEL]
    FR = [OperandType.FREGISTER, OperandType.FREGISTER, OperandType.FREGISTER]
    CSR_R = [OperandType.REGISTER, OperandType.CSR, OperandType.REGISTER]
    CSR_I = [OperandType.REGISTER, OperandType.CSR, OperandType.IMMEDIATE]
    LOAD_STORE = [OperandType.REGISTER, OperandType.BASE_OFFSET]
    
    def __str__(self):
        return f"{self.name}: {', '.join([val.name for val in self.value])}"

class InstructionDefinition:
    """Defines properties and behaviors of a RISC-V instruction."""

    def __init__(self, mnemonic: str, format: InstructionFormat, extension: str):
        """
        Initialize an instruction definition.

        :param mnemonic: The instruction mnemonic.
        :param format: The operand format for the instruction.
        :param extension: The RISC-V extension this instruction belongs to.
        """
        self.mnemonic = mnemonic
        self.format = format
        self.extension = extension

    def generate(self, *operands: list) -> str:
        """
        Generate an assembly representation of the instruction with given operands.

        :param operands: The operands for the instruction.
        :return: A string representing the assembly code.
        """
        if len(operands) != len(self.format.value):
            raise ValueError(f"Expected {len(self.format.value)} operands but got {len(operands)}.")
        formatted_operands = []
        for i, operand in enumerate(operands):
            expected_type = self.format.value[i]

            if expected_type == OperandType.REGISTER:
                if not isinstance(operand, Register) or operand.type != RegisterType.X:
                    raise ValueError(f"Expected a general-purpose register for operand {i+1} but got {operand}.")
                formatted_operands.append(operand.abi_name)
            elif expected_type == OperandType.FREGISTER:
                if not isinstance(operand, Register) or operand.type != RegisterType.F:
                    raise ValueError(f"Expected a floating-point register for operand {i+1} but got {operand}.")
                formatted_operands.append(operand.abi_name)                
            elif expected_type == OperandType.CSR:
                if not isinstance(operand, CSRRegister):
                    raise ValueError(f"Expected a CSR register for operand {i+1} but got {operand}.")
                formatted_operands.append(operand.name)              
            elif expected_type == OperandType.LABEL:
                if not isinstance(operand, Label):
                    raise ValueError(f"Expected a label for operand {i+1} but got {operand}.")
                formatted_operands.append(operand.name)
            elif expected_type == OperandType.IMMEDIATE:
                if not isinstance(operand, int):
                    raise ValueError(f"Expected an integer immediate value for operand {i+1} but got {operand}.")
                formatted_operands.append(hex(operand))
            elif expected_type == OperandType.BASE_OFFSET: 
                if not isinstance(operand, tuple):
                    raise ValueError(f"Expected a tuple(offset(base)) for operand {i+1} but got {operand}.")
                base_register, offset = operand
                formatted_operands.append(f"{offset}({base_register.abi_name})")
        return f"{self.mnemonic.lower()} {', '.join(formatted_operands)}"

    def get_extension(self) -> str:
        """Retrieve the instruction's RISC-V extension."""
        return self.extension

    def __str__(self) -> str:
        return f"{self.mnemonic} - Format: {self.format} - Extension: {self.extension}"
    
    def __repr__(self) -> str:
        return self.__str__() + '\n'


class InstructionSet:
    """Represents a set of RISC-V instructions."""

    def __init__(self, instructions: dict = None, random_engine=None):
        """
        Initialize an instruction set.

        :param instructions: A dictionary of instructions to initialize with.
        :param random_engine: A random number generator.
        """
        self.random_engine = random_engine if random_engine else random
        self.instructions = instructions or self._default_instructions()

    @staticmethod
    def _default_instructions() -> dict:
        """Return a default set of RISC-V instructions."""
        return {
                "ADD": InstructionDefinition("ADD", InstructionFormat.R, "I"),
                "XOR": InstructionDefinition("XOR", InstructionFormat.R, "I"),
                "ADDI": InstructionDefinition("ADDI", InstructionFormat.I, "I"),
                "SW": InstructionDefinition("SW", InstructionFormat.LOAD_STORE, "I"),
                "BEQ": InstructionDefinition("BEQ", InstructionFormat.B, "I"),
                "LUI": InstructionDefinition("LUI", InstructionFormat.U, "I"),
                "JAL": InstructionDefinition("JAL", InstructionFormat.J, "I"),
                "FADD.S": InstructionDefinition("FADD.S", InstructionFormat.FR, "F"),
                "CSRRW": InstructionDefinition("CSRRW", InstructionFormat.CSR_R, "I"),
                "CSRRCI": InstructionDefinition("CSRRCI", InstructionFormat.CSR_I, "I"),
                "LW": InstructionDefinition("LW", InstructionFormat.LOAD_STORE, "I"),
            }

    def filter(self, extension: str = None, mnemonic: str = None, format: list = None) -> 'InstructionSet':
        """
        Filter the instruction set based on given criteria.

        :param extension: The RISC-V extension.
        :param mnemonic: The instruction mnemonic.
        :param format: The instruction format.
        :return: A filtered instruction set.
        """
        filtered_instructions = dict(filter(lambda instr: (
            (not extension or instr[1].get_extension() == extension) and
            (not mnemonic or instr[1].mnemonic == mnemonic) and
            (not format or instr[1].format == format)
        ), self.instructions.items()))
        return InstructionSet(filtered_instructions)  

    def pick_random_instruction(self, extension: str = None, format: list = None, specific_list: list = None) -> 'InstructionDefinition':
        """
        Pick a random instruction from the set based on provided criteria.

        :param extension: The RISC-V extension.
        :param format: The instruction format.
        :param specific_list: A list of specific instruction mnemonics to choose from.
        :return: A randomly picked instruction definition.
        """
        if specific_list:
            available_instructions = {instr: self.instructions[instr] for instr in specific_list if instr in self.instructions}
        else:
            available_instructions = self.filter(extension=extension, format=format).instructions

        return self.random_engine.choice(list(available_instructions.values())) if available_instructions else None
