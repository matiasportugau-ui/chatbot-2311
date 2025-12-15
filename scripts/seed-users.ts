#!/usr/bin/env ts-node
/**
 * Seed script to create initial admin user
 *
 * Usage: npx tsx scripts/seed-users.ts
 */

import 'dotenv/config'
import { createUser, getUserByEmail } from '../src/lib/auth/auth-service'

async function seedUsers() {
  console.log('🌱 Seeding users...')

  // Create admin user
  const adminEmail = 'admin@example.com'

  try {
    const existingAdmin = await getUserByEmail(adminEmail)

    if (existingAdmin) {
      console.log('✓ Admin user already exists:', adminEmail)
    } else {
      await createUser({
        email: adminEmail,
        password: 'admin123',
        name: 'Admin User',
        role: 'admin'
      })
      console.log('✓ Created admin user:', adminEmail)
      console.log('  Password: admin123')
    }

    // Create other demo users
    const users = [
      {
        email: 'manager@example.com',
        password: 'manager123',
        name: 'Manager User',
        role: 'manager' as const
      },
      {
        email: 'sales@example.com',
        password: 'sales123',
        name: 'Sales User',
        role: 'sales' as const
      },
      {
        email: 'viewer@example.com',
        password: 'viewer123',
        name: 'Viewer User',
        role: 'viewer' as const
      }
    ]

    for (const userData of users) {
      const existing = await getUserByEmail(userData.email)

      if (existing) {
        console.log(`✓ User already exists: ${userData.email}`)
      } else {
        await createUser(userData)
        console.log(`✓ Created ${userData.role} user: ${userData.email}`)
        console.log(`  Password: ${userData.password}`)
      }
    }

    console.log('\n✅ User seeding complete!')
    console.log('\nDemo credentials:')
    console.log('Admin:   admin@example.com   / admin123')
    console.log('Manager: manager@example.com / manager123')
    console.log('Sales:   sales@example.com   / sales123')
    console.log('Viewer:  viewer@example.com  / viewer123')

  } catch (error) {
    console.error('❌ Error seeding users:', error)
    process.exit(1)
  }

  process.exit(0)
}

// Run the seed function
seedUsers()
