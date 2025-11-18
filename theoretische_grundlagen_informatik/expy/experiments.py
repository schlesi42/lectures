class Human:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def introduce(self):
        return f"Hello, my name is {self.name} and I am {self.age} years old."

class Student(Human):
    def __init__(self, name, age, immatriculation_number):
        super().__init__(name, age)
        self.immatriculation_number = immatriculation_number
    def introduce(self):
        return f"Hello, I am a Student, my name is {self.name} and my immatriculation number is {self.immatriculation_number}."
    
    def __eq__(self, other):
        if not isinstance(other, Student):
            return NotImplemented
        return (self.immatriculation_number == other.immatriculation_number)

s1 = Student("Alice", 20, 1)
s2 = Student("Alice", 20, 1)
print(s1 == s2)