chunksOf7 :: [Int] -> [[Int]]
chunksOf7 [] = []
chunksOf7 xs = take 7 xs : chunksOf7 (drop 7 xs)

main = do
  n <- readLn :: IO Int
  line <- getLine 
  let as = map read (words line) :: [Int]
  putStrLn $ unwords $ map show $ map sum $ chunksOf7 as
