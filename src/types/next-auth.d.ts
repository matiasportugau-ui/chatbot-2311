import 'next-auth'
import 'next-auth/jwt'
import type { UserRole } from './user'

/**
 * Extend NextAuth types to include custom user properties
 */
declare module 'next-auth' {
  interface User {
    id: string
    email: string
    name: string
    role: UserRole
    image?: string
  }

  interface Session {
    user: {
      id: string
      email: string
      name: string
      role: UserRole
      image?: string
    }
  }
}

declare module 'next-auth/jwt' {
  interface JWT {
    id: string
    email: string
    name: string
    role: UserRole
  }
}
