import { Injectable, OnModuleInit } from '@nestjs/common';
// import { PrismaClient } from '@repo/database';
class PrismaClient {}

@Injectable()
export class PrismaService extends PrismaClient implements OnModuleInit {
  async onModuleInit() {
    // /eslint-disable-next-line @typescript-eslint/no-unsafe-call
    // await this.$connect();
  }
}
