module Main (main) where

import Test.HUnit (runTestTT, (~:), (~?=))

main :: IO ()
main = do
  runTestTT $ "Test1" ~: 1 + 1 ~?= 2
  return ()
