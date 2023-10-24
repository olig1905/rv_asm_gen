import random

class CSRRegister:
    def __init__(self, name: str, description: str, address: int):
        self.name = name
        self.description = description
        self.address = address  # Now an integer

    def __str__(self):
        return f"{self.name} (0x{self.address:03x}): {self.description}"

class CSRRegisters:
    def __init__(self, random_engine=None):
        self.random_engine = random_engine if random_engine else random
        self.registers = {
            "MSTATUS": CSRRegister("mstatus", "Machine status register", 0x300),
            "MIE": CSRRegister("mie", "Machine interrupt-enable register", 0x304),
            "MTVEC": CSRRegister("mtvec", "Machine trap-handler base address", 0x305),
        }

    def add_csr(self, name: str, description: str, address: int):
        """Add a CSR to the register set."""
        self.registers[name.upper()] = CSRRegister(name, description, address)

    def remove_csr(self, name: str):
        """Remove a CSR from the register set."""
        if name.upper() in self.registers:
            del self.registers[name.upper()]
        else:
            raise ValueError(f"No CSR named {name} found.")

    def get_csr(self, name: str) -> CSRRegister:
        """Retrieve a CSR by name."""
        csr = self.registers.get(name.upper(), None)
        if not csr:
            raise ValueError(f"No CSR named {name} found.")
        return csr

    def pick_random_csr(self) -> CSRRegister:
        """Pick a random CSR from the register set."""
        if not self.registers:
            raise ValueError("No CSRRegisters available to pick from.")
        return self.random_engine.choice(list(self.registers.values()))

    def load_csrs_from_list(self, csr_list: list):
        """Load multiple CSRRegisters from a list of tuples."""
        for item in csr_list:
            if len(item) != 3:
                raise ValueError(f"Expected each item in csr_list to be a tuple of (name, description, address), but got {item}.")

            name, description, address = item
            self.add_csr(name, description, address)

    def __str__(self):
        return "\n".join(str(reg) for reg in self.registers.values())