export const dynamic = 'force-dynamic'

<<<<<<< Updated upstream
import { NextRequest, NextResponse } from 'next/server'
import { connectDB } from '@/lib/mongodb'
import { requireAuth } from '@/lib/auth'
import { withRateLimit } from '@/lib/rate-limit'
=======
import {
  errorResponse,
  successResponse,
  validationErrorResponse,
} from '@/lib/api-response'
import { requireAuth } from '@/lib/auth'
import { connectDB } from '@/lib/mongodb'
import { withRateLimit } from '@/lib/rate-limit'
import { NextRequest } from 'next/server'

/**
 * Type definitions for search results
 */
interface SearchResult {
  type: 'conversation' | 'quote' | 'user' | 'product'
  id: string
  title: string
  description: string
  relevance: number
  data: unknown
}

interface ConversationDocument {
  _id?: { toString(): string }
  user_phone?: string
  messages?: Array<{ content?: string }>
  intent?: string
  [key: string]: unknown
}

interface QuoteDocument {
  _id?: { toString(): string }
  cliente?: string
  telefono?: string
  consulta?: string
  direccion?: string
  items?: Array<{ product?: string }>
  [key: string]: unknown
}
>>>>>>> Stashed changes

/**
 * Sanitize regex query to prevent regex injection
 */
function sanitizeRegexQuery(query: string): string {
  return query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
}

/**
 * Search API Endpoint
 * POST /api/search
 *
 * Full-text search across conversations, quotes, users, and products
 * Requires authentication
 *
 * Request body:
 * - query: string (required)
 * - type: 'all' | 'conversations' | 'quotes' | 'users' | 'products' (default: 'all')
 * - limit: number (default: 20, max: 100)
 */
async function searchHandler(request: NextRequest) {
  try {
    const body = await request.json()
    let { query, type = 'all', limit = 20 } = body

    if (!query || typeof query !== 'string') {
      return validationErrorResponse(
        ['Query parameter is required'],
        'Missing required parameter'
      )
    }

    // Validate and limit limit parameter
    let parsedLimit = parseInt(String(limit), 10)
    if (Number.isNaN(parsedLimit) || parsedLimit <= 0) {
      parsedLimit = 20 // Use default if invalid
    }
    limit = Math.min(Math.max(parsedLimit, 1), 100)

    // Sanitize query for regex fallback
    const sanitizedQuery = sanitizeRegexQuery(query)

    const db = await connectDB()
    const results: any[] = []

    // Search conversations
    if (type === 'all' || type === 'conversations') {
<<<<<<< Updated upstream
      const conversations = db.collection('conversations')
      
=======
      const conversations = db.collection<ConversationDocument>('conversations')

>>>>>>> Stashed changes
      // Try MongoDB full-text search first (requires text index)
      let conversationResults: any[] = []
      try {
        conversationResults = await conversations
          .find({ $text: { $search: query } })
          .limit(limit)
          .toArray()
      } catch (textSearchError: any) {
        // Fallback to sanitized regex if text index doesn't exist
<<<<<<< Updated upstream
        if (textSearchError.message?.includes('text index') || 
            textSearchError.message?.includes('no text index')) {
          conversationResults = await conversations.find({
            $or: [
              { user_phone: { $regex: sanitizedQuery, $options: 'i' } },
              { 'messages.content': { $regex: sanitizedQuery, $options: 'i' } },
              { intent: { $regex: sanitizedQuery, $options: 'i' } }
            ]
          })
=======
        const errorMessage =
          textSearchError instanceof Error
            ? textSearchError.message
            : String(textSearchError)
        if (
          errorMessage.includes('text index') ||
          errorMessage.includes('no text index')
        ) {
          conversationResults = await conversations
            .find({
              $or: [
                { user_phone: { $regex: sanitizedQuery, $options: 'i' } },
                {
                  'messages.content': { $regex: sanitizedQuery, $options: 'i' },
                },
                { intent: { $regex: sanitizedQuery, $options: 'i' } },
              ],
            })
>>>>>>> Stashed changes
            .limit(limit)
            .toArray()
        } else {
          throw textSearchError
        }
      }

<<<<<<< Updated upstream
      results.push(...conversationResults.map(conv => ({
        type: 'conversation',
        id: conv._id?.toString(),
        title: `Conversation with ${conv.user_phone}`,
        description: conv.messages?.[0]?.content || 'No messages',
        relevance: 0.8,
        data: conv
      })))
=======
      results.push(
        ...conversationResults.map(conv => ({
          type: 'conversation' as const,
          id: conv._id?.toString() || '',
          title: `Conversation with ${conv.user_phone}`,
          description: conv.messages?.[0]?.content || 'No messages',
          relevance: 0.8,
          data: conv,
        }))
      )
>>>>>>> Stashed changes
    }

    // Search quotes
    if (type === 'all' || type === 'quotes') {
<<<<<<< Updated upstream
      const quotes = db.collection('quotes')
      
=======
      const quotes = db.collection<QuoteDocument>('quotes')

>>>>>>> Stashed changes
      // Try MongoDB full-text search first
      let quoteResults: any[] = []
      try {
        quoteResults = await quotes
          .find({ $text: { $search: query } })
          .limit(limit)
          .toArray()
      } catch (textSearchError: any) {
        // Fallback to sanitized regex if text index doesn't exist
<<<<<<< Updated upstream
        if (textSearchError.message?.includes('text index') || 
            textSearchError.message?.includes('no text index')) {
          quoteResults = await quotes.find({
            $or: [
              { cliente: { $regex: sanitizedQuery, $options: 'i' } },
              { telefono: { $regex: sanitizedQuery, $options: 'i' } },
              { consulta: { $regex: sanitizedQuery, $options: 'i' } },
              { direccion: { $regex: sanitizedQuery, $options: 'i' } }
            ]
          })
=======
        const errorMessage =
          textSearchError instanceof Error
            ? textSearchError.message
            : String(textSearchError)
        if (
          errorMessage.includes('text index') ||
          errorMessage.includes('no text index')
        ) {
          quoteResults = await quotes
            .find({
              $or: [
                { cliente: { $regex: sanitizedQuery, $options: 'i' } },
                { telefono: { $regex: sanitizedQuery, $options: 'i' } },
                { consulta: { $regex: sanitizedQuery, $options: 'i' } },
                { direccion: { $regex: sanitizedQuery, $options: 'i' } },
              ],
            })
>>>>>>> Stashed changes
            .limit(limit)
            .toArray()
        } else {
          throw textSearchError
        }
      }

<<<<<<< Updated upstream
      results.push(...quoteResults.map(quote => ({
        type: 'quote',
        id: quote._id?.toString(),
        title: `Quote for ${quote.cliente || 'Unknown'}`,
        description: quote.consulta || 'No description',
        relevance: 0.9,
        data: quote
      })))
=======
      results.push(
        ...quoteResults.map(quote => ({
          type: 'quote' as const,
          id: quote._id?.toString() || '',
          title: `Quote for ${quote.cliente || 'Unknown'}`,
          description: quote.consulta || 'No description',
          relevance: 0.9,
          data: quote,
        }))
      )
>>>>>>> Stashed changes
    }

    // Search users (by phone)
    if (type === 'all' || type === 'users') {
      const conversations = db.collection('conversations')
      const userPhones = await conversations.distinct('user_phone', {
        user_phone: { $regex: query, $options: 'i' },
      })

<<<<<<< Updated upstream
      results.push(...userPhones.slice(0, limit).map(phone => ({
        type: 'user',
        id: phone,
        title: `User: ${phone}`,
        description: `Phone number: ${phone}`,
        relevance: 0.7,
        data: { phone }
      })))
=======
      results.push(
        ...userPhones.slice(0, limit).map(phone => ({
          type: 'user' as const,
          id: String(phone),
          title: `User: ${phone}`,
          description: `Phone number: ${phone}`,
          relevance: 0.7,
          data: { phone },
        }))
      )
>>>>>>> Stashed changes
    }

    // Search products
    if (type === 'all' || type === 'products') {
      const quotes = db.collection('quotes')
      const productResults = await quotes
        .aggregate([
          { $unwind: { path: '$items', preserveNullAndEmptyArrays: true } },
          {
            $match: {
              'items.product': { $regex: query, $options: 'i' },
            },
          },
          {
            $group: {
              _id: '$items.product',
              count: { $sum: 1 },
            },
          },
          { $limit: limit },
        ])
        .toArray()

<<<<<<< Updated upstream
      results.push(...productResults.map(product => ({
        type: 'product',
        id: product._id,
        title: product._id,
        description: `Found in ${product.count} quotes`,
        relevance: 0.8,
        data: product
      })))
=======
      results.push(
        ...productResults.map(product => ({
          type: 'product' as const,
          id: String(product._id || ''),
          title: String(product._id || ''),
          description: `Found in ${product.count} quotes`,
          relevance: 0.8,
          data: product,
        }))
      )
>>>>>>> Stashed changes
    }

    // Sort by relevance and limit
    results.sort((a, b) => b.relevance - a.relevance)
    const limitedResults = results.slice(0, limit)

    // Store search history (optional)
    try {
      const searchHistory = db.collection('search_history')
      await searchHistory.insertOne({
        query,
        type,
        resultCount: limitedResults.length,
        timestamp: new Date(),
      })
    } catch (err) {
      // Ignore search history errors
      console.warn('Failed to store search history:', err)
    }

    return successResponse({
      query,
      type,
      results: limitedResults,
      count: limitedResults.length,
    })
  } catch (error: any) {
    console.error('Search API Error:', error)
<<<<<<< Updated upstream
    return NextResponse.json(
      {
        success: false,
        error: error.message || 'Internal server error',
        data: { query: '', type: 'all', results: [], count: 0 }
      },
      { status: 500 }
    )
  }
}


=======
    const errorMessage =
      error instanceof Error ? error.message : 'Internal server error'
    return errorResponse(errorMessage, 500)
  }
}

// Export with authentication and rate limiting
export const POST = withRateLimit(
  requireAuth(async (request: NextRequest) => searchHandler(request)),
  30, // 30 requests per 15 minutes
  15 * 60 * 1000
)
>>>>>>> Stashed changes
