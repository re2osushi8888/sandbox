'use client'

import { UserRole } from "@repo/database"
import { useState } from "react"

export const CreateUserInput =  () => {
  const [suffix, setSuffix] = useState<string>('xxx')

  const data = {
    name: `test-user-${suffix}`,
    email: `test-user-${suffix}@example.com`,
    role: UserRole.BBB
  }

  return (
    <div>
      <input
        type="text"
        value={suffix}
        onChange={(e) => setSuffix(e.target.value)}
        placeholder="suffix"
      />
      <p>Name: {data.name}</p>
      <p>Email: {data.email}</p>
      <p>Role: {data.role}</p>
      <button>Create User</button>
    </div>
  )
}
