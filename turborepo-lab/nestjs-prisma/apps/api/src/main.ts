import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';

if (process.env.NODE_ENV == 'PROD') {
  async function bootstrap() {
    const app = await NestFactory.create(AppModule);
    await app.listen(3000);
  }
  // eslint-disable-next-line @typescript-eslint/no-floating-promises
  bootstrap();
}

export const viteNodeApp = NestFactory.create(AppModule);
