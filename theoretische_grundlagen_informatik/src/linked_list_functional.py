from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class Empty: pass

@dataclass(frozen=True)
class Node:
    data: int
    next: 'List'

List = Empty | Node

def append(lst: List, x: int) -> List:
    match lst:
        case Empty():
            return Node(x, Empty())
        case Node(d, nxt):
            return Node(d, append(nxt, x))

def is_in(lst: List, x: int) -> bool:
    match lst:
        case Empty():
            return False
        case Node(d, nxt):
            return d == x or is_in(nxt, x)

def remove(lst: List, x: int) -> List:
    match lst:
        case Empty():
            return Empty()
        case Node(d, nxt):
            if d == x:
                return nxt
            else:
                return Node(d, remove(nxt, x))
            
def str(lst: List) -> str:
    match lst:
        case Empty():
            return "[]"
        case Node(d, nxt):
            return f"{d}," + str(nxt) if nxt != Empty() else f"{d}"

def map(lst: List, func) -> List:
    match lst:
        case Empty():
            return Empty()
        case Node(d, nxt):
            return Node(func(d), map(nxt, func))

def filter(lst: List, predicate) -> List:
    match lst:
        case Empty():
            return Empty()
        case Node(d, nxt):
            if predicate(d):
                return Node(d, filter(nxt, predicate))
            else:
                return filter(nxt, predicate)

def reduce(lst: List, func, initial)-> int:
    match lst:
        case Empty():
            return initial
        case Node(d, nxt):
            return reduce(nxt, func, func(initial, d))
    
        
class Set:
    def __init__(self, lst: List = Empty()):
        self.lst = lst

    def add(self, x: int) -> Set:
        if not is_in(self.lst, x):
            self.lst = append(self.lst, x)
        return self

    def remove(self, x: int) -> Set:
        self.lst = remove(self.lst, x)
        return self

    def contains(self, x: int) -> bool:
        return is_in(self.lst, x)
    
    def union(self, other: Set) -> Set:
        result = Set(self.lst)
        match other.lst:
            case Empty():
                return result
            case Node(d, nxt):
                result.add(d)
                return result.union(Set(nxt))
    
    def intersection(self, other: Set) -> Set:
        result = Set()
        match self.lst:
            case Empty():
                return result
            case Node(d, nxt):
                if other.contains(d):
                    result.add(d)
                return result.union(Set(nxt).intersection(other))

    def __str__(self) -> str:
        return "{" + str(self.lst) + "}"

if __name__ == "__main__":
    lst = Empty()
    lst = append(lst, 1)
    lst = append(lst, 2)
    lst = append(lst, 3)
    print(is_in(lst, 2))  # Output: True
    print(is_in(lst, 4))  # Output: False
    lst = remove(lst, 2)
    print(is_in(lst, 2))  # Output: False
    print(str(lst))  # Output: [1 -> 3]
    lst = map(lst, lambda x: x * 2)
    print(str(lst))  # Output: [2 -> 6]
    lst = filter(lst, lambda x: x > 2)
    print(str(lst))  # Output: [6]
    lst = Empty()
    lst = append(lst, 1)
    lst = append(lst, 2)
    lst = append(lst, 3)
    total = reduce(lst, lambda acc, x: acc + x, 0)
    print(total)  # Output: 6

    s=Set()
    s.add(1).add(2).add(3).add(2).add(1)
    print(s)  # Output: [1 -> 2 -> 3]
    s.remove(2)
    print(s)  # Output: [1 -> 3]
    s2=Set()
    s2.add(3).add(4).add(5)
    union_set=s.union(s2)
    print(union_set)  # Output: [1 -> 3 -> 4 -> 5]
    intersection_set=s.intersection(s2)
    print(intersection_set)  # Output: [3]  
