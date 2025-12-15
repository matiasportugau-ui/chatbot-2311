import NextAuth, { type NextAuthConfig } from 'next-auth'
import Credentials from 'next-auth/providers/credentials'
import type { UserRole } from '@/types/user'

/**
 * NextAuth configuration for CRM authentication
 */
export const authConfig: NextAuthConfig = {
  providers: [
    Credentials({
      name: 'credentials',
      credentials: {
        email: {
          label: 'Email',
          type: 'email',
          placeholder: 'email@example.com'
        },
        password: {
          label: 'Password',
          type: 'password'
        }
      },
      async authorize(credentials) {
        if (!credentials?.email || !credentials?.password) {
          return null
        }

        try {
          // Dynamic import to avoid bundling MongoDB in Edge runtime
          const { authenticateUser } = await import('./auth-service')

          const user = await authenticateUser(
            credentials.email as string,
            credentials.password as string
          )

          if (!user) {
            return null
          }

          return {
            id: user.id,
            email: user.email,
            name: user.name,
            role: user.role,
            image: user.avatar
          }
        } catch (error) {
          console.error('Authentication error:', error)
          return null
        }
      }
    })
  ],

  pages: {
    signIn: '/login',
    error: '/login'
  },

  session: {
    strategy: 'jwt',
    maxAge: 30 * 24 * 60 * 60 // 30 days
  },

  callbacks: {
    async jwt({ token, user, trigger, session }) {
      // Initial sign in
      if (user) {
        token.id = user.id
        token.role = (user as any).role as UserRole
        token.email = user.email
        token.name = user.name
      }

      // Handle session update
      if (trigger === 'update' && session) {
        if (session.name) token.name = session.name
        if (session.role) token.role = session.role
      }

      return token
    },

    async session({ session, token }) {
      if (token) {
        session.user.id = token.id as string
        session.user.role = token.role as UserRole
        session.user.email = token.email as string
        session.user.name = token.name as string
      }

      return session
    },

    async authorized({ auth, request }) {
      const { pathname } = request.nextUrl

      // Public routes that don't require authentication
      const publicRoutes = ['/login', '/register', '/api/auth']

      // Check if the route is public
      const isPublicRoute = publicRoutes.some(route =>
        pathname.startsWith(route)
      )

      // Allow public routes
      if (isPublicRoute) {
        return true
      }

      // Require authentication for all other routes
      const isAuthenticated = !!auth?.user

      return isAuthenticated
    }
  },

  events: {
    async signIn({ user }) {
      console.log(`User signed in: ${user.email}`)
    },
    async signOut({ token }) {
      console.log(`User signed out: ${token?.email}`)
    }
  },

  trustHost: true
}

export const {
  handlers: { GET, POST },
  auth,
  signIn,
  signOut
} = NextAuth(authConfig)
