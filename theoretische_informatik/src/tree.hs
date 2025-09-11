

-- Example: Binary tree
data Tree a = Empty | Node a (Tree a) (Tree a)
              deriving (Eq, Show)

-- assumption: < is a linear ordering

find :: Ord a => a -> Tree a -> Bool
find _ Empty  =  False
find x (Node a l r)
  | x < a      =  find x l
  | a < x      =  find x r
  | otherwise  =  True

insert :: Ord a => a -> Tree a -> Tree a
insert x Empty  =  Node x Empty Empty
insert x (Node a l r)
  | x < a      =  Node a (insert x l) r
  | a < x      =  Node a l (insert x r)
  | otherwise  =  Node a l r



sumTree :: Num a => Tree a -> a
sumTree Empty = 0
sumTree (Node x l r) = x + sumTree l + sumTree r

testTree = (Node 1 (Node 2 Empty (Node 3 Empty Empty)) (Node 4 (Node 5 Empty Empty) Empty))
main = print(sumTree testTree)