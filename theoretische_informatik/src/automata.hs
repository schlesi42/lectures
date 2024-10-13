import Data.Char (chr)
data State = State { name :: Int } deriving Eq
instance Show State where
    show (State x) = "q_" ++ [chr x]


data DEA = DEA { states :: [State], alphabet :: [Char], delta :: [(State, Char, State)], start :: State, accepting :: [State] } deriving (Show)
main = print(State(1))