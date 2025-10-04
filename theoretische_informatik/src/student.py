class Student:
    def __init__(self, name: str, matriculation_number: int):
        self.name = name
        self.matriculation_number = matriculation_number

    def __eq__(self, value):
        if not isinstance(value, Student):
            return NotImplemented
        return (self.name == value.name and
                self.matriculation_number == value.matriculation_number)