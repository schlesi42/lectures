reverseInt :: [Int] -> [Int]
reverseInt [] = []
reverseInt (x:xs) = reverseInt xs ++ [x]

reverseChar :: String -> String
reverseChar [] = []
reverseChar (x:xs) = reverseChar xs ++ [x]

-- All the same right? What about DRY?
-- Parametrization
reverse2 :: [a] -> [a]
reverse2 [] = []
reverse2  (x:xs) = reverse2 xs ++ [x]

reverse_tail_rec :: [a] -> [a] -> [a]
reverse_tail_rec [] xs = xs
reverse_tail_rec (x:xs) ys = reverse_tail_rec xs (x:ys)

-- now combined
reverse3 :: [a] -> [a]
reverse3 xs = reverse' xs [] 
    where
        reverse' [] xs = xs
        reverse' (x:xs) ys = reverse' xs (x:ys)

-- important: restrictions on types
sum2 :: Num a => [a] -> a
sum2 [] = 0
sum2 (x:xs) = x + sum2 xs

-- sum with accumulator
-- $! makes it an eager evaluation
sum3 :: Num a => [a] -> a
sum3 xs = sum' xs 0 
    where
        sum' [] x = x
        sum' (x:xs) y = sum' xs $!(x+y)

-- or with case distinction
sum4 :: Num a => [a] -> a
sum4 xs = sum' xs 0
    where
        sum' xs y = case xs of
            [] -> y
            (x:xs) -> sum' xs $!(y+x)

head2 :: [a] -> a
head2 [] = error "no head for empty lists"
head2 (x:_) = x

tail2 :: [a] -> [a]
tail2 [] = []
tail2 (_:xs) = xs

append :: [a] -> [a] -> [a]
append [] ys = ys
append (x:xs) ys = (x:append xs ys)

-- init gives all elements except the last
init2 :: [a] -> [a]
init2 [] = []
init2 [x] = []
init2 (x:xs) = (x: init2 xs)

sorted :: Ord a => [a] -> Bool
sorted [] = True
sorted [x] = True
sorted (x:y:xs) = (x<=y) && (sorted (y:xs))

zip2 :: [a] -> [b] -> [(a,b)]
zip2 [] _ = []
zip2 _ [] = []
zip2 (x:xs) (y:ys) = (x,y):(zip2 xs ys)

quicksort :: Ord a => [a] -> [a]
quicksort [] = []
quicksort (x:xs) = quicksort [a|a<-xs,a<=x] ++ [x] ++ quicksort [a|a<-xs, a>x]

-- merge now appends and sorts two lists
merge2 :: Ord a => [a] -> [a] -> [a]
merge2 xs ys = quicksort (append xs ys)

length2 :: [a] -> Int
length2 xs = case xs of
    [] -> 0
    (x:xs) -> 1 + length2 xs

elem2 :: Eq a => a -> [a] -> Bool
elem2 x ys = case ys of
    [] -> False
    (y:ys) -> if x==y then True else elem2 x ys

-- now let's motivate higher order functions
filter_2 [] = []
filter_2 (x:xs) 
    | x>2 = (x:filter_2 xs)
    | otherwise = filter_2 xs

-- also possible with list comprehension
filter_2_1 xs = [x|x<-xs, x>2]

filter_3 [] = []
filter_3 (x:xs) 
    | x>3 = (x:filter_3 xs)
    | otherwise = filter_3 xs

-- stupid, right? So, let's add a parameter
filter_x _ [] = []
filter_x x (y:ys)
    | y>x = (y:filter_x x ys)
    | otherwise = filter_x x ys

-- but now what if we want to filter for x<2 or something else? Let's just add all predicates at once:
filter_new :: (a-> Bool) -> [a] -> [a]
filter_new _ [] = []
filter_new p (x:xs) 
    | p(x) = (x:filter_new p xs)
    | otherwise = filter_new p xs

-- now filter_2 == filter_new (>2)
-- let's define more - motivate it first as well with doubling, squaring etc.
map2 :: (a -> b) -> [a] -> [b]
map2 _ [] = []
map2 f (x:xs) = (f x):(map2 f xs)

all2 :: (a -> Bool) -> [a] -> Bool
all2 _ [] = True
all2 p (x:xs) = (p x) && (all2 p xs)

exists2 :: (a -> Bool) -> [a] -> Bool
exists2 _ [] = False
exists2 p (x:xs) = (p x) || (exists2 p xs)

filter2 :: (a -> Bool) -> [a] -> [a]
filter2 p xs = [x|x<-xs, p x]

-- remember merge? Wanna do it with composition, but it doesn't work with standard composition, which is . :: (b->c) -> (a->b) -> (a->c)
compose2 :: (c -> d) -> (a -> b -> c) -> a -> b -> d
compose2 g f x y = g (f x y)
merge3 :: Ord a => [a] -> [a] -> [a]
merge3 = compose2 quicksort append

-- with composition2, also crazy things like another version of diffsq a b = (a-b)^2
diffsq = (^2) `compose2` (-)

-- now what about curry?
curry2 :: ((a,b) -> c) -> a -> b -> c
curry2 f x y = f (x,y)

plus (x,y) = x+y
f = curry2 plus
-- now we can apply for instance f 2 3

uncurry2 :: (a -> b -> c) -> (a,b) -> c
uncurry2 f (x,y) = f x y
plus2 x y = x+y
g = uncurry2 plus2
-- now we can apply g (2,3)

foldlNew :: (b -> a -> b) -> b -> [a] -> b
foldlNew _ z [] = z
foldlNew f z (x:xs) = foldlNew f (f z x) xs

ascending :: Ord a => [a] -> Bool
ascending [] = True
ascending [x] = True
ascending (x:y:xs) = (x<=y) && ascending (y:xs)

pow :: Int -> Int -> Int
pow _ 0 = 1
pow x n = x * pow x (n-1)

takeWhile' :: (a -> Bool) -> [a] -> [a]
takeWhile' _ [] = []
takeWhile' p (x:xs)
    | p x = x : takeWhile' p xs
    | otherwise = []

testlist = [1,2,3,4,5]
testlist2 = [11,13,12]

-- main = print(foldlNew (+) 0 testlist2)

main = print(g (2,3))
-- main = print(ascending testlist)
-- main = print(takeWhile' (<4) testlist)