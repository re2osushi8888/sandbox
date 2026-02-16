countSimularChars :: [Char] -> [Char] -> Int
countSimularChars s t =
    length $ filter (== True) $ zipWith equivChar s t

equivChar :: Char -> Char -> Bool
equivChar a b = normalize a == normalize b

normalize :: Char -> Char
normalize '1' = 'l'
normalize '0' = 'o'
normalize c = c

toYesNo :: Bool -> String
toYesNo True = "Yes"
toYesNo False = "No"

main = do
    xs <- getContents
    let (nLine : s : t : _) = lines xs
        n = read nLine :: Int
    
    putStrLn $ toYesNo (n == countSimularChars s t)
