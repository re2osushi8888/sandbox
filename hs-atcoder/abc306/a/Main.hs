main = do
    _x <- readLn :: IO Int
    s <- getLine
    let ds = concatMap (replicate 2) s
    putStrLn ds
