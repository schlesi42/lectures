data Signal = Red | Yellow | Green deriving (Eq, Show, Ord)


stopwhen :: Signal -> Bool
stopwhen Red = True
stopwhen _ = False

stopwhen2:: Signal -> Bool
stopwhen2 c
    | (c==Red) = True
    | otherwise = False

main = print(Red<Yellow)