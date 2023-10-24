class Label:
    def __init__(self, name, address=None, comment=None):
        """
        Initializes a Label object.
        
        Args:
        - name (str): The name of the label.
        - address (int, optional): The memory address or location of the label.
        - comment (str, optional): Any associated comments or descriptions for the label.
        """
        if not self.is_valid_name(name):
            raise ValueError(f"Invalid label name: {name}")
        self.name = name
        self.address = address
        self.comment = comment

    @staticmethod
    def is_valid_name(name):
        """
        Validates the label name.
        This is a basic validation to ensure the label doesn't start with a number.
        More rules can be added as needed.
        """
        if name[0].isdigit():
            return False
        return True

    def __str__(self):
        """Returns the name of the label."""
        return self.name

    def __repr__(self):
        """Returns a representation of the label object for debugging."""
        return f"<Label(name={self.name}, address={hex(self.address)}, comment={self.comment})>"

    def __eq__(self, other):
        """Checks if two labels are the same based on their names."""
        if isinstance(other, Label):
            return self.name == other.name
        return False
