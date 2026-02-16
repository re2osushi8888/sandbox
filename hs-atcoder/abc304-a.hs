import Control.Monad (replicateM)
import Data.List (break, minimumBy, sortOn)
import Data.Ord (comparing)

main = do
    n <- readLn
    xs <- replicateM n getLine
    let pairs = map parse xs :: [(String, Int)]

        rotated = rotateToMin pairs
        names = map fst rotated
    mapM_ putStrLn names

parse :: String -> (String, Int)
parse l =
    case words l of
        [s, c] -> (s, read c)
        _ -> error ("invalid line")

rotateToMin :: [(String, Int)] -> [(String, Int)]
rotateToMin xs = ys ++ zs
  where
    m = minimumBy (comparing snd) xs
    (zs, ys) = break (== m) xs
