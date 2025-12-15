import { ObjectId } from 'mongodb'
import bcrypt from 'bcryptjs'
import { connectDB } from '@/lib/mongodb'
import type { User, CreateUserInput, UpdateUserInput, SafeUser } from '@/types/user'

const SALT_ROUNDS = 12

/**
 * Get the users collection from MongoDB
 */
async function getUsersCollection() {
  const db = await connectDB()
  return db.collection<User>('users')
}

/**
 * Convert User document to SafeUser (remove password)
 */
function toSafeUser(user: User): SafeUser {
  const { password, ...safeUser } = user
  return {
    ...safeUser,
    id: user._id?.toString() || ''
  }
}

/**
 * Hash a plain text password
 */
export async function hashPassword(password: string): Promise<string> {
  return bcrypt.hash(password, SALT_ROUNDS)
}

/**
 * Verify a password against a hash
 */
export async function verifyPassword(password: string, hash: string): Promise<boolean> {
  return bcrypt.compare(password, hash)
}

/**
 * Get user by email
 */
export async function getUserByEmail(email: string): Promise<User | null> {
  const users = await getUsersCollection()
  return users.findOne({ email: email.toLowerCase() })
}

/**
 * Get user by ID
 */
export async function getUserById(id: string): Promise<User | null> {
  const users = await getUsersCollection()

  try {
    const objectId = new ObjectId(id)
    return users.findOne({ _id: objectId })
  } catch (error) {
    // Invalid ObjectId format
    return null
  }
}

/**
 * Get safe user by ID (without password)
 */
export async function getSafeUserById(id: string): Promise<SafeUser | null> {
  const user = await getUserById(id)
  return user ? toSafeUser(user) : null
}

/**
 * Create a new user
 */
export async function createUser(input: CreateUserInput): Promise<User> {
  const users = await getUsersCollection()

  // Check if user already exists
  const existing = await getUserByEmail(input.email)
  if (existing) {
    throw new Error('User with this email already exists')
  }

  // Validate password strength
  if (input.password.length < 8) {
    throw new Error('Password must be at least 8 characters long')
  }

  // Hash password
  const hashedPassword = await hashPassword(input.password)

  // Create user document
  const now = new Date()
  const user: User = {
    email: input.email.toLowerCase(),
    password: hashedPassword,
    name: input.name,
    role: input.role,
    settings: {
      theme: 'light',
      notifications: true,
      language: 'es'
    },
    createdAt: now,
    updatedAt: now
  }

  const result = await users.insertOne(user)

  return {
    ...user,
    _id: result.insertedId
  }
}

/**
 * Update user
 */
export async function updateUser(id: string, input: UpdateUserInput): Promise<User> {
  const users = await getUsersCollection()

  try {
    const objectId = new ObjectId(id)
    const now = new Date()

    // Build update object
    const updateDoc: any = {
      updatedAt: now
    }

    if (input.name !== undefined) updateDoc.name = input.name
    if (input.role !== undefined) updateDoc.role = input.role
    if (input.avatar !== undefined) updateDoc.avatar = input.avatar
    if (input.settings !== undefined) {
      updateDoc['settings'] = input.settings
    }

    const result = await users.findOneAndUpdate(
      { _id: objectId },
      { $set: updateDoc },
      { returnDocument: 'after' }
    )

    if (!result) {
      throw new Error('User not found')
    }

    return result
  } catch (error) {
    if (error instanceof Error) {
      throw error
    }
    throw new Error('Invalid user ID')
  }
}

/**
 * Update user password
 */
export async function updateUserPassword(id: string, newPassword: string): Promise<void> {
  const users = await getUsersCollection()

  // Validate password strength
  if (newPassword.length < 8) {
    throw new Error('Password must be at least 8 characters long')
  }

  try {
    const objectId = new ObjectId(id)
    const hashedPassword = await hashPassword(newPassword)

    const result = await users.updateOne(
      { _id: objectId },
      {
        $set: {
          password: hashedPassword,
          updatedAt: new Date()
        }
      }
    )

    if (result.matchedCount === 0) {
      throw new Error('User not found')
    }
  } catch (error) {
    if (error instanceof Error) {
      throw error
    }
    throw new Error('Invalid user ID')
  }
}

/**
 * Delete user
 */
export async function deleteUser(id: string): Promise<void> {
  const users = await getUsersCollection()

  try {
    const objectId = new ObjectId(id)
    const result = await users.deleteOne({ _id: objectId })

    if (result.deletedCount === 0) {
      throw new Error('User not found')
    }
  } catch (error) {
    if (error instanceof Error) {
      throw error
    }
    throw new Error('Invalid user ID')
  }
}

/**
 * Update user's last login timestamp
 */
export async function updateLastLogin(userId: string): Promise<void> {
  const users = await getUsersCollection()

  try {
    const objectId = new ObjectId(userId)
    await users.updateOne(
      { _id: objectId },
      { $set: { lastLogin: new Date() } }
    )
  } catch (error) {
    // Silently fail - last login is not critical
    console.error('Failed to update last login:', error)
  }
}

/**
 * List all users (for admin)
 */
export async function listUsers(options: {
  limit?: number
  skip?: number
  role?: string
} = {}): Promise<{ users: SafeUser[], total: number }> {
  const users = await getUsersCollection()

  const query = options.role ? { role: options.role } : {}

  const [usersList, total] = await Promise.all([
    users
      .find(query)
      .sort({ createdAt: -1 })
      .skip(options.skip || 0)
      .limit(options.limit || 50)
      .toArray(),
    users.countDocuments(query)
  ])

  return {
    users: usersList.map(toSafeUser),
    total
  }
}

/**
 * Check if email is available
 */
export async function isEmailAvailable(email: string): Promise<boolean> {
  const user = await getUserByEmail(email)
  return user === null
}

/**
 * Authenticate user with email and password
 */
export async function authenticateUser(
  email: string,
  password: string
): Promise<SafeUser | null> {
  const user = await getUserByEmail(email)

  if (!user) {
    return null
  }

  const isValid = await verifyPassword(password, user.password)

  if (!isValid) {
    return null
  }

  // Update last login
  if (user._id) {
    await updateLastLogin(user._id.toString())
  }

  return toSafeUser(user)
}
