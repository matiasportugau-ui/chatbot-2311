import { NextRequest, NextResponse } from 'next/server';
import { exec } from 'child_process';
import { promisify } from 'util';
import path from 'path';

<<<<<<< Updated upstream
const execAsync = promisify(exec);
=======
import {
  errorResponse,
  successResponse,
  validationErrorResponse,
} from '@/lib/api-response'
import { requireAdmin } from '@/lib/auth'
import { connectDB } from '@/lib/mongodb'
import { withRateLimit } from '@/lib/rate-limit'
import { promises as fs } from 'fs'
import { NextRequest } from 'next/server'
import path from 'path'
>>>>>>> Stashed changes

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const action = searchParams.get('action') || 'scan';
    const source = searchParams.get('source') || 'all';

    if (action === 'scan') {
      const { stdout } = await execAsync(
        `python3 ${path.join(process.cwd(), 'recover.py')} scan --source ${source} --config backup_system/backup_config.json`
      );
      
      return NextResponse.json({
        success: true,
        data: stdout
      });
    }

<<<<<<< Updated upstream
    return NextResponse.json({ error: 'Invalid action' }, { status: 400 });
  } catch (error: any) {
    return NextResponse.json(
      { error: error.message },
      { status: 500 }
    );
=======
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
            if (
              collectionName === 'conversations' ||
              collectionName === 'conversaciones'
            ) {
              report.summary.totalConversations += count
            } else if (
              collectionName === 'quotes' ||
              collectionName === 'cotizaciones'
            ) {
              report.summary.totalQuotes += count
            } else if (
              collectionName === 'sessions' ||
              collectionName === 'context'
            ) {
              report.summary.totalSessions += count
            }
          }
        } catch (err: unknown) {
          console.warn(
            `Error scanning collection ${collectionName}:`,
            err instanceof Error ? err.message : String(err)
          )
        }
      }
    } catch (error: unknown) {
      report.mongodb.collections.push({
        source: 'mongodb',
        count: 0,
        data: [],
        errors: [
          error instanceof Error
            ? error.message
            : 'Failed to connect to MongoDB',
        ],
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
            if (
              file.isFile() &&
              backupPatterns.some(pattern => pattern.test(file.name))
            ) {
              try {
                const filePath = path.join(dirPath, file.name)
                const content = await fs.readFile(filePath, 'utf-8')
                const data = JSON.parse(content)

                let conversations: Record<string, unknown>[] = []
                if (Array.isArray(data)) {
                  conversations = data
                } else if (
                  data.conversations &&
                  Array.isArray(data.conversations)
                ) {
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
              } catch (err: unknown) {
                // Skip files that can't be parsed
                console.warn(
                  `Error reading file ${file.name}:`,
                  err instanceof Error ? err.message : String(err)
                )
              }
            }
          }
        } catch (err: unknown) {
          // Directory might not exist, skip
        }
      }
    } catch (error: unknown) {
      report.summary.recommendations.push(
        `Filesystem scan error: ${error instanceof Error ? error.message : String(error)}`
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

    return successResponse({
      report,
      action: 'scan',
      dryRun,
    })
  } catch (error: unknown) {
    console.error('Recovery API Error:', error)
    const errorMessage =
      error instanceof Error ? error.message : 'Internal server error'
    return errorResponse(errorMessage, 500)
>>>>>>> Stashed changes
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { action, backup_id, scope, selective, dry_run, conflict_resolution } = body;

    if (action === 'restore') {
      const scopeArg = scope ? `--scope ${scope.join(',')}` : '';
      const selectiveArg = selective ? `--selective ${selective.join(',')}` : '';
      const dryRunArg = dry_run ? '--dry-run' : '';
      const conflictArg = conflict_resolution ? `--conflict-resolution ${conflict_resolution}` : '';
      
      const { stdout } = await execAsync(
        `python3 ${path.join(process.cwd(), 'recover.py')} restore ${backup_id} ${scopeArg} ${selectiveArg} ${dryRunArg} ${conflictArg} --config backup_system/backup_config.json`
      );
      
      return NextResponse.json({
        success: true,
        data: stdout
      });
    }

<<<<<<< Updated upstream
    if (action === 'preview') {
      const { stdout } = await execAsync(
        `python3 ${path.join(process.cwd(), 'recover.py')} preview ${backup_id} --config backup_system/backup_config.json`
      );
      
      return NextResponse.json({
        success: true,
        data: stdout
      });
    }

    return NextResponse.json({ error: 'Invalid action' }, { status: 400 });
  } catch (error: any) {
    return NextResponse.json(
      { error: error.message },
      { status: 500 }
    );
  }
}
=======
    return validationErrorResponse(
      ['Invalid action'],
      'Invalid action parameter'
    )
  } catch (error: unknown) {
    console.error('Recovery POST API Error:', error)
    const errorMessage =
      error instanceof Error ? error.message : 'Internal server error'
    return errorResponse(errorMessage, 500)
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

    const collections = [
      'conversations',
      'conversaciones',
      'quotes',
      'sessions',
    ]
    const backupData: {
      timestamp: string
      collections: Record<string, unknown[]>
    } = {
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
      } catch (err: unknown) {
        console.warn(
          `Error backing up ${collectionName}:`,
          err instanceof Error ? err.message : String(err)
        )
      }
    }

    const backupFile = path.join(backupDir, `backup_${timestamp}.json`)
    await fs.writeFile(backupFile, JSON.stringify(backupData, null, 2), 'utf-8')

    const collectionNames =
      backupData.collections && typeof backupData.collections === 'object'
        ? Object.keys(backupData.collections)
        : []

    return successResponse(
      {
        file: backupFile,
        timestamp: backupData.timestamp,
        collections: collectionNames,
      },
      'Backup created successfully'
    )
  } catch (error: unknown) {
    const errorMessage =
      error instanceof Error ? error.message : 'Failed to create backup'
    return errorResponse(errorMessage, 500)
  }
}

async function restoreData(source: string, data: Record<string, unknown>[]) {
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
      } catch (err: unknown) {
        failed++
        errors.push(
          `Item ${restored + failed}: ${err instanceof Error ? err.message : String(err)}`
        )
      }
    }

    return successResponse(
      {
        restored,
        failed,
        errors: errors.slice(0, 10), // Limit error messages
      },
      'Data restored successfully'
    )
  } catch (error: unknown) {
    const errorMessage =
      error instanceof Error ? error.message : 'Failed to restore data'
    return errorResponse(errorMessage, 500)
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
>>>>>>> Stashed changes
