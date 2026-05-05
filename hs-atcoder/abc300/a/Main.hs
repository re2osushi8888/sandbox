#!/usr/bin/env runghc 

import Data.List (elemIndex)
import Data.Maybe (fromJust)

main :: IO ()
main = do
  xs <- map (read :: String -> Int) . words <$> getLine
  c <- map (read :: String -> Int) . words <$> getLine
  let n = head xs
  let a = xs !! 1
  let b = xs !! 2
  let s = a + b 
  let ans = 1 + fromJust (elemIndex s c)
  print ans
