export const dynamic = 'force-dynamic'

import { errorResponse, successResponse } from '@/lib/api-response'
import { connectDB, validateMongoDBURI } from '@/lib/mongodb'
import { withRateLimit } from '@/lib/rate-limit'
import {
  getSystemStatus,
  initializeSimpleSystem,
} from '@/lib/simple-initialize'

import { RATE_LIMITS } from '@/types/api'
import { NextRequest } from 'next/server'


/**
 * Health Check Endpoint Simplificado
 * Verifica el estado de todos los servicios del sistema BMC
 */
export async function GET() {
  try {
    const result = await initializeSimpleSystem()

    // Test MongoDB connection
    let mongodbStatus = 'missing'
    let mongodbError: string | undefined = undefined
    let mongodbConfigured = false

    if (process.env.MONGODB_URI) {
      mongodbConfigured = true
      try {
        // Validate connection string format
        validateMongoDBURI(process.env.MONGODB_URI)

        // Try to connect (with timeout)
        const connectionPromise = connectDB()
        const timeoutPromise = new Promise((_, reject) =>
          setTimeout(() => reject(new Error('Connection timeout')), 5000)
        )

        await Promise.race([connectionPromise, timeoutPromise])
        mongodbStatus = 'ready'
      } catch (error: any) {
        mongodbStatus = 'error'

        mongodbError =
          error instanceof Error ? error.message : 'Connection failed'

      }
    }

    const services = {
      openai: {
        configured: !!process.env.OPENAI_API_KEY,
        status: process.env.OPENAI_API_KEY ? 'ready' : 'missing',
      },
      googleSheets: {
        configured: !!(
          process.env.GOOGLE_SERVICE_ACCOUNT_EMAIL &&
          process.env.GOOGLE_PRIVATE_KEY
        ),
        sheetId: process.env.GOOGLE_SHEET_ID || 'not configured',
        status:
          process.env.GOOGLE_SERVICE_ACCOUNT_EMAIL &&
          process.env.GOOGLE_PRIVATE_KEY
            ? 'ready'
            : 'missing',
      },
      mongodb: {
        configured: mongodbConfigured,
        status: mongodbStatus,
        ...(mongodbError && { error: mongodbError }),
        uriFormat: process.env.MONGODB_URI
          ? process.env.MONGODB_URI.startsWith('mongodb://') ||
            process.env.MONGODB_URI.startsWith('mongodb+srv://')
            ? 'valid'
            : 'invalid'
          : 'not configured',
      },
      whatsapp: {
        configured: !!(
          process.env.WHATSAPP_ACCESS_TOKEN &&
          process.env.WHATSAPP_PHONE_NUMBER_ID
        ),
        status:
          process.env.WHATSAPP_ACCESS_TOKEN &&
          process.env.WHATSAPP_PHONE_NUMBER_ID
            ? 'ready'
            : 'optional',
      },
    }

    const allCriticalServicesReady =
      services.openai.configured &&
      services.googleSheets.configured &&
      services.mongodb.configured


    return successResponse(
      {
        status: allCriticalServicesReady ? 'healthy' : 'partial',
        timestamp: new Date().toISOString(),
        environment: process.env.NODE_ENV || 'development',
        services,
        initialization: result,
        systemStatus: getSystemStatus(),
      },
      allCriticalServicesReady
        ? 'All critical services are configured and ready'
        : 'Some services need configuration'
    )
  } catch (error: unknown) {
    const errorMessage =
      error instanceof Error ? error.message : 'Unknown error'
    const errorStack = error instanceof Error ? error.stack : undefined
    return errorResponse(
      errorMessage,
      500,
      process.env.NODE_ENV === 'development' ? errorStack : undefined

    )
  }
}
