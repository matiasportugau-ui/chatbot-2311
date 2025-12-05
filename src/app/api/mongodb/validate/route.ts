export const dynamic = 'force-dynamic'

import { validateMongoDBURI } from '@/lib/mongodb'

import { withRateLimit } from '@/lib/rate-limit'
import { RATE_LIMITS } from '@/types/api'
import { NextRequest } from 'next/server'
import {
  successResponse,
  errorResponse,
  validationErrorResponse,
} from '@/lib/api-response'


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
      return validationErrorResponse(
        ['MongoDB connection string is required'],
        'Missing required field'
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

      return successResponse({
        valid: true,
        format: isSRV ? 'mongodb+srv' : isStandard ? 'mongodb' : 'unknown',
        databaseName: databaseName || null,

      }, 'MongoDB connection string format is valid')
    } catch (validationError: unknown) {
      const errorMessage = validationError instanceof Error
        ? validationError.message
        : 'Invalid MongoDB connection string format'
      return validationErrorResponse(
        [errorMessage],
        'MongoDB connection strings must begin with "mongodb://" or "mongodb+srv://"'

      )
    }
  } catch (error: any) {
    console.error('MongoDB Validation API Error:', error)

    const errorMessage = error instanceof Error ? error.message : 'Internal server error'
    return errorResponse(errorMessage, 500)

  }
}

/**
 * GET /api/mongodb/validate
 * Returns validation rules and examples
 */

async function getValidateHandler() {
  return successResponse({

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
