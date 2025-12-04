export const dynamic = 'force-dynamic'

import { connectDB } from '@/lib/mongodb'
import { NextRequest, NextResponse } from 'next/server'
import * as XLSX from 'xlsx'
import { requireAuth } from '@/lib/auth'
import { withRateLimit } from '@/lib/rate-limit'

// Security constants
const MAX_RECORDS = 10000 // Maximum records to export
const MAX_EXCEL_SIZE_MB = 10 // Maximum Excel file size in MB
const EXCEL_TIMEOUT_MS = 30000 // 30 seconds timeout for Excel operations
const ALLOWED_TYPES = ['conversations', 'quotes', 'analytics'] as const
const ALLOWED_FORMATS = ['CSV', 'JSON', 'EXCEL'] as const

/**
 * Sanitize filename to prevent path traversal and injection attacks
 */
function sanitizeFilename(filename: string): string {
  // Remove path traversal attempts
  let sanitized = filename.replace(/\.\./g, '')
  // Remove special characters, keep only alphanumeric, dots, dashes, underscores
  sanitized = sanitized.replace(/[^a-zA-Z0-9._-]/g, '_')
  // Limit length
  sanitized = sanitized.substring(0, 255)
  // Ensure it doesn't start with a dot
  if (sanitized.startsWith('.')) {
    sanitized = 'export' + sanitized
  }
  return sanitized
}

/**
 * Validate export type
 */
function validateType(type: string): type is typeof ALLOWED_TYPES[number] {
  return ALLOWED_TYPES.includes(type as typeof ALLOWED_TYPES[number])
}

/**
 * Validate export format
 */
function validateFormat(format: string): format is typeof ALLOWED_FORMATS[number] {
  return ALLOWED_FORMATS.includes(format.toUpperCase() as typeof ALLOWED_FORMATS[number])
}

/**
 * Export API Endpoint
 * POST /api/export
 *
 * Export data to CSV, JSON, or Excel format
 *
 * Request body:
 * - type: 'conversations' | 'quotes' | 'analytics' (required)
 * - format: 'CSV' | 'JSON' | 'Excel' (default: 'JSON')
 * - filters: object (optional) - date range, status, etc.
 */
async function exportHandler(request: NextRequest) {
  try {
    const body = await request.json()
    const { type, format = 'JSON', filters = {} } = body

    // Validate required parameters
    if (!type) {
      return NextResponse.json(
        { success: false, error: 'Type parameter is required' },
        { status: 400 }
      )
    }

    // Validate type
    if (!validateType(type)) {
      return NextResponse.json(
        {
          success: false,
          error: `Invalid type. Allowed values: ${ALLOWED_TYPES.join(', ')}`,
        },
        { status: 400 }
      )
    }

    // Validate format
    if (!validateFormat(format)) {
      return NextResponse.json(
        {
          success: false,
          error: `Invalid format. Allowed values: ${ALLOWED_FORMATS.join(', ')}`,
        },
        { status: 400 }
      )
    }

    // Validate filters object structure
    if (filters && typeof filters !== 'object') {
      return NextResponse.json(
        { success: false, error: 'Filters must be an object' },
        { status: 400 }
      )
    }

    const db = await connectDB()
    let data: any[] = []
    let filename = ''

    // Build filter query with validation
    const query: any = {}

    // Validate and sanitize date filters
    if (filters.dateFrom || filters.dateTo) {
      query.timestamp = {}
      if (filters.dateFrom) {
        const dateFrom = new Date(filters.dateFrom)
        if (isNaN(dateFrom.getTime())) {
          return NextResponse.json(
            { success: false, error: 'Invalid dateFrom format' },
            { status: 400 }
          )
        }
        query.timestamp.$gte = dateFrom
      }
      if (filters.dateTo) {
        const dateTo = new Date(filters.dateTo)
        if (isNaN(dateTo.getTime())) {
          return NextResponse.json(
            { success: false, error: 'Invalid dateTo format' },
            { status: 400 }
          )
        }
        query.timestamp.$lte = dateTo
      }
    }

    // Validate and sanitize status filter
    if (filters.status) {
      if (typeof filters.status !== 'string') {
        return NextResponse.json(
          { success: false, error: 'Status must be a string' },
          { status: 400 }
        )
      }
      // Sanitize status - only allow alphanumeric and common status values
      const statusPattern = /^[a-zA-Z0-9_-]+$/
      if (!statusPattern.test(filters.status)) {
        return NextResponse.json(
          { success: false, error: 'Invalid status format' },
          { status: 400 }
        )
      }
      query.estado = filters.status
    }

    // Validate and sanitize userPhone filter
    if (filters.userPhone) {
      if (typeof filters.userPhone !== 'string') {
        return NextResponse.json(
          { success: false, error: 'User phone must be a string' },
          { status: 400 }
        )
      }
      // Sanitize phone - only allow digits, +, -, spaces
      const phonePattern = /^[0-9+\-\s()]+$/
      if (!phonePattern.test(filters.userPhone)) {
        return NextResponse.json(
          { success: false, error: 'Invalid phone format' },
          { status: 400 }
        )
      }
      query.user_phone = filters.userPhone
    }

    // Fetch data based on type with record limit
    switch (type) {
      case 'conversations': {
        const conversations = db.collection('conversations')
        // Apply limit to prevent excessive data export
        data = await conversations.find(query).limit(MAX_RECORDS).toArray()
        filename = `conversations_${
          new Date().toISOString().split('T')[0]
        }.${format.toLowerCase()}`
        break
      }

      case 'quotes': {
        const quotes = db.collection('quotes')
        // Apply limit to prevent excessive data export
        data = await quotes.find(query).limit(MAX_RECORDS).toArray()
        filename = `quotes_${
          new Date().toISOString().split('T')[0]
        }.${format.toLowerCase()}`
        break
      }

      case 'analytics': {
        // Export analytics summary
        const analyticsQuotes = db.collection('quotes')
        const analyticsConversations = db.collection('conversations')

        const totalQuotes = await analyticsQuotes.countDocuments(query)
        const totalConversations = await analyticsConversations.countDocuments(
          query
        )

        data = [
          {
            totalQuotes,
            totalConversations,
            exportDate: new Date().toISOString(),
            filters,
          },
        ]
        filename = `analytics_${
          new Date().toISOString().split('T')[0]
        }.${format.toLowerCase()}`
        break
      }
    }

    // Check if data limit was reached
    if (data.length >= MAX_RECORDS && type !== 'analytics') {
      console.warn(
        `Export limit reached: ${data.length} records (max: ${MAX_RECORDS})`
      )
    }

    // Sanitize filename
    filename = sanitizeFilename(filename)

    // Format data based on requested format
    let exportData: string | Buffer
    let contentType: string

    switch (format.toUpperCase()) {
      case 'CSV': {
        exportData = convertToCSV(data)
        contentType = 'text/csv'
        break
      }

      case 'EXCEL': {
        // Generate Excel file using xlsx library with timeout protection
        try {
          // Create a promise with timeout
          const excelPromise = new Promise<Buffer>((resolve, reject) => {
            try {
              const worksheet = XLSX.utils.json_to_sheet(data)
              const workbook = XLSX.utils.book_new()
              XLSX.utils.book_append_sheet(workbook, worksheet, 'Data')
              const excelBuffer = XLSX.write(workbook, {
                type: 'buffer',
                bookType: 'xlsx',
              })
              resolve(excelBuffer as Buffer)
            } catch (error) {
              reject(error)
            }
          })

          // Add timeout protection
          const timeoutPromise = new Promise<never>((_, reject) => {
            setTimeout(() => {
              reject(new Error('Excel generation timeout'))
            }, EXCEL_TIMEOUT_MS)
          })

          const excelBuffer = await Promise.race([
            excelPromise,
            timeoutPromise,
          ])

          // Check file size
          const fileSizeMB = excelBuffer.length / (1024 * 1024)
          if (fileSizeMB > MAX_EXCEL_SIZE_MB) {
            throw new Error(
              `Excel file too large: ${fileSizeMB.toFixed(2)}MB (max: ${MAX_EXCEL_SIZE_MB}MB)`
            )
          }

          exportData = excelBuffer
          contentType =
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
          filename = filename.replace(/\.(json|excel)$/i, '.xlsx')
        } catch (excelError: any) {
          console.error('Excel export error:', excelError)

          // If timeout or size limit, return error instead of fallback
          if (
            excelError.message?.includes('timeout') ||
            excelError.message?.includes('too large')
          ) {
            return NextResponse.json(
              {
                success: false,
                error: excelError.message || 'Excel generation failed',
                suggestion:
                  'Try reducing the date range or number of records, or export as JSON/CSV',
              },
              { status: 413 } // Payload Too Large
            )
          }

          // For other errors, fallback to JSON
          exportData = JSON.stringify(data, null, 2)
          contentType = 'application/json'
          filename = filename.replace(/\.(excel|xlsx)$/i, '.json')
        }
        break
      }

      case 'JSON':
      default: {
        exportData = JSON.stringify(data, null, 2)
        contentType = 'application/json'
        break
      }
    }

    // For Excel and CSV, return file directly as download
    if (format.toUpperCase() === 'EXCEL' || format.toUpperCase() === 'CSV') {
      // Additional security: Sanitize filename in Content-Disposition header
      const safeFilename = sanitizeFilename(filename)

      // NextResponse accepts BodyInit which includes string and Buffer
      // When exportData is already a Buffer (from Excel), pass it directly - no need for Buffer.from()
      // When exportData is a string (from CSV), pass it directly
      // Type assertion needed because TypeScript doesn't recognize Buffer as BodyInit in Next.js types
      return new NextResponse(exportData as BodyInit, {
        status: 200,
        headers: {
          'Content-Type': contentType,
          'Content-Disposition': `attachment; filename="${safeFilename}"; filename*=UTF-8''${encodeURIComponent(safeFilename)}`,
          'X-Export-Records': data.length.toString(),
          'X-Export-Max-Records': MAX_RECORDS.toString(),
        },
      })
    }

    // For JSON, return JSON response with data
    return NextResponse.json({
      success: true,
      data: {
        filename,
        format: format.toUpperCase(),
        recordCount: data.length,
        content: JSON.parse(exportData as string),
      },
    })
  } catch (error: any) {
    console.error('Export API Error:', error)
    return NextResponse.json(
      {
        success: false,
        error: error.message || 'Internal server error',
      },
      { status: 500 }
    )
  }
}

function escapeCSVValue(value: any): string {
  if (value === null || value === undefined) {
    return ''
  }

  let stringValue: string
  if (typeof value === 'object') {
    stringValue = JSON.stringify(value)
  } else {
    stringValue = String(value)
  }

  // Only quote if value contains comma, newline, or quote
  if (
    stringValue.includes(',') ||
    stringValue.includes('\n') ||
    stringValue.includes('"')
  ) {
    // Escape quotes by doubling them and wrap in quotes
    return `"${stringValue.replace(/"/g, '""')}"`
  }

  return stringValue
}

function convertToCSV(data: any[]): string {
  if (!data || data.length === 0) {
    return ''
  }

  // Get headers from first object
  const headers = Object.keys(data[0])
  const csvRows = [headers.map(escapeCSVValue).join(',')]

  // Convert each object to CSV row
  for (const row of data) {
    const values = headers.map(header => escapeCSVValue(row[header]))
    csvRows.push(values.join(','))
  }

  return csvRows.join('\n')
}

// Export with authentication and rate limiting
export const POST = withRateLimit(requireAuth(async (request: NextRequest) => exportHandler(request)), 20, 15 * 60 * 1000)
