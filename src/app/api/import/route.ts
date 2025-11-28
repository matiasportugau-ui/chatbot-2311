export const dynamic = 'force-dynamic'

import { connectDB } from '@/lib/mongodb'
import { NextRequest, NextResponse } from 'next/server'

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
export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData()
    const file = formData.get('file') as File
    const type = formData.get('type') as string
    const validateOnly = formData.get('validateOnly') === 'true'

    if (!file) {
      return NextResponse.json(
        { success: false, error: 'File is required' },
        { status: 400 }
      )
    }

    if (!type) {
      return NextResponse.json(
        { success: false, error: 'Type parameter is required' },
        { status: 400 }
      )
    }

    // Read file content
    const fileContent = await file.text()
    const fileName = file.name.toLowerCase()

    let data: any[]

    // Parse file based on extension
    if (fileName.endsWith('.json')) {
      data = JSON.parse(fileContent)
      if (!Array.isArray(data)) {
        data = [data]
      }
    } else if (fileName.endsWith('.csv')) {
      data = parseCSV(fileContent)
    } else {
      return NextResponse.json(
        { success: false, error: 'Unsupported file format. Use JSON or CSV' },
        { status: 400 }
      )
    }

    // Validate data structure
    const validationResult = validateData(data, type)
    if (!validationResult.valid) {
      return NextResponse.json(
        {
          success: false,
          error: 'Data validation failed',
          validationErrors: validationResult.errors,
        },
        { status: 400 }
      )
    }

    if (validateOnly) {
      return NextResponse.json({
        success: true,
        message: 'Data validation passed',
        recordCount: data.length,
        validated: true,
      })
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
            } catch (err: any) {
              failed++
              errors.push(`Record ${imported + failed}: ${err.message}`)
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
            } catch (err: any) {
              failed++
              errors.push(`Record ${imported + failed}: ${err.message}`)
            }
          }
          break

        case 'products':
          const products = db.collection('products')
          for (const record of data) {
            try {
              await products.insertOne(record)
              imported++
            } catch (err: any) {
              failed++
              errors.push(`Record ${imported + failed}: ${err.message}`)
            }
          }
          break

        default:
          return NextResponse.json(
            {
              success: false,
              error: 'Invalid type. Use: conversations, quotes, or products',
            },
            { status: 400 }
          )
      }
    } catch (err: any) {
      return NextResponse.json(
        {
          success: false,
          error: `Import failed: ${err.message}`,
          imported,
          failed,
          errors: errors.slice(0, 10), // Limit error messages
        },
        { status: 500 }
      )
    }

    return NextResponse.json({
      success: true,
      data: {
        imported,
        failed,
        total: data.length,
        errors: errors.slice(0, 10), // Return first 10 errors
      },
    })
  } catch (error: any) {
    console.error('Import API Error:', error)
    return NextResponse.json(
      {
        success: false,
        error: error.message || 'Internal server error',
      },
      { status: 500 }
    )
  }
}

function parseCSV(csvContent: string): any[] {
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
  const data: any[] = []

  // Parse rows
  for (let i = 1; i < lines.length; i++) {
    const values = parseCSVLine(lines[i]).map(v => v.replace(/^"|"$/g, ''))
    const record: any = {}
    headers.forEach((header, index) => {
      record[header] = values[index] || ''
    })
    data.push(record)
  }

  return data
}

function validateData(
  data: any[],
  type: string
): { valid: boolean; errors: string[] } {
  const errors: string[] = []

  if (!Array.isArray(data) || data.length === 0) {
    errors.push('Data must be a non-empty array')
    return { valid: false, errors }
  }

  // Type-specific validation
  switch (type) {
    case 'conversations':
      data.forEach((record, index) => {
        if (!record.user_phone) {
          errors.push(`Record ${index + 1}: Missing user_phone`)
        }
      })
      break

    case 'quotes':
      data.forEach((record, index) => {
        if (!record.cliente) {
          errors.push(`Record ${index + 1}: Missing cliente`)
        }
        if (!record.telefono) {
          errors.push(`Record ${index + 1}: Missing telefono`)
        }
      })
      break

    case 'products':
      data.forEach((record, index) => {
        if (!record.name && !record.product) {
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
