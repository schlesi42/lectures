quicksort [] = []
quicksort (x:xs) = quicksort ys ++ [x] ++ quicksort zs
    where ys = [y|y<-xs, y<=x]
          zs = [z|z<-xs, x<z]

l = [3,4,1,5,7,10,9,2]
main = print(quicksort l)