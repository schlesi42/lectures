reverse2 :: [a] -> [a]
reverse2 [] = []
reverse2 (x:xs) = reverse2 xs ++ [x]



reverse_tail_recursive :: [a] -> [a] -> [a]
reverse_tail_recursive [] acc = acc
reverse_tail_recursive (x:xs) acc = reverse_tail_recursive xs (acc ++ [x])



sum2 :: Num a => [a] -> a
sum2 [] = 0
sum2 (x:xs) = x + sum2 xs

sorted :: Ord a => [a] -> Bool
sorted [] = True
sorted [x] = True
sorted (x:y:xs) = x <= y && sorted (y:xs)

filter2 :: (a -> Bool) -> [a] -> [a]
filter2 _ [] = []
filter2 p (x:xs)
    | p x       = x : filter2 p xs
    | otherwise = filter2 p xs

map2 :: (a -> b) -> [a] -> [b]
map2 _ [] = []
map2 f (x:xs) = f x : map2 f xs

f = \x -> x * 2

main = print (f 2)
