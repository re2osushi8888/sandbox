{-# LANGUAGE OverloadedStrings #-}

module Main (main) where

import Data.Hjq.Parser (JqFilter (..), parseJqFilter)
import Data.Text ()
import Test.HUnit (Test (TestList), runTestTT, (~:), (~?=))

main :: IO ()
main = do
    _ <-
        runTestTT $
            TestList
                [ jqFilterParserTest
                -- テストケースが増えたら追加していく
                ]
    return ()

jqFilterParserTest :: Test
jqFilterParserTest =
    TestList
        [ "jqFilterParserTest test 1"
            ~: parseJqFilter (".")
            ~?= Right JqNil -- .が来たらJqNil
        , "jqFilterParserTest test 2"
            ~: parseJqFilter (".[0]")
            ~?= Right (JqIndex 0 JqNil) -- .[0]がきたらJqIndex 0 JqNil
        , "jqFilterParserTest test 3"
            ~: parseJqFilter (".fieldName")
            ~?= Right (JqField ("fieldName") JqNil)
        , "jqFilterParserTest test 4"
            ~: parseJqFilter (".[0].fieldName")
            ~?= Right (JqIndex 0 (JqField ("fieldName") JqNil))
        , "jqFilterParserTest test5"
            ~: parseJqFilter (".fieldName[0]")
            ~?= Right (JqField ("fieldName") (JqIndex 0 JqNil))
        , -- 引数にspaceが含まれたクエリのバージョン
          "jqFilterParserTest test 1'"
            ~: parseJqFilter (" . ")
            ~?= Right JqNil -- .が来たらJqNil
        , "jqFilterParserTest test 2'"
            ~: parseJqFilter (" . [ 0 ] ")
            ~?= Right (JqIndex 0 JqNil) -- .[0]がきたらJqIndex 0 JqNil
        , "jqFilterParserTest test 3'"
            ~: parseJqFilter (" . fieldName ")
            ~?= Right (JqField ("fieldName") JqNil)
        , "jqFilterParserTest test 4'"
            ~: parseJqFilter (" . [ 0 ] . fieldName ")
            ~?= Right (JqIndex 0 (JqField ("fieldName") JqNil))
        , "jqFilterParserTest test5'"
            ~: parseJqFilter (" . fieldName [ 0 ] ")
            ~?= Right (JqField ("fieldName") (JqIndex 0 JqNil))
        ]
