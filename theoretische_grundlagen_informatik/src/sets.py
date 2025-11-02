def is_subset(A, B):
    
    return all(elem in B for elem in A)

def union(A, B):
    return A.union(B)
    #return {x for s in (A, B) for x in s}
    #return A | B

def intersection(A, B):
    return A.intersection(B)
    #return A & B

def difference(A, B):
    return A.difference(B)
    #return A - B

def cartesian_product(A, B):
    
    return {(a, b) for a in A for b in B}

def power_set(S: set) -> set[frozenset]:
    match S:
        case set() if not S:               # nur leere Menge matchen!
            return {frozenset()}
        case _:
            elem = next(iter(S))
            rest = S - {elem}
            without = power_set(rest)
            with_elem = {ss.union({elem}) for ss in without}
            return without.union(with_elem)

def format_set(s):
    if not s:
        return "∅"
    return "{" + ", ".join(str(x) for x in sorted(s)) + "}"

def format_power_set(P):
    elements = [format_set(s) for s in sorted(P, key=lambda s: (len(s), sorted(s)))]
    return "{" + ", ".join(elements) + "}"

if __name__ == "__main__":
    A = {1, 2, 3}
    B = {3, 4, 5}
    
    print("A:", A)
    print("B:", B)
    print("A ⊆ B:", is_subset(A, B))
    print("A ∪ B:", union(A, B))
    print("A ∩ B:", intersection(A, B))
    print("A \\ B:", difference(A, B))
    print("A × B:", cartesian_product(A, B))
    print("P(A):", power_set(A))
    print("P(A) formatted:", format_power_set(power_set(A)))