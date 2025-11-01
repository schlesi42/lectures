from __future__ import annotations

class Node:
    def __init__(self, data: int, next: 'LinkedList'):
        self.data = data
        self.next = next
class LinkedList:
    def __init__(self, head: Node = None):
        self.head = head
    def append(lst: 'LinkedList', x: int) -> 'LinkedList':
        if lst.head is None:
            lst.head = Node(x, None)
        else:
            current = lst.head
            while current.next is not None:
                current = current.next
            current.next = Node(x, None)
        return lst
    def is_in(lst: 'LinkedList', x: int) -> bool:
        current = lst.head
        while current is not None:
            if current.data == x:
                return True
            current = current.next
        return False
    def remove(lst: 'LinkedList', x: int) -> 'LinkedList':
        current = lst.head
        prev = None
        while current is not None:
            if current.data == x:
                if prev is None:
                    lst.head = current.next
                else:
                    prev.next = current.next
                return lst
            prev = current
            current = current.next
        return lst
    def __str__(lst: 'LinkedList') -> str:
        s = ""
        current = lst.head
        while current is not None:
            s += str(current.data) + " -> "
            current = current.next
        return s[:-4] if s else "[]"

if __name__ == "__main__":
    lst = LinkedList()
    lst.append(1)
    lst.append(2)
    lst.append(3)
    print(lst.is_in(2))  # Output: True
    print(lst.is_in(4))  # Output: False
    lst.remove(2)
    print(lst.is_in(2))  # Output: False
    print(lst)  # Output: [1 -> 3]