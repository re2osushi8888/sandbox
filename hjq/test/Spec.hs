{-# LANGUAGE OverloadedStrings #-}

module Main (main) where

import Control.Lens ((^?))
import Data.Aeson (Value (..))
import qualified Data.Aeson.KeyMap as KM
import Data.Aeson.Lens (key, nth)
import Data.Hjq.Parser
import Data.Hjq.Query
import Data.Text (Text, unpack)
import qualified Data.Vector as V
import Test.HUnit (Test (TestList), runTestTT, (~:), (~?=))

main :: IO ()
main = do
    _ <-
        runTestTT $
            TestList
                [ jqFilterParserTest
                , jqQueryParserTest
                , jqQueryParserSpaceTest
                , applyFilterTest
                , executeQueryTest
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

jqQueryParserTest :: Test
jqQueryParserTest =
    TestList
        [ "jqQueryParser test 1"
            ~: parseJqQuery "[]"
            ~?= Right (JqQueryArray [])
        , "jqQueryParser test 2"
            ~: parseJqQuery "[.hoge,.piyo]"
            ~?= Right (JqQueryArray [JqQueryFilter (JqField "hoge" JqNil), JqQueryFilter (JqField "piyo" JqNil)]) -- [{hoge: ""}, {piyo: ""}]
        , "jqQueryParser test 3"
            ~: parseJqQuery "{\"hoge\":[],\"piyo\":[]}"
            ~?= Right (JqQueryObject [("hoge", JqQueryArray []), ("piyo", JqQueryArray [])])
        ]

jqQueryParserSpaceTest :: Test
jqQueryParserSpaceTest =
    TestList
        [ "jqQueryParser space test 1"
            ~: parseJqQuery "[ ]"
            ~?= Right (JqQueryArray [])
        , "jqQueryParser space test 2"
            ~: parseJqQuery "[ . hoge , . piyo ]"
            ~?= Right (JqQueryArray [JqQueryFilter (JqField "hoge" JqNil), JqQueryFilter (JqField "piyo" JqNil)]) -- [{hoge: ""}, {piyo: ""}]
        , "jqQueryParser space test 3"
            ~: parseJqQuery "{ \"hoge\" : [ ] , \"piyo\" : [ ] }"
            ~?= Right (JqQueryObject [("hoge", JqQueryArray []), ("piyo", JqQueryArray [])])
        ]

testData :: Value
testData =
    Object $
        KM.fromList
            [ ("string-field", String "string value")
            ,
                ( "nested-field"
                , Object $
                    KM.fromList
                        [ ("inner-string", String "inner value")
                        , ("inner-number", Number 100)
                        ]
                )
            ,
                ( "array-field"
                , Array $
                    V.fromList
                        [ String "first field"
                        , String "next field"
                        , Object
                            ( KM.fromList
                                [("object-in-array", String "string value in object-in-array")]
                            )
                        ]
                )
            ]

applyFilterTest :: Test
applyFilterTest =
    TestList
        [ "applyFilter test1"
            ~: applyFilter (unsafeParseFilter ".") testData
            ~?= Right testData
        , "applyFilter test2"
            ~: (Just $ applyFilter (unsafeParseFilter ".string-field") testData)
            ~?= fmap Right (testData ^? key "string-field")
        , "applyFilter test3"
            ~: (Just $ applyFilter (unsafeParseFilter ".nested-field.inner-string") testData)
            ~?= fmap Right (testData ^? key "nested-field" . key "inner-string")
        , "applyFilter test4"
            ~: (Just $ applyFilter (unsafeParseFilter ".nested-field.inner-number") testData)
            ~?= fmap Right (testData ^? key "nested-field" . key "inner-number")
        , "applyFilter test5"
            ~: (Just $ applyFilter (unsafeParseFilter ".array-field[0]") testData)
            ~?= fmap Right (testData ^? key "array-field" . nth 0)
        , "applyFilter test6"
            ~: (Just $ applyFilter (unsafeParseFilter ".array-field[1]") testData)
            ~?= fmap Right (testData ^? key "array-field" . nth 1)
        , "applyFilter test7"
            ~: (Just $ applyFilter (unsafeParseFilter ".array-field[2]") testData)
            ~?= fmap Right (testData ^? key "array-field" . nth 2)
        ]

executeQueryTest :: Test
executeQueryTest =
    TestList
        [ "executeQuery test 1"
            ~: executeQuery (unsafeParseQuery "{}") testData
            ~?= Right (Object $ KM.fromList [])
        , "executeQuery test 2"
            ~: executeQuery (unsafeParseQuery "{ \"field1\": . , \"field2\": .string-field}") testData
            ~?= Right (Object $ KM.fromList [("field1", testData), ("field2", String "string value")])
        , "executeQuery test 3"
            ~: executeQuery (unsafeParseQuery "[ .string-field, .nested-field.inner-string]") testData
            ~?= Right (Array $ V.fromList [String "string value", String "inner value"])
        ]

unsafeParseQuery :: Text -> JqQuery
unsafeParseQuery t = case parseJqQuery t of
    Right q -> q
    Left s -> error $ "PARSE FAILURE IN A TEST : " ++ unpack s
