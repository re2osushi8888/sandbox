main :: IO ()
main = do
  [a, b] <- map (read :: String -> Integer) . words <$> getLine
  print $ (a + b - 1) `div` b 
