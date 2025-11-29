export const dynamic = 'force-dynamic'

import { NextRequest, NextResponse } from 'next/server'
import { connectDB } from '@/lib/mongodb'
import { promises as fs } from 'fs'
import path from 'path'
import { requireAdmin } from '@/lib/auth'
import { withRateLimit } from '@/lib/rate-limit'

/**
 * Data Recovery API Endpoint
 * GET /api/recovery - Scan and recover lost conversation data
 * POST /api/recovery - Restore recovered data
 */

interface RecoveryResult {
  source: string
  collection?: string
  count: number
  data: any[]
  errors?: string[]
}

interface RecoveryReport {
  timestamp: string
  mongodb: {
    connected: boolean
    database: string
    collections: RecoveryResult[]
    totalFound: number
  }
  filesystem: {
    backups: RecoveryResult[]
    exports: RecoveryResult[]
    totalFound: number
  }
  summary: {
    totalConversations: number
    totalQuotes: number
    totalSessions: number
    recoveryStatus: 'success' | 'partial' | 'failed'
    recommendations: string[]
  }
}

async function getRecoveryHandler(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const action = searchParams.get('action') || 'scan' // 'scan' | 'restore' | 'backup'
    const dryRun = searchParams.get('dryRun') === 'true'

    if (action === 'backup') {
      return await createBackup()
    }

    const report: RecoveryReport = {
      timestamp: new Date().toISOString(),
      mongodb: {
        connected: false,
        database: '',
        collections: [],
        totalFound: 0,
      },
      filesystem: {
        backups: [],
        exports: [],
        totalFound: 0,
      },
      summary: {
        totalConversations: 0,
        totalQuotes: 0,
        totalSessions: 0,
        recoveryStatus: 'failed',
        recommendations: [],
      },
    }

    // Scan MongoDB
    try {
      const db = await connectDB()
      report.mongodb.connected = true
      report.mongodb.database = db.databaseName

      // Check multiple possible collection names
      const collectionNames = [
        'conversations',
        'conversaciones',
        'sessions',
        'context',
        'quotes',
        'cotizaciones',
      ]

      for (const collectionName of collectionNames) {
        try {
          const collection = db.collection(collectionName)
          const count = await collection.countDocuments({})
          
          if (count > 0) {
            const data = await collection
              .find({})
              .sort({ timestamp: -1, createdAt: -1, _id: -1 })
              .limit(1000)
              .toArray()

            const result: RecoveryResult = {
              source: 'mongodb',
              collection: collectionName,
              count,
              data: data.slice(0, 100), // Limit data in response
            }

            report.mongodb.collections.push(result)
            report.mongodb.totalFound += count

            // Update summary counts
            if (collectionName === 'conversations' || collectionName === 'conversaciones') {
              report.summary.totalConversations += count
            } else if (collectionName === 'quotes' || collectionName === 'cotizaciones') {
              report.summary.totalQuotes += count
            } else if (collectionName === 'sessions' || collectionName === 'context') {
              report.summary.totalSessions += count
            }
          }
        } catch (err: any) {
          console.warn(`Error scanning collection ${collectionName}:`, err.message)
        }
      }
    } catch (error: any) {
      report.mongodb.collections.push({
        source: 'mongodb',
        count: 0,
        data: [],
        errors: [error.message || 'Failed to connect to MongoDB'],
      })
      report.summary.recommendations.push(
        'MongoDB connection failed. Check MONGODB_URI environment variable.'
      )
    }

    // Scan filesystem for backup files
    try {
      const workspaceRoot = process.cwd()
      const backupDirs = ['backups', 'exportaciones', 'exports', '.']
      const backupPatterns = [
        /conversation.*\.json$/i,
        /backup.*\.json$/i,
        /export.*\.json$/i,
        /.*_conversations\.json$/i,
        /.*_export\.json$/i,
      ]

      for (const dir of backupDirs) {
        try {
          const dirPath = path.join(workspaceRoot, dir)
          const files = await fs.readdir(dirPath, { withFileTypes: true })

          for (const file of files) {
            if (file.isFile() && backupPatterns.some((pattern) => pattern.test(file.name))) {
              try {
                const filePath = path.join(dirPath, file.name)
                const content = await fs.readFile(filePath, 'utf-8')
                const data = JSON.parse(content)

                let conversations: any[] = []
                if (Array.isArray(data)) {
                  conversations = data
                } else if (data.conversations && Array.isArray(data.conversations)) {
                  conversations = data.conversations
                } else if (data.messages && Array.isArray(data.messages)) {
                  conversations = [data]
                } else if (data.data && Array.isArray(data.data)) {
                  conversations = data.data
                }

                if (conversations.length > 0) {
                  report.filesystem.backups.push({
                    source: 'filesystem',
                    count: conversations.length,
                    data: conversations.slice(0, 50),
                  })
                  report.filesystem.totalFound += conversations.length
                  report.summary.totalConversations += conversations.length
                }
              } catch (err: any) {
                // Skip files that can't be parsed
                console.warn(`Error reading file ${file.name}:`, err.message)
              }
            }
          }
        } catch (err: any) {
          // Directory might not exist, skip
        }
      }
    } catch (error: any) {
      report.summary.recommendations.push(
        `Filesystem scan error: ${error.message}`
      )
    }

    // Determine recovery status
    if (report.mongodb.totalFound > 0 || report.filesystem.totalFound > 0) {
      report.summary.recoveryStatus = 'success'
      if (report.mongodb.totalFound === 0 && report.filesystem.totalFound > 0) {
        report.summary.recommendations.push(
          'Data found in backup files but not in MongoDB. Consider restoring from backups.'
        )
      }
    } else {
      report.summary.recoveryStatus = 'failed'
      report.summary.recommendations.push(
        'No conversation data found. Check if MongoDB is properly configured and contains data.'
      )
    }

    // Add general recommendations
    if (report.summary.totalConversations === 0) {
      report.summary.recommendations.push(
        'No conversations found. Verify that the chat system is saving conversations correctly.'
      )
    }

    if (report.mongodb.connected && report.mongodb.totalFound === 0) {
      report.summary.recommendations.push(
        'MongoDB is connected but empty. Check if data was accidentally deleted or if collections use different names.'
      )
    }

    return NextResponse.json({
      success: true,
      report,
      action: 'scan',
      dryRun,
    })
  } catch (error: any) {
    console.error('Recovery API Error:', error)
    return NextResponse.json(
      {
        success: false,
        error: error.message || 'Internal server error',
        report: null,
      },
      { status: 500 }
    )
  }
}

async function postRecoveryHandler(request: NextRequest) {
  try {
    const body = await request.json()
    const { action, source, data } = body

    if (action === 'restore') {
      return await restoreData(source, data)
    }

    return NextResponse.json(
      { success: false, error: 'Invalid action' },
      { status: 400 }
    )
  } catch (error: any) {
    console.error('Recovery POST API Error:', error)
    return NextResponse.json(
      {
        success: false,
        error: error.message || 'Internal server error',
      },
      { status: 500 }
    )
  }
}

async function createBackup() {
  try {
    const db = await connectDB()
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-')
    const backupDir = path.join(process.cwd(), 'backups')
    
    // Ensure backup directory exists
    try {
      await fs.mkdir(backupDir, { recursive: true })
    } catch (err) {
      // Directory might already exist
    }

    const collections = ['conversations', 'conversaciones', 'quotes', 'sessions']
    const backupData: any = {
      timestamp: new Date().toISOString(),
      collections: {},
    }

    for (const collectionName of collections) {
      try {
        const collection = db.collection(collectionName)
        const data = await collection.find({}).toArray()
        if (data.length > 0) {
          backupData.collections[collectionName] = data
        }
      } catch (err: any) {
        console.warn(`Error backing up ${collectionName}:`, err.message)
      }
    }

    const backupFile = path.join(backupDir, `backup_${timestamp}.json`)
    await fs.writeFile(backupFile, JSON.stringify(backupData, null, 2), 'utf-8')

    return NextResponse.json({
      success: true,
      message: 'Backup created successfully',
      file: backupFile,
      timestamp: backupData.timestamp,
      collections: Object.keys(backupData.collections),
    })
  } catch (error: any) {
    return NextResponse.json(
      {
        success: false,
        error: error.message || 'Failed to create backup',
      },
      { status: 500 }
    )
  }
}

async function restoreData(source: string, data: any[]) {
  try {
    const db = await connectDB()
    const targetCollection = db.collection('conversations')
    
    let restored = 0
    let failed = 0
    const errors: string[] = []

    for (const item of data) {
      try {
        // Remove _id to allow MongoDB to create new one
        const { _id, ...itemData } = item
        
        // Ensure required fields
        if (!itemData.timestamp && !itemData.createdAt) {
          itemData.timestamp = new Date()
        }
        if (!itemData.createdAt) {
          itemData.createdAt = itemData.timestamp || new Date()
        }

        await targetCollection.insertOne(itemData)
        restored++
      } catch (err: any) {
        failed++
        errors.push(`Item ${restored + failed}: ${err.message}`)
      }
    }

    return NextResponse.json({
      success: true,
      message: 'Data restored successfully',
      restored,
      failed,
      errors: errors.slice(0, 10), // Limit error messages
    })
  } catch (error: any) {
    return NextResponse.json(
      {
        success: false,
        error: error.message || 'Failed to restore data',
      },
      { status: 500 }
    )
  }
}


// Export with admin authentication and rate limiting
export const GET = withRateLimit(
  requireAdmin(async (request: NextRequest) => getRecoveryHandler(request)),
  10, // 10 requests per 15 minutes (admin only)
  15 * 60 * 1000
)
export const POST = withRateLimit(
  requireAdmin(async (request: NextRequest) => postRecoveryHandler(request)),
  5, // 5 requests per 15 minutes (admin only, lower for write operations)
  15 * 60 * 1000
)
