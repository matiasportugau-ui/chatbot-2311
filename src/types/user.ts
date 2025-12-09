export interface User {
    id: string
    role: 'admin' | 'user' | string
    name?: string
    email?: string
    image?: string
}

export type AuthenticatedUser = User | null
