export const dynamic = 'force-dynamic'

import { requireAuth } from '@/lib/auth'
import { connectDB } from '@/lib/mongodb'
import { withRateLimit } from '@/lib/rate-limit'
import type {
  ConversationRecord,
  ImportRecord,
  ProductRecord,
  QuoteRecord,
  ValidationResult,
} from '@/types/import-export'
import { NextRequest } from 'next/server'
import {
  successResponse,
  errorResponse,
  validationErrorResponse,
} from '@/lib/api-response'

/**
 * Import API Endpoint
 * POST /api/import
 *
 * Import data from CSV, JSON, or Excel files
 *
 * Request body (multipart/form-data):
 * - file: File (required)
 * - type: 'conversations' | 'quotes' | 'products' (required)
 * - validateOnly: boolean (default: false) - if true, only validate without importing
 */
async function importHandler(request: NextRequest) {
  try {
    const formData = await request.formData()
    const file = formData.get('file') as File
    const type = formData.get('type') as string
    const validateOnly = formData.get('validateOnly') === 'true'

    if (!file) {
      return validationErrorResponse(
        ['File is required'],
        'Missing required field'
      )
    }

    if (!type) {
      return validationErrorResponse(
        ['Type parameter is required'],
        'Missing required parameter'
      )
    }

    // Read file content
    const fileContent = await file.text()
    const fileName = file.name.toLowerCase()

    let data: ImportRecord[]

    // Parse file based on extension
    if (fileName.endsWith('.json')) {
      data = JSON.parse(fileContent)
      if (!Array.isArray(data)) {
        data = [data]
      }
    } else if (fileName.endsWith('.csv')) {
      data = parseCSV(fileContent)
    } else {
      return validationErrorResponse(
        ['Unsupported file format. Use JSON or CSV'],
        'Invalid file format'
      )
    }

    // Validate data structure
    const validationResult = validateData(data, type)
    if (!validationResult.valid) {
      return validationErrorResponse(
        validationResult.errors,
        'Data validation failed'
      )
    }

    if (validateOnly) {
      return successResponse(
        {
          recordCount: data.length,
          validated: true,
        },
        'Data validation passed'
      )
    }

    // Import data to MongoDB
    const db = await connectDB()
    let imported = 0
    let failed = 0
    const errors: string[] = []

    try {
      switch (type) {
        case 'conversations':
          const conversations = db.collection('conversations')
          for (const record of data) {
            try {
              // Add timestamp if missing
              if (!record.timestamp) {
                record.timestamp = new Date()
              }
              await conversations.insertOne(record)
              imported++
            } catch (err: unknown) {
              failed++
              const errorMessage =
                err instanceof Error ? err.message : 'Unknown error'
              errors.push(`Record ${imported + failed}: ${errorMessage}`)
            }
          }
          break

        case 'quotes':
          const quotes = db.collection('quotes')
          for (const record of data) {
            try {
              // Add timestamps if missing
              if (!record.timestamp) {
                record.timestamp = new Date()
              }
              if (!record.createdAt) {
                record.createdAt = new Date()
              }
              if (!record.updatedAt) {
                record.updatedAt = new Date()
              }
              await quotes.insertOne(record)
              imported++
            } catch (err: unknown) {
              failed++
              const errorMessage =
                err instanceof Error ? err.message : 'Unknown error'
              errors.push(`Record ${imported + failed}: ${errorMessage}`)
            }
          }
          break

        case 'products':
          const products = db.collection('products')
          for (const record of data) {
            try {
              await products.insertOne(record)
              imported++
            } catch (err: unknown) {
              failed++
              const errorMessage =
                err instanceof Error ? err.message : 'Unknown error'
              errors.push(`Record ${imported + failed}: ${errorMessage}`)
            }
          }
          break

        default:
          return validationErrorResponse(
            ['Invalid type. Use: conversations, quotes, or products'],
            'Invalid type parameter'
          )
      }
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error'
      return errorResponse(
        `Import failed: ${errorMessage}`,
        500
      )
    }

    return successResponse({
      imported,
      failed,
      total: data.length,
      errors: errors.slice(0, 10), // Return first 10 errors
    })
  } catch (error: unknown) {
    console.error('Import API Error:', error)
    const errorMessage =
      error instanceof Error ? error.message : 'Internal server error'
    return errorResponse(errorMessage, 500)
  }
}

function parseCSV(csvContent: string): ImportRecord[] {
  const lines = csvContent.split('\n').filter(line => line.trim())
  if (lines.length === 0) {
    return []
  }

  // Parse CSV line handling quoted fields with commas
  function parseCSVLine(line: string): string[] {
    const values: string[] = []
    let currentValue = ''
    let insideQuotes = false

    for (let i = 0; i < line.length; i++) {
      const char = line[i]
      const nextChar = line[i + 1]

      if (char === '"') {
        if (insideQuotes && nextChar === '"') {
          // Escaped quote
          currentValue += '"'
          i++ // Skip next quote
        } else {
          // Toggle quote state
          insideQuotes = !insideQuotes
        }
      } else if (char === ',' && !insideQuotes) {
        // End of field
        values.push(currentValue.trim())
        currentValue = ''
      } else {
        currentValue += char
      }
    }

    // Add last value
    values.push(currentValue.trim())
    return values
  }

  // Parse header
  const headers = parseCSVLine(lines[0]).map(h => h.replace(/^"|"$/g, ''))
  const data: ImportRecord[] = []

  // Parse rows
  for (let i = 1; i < lines.length; i++) {
    const values = parseCSVLine(lines[i]).map(v => v.replace(/^"|"$/g, ''))
    const record: ImportRecord = {}
    headers.forEach((header, index) => {
      record[header] = values[index] || ''
    })
    data.push(record)
  }

  return data
}

function validateData(data: ImportRecord[], type: string): ValidationResult {
  const errors: string[] = []

  if (!Array.isArray(data) || data.length === 0) {
    errors.push('Data must be a non-empty array')
    return { valid: false, errors }
  }

  // Type-specific validation
  switch (type) {
    case 'conversations':
      data.forEach((record, index) => {
        const convRecord = record as ConversationRecord
        if (!convRecord.user_phone) {
          errors.push(`Record ${index + 1}: Missing user_phone`)
        }
      })
      break

    case 'quotes':
      data.forEach((record, index) => {
        const quoteRecord = record as QuoteRecord
        if (!quoteRecord.cliente) {
          errors.push(`Record ${index + 1}: Missing cliente`)
        }
        if (!quoteRecord.telefono) {
          errors.push(`Record ${index + 1}: Missing telefono`)
        }
      })
      break

    case 'products':
      data.forEach((record, index) => {
        const productRecord = record as ProductRecord
        if (!productRecord.name && !productRecord.product) {
          errors.push(`Record ${index + 1}: Missing product name`)
        }
      })
      break
  }

  return {
    valid: errors.length === 0,
    errors,
  }
}

// Export with authentication and rate limiting
export const POST = withRateLimit(
  requireAuth(async (request: NextRequest) => importHandler(request)),
  10,
  15 * 60 * 1000
)
