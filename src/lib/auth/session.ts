import { auth } from './auth.config'
import type { UserRole } from '@/types/user'
import { hasPermission, type Permission } from './rbac'

/**
 * Get the current session on the server
 */
export async function getSession() {
  return auth()
}

/**
 * Get the current user from the session
 */
export async function getCurrentUser() {
  const session = await getSession()
  return session?.user ?? null
}

/**
 * Require authentication - throw error if not authenticated
 */
export async function requireAuth() {
  const session = await getSession()

  if (!session?.user) {
    throw new Error('Unauthorized - Authentication required')
  }

  return session.user
}

/**
 * Require specific role(s)
 */
export async function requireRole(roles: UserRole | UserRole[]) {
  const user = await requireAuth()

  const allowedRoles = Array.isArray(roles) ? roles : [roles]

  if (!allowedRoles.includes(user.role)) {
    throw new Error(
      `Forbidden - Required role: ${allowedRoles.join(' or ')}, got: ${user.role}`
    )
  }

  return user
}

/**
 * Require specific permission(s)
 */
export async function requirePermission(permission: Permission | Permission[]) {
  const user = await requireAuth()

  const permissions = Array.isArray(permission) ? permission : [permission]

  for (const perm of permissions) {
    if (!hasPermission(user.role, perm)) {
      throw new Error(`Forbidden - Missing permission: ${perm}`)
    }
  }

  return user
}

/**
 * Check if user has permission (returns boolean instead of throwing)
 */
export async function checkPermission(permission: Permission): Promise<boolean> {
  try {
    const user = await getCurrentUser()
    if (!user) return false
    return hasPermission(user.role, permission)
  } catch {
    return false
  }
}

/**
 * Check if user is authenticated (returns boolean instead of throwing)
 */
export async function isAuthenticated(): Promise<boolean> {
  const session = await getSession()
  return !!session?.user
}

/**
 * Check if user has role (returns boolean instead of throwing)
 */
export async function hasRole(roles: UserRole | UserRole[]): Promise<boolean> {
  try {
    const user = await getCurrentUser()
    if (!user) return false

    const allowedRoles = Array.isArray(roles) ? roles : [roles]
    return allowedRoles.includes(user.role)
  } catch {
    return false
  }
}

/**
 * Get user ID from session
 */
export async function getCurrentUserId(): Promise<string | null> {
  const user = await getCurrentUser()
  return user?.id ?? null
}

/**
 * Check if current user is admin
 */
export async function isAdmin(): Promise<boolean> {
  return hasRole('admin')
}

/**
 * Check if current user is admin or manager
 */
export async function isAdminOrManager(): Promise<boolean> {
  return hasRole(['admin', 'manager'])
}
