# Install stage
FROM oven/bun:1.4.0-alpine AS install

WORKDIR /app

COPY package.json bun.lock* ./

RUN bun install --frozen-lockfile --production

# Release stage
FROM oven/bun:1.4.0-alpine AS release

WORKDIR /app

COPY --from=install /app/node_modules ./node_modules
COPY package.json ./
COPY src ./src

# レイヤーキャッシュを保護するため、変動する値は最後に配置
ARG VERSION=dev
ARG GIT_SHA=unknown
ARG BUILD_TIME=unknown

ENV APP_VERSION=$VERSION \
    APP_GIT_SHA=$GIT_SHA \
    APP_BUILD_TIME=$BUILD_TIME

LABEL org.opencontainers.image.version=$VERSION \
      org.opencontainers.image.revision=$GIT_SHA \
      maintainer="Release Flow Practice"

USER bun
EXPOSE 4000/tcp

ENTRYPOINT ["bun", "run", "src/index.ts"]
