import { ObjectId } from 'mongodb'

export type UserRole = 'admin' | 'manager' | 'sales' | 'viewer'

export interface User {
  _id?: ObjectId
  email: string
  password: string // hashed
  name: string
  role: UserRole
  avatar?: string
  settings: {
    theme: 'light' | 'dark'
    notifications: boolean
    language: 'es' | 'en'
  }
  createdAt: Date
  updatedAt: Date
  lastLogin?: Date
}

export interface CreateUserInput {
  email: string
  password: string
  name: string
  role: UserRole
}

export interface UpdateUserInput {
  name?: string
  role?: UserRole
  avatar?: string
  settings?: Partial<User['settings']>
}

export interface SafeUser extends Omit<User, 'password'> {
  id: string
}

// For NextAuth session
export interface AuthenticatedUser {
  id: string
  email: string
  name: string
  role: UserRole
}
