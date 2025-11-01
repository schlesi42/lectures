l = [1, 2, 3]
print(l[0])  # Output: 1
print(l[1:])  # Output: [2, 3]
print(l[-1])  # Output: 3
l = [x * 2 for x in l]
print(l)      # Output: [2, 4, 6]
s = {1,1,2,3,1,2}
print(s)      # Output: {1, 2, 3}
d = {'a': 1, 'b': 2}
print(d['a']) # Output: 1
d['c'] = 3
print(d)      # Output: {'a': 1, 'b': 2, 'c': 3}


class Human:
    def __init__(self, name: str):
        self.name = name
    

    def __str__(self) -> str:
        return f"Human(name={self.name})"

class Student(Human):
    def __init__(self, name: str, id: int):
        super().__init__(name)
        self.id = id

    def __str__(self) -> str:
        return f"Student(name={self.name}, id={self.id})"
    
    def __eq__(self, other) -> bool:
        return self.id == other.id if isinstance(other, Student) else False
    
student1 = Student("Alice", 1)
student2 = Student("Bob", 2)
student3 = Student("Alice", 1)
human = Human("Charlie")
print(student1)  # Output: Student(name=Alice, id=1)
print(human)      # Output: Human(name=Charlie)
print(student1 == student2)  # Output: False
print(student1 == human)      # Output: False
print(student1 == student3)  # Output: True