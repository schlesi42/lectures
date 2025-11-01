from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class NaturalNumber:
    def to_int(self) -> int:
        raise NotImplementedError("Subclasses should implement this method.")
    
    def __str__(self):
        return str(self.to_int())

class Zero(NaturalNumber):
    
    def to_int(self) -> int:
        return 0
    
    def __str__(self):
        return "0"
    
class Succ(NaturalNumber):
    def __init__(self, pred: NaturalNumber):
        self.pred = pred

    def to_int(self) -> int:
        return 1 + self.pred.to_int() if isinstance(self.pred, Succ) else 1
    
    def __str__(self):
        return self.to_int().__str__()
    
def add(n1: NaturalNumber, n2: NaturalNumber) -> NaturalNumber:
    if isinstance(n1, Zero):
        return n2
    elif isinstance(n1, Succ):
        return Succ(add(n1.pred, n2))
    else:
        raise ValueError("Invalid NaturalNumber")
    
if __name__ == "__main__":
    # Example usage:
    zero = Zero()
    one = Succ(zero)
    two = Succ(one)
    three = Succ(two)
    
    result = add(two, three)  # Should represent 5
    print(result)  # Output: S(S(S(S(S(0)))))
    