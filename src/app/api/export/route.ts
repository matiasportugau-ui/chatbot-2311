export const dynamic = 'force-dynamic'

import { connectDB } from '@/lib/mongodb'
import { NextRequest, NextResponse } from 'next/server'

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
export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { type, format = 'JSON', filters = {} } = body

    if (!type) {
      return NextResponse.json(
        { success: false, error: 'Type parameter is required' },
        { status: 400 }
      )
    }

    const db = await connectDB()
    let data: any[] = []
    let filename = ''

    // Build filter query
    const query: any = {}
    if (filters.dateFrom || filters.dateTo) {
      query.timestamp = {}
      if (filters.dateFrom) {
        query.timestamp.$gte = new Date(filters.dateFrom)
      }
      if (filters.dateTo) {
        query.timestamp.$lte = new Date(filters.dateTo)
      }
    }
    if (filters.status) {
      query.estado = filters.status
    }
    if (filters.userPhone) {
      query.user_phone = filters.userPhone
    }

    // Fetch data based on type
    switch (type) {
      case 'conversations':
        const conversations = db.collection('conversations')
        data = await conversations.find(query).toArray()
        filename = `conversations_${
          new Date().toISOString().split('T')[0]
        }.${format.toLowerCase()}`
        break

      case 'quotes':
        const quotes = db.collection('quotes')
        data = await quotes.find(query).toArray()
        filename = `quotes_${
          new Date().toISOString().split('T')[0]
        }.${format.toLowerCase()}`
        break

      case 'analytics':
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

      default:
        return NextResponse.json(
          {
            success: false,
            error: 'Invalid type. Use: conversations, quotes, or analytics',
          },
          { status: 400 }
        )
    }

    // Format data based on requested format
    let exportData: string | Buffer
    let contentType: string

    switch (format.toUpperCase()) {
      case 'CSV':
        exportData = convertToCSV(data)
        contentType = 'text/csv'
        break

      case 'EXCEL':
        // For Excel, we'd need a library like xlsx
        // For now, return JSON and let client handle Excel conversion
        exportData = JSON.stringify(data, null, 2)
        contentType = 'application/json'
        filename = filename.replace('.excel', '.json')
        break

      case 'JSON':
      default:
        exportData = JSON.stringify(data, null, 2)
        contentType = 'application/json'
        break
    }

    // Return download URL or data
    // In a real implementation, you might want to:
    // 1. Save file to storage (S3, local filesystem)
    // 2. Return download URL
    // 3. Or stream the file directly

    return NextResponse.json({
      success: true,
      data: {
        filename,
        format: format.toUpperCase(),
        recordCount: data.length,
        downloadUrl: `/api/export/download/${filename}`, // Placeholder
        // For small files, we can return data directly
        ...(format.toUpperCase() === 'JSON' && {
          content: JSON.parse(exportData as string),
        }),
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

function convertToCSV(data: any[]): string {
  if (!data || data.length === 0) {
    return ''
  }

  // Helper function to escape and quote CSV value only when necessary
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
      return `"${stringValue.replaceAll('"', '""')}"`
    }

    return stringValue
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
