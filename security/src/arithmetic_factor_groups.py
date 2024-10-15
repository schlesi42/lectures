from math import gcd
from matplotlib import pyplot as plt


class ModNMultGroup:
    def __init__(self, modulus: int) -> None:
        self.modulus = modulus
        self.members = self.group_members()
        self.mult_table = self.multiplication_table()
        

    def mult(self, x: int, y: int):
        return (x+y) % self.modulus

    def has_multiplicative_inverse(self, n: int):
        return gcd(n, self.modulus) == 1
    
    def in_group(self, n: int):
        return self.has_multiplicative_inverse(n)
    
    def group_members(self):
        return [x for x in range(1,self.modulus) if self.in_group(x)]
    
    def multiplication_table(self):
        mult_table = {}
        for i in self.members:   
            mults = []
            for j in self.members:
                mults.append((i*j)%self.modulus)
                mult_table[i]=mults
        return mult_table
    
    def eulerphi(self):
        return len(self.mult_table)
    
    def inverse(self, n: int):
        if n%self.modulus not in self.mult_table:
            raise Exception("element not in group")
        else:
            return list(self.mult_table)[self.mult_table[n%self.modulus].index(1)]
    
    def fast_mult(self, x: int, y: int):
        if x%self.modulus not in self.members or y%self.modulus not in self.members:
            raise Exception("Elements not in group")
        return self.mult_table[x%self.modulus][list(self.mult_table).index(y%self.modulus)]
    
    def power(self, x: int, n: int):
        if n<0:
            return self.inverse(self.power(x%self.modulus,-n))
        if n==0:
            return 1
        if n==1:
            return x%self.modulus
        return self.fast_mult(self.power(x, n-1),x)
    
    def order(self, n: int):
        if not self.in_group(n):
            raise Exception("element not in group")
        return self.powers(n)[1:].index(1)+1
    
    def powers(self, n: int):
        return [self.power(n,y) for y in range(0,self.eulerphi()+1)]
    
    def all_powers(self):
        result = {}
        args = [x for x in range(1,self.modulus) if x in self.members]
        for n in args:
            values = [self.power(n,y) for y in range(0,self.eulerphi()+1)]
            result[n]=values
        return result
    
    def is_primitive_root(self,n:int):
        powers = self.powers(n%self.modulus)
        return set(powers) == set(self.members)
    
    def all_primitive_roots(self):
        return [x for x in self.members if self.is_primitive_root(x)]
    
    def plot_powers(self, n: int):
        args = list(range(0,self.eulerphi()+1))
        values = [self.power(n,y) for y in args]
        plt.scatter(args, values)
        plt.show()
    
if __name__ == '__main__':
    # grp = ModNMultGroup(941)
    # n = 627
    # print(grp.mult_table)
    # print(grp.eulerphi())
    # grp.plot_powers(627)
    
    # grp = ModNMultGroup(10)
    # print(grp.all_powers())
    # print(grp.order(9))

    grp = ModNMultGroup(124)
    print(grp.mult_table)
    print(grp.eulerphi())
    
    print(grp.all_powers())
    print(grp.all_primitive_roots())
    print(grp.order(9))
    grp.plot_powers(9)