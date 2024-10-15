from typing import Set, List, Tuple
class Relation:
    def __init__(self, m: Set[int], n: Set[int], l: Set[Tuple[int,int]]):
        self.m = m
        self.n = n
        self.l = l
    
    
    def adjacency_matrix(self) -> List[List[int]]:
        #return [[1 if (i,j) in self.l else 0 for j in sorted(self.n)] for i in sorted(self.m)]
        rows = len(self.m)
        cols = len(self.n)    
        ad_m = [[0 for i in range(0, cols)] for j in range(0, rows)]
        sorted_m = sorted(self.m)
        sorted_n = sorted(self.n)
        for (a,b) in self.l:
            i = sorted_m.index(a)
            j = sorted_n.index(b)
            ad_m[i][j] = 1
        return ad_m

    def __str__(self) -> str:
        return str(self.adjacency_matrix())
        
    
    
class Mono_Set_Relation(Relation):
    def __init__(self, m: Set[int], l: Set[Tuple[int, int]]):
        super().__init__(m, m, l)
    
    def is_reflexive(self) -> bool:
        for x in self.m:
            if (x,x) not in self.l:
                return False
        return True
    
    def is_antisymmetric(self) -> bool:
        for (x,y) in self.l:
            if x!=y and (y,x) in self.l:
                return False
        return True
    
    def is_symmetric(self) -> bool:
        for (a,b) in self.l:
            if (b,a) not in self.l:
                return False
        return True
    
    def is_transitive(self) -> bool:
        for (x,y) in self.l:
            for z in [b for (a,b) in self.l if a==y]:
                if (x,z) not in self.l:
                    print(f"{(x,z)} is missing")
                    return False
        return True
        
    def is_order(self) -> bool:
        return self.is_reflexive() and self.is_antisymmetric() and self.is_transitive()
    
    def equivalence_relation(self) -> bool:
        return self.is_reflexive() and self.is_symmetric() and self.is_transitive()
    
class Function(Relation):
    def __init__(self, m: Set[int], n: Set[int], l: Set[Tuple[int, int]]):
        super().__init__(m, n, l)
        if not self.is_function():
            raise Exception("not a function")
    def is_function(self) -> bool:
        for x in self.m:
            x_maps = [b for (a,b) in self.l if a==x]
            if len(x_maps)!=1:
                return False
        return False

if __name__ == '__main__':
    m = {1,2,3}
    l = {(1,1),(1,2),(2,3),(3,1), (2,2)}
    
    r = Mono_Set_Relation(m,l)
    r2 = Mono_Set_Relation(m,{(1,1),(1,2),(2,3), (3,1), (2,1),(1,3),(3,2), (2,2),(3,3)})
    print(r2.is_transitive())

    