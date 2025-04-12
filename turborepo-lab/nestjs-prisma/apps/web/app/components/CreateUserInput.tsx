'use client'

import { useState } from "react"

export const CreateUserInput =  () => {
  const [suffix, setSuffix] = useState<string>()

  return (
    <div>
      <input
        type="text"
        value={suffix}
        onChange={(e) => setSuffix(e.target.value)}
        placeholder="suffix"
      />
      <button>Create User</button>
    </div>
  )
}
