import type { UserRole } from '@/types/user'

/**
 * Permission types for the CRM system
 */
export type Permission =
  // User Management
  | 'users:create'
  | 'users:read'
  | 'users:update'
  | 'users:delete'
  | 'users:list'

  // Quote Management
  | 'quotes:create'
  | 'quotes:read:own'
  | 'quotes:read:all'
  | 'quotes:update:own'
  | 'quotes:update:all'
  | 'quotes:delete:own'
  | 'quotes:delete:all'
  | 'quotes:change_status'

  // Customer Management
  | 'customers:create'
  | 'customers:read:own'
  | 'customers:read:all'
  | 'customers:update:own'
  | 'customers:update:all'
  | 'customers:delete'

  // Analytics & Reports
  | 'analytics:view:basic'
  | 'analytics:view:advanced'
  | 'analytics:export'

  // Settings & Configuration
  | 'settings:view'
  | 'settings:update'

  // Google Sheets Sync
  | 'sheets:sync'
  | 'sheets:configure'

/**
 * Permission matrix defining what each role can do
 */
const ROLE_PERMISSIONS: Record<UserRole, Permission[]> = {
  // Admin: Full access to everything
  admin: [
    // Users
    'users:create',
    'users:read',
    'users:update',
    'users:delete',
    'users:list',

    // Quotes
    'quotes:create',
    'quotes:read:own',
    'quotes:read:all',
    'quotes:update:own',
    'quotes:update:all',
    'quotes:delete:own',
    'quotes:delete:all',
    'quotes:change_status',

    // Customers
    'customers:create',
    'customers:read:own',
    'customers:read:all',
    'customers:update:own',
    'customers:update:all',
    'customers:delete',

    // Analytics
    'analytics:view:basic',
    'analytics:view:advanced',
    'analytics:export',

    // Settings
    'settings:view',
    'settings:update',

    // Sheets
    'sheets:sync',
    'sheets:configure'
  ],

  // Manager: Manage team and view all data
  manager: [
    // Users (limited)
    'users:read',
    'users:update', // Can update team members but not delete
    'users:list',

    // Quotes
    'quotes:create',
    'quotes:read:own',
    'quotes:read:all',
    'quotes:update:own',
    'quotes:update:all',
    'quotes:delete:own',
    'quotes:change_status',

    // Customers
    'customers:create',
    'customers:read:own',
    'customers:read:all',
    'customers:update:own',
    'customers:update:all',

    // Analytics
    'analytics:view:basic',
    'analytics:view:advanced',
    'analytics:export',

    // Settings
    'settings:view',

    // Sheets
    'sheets:sync'
  ],

  // Sales: Manage own quotes and customers
  sales: [
    // Quotes
    'quotes:create',
    'quotes:read:own',
    'quotes:update:own',
    'quotes:delete:own',
    'quotes:change_status',

    // Customers
    'customers:create',
    'customers:read:own',
    'customers:update:own',

    // Analytics (basic only)
    'analytics:view:basic',

    // Settings (view only)
    'settings:view'
  ],

  // Viewer: Read-only access
  viewer: [
    // Quotes (read only)
    'quotes:read:all',

    // Customers (read only)
    'customers:read:all',

    // Analytics (basic only)
    'analytics:view:basic',

    // Settings (view only)
    'settings:view'
  ]
}

/**
 * Check if a role has a specific permission
 */
export function hasPermission(role: UserRole, permission: Permission): boolean {
  const permissions = ROLE_PERMISSIONS[role]
  return permissions.includes(permission)
}

/**
 * Check if a role has any of the specified permissions
 */
export function hasAnyPermission(role: UserRole, permissions: Permission[]): boolean {
  return permissions.some(permission => hasPermission(role, permission))
}

/**
 * Check if a role has all of the specified permissions
 */
export function hasAllPermissions(role: UserRole, permissions: Permission[]): boolean {
  return permissions.every(permission => hasPermission(role, permission))
}

/**
 * Get all permissions for a role
 */
export function getRolePermissions(role: UserRole): Permission[] {
  return ROLE_PERMISSIONS[role]
}

/**
 * Check if a user can access a resource owned by another user
 */
export function canAccessResource(
  userRole: UserRole,
  resourceOwnerId: string,
  currentUserId: string,
  resourceType: 'quote' | 'customer'
): boolean {
  // Admins and managers can access all resources
  if (userRole === 'admin' || userRole === 'manager') {
    return true
  }

  // Viewers can read all resources
  if (userRole === 'viewer') {
    return true
  }

  // Sales users can only access their own resources
  if (userRole === 'sales') {
    return resourceOwnerId === currentUserId
  }

  return false
}

/**
 * Check if a user can modify a resource owned by another user
 */
export function canModifyResource(
  userRole: UserRole,
  resourceOwnerId: string,
  currentUserId: string,
  resourceType: 'quote' | 'customer'
): boolean {
  // Admins can modify all resources
  if (userRole === 'admin') {
    return true
  }

  // Managers can modify all quotes and customers
  if (userRole === 'manager') {
    return true
  }

  // Sales users can only modify their own resources
  if (userRole === 'sales') {
    return resourceOwnerId === currentUserId
  }

  // Viewers cannot modify anything
  return false
}

/**
 * Check if a user can delete a resource
 */
export function canDeleteResource(
  userRole: UserRole,
  resourceOwnerId: string,
  currentUserId: string,
  resourceType: 'quote' | 'customer'
): boolean {
  // Only admins can delete customers
  if (resourceType === 'customer') {
    return userRole === 'admin'
  }

  // For quotes:
  // - Admins can delete all quotes
  if (userRole === 'admin') {
    return true
  }

  // - Managers and sales can delete their own quotes
  if (userRole === 'manager' || userRole === 'sales') {
    return resourceOwnerId === currentUserId
  }

  return false
}

/**
 * Check if a role is higher in hierarchy than another
 */
export function isRoleHigherThan(role: UserRole, comparedTo: UserRole): boolean {
  const hierarchy: Record<UserRole, number> = {
    admin: 4,
    manager: 3,
    sales: 2,
    viewer: 1
  }

  return hierarchy[role] > hierarchy[comparedTo]
}

/**
 * Check if a user can manage another user
 * (Admins can manage everyone, managers can manage sales and viewers)
 */
export function canManageUser(managerRole: UserRole, targetRole: UserRole): boolean {
  if (managerRole === 'admin') {
    return true
  }

  if (managerRole === 'manager') {
    return targetRole === 'sales' || targetRole === 'viewer'
  }

  return false
}

/**
 * Get the maximum role a user can assign
 */
export function getMaxAssignableRole(role: UserRole): UserRole[] {
  switch (role) {
    case 'admin':
      return ['admin', 'manager', 'sales', 'viewer']
    case 'manager':
      return ['sales', 'viewer']
    default:
      return []
  }
}

/**
 * Validate if an action is allowed
 */
export function validateAction(
  role: UserRole,
  action: Permission,
  context?: {
    resourceOwnerId?: string
    currentUserId?: string
    resourceType?: 'quote' | 'customer'
  }
): { allowed: boolean; reason?: string } {
  // Check basic permission
  if (!hasPermission(role, action)) {
    return {
      allowed: false,
      reason: `Role '${role}' does not have permission '${action}'`
    }
  }

  // For 'own' permissions, check ownership
  if (action.includes(':own') && context) {
    if (!context.resourceOwnerId || !context.currentUserId) {
      return {
        allowed: false,
        reason: 'Resource ownership information is required'
      }
    }

    if (context.resourceOwnerId !== context.currentUserId) {
      return {
        allowed: false,
        reason: 'You can only access your own resources'
      }
    }
  }

  return { allowed: true }
}
