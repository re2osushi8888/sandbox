import { prisma } from "@repo/database";
import { CreateUserInput } from "./components/CreateUserInput";

export default async function IndexPage() {
  const users = await prisma.user.findMany();

  return (
    <div>
      <h1>Hello World</h1>
      <CreateUserInput />
      <pre>{JSON.stringify(users, null, 2)}</pre>
    </div>
  );
}
