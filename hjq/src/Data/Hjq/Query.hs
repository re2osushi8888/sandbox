{-# LANGUAGE OverloadedStrings #-}

module Data.Hjq.Query (
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
import Data.Attoparsec.Text (Parser, endOfInput, feed, parse, sepBy)
import Data.Hjq.Parser
import Data.Text (Text, pack, unpack)
import qualified Data.Vector as V

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
