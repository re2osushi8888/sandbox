{-# LANGUAGE CPP #-}
{-# LANGUAGE NoRebindableSyntax #-}
#if __GLASGOW_HASKELL__ >= 810
{-# OPTIONS_GHC -Wno-prepositive-qualified-module #-}
#endif
{-# OPTIONS_GHC -fno-warn-missing-import-lists #-}
{-# OPTIONS_GHC -w #-}
module Paths_hjq (
    version,
    getBinDir, getLibDir, getDynLibDir, getDataDir, getLibexecDir,
    getDataFileName, getSysconfDir
  ) where


import qualified Control.Exception as Exception
import qualified Data.List as List
import Data.Version (Version(..))
import System.Environment (getEnv)
import Prelude


#if defined(VERSION_base)

#if MIN_VERSION_base(4,0,0)
catchIO :: IO a -> (Exception.IOException -> IO a) -> IO a
#else
catchIO :: IO a -> (Exception.Exception -> IO a) -> IO a
#endif

#else
catchIO :: IO a -> (Exception.IOException -> IO a) -> IO a
#endif
catchIO = Exception.catch

version :: Version
version = Version [0,1,0,0] []

getDataFileName :: FilePath -> IO FilePath
getDataFileName name = do
  dir <- getDataDir
  return (dir `joinFileName` name)

getBinDir, getLibDir, getDynLibDir, getDataDir, getLibexecDir, getSysconfDir :: IO FilePath




bindir, libdir, dynlibdir, datadir, libexecdir, sysconfdir :: FilePath
bindir     = "/home/r-yamamoto/repos/github.com/re2osushi8888/sandbox/hjq/.stack-work/install/x86_64-linux/17166516f007a2cc56c7c83074dccd064f7268fefb365a5b023de6853f4d6fa7/9.10.3/bin"
libdir     = "/home/r-yamamoto/repos/github.com/re2osushi8888/sandbox/hjq/.stack-work/install/x86_64-linux/17166516f007a2cc56c7c83074dccd064f7268fefb365a5b023de6853f4d6fa7/9.10.3/lib/x86_64-linux-ghc-9.10.3-b4c3/hjq-0.1.0.0-6KbclsEYi4d88wvQyDDWYJ"
dynlibdir  = "/home/r-yamamoto/repos/github.com/re2osushi8888/sandbox/hjq/.stack-work/install/x86_64-linux/17166516f007a2cc56c7c83074dccd064f7268fefb365a5b023de6853f4d6fa7/9.10.3/lib/x86_64-linux-ghc-9.10.3-b4c3"
datadir    = "/home/r-yamamoto/repos/github.com/re2osushi8888/sandbox/hjq/.stack-work/install/x86_64-linux/17166516f007a2cc56c7c83074dccd064f7268fefb365a5b023de6853f4d6fa7/9.10.3/share/x86_64-linux-ghc-9.10.3-b4c3/hjq-0.1.0.0"
libexecdir = "/home/r-yamamoto/repos/github.com/re2osushi8888/sandbox/hjq/.stack-work/install/x86_64-linux/17166516f007a2cc56c7c83074dccd064f7268fefb365a5b023de6853f4d6fa7/9.10.3/libexec/x86_64-linux-ghc-9.10.3-b4c3/hjq-0.1.0.0"
sysconfdir = "/home/r-yamamoto/repos/github.com/re2osushi8888/sandbox/hjq/.stack-work/install/x86_64-linux/17166516f007a2cc56c7c83074dccd064f7268fefb365a5b023de6853f4d6fa7/9.10.3/etc"

getBinDir     = catchIO (getEnv "hjq_bindir")     (\_ -> return bindir)
getLibDir     = catchIO (getEnv "hjq_libdir")     (\_ -> return libdir)
getDynLibDir  = catchIO (getEnv "hjq_dynlibdir")  (\_ -> return dynlibdir)
getDataDir    = catchIO (getEnv "hjq_datadir")    (\_ -> return datadir)
getLibexecDir = catchIO (getEnv "hjq_libexecdir") (\_ -> return libexecdir)
getSysconfDir = catchIO (getEnv "hjq_sysconfdir") (\_ -> return sysconfdir)



joinFileName :: String -> String -> FilePath
joinFileName ""  fname = fname
joinFileName "." fname = fname
joinFileName dir ""    = dir
joinFileName dir fname
  | isPathSeparator (List.last dir) = dir ++ fname
  | otherwise                       = dir ++ pathSeparator : fname

pathSeparator :: Char
pathSeparator = '/'

isPathSeparator :: Char -> Bool
isPathSeparator c = c == '/'
