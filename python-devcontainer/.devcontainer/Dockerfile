FROM mcr.microsoft.com/devcontainers/python:1-3.12-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
########## 入っている ##########
# wget: ファイルをダウンロードするためのツール
# curl: データ転送を行うツール（主にHTTP、FTPなどのプロトコルに対応）
# libmariadb-dev: MySQLと互換性のあるクライアントライブラリの開発用パッケージ
# git
# libssl-dev: OpenSSLライブラリを開発するためのヘッダーファイルとライブラリ
# ca-certificates: SSL/TLSのための認証局証明書を管理するためのパッケージ
# zlib1g-dev: zlib（データ圧縮ライブラリ）の開発用パッケージ
# zlib1g-dev: bzip2圧縮ライブラリの開発用パッケージ
# libreadline-dev: ターミナルの入力処理を行うためのReadlineライブラリの開発パッケージ
# libncurses5-dev: 端末操作ライブラリ（ncurses）の開発用パッケージ
# xz-utils: xz形式の圧縮・解凍ツール
# tk-dev: Tk（GUIツールキット）の開発用パッケージ。
# libxml2-dev: XMLパーサーライブラリの開発用パッケージ。
# libxmlsec1-dev: XMLセキュリティライブラリの開発用パッケージ
# libffi-dev: Cの外部関数インターフェース（FFI）ライブラリの開発用パッケージ。
# liblzma-dev: XZ形式の圧縮ツール用のライブラリ（LZMA）の開発パッケージ。
########## 必要じゃなさそう ##########
# libsqlite3-dev: SQLiteデータベースの開発用パッケージ。廃止された？？？
# llvm: 高度なコンパイラとツールチェーンのインフラストラクチャ。

# Python and poetry installation
# USER $USER
# ARG HOME="/home/$USER"
# ARG PYTHON_VERSION=3.12

# ENV PYENV_ROOT="${HOME}/.pyenv"
# ENV PATH="${PYENV_ROOT}/shims:${PYENV_ROOT}/bin:${HOME}/.local/bin:$PATH"

# SHELL ["/bin/bash", "-c"]

# RUN echo "done 0" \
#     && curl https://pyenv.run | bash

# RUN echo "done 1" \
#     && curl -LsSf https://astral.sh/uv/install.sh | sh

# RUN echo "done 2" \
#     && source $HOME/.cargo/env

# RUN echo ${workspaceFolder}
# RUN echo "done 3" \
#     uv python install ${PYTHON_VERSION}
