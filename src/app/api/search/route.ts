export const dynamic = 'force-dynamic';

import { NextRequest, NextResponse } from 'next/server'
import { connectDB } from '@/lib/mongodb'
import { requireAuth } from '@/lib/auth'
import { withRateLimit } from '@/lib/rate-limit'

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
      return NextResponse.json(
        { success: false, error: 'Query parameter is required' },
        { status: 400 }
      )
    }

    // Validate and limit limit parameter
    limit = Math.min(Math.max(parseInt(String(limit)) || 20, 1), 100)

    // Sanitize query for regex fallback
    const sanitizedQuery = sanitizeRegexQuery(query)

    const db = await connectDB()
    const results: any[] = []

    // Search conversations
    if (type === 'all' || type === 'conversations') {
      const conversations = db.collection('conversations')
      
      // Try MongoDB full-text search first (requires text index)
      let conversationResults: any[] = []
      try {
        conversationResults = await conversations
          .find({ $text: { $search: query } })
          .limit(limit)
          .toArray()
      } catch (textSearchError: any) {
        // Fallback to sanitized regex if text index doesn't exist
        if (textSearchError.message?.includes('text index') || 
            textSearchError.message?.includes('no text index')) {
          conversationResults = await conversations.find({
            $or: [
              { user_phone: { $regex: sanitizedQuery, $options: 'i' } },
              { 'messages.content': { $regex: sanitizedQuery, $options: 'i' } },
              { intent: { $regex: sanitizedQuery, $options: 'i' } }
            ]
          })
            .limit(limit)
            .toArray()
        } else {
          throw textSearchError
        }
      }

      results.push(...conversationResults.map(conv => ({
        type: 'conversation',
        id: conv._id?.toString(),
        title: `Conversation with ${conv.user_phone}`,
        description: conv.messages?.[0]?.content || 'No messages',
        relevance: 0.8,
        data: conv
      })))
    }

    // Search quotes
    if (type === 'all' || type === 'quotes') {
      const quotes = db.collection('quotes')
      
      // Try MongoDB full-text search first
      let quoteResults: any[] = []
      try {
        quoteResults = await quotes
          .find({ $text: { $search: query } })
          .limit(limit)
          .toArray()
      } catch (textSearchError: any) {
        // Fallback to sanitized regex if text index doesn't exist
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
            .limit(limit)
            .toArray()
        } else {
          throw textSearchError
        }
      }

      results.push(...quoteResults.map(quote => ({
        type: 'quote',
        id: quote._id?.toString(),
        title: `Quote for ${quote.cliente || 'Unknown'}`,
        description: quote.consulta || 'No description',
        relevance: 0.9,
        data: quote
      })))
    }

    // Search users (by phone)
    if (type === 'all' || type === 'users') {
      const conversations = db.collection('conversations')
      const userPhones = await conversations.distinct('user_phone', {
        user_phone: { $regex: query, $options: 'i' }
      })

      results.push(...userPhones.slice(0, limit).map(phone => ({
        type: 'user',
        id: phone,
        title: `User: ${phone}`,
        description: `Phone number: ${phone}`,
        relevance: 0.7,
        data: { phone }
      })))
    }

    // Search products
    if (type === 'all' || type === 'products') {
      const quotes = db.collection('quotes')
      const productResults = await quotes.aggregate([
        { $unwind: { path: '$items', preserveNullAndEmptyArrays: true } },
        {
          $match: {
            'items.product': { $regex: query, $options: 'i' }
          }
        },
        {
          $group: {
            _id: '$items.product',
            count: { $sum: 1 }
          }
        },
        { $limit: limit }
      ]).toArray()

      results.push(...productResults.map(product => ({
        type: 'product',
        id: product._id,
        title: product._id,
        description: `Found in ${product.count} quotes`,
        relevance: 0.8,
        data: product
      })))
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
        timestamp: new Date()
      })
    } catch (err) {
      // Ignore search history errors
      console.warn('Failed to store search history:', err)
    }

    return NextResponse.json({
      success: true,
      data: {
        query,
        type,
        results: limitedResults,
        count: limitedResults.length
      }
    })
  } catch (error: any) {
    console.error('Search API Error:', error)
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


