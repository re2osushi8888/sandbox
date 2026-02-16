judge :: String -> String
judge s
    | t > a = "T"
    | t < a = "A"
    | otherwise = judge s'
  where
    t = length (filter (== 'T') s)
    a = length (filter (== 'A') s)
    s' = init s

main :: IO ()
main = do
    input <- getContents
    let (_nLine : sLine : _) = lines input
        _n = read _nLine :: Int
        s = sLine :: String

    putStrLn $ judge s
