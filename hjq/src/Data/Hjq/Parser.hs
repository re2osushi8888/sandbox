{-# LANGUAGE OverloadedStrings #-}

module Data.Hjq.Parser (
    JqFilter (..),
    parseJqFilter,
    JqQuery (..),
    parseJqQuery,
    unsafeParseFilter,
    applyFilter,
    executeQuery,
) where

import Control.Applicative ((<|>))
import Control.Lens ((^.), (^?))
import Control.Monad (join)
import Data.Aeson (Value (..))
import qualified Data.Aeson.Key as K
import qualified Data.Aeson.KeyMap as KM
import Data.Aeson.Lens (key, nth, _Key)
import Data.Attoparsec.Text (IResult (Done), Parser, Result, char, decimal, digit, endOfInput, feed, letter, many1, parse, sepBy, skipSpace)
import Data.Text (Text, pack, unpack)
import qualified Data.Vector as V

data JqFilter
    = JqField Text JqFilter
    | JqIndex Int JqFilter
    | JqNil -- フィールド名とインデックスが存在しない場合にも使う
    deriving (Show, Read, Eq)

-- スペースが入っていたら修正する
schar :: Char -> Parser Char
schar c = skipSpace *> char c <* skipSpace

-- ユーザの入力をパースする
parseJqFilter :: Text -> Either Text JqFilter
parseJqFilter s =
    showParseResult $
        parse (jqFilterParser <* endOfInput) s `feed` ""

-- attoparsecを使ってフィルタの文字列をJqFilter型にパース
-- attoparsecについては7章を参照
jqFilterParser :: Parser JqFilter
jqFilterParser = schar '.' >> (jqField <|> jqIndex <|> pure JqNil)
  where
    jqFilter :: Parser JqFilter
    jqFilter = (schar '.' >> jqField) <|> jqIndex <|> pure JqNil

    jqField :: Parser JqFilter
    jqField = JqField <$> (word <* skipSpace) <*> jqFilter

    jqIndex :: Parser JqFilter
    jqIndex = JqIndex <$> (schar '[' *> decimal <* schar ']') <*> jqFilter

-- パース結果の表示
showParseResult :: (Show a) => Result a -> Either Text a
showParseResult (Done _ r) = Right r
showParseResult r = Left . pack $ show r

-- フィールド名などの識別子をパースするパーサ
word :: Parser Text
word = fmap pack $ many1 (letter <|> char '-' <|> char '_' <|> digit)

data JqQuery
    = JqQueryObject [(Text, JqQuery)]
    | JqQueryArray [JqQuery]
    | JqQueryFilter JqFilter
    deriving (Show, Read, Eq)

parseJqQuery :: Text -> Either Text JqQuery
parseJqQuery s = showParseResult $ parse (jqQueryParser <* endOfInput) s `feed` ""

jqQueryParser :: Parser JqQuery
jqQueryParser = queryArray <|> queryFilter <|> queryObject
  where
    queryArray :: Parser JqQuery
    queryArray = JqQueryArray <$> (schar '[' *> jqQueryParser `sepBy` (schar ',') <* schar ']')

    queryObject :: Parser JqQuery
    queryObject = JqQueryObject <$> (schar '{' *> (qObj `sepBy` schar ',') <* schar '}')

    qObj :: Parser (Text, JqQuery)
    qObj = (,) <$> (schar '"' *> word <* schar '"') <*> (schar ':' *> jqQueryParser)

    queryFilter :: Parser JqQuery
    queryFilter = JqQueryFilter <$> jqFilterParser

unsafeParseFilter :: Text -> JqFilter
unsafeParseFilter t = case parseJqFilter t of
    Right f -> f
    Left s -> error $ "PARSE FAILURE IN A TEST : " ++ unpack s

applyFilter :: JqFilter -> Value -> Either Text Value
applyFilter (JqField fieldName n) obj@(Object _) =
    join $ noteNotFoundError fieldName (fmap (applyFilter n) (obj ^? key (fieldName ^. _Key)))
applyFilter (JqIndex index n) array@(Array _) =
    join $ noteOutOfRangeError index (fmap (applyFilter n) (array ^? nth index))
applyFilter JqNil v = Right v
applyFilter f o = Left $ "unexpected pattern : " <> tshow f <> " : " <> tshow o

noteNotFoundError :: Text -> Maybe a -> Either Text a
noteNotFoundError _ (Just x) = Right x
noteNotFoundError s Nothing = Left $ "field name not found " <> s

noteOutOfRangeError :: Int -> Maybe a -> Either Text a
noteOutOfRangeError _ (Just x) = Right x
noteOutOfRangeError s Nothing = Left $ "out of range : " <> tshow s

tshow :: (Show a) => a -> Text
tshow = pack . show

executeQuery :: JqQuery -> Value -> Either Text Value
executeQuery (JqQueryObject o) v =
    fmap (Object . KM.fromList)
        . sequence
        . fmap sequence
        $ fmap (\(kTxt, q) -> (K.fromText kTxt, executeQuery q v)) o
executeQuery (JqQueryArray l) v =
    fmap (Array . V.fromList) . sequence $ fmap (flip executeQuery v) l
executeQuery (JqQueryFilter f) v = applyFilter f v
