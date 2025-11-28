export const dynamic = 'force-dynamic'

import { validateMongoDBURI } from '@/lib/mongodb'
import { NextRequest, NextResponse } from 'next/server'

/**
 * MongoDB Connection String Validation Endpoint
 * POST /api/mongodb/validate
 *
 * Validates MongoDB connection string format
 *
 * Request body:
 * - uri: string (required) - MongoDB connection string
 */
export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { uri } = body

    if (!uri || typeof uri !== 'string') {
      return NextResponse.json(
        {
          success: false,
          error: 'MongoDB connection string is required',
          valid: false,
        },
        { status: 400 }
      )
    }

    try {
      validateMongoDBURI(uri)

      // Additional checks
      const trimmedUri = uri.trim()
      const isSRV = trimmedUri.startsWith('mongodb+srv://')
      const isStandard = trimmedUri.startsWith('mongodb://')

      // Extract database name if present
      let databaseName: string | null = null
      try {
        const url = new URL(trimmedUri)
        if (url.pathname && url.pathname.length > 1) {
          databaseName = url.pathname.substring(1)
        }
      } catch (e) {
        // URL parsing failed, but format is valid
      }

      return NextResponse.json({
        success: true,
        valid: true,
        format: isSRV ? 'mongodb+srv' : isStandard ? 'mongodb' : 'unknown',
        databaseName: databaseName || null,
        message: 'MongoDB connection string format is valid',
      })
    } catch (validationError: any) {
      return NextResponse.json(
        {
          success: false,
          valid: false,
          error:
            validationError.message ||
            'Invalid MongoDB connection string format',
          message:
            'MongoDB connection strings must begin with "mongodb://" or "mongodb+srv://"',
        },
        { status: 400 }
      )
    }
  } catch (error: any) {
    console.error('MongoDB Validation API Error:', error)
    return NextResponse.json(
      {
        success: false,
        valid: false,
        error: error.message || 'Internal server error',
      },
      { status: 500 }
    )
  }
}

/**
 * GET /api/mongodb/validate
 * Returns validation rules and examples
 */
export async function GET() {
  return NextResponse.json({
    success: true,
    rules: {
      format: 'Must start with "mongodb://" or "mongodb+srv://"',
      examples: {
        local: 'mongodb://localhost:27017/bmc-cotizaciones',
        atlas: 'mongodb+srv://username:password@cluster0.mongodb.net/database',
        standard: 'mongodb://username:password@host:port/database',
      },
      notes: [
        'For MongoDB Atlas, use mongodb+srv:// format',
        'For local MongoDB, use mongodb:// format',
        'Replace <password> with your actual password',
        'Database name can be specified in the path',
      ],
    },
  })
}
