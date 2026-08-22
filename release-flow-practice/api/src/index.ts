import { Hono } from 'hono'

const app = new Hono()

const port = Number(process.env.PORT) || 4000

app.get('/', (c) => {
  return c.text('Hello Hono!')
})

app.get('/health', (c) => {
  return c.json({ status: 'ok' })
})

app.get('/version', (c) => {
  return c.json({
    version:   process.env.APP_VERSION    ?? 'dev',
    gitSha:    process.env.APP_GIT_SHA    ?? 'unknown',
    buildTime: process.env.APP_BUILD_TIME ?? 'unknown',
    env:       process.env.ENVIRONMENT    ?? 'local',
    revision:  process.env.K_REVISION     ?? 'local',
  })
})

export default {
  fetch: app.fetch,
  port,
}
