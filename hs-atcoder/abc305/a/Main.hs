#!/usr/bin/env runghc

main :: IO ()
main = do
    x <- readLn :: IO Int
    let a = mod x 5
    if a < 3 then print (x - a) else print (x - a + 5)
