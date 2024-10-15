import os 
import functools

class Tree:
    def __init__(self, value=None, children=None) -> None:
        self.value = value
        # Attention: In my first attempt, I had children = [] as default value.
        # However, stupid Python then creates a n empty list and the next time you set up a tree with the
        # default value, i.e., via Tree(value), it does not create a new empty list (as desired) but
        # it provides the reference to the same list (which may have been changed because it is mutable)
        # Stupid Python shit.
        if children is None:
            self.children = []
        else:
            self.children = children

    def is_leaf(self) -> bool:
        return self.children == []
    
    
    def insert(self, value, f=None):
        if f==None:
            self.children.append(Tree(value=value)) 
            
        elif f(self.value, value):
            candidates_to_append_below = [x for x in self.children if f(x.value, value)]
            if candidates_to_append_below == []:
                
                self.children.append(Tree(value))
                
            else:
                # take the first for which the predicate hits
                
                candidates_to_append_below[0].insert(value, f)
                

    def elem(self, value):
        if self.value==value:
            return True
        else:
            return any(subtree.elem(value) for subtree in self.children)
        
    def count_elements(self):
        return 1+sum([x.count_elements() for x in self.children])
    
    def depth(self):
        if self.is_leaf():
            return 1
        else:
            return 1+max([x.depth() for x in self.children])
        
    def reduce(self, f, extract_val):
        if self.is_leaf():

            return extract_val(self.value)
        else:
            return f(functools.reduce(f,[children.reduce(f,extract_val) for children in self.children]),extract_val(self.value))

    def tree_map(self, f, aggregate=None):
        
        def transform(t):
            
            new_children = [transform(x) for x in t.children]
            if aggregate:

                aggregated_value = t.reduce(aggregate, extract_val = lambda node: node)
                new_node_value = f(aggregated_value)
            else:
                new_node_value = f(t.value)
            return Tree(new_node_value, new_children)
        
        return transform(self)
    
    def __str__(self, level=0):
        ret = "  " * level + str(self.value) + "/\n"
        if self.is_leaf():
            ret = ret[:-2] + "\n"
        for child in self.children:
            ret += child.__str__(level + 1)
        return ret


class FileSystem:
    def __init__(self, path="/") -> None:
        self.tree = FileSystem.list_to_tree(FileSystem.filesystem_to_node_list(path))
    
    @staticmethod
    def filesystem_to_node_list(path):
        result = []
        for root, d_names, f_names in os.walk(path):
            node = (root, len(d_names), len(f_names))
            result.append(node)
        return result
    
    @staticmethod
    def list_to_tree(node_list):
        sorted_list = sorted(node_list, key=lambda x: len(x[0]))
        f = lambda elem_1, elem_2: elem_1[0] in elem_2[0]
        new_tree = Tree(sorted_list[0])
        for elem in sorted_list[1:]:
            new_tree.insert(elem, f)
        return new_tree
    
    
    # def prettify(self):
    #     def transform(t):
    #         new_node_value = {
    #             "dir": t.value[0],
    #             "num_dirs": t.value[1],
    #             "num_files": t.value[2]
    #         }
    #         new_children = [transform(x) for x in t.children]
    #         return Tree(new_node_value, new_children)
    #     return transform(self.tree)

    def prettify(self):
        f = lambda x: {
            "dir": x[0],
            "num_direct_dirs": x[1],
            "num_direct_files": x[2]
        }
        return self.tree.tree_map(f)

    def count_elements(self):
        return self.tree.count_elements()
    
    def depth(self):
        return self.tree.depth()
    
    def sum_dirs(self):
        return self.tree.reduce(lambda x,y: x+y, lambda x:x[1])
    
    def sum_files(self):
        return self.tree.reduce(lambda x,y: x+y, lambda x:x[2])
    
    def cumulative_fs(self):
        f = lambda x: {
            "dir": x[0],
            "cumulative_dirs": x[1],
            "cumulative_files": x[2]
        }
        def aggregate(acc, node_value):
            dirs = acc[1] + node_value[1]
            files = acc[2] + node_value[2]
            return acc[0], dirs, files
        
        return self.tree.tree_map(f, aggregate)

    def __str__(self) -> str:
        return str(self.prettify())


if __name__ == '__main__':
    
    path = "/Users/schlesinger/code/security/"
    fs = FileSystem(path)
    
    print(fs.cumulative_fs())
   
    
    
    
    