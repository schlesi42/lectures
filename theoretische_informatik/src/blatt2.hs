import GHC.Real (reduce)
import Text.XHtml (rev)

is_in :: Eq a => [a] -> a -> Bool
is_in [] _ = False
is_in (x:xs) y = (x == y) || is_in xs y

sum1 :: [Int] -> Int
sum1 [] = 0
sum1 (x:xs) = x + sum1 xs

map2 :: (a -> b) -> [a] -> [b]
map2 _ [] = []
map2 f (x:xs) = f x : map2 f xs

reduce2 :: (a -> a -> a) -> a -> [a] -> a
reduce2 _ z [] = z
reduce2 f z (x:xs) = f x (reduce2 f z xs)
sum2 :: [Int] -> Int

sum2 xs = foldl (+) 0 xs

take2 :: Int -> [a] -> [a]
take2 0 _ = []
take2 _ [] = []
take2 n (x:xs) = x : take2 (n-1) xs

reverse2 :: [a] -> [a]
reverse2 [] = []
reverse2 (x:xs) = reverse2 xs ++ [x]


ascending :: Ord a => [a] -> Bool
ascending [] = True
ascending [x] = True
ascending (x:y:xs) = (x <= y) && ascending (y:xs)


takeWhile' :: (a -> Bool) -> [a] -> [a]
takeWhile' _ [] = []
takeWhile' p (x:xs)
  | p x       = x : takeWhile' p xs
  | otherwise = []



take_as_long_as :: (Int -> Bool) -> [Int] -> Int
take_as_long_as _ [] = 0
take_as_long_as p (x:xs)
  | p x       = x
  | otherwise = take_as_long_as p xs

main = print(take_as_long_as (\x -> x < 3) [1,2,3,4,5])