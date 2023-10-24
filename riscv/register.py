import random
from enum import Enum

class RegisterType(Enum):
    X = 1
    F = 2

class RegisterSaveType(Enum):
    Caller = 1
    Callee = 2
    System = 3

class Register:
    def __init__(
        self,
        name,
        abi_name=None,
        type=RegisterType.X,
        saved_by=RegisterSaveType.Caller,
        is_reserved=False,
        is_in_use=False,
    ):
        # Validate name (assuming it starts with x or f, followed by a number)
        if not (name.startswith("x") or name.startswith("f")) or not name[1:].isdigit():
            raise ValueError(f"Invalid register name: {name}")

        # Validate type
        if not isinstance(type, RegisterType):
            raise ValueError(
                f"Invalid register type: {type}. Expected one of {', '.join(RegisterType)}."
            )

        # Validate saved_by
        if not isinstance(saved_by, RegisterSaveType):
            raise ValueError(
                f"Invalid saved_by value: {saved_by}. Expected one of {', '.join(RegisterSaveType)}."
            )

        self.name = name
        if abi_name:
            self.abi_name = abi_name
        else:
            self.abi_name = name
        self.type = type
        self.saved_by = saved_by
        self._is_reserved = is_reserved
        self._is_in_use = is_in_use
    @property
    def is_in_use(self):
        return self._is_in_use

    @is_in_use.setter
    def is_in_use(self, value):
        self._is_in_use = value

    @property
    def is_reserved(self):
        return self._is_reserved

    @is_reserved.setter
    def is_reserved(self, value):
        self._is_reserved = value


    def __str__(self):
        return (
            f"{self.type.name}: {self.name}({self.abi_name})\n"
            + f"Saved By: {self.saved_by.name}\n"
            + f"Reserved: {'Yes' if self.is_reserved else 'No'}\n"
            + f"In Use: {'Yes' if self.is_in_use else 'No'}\n"
        )
    
class Registers:
    def __init__(self, registers=None, random_engine=None):
        self.random_engine = random_engine if random_engine else random
        if registers:
            self.registers = registers
        else:
            # Initializing integer and F registers as per RISC-V calling conventions
            self.registers = {
                "x0": Register("x0", "zero", is_reserved=True),
                "x1": Register("x1", "ra", saved_by=RegisterSaveType.Caller, is_reserved=True),
                "x2": Register("x2", "sp", saved_by=RegisterSaveType.System, is_reserved=True),
                "x3": Register("x3", "gp", saved_by=RegisterSaveType.System, is_reserved=True),
                "x4": Register("x4", "tp", saved_by=RegisterSaveType.System, is_reserved=True),
            }
            # Integer temporaries: Caller-saved
            for i in range(5, 8):
                self.registers[f"x{i}"] = Register(
                    f"x{i}", f"t{i-5}", saved_by=RegisterSaveType.Caller
                )

            # Integer saved registers: Callee-saved
            for i in range(8, 10):
                self.registers[f"x{i}"] = Register(
                    f"x{i}", f"s{i-8}", saved_by=RegisterSaveType.Callee
                )

            # Integer function arguments/return values: Caller-saved
            for i in range(10, 18):
                self.registers[f"x{i}"] = Register(
                    f"x{i}", f"a{i-10}", saved_by=RegisterSaveType.Caller
                )

            # More integer saved registers: Callee-saved
            for i in range(18, 28):
                self.registers[f"x{i}"] = Register(
                    f"x{i}", f"s{i-8}", saved_by=RegisterSaveType.Callee
                )

            # More integer temporaries: Caller-saved
            for i in range(28, 32):
                self.registers[f"x{i}"] = Register(
                    f"x{i}", f"t{i-23}", saved_by=RegisterSaveType.Caller
                )

            # F function arguments/return values: Caller-saved
            for i in range(8):
                self.registers[f"f{i}"] = Register(
                    f"f{i}", f"ft{i}", type=RegisterType.F, saved_by=RegisterSaveType.Caller
                )

            # Additional F function arguments: Caller-saved
            for i in range(10, 18):
                self.registers[f"f{i}"] = Register(
                    f"f{i}", f"fa{i-10}", type=RegisterType.F, saved_by=RegisterSaveType.Caller
                )

            # F callee-saved registers
            for i in range(8, 32):
                self.registers[f"f{i}"] = Register(
                    f"f{i}", f"fs{i-8}", type=RegisterType.F, saved_by=RegisterSaveType.Callee
                )

    def reset_usage(self):
        for reg in self.registers.values():
            reg.is_in_use = False
            reg.is_reserved = False

    def reserve_register(self, name):
        """Reserve a specified register."""
        reg = self.get_register(name)
        if not reg:
            raise ValueError(f"Invalid register name: {name}")
        reg.is_reserved = True
        return reg

    def pick_register(
        self, type=None, saved_by=None, is_reserved=False, is_in_use=None, reserve=False
    ):
        """Pick a random register based on the given preference and set its state to used."""
        try:
            regs = self.filter(type, saved_by, is_reserved, is_in_use)
        except:
            raise ValueError(f"No appropriate register found")
        try:
            unused_regs = regs.filter(is_in_use=False)
            regs_list = list(unused_regs.registers.values())
        except ValueError:
            regs_list = list(regs.registers.values())
        chosen_reg = self.random_engine.choice(regs_list)
        chosen_reg.is_in_use = True
        if reserve:
            chosen_reg.is_reserved = True
        return chosen_reg

    def filter(self, type=None, saved_by=None, is_reserved=None, is_in_use=None):
        """Retrieve a subset of registers based on the specified criteria and return as a new instance."""
        subset = (
            self.registers.values()
            if type is None
            else [reg for reg in self.registers.values() if reg.type == type]
        )
        if saved_by is not None:
            subset = [reg for reg in subset if reg.saved_by == saved_by]
        if is_reserved is not None:
            subset = [reg for reg in subset if reg.is_reserved == is_reserved]
        if is_in_use is not None:
            subset = [reg for reg in subset if reg.is_in_use == is_in_use]
        if not subset:
            raise ValueError(f"No registers matching the filter were found")
        # Create a new XRegisters instance with the filtered subset.
        subset_dict = {reg.name: reg for reg in subset}
        return Registers(subset_dict, self.random_engine)

    def get_register(self, name):
        """Get a specific register by its name."""
        reg = self.registers.get(name, None)
        if reg is None:
            for abi_reg in self.registers.values():
                if abi_reg.abi_name == name:
                    return abi_reg
        return reg

    def __str__(self):
        return "\n".join(str(reg) for reg in self.registers.values())