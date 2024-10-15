from typing import List, Set, Tuple

class Human:
    def __init__(self, name: str) -> None:
        self.name = name

    def __str__(self) -> str:
        return f"This is a human named {self.name}"

    def __eq__(self, other) -> bool:
        return self.name == other.name

class Student(Human):
    def __init__(self, name: str, id: int) -> None:
        super().__init__(name)
        self.id = id

    def __str__(self) -> str:
        return f"This is a student named {self.name} with id {self.id}"

def test(n: int) -> int: 
    if n>0:
        return 0
    else:
        return 1

if __name__ == '__main__':
    h = Student("Isabelle", 1) 
    h2 = Human("Isabelle") 
    print(h)