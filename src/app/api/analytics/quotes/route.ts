export const dynamic = 'force-dynamic'

import { errorResponse, successResponse } from '@/lib/api-response'
import { connectDB } from '@/lib/mongodb'
import { NextRequest } from 'next/server'

/**
 * Analytics Quotes API Endpoint
 * GET /api/analytics/quotes
 *
 * Returns quote statistics including:
 * - Total quotes, monthly quotes, conversion rates
 * - Revenue metrics
 * - Top products
 * - Quotes by status
 * - Hourly distribution
 *
 * Query parameters:
 * - dateFrom: ISO date string (optional)
 * - dateTo: ISO date string (optional)
 */
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const dateFrom = searchParams.get('dateFrom')
    const dateTo = searchParams.get('dateTo')

    const db = await connectDB()
    const conversations = db.collection('conversations')
    const quotes = db.collection('quotes')

    // Build date filter
    const dateFilter: any = {}
    if (dateFrom || dateTo) {
      const timestampFilter: { $gte?: Date; $lte?: Date } = {}
      if (dateFrom) {
        timestampFilter.$gte = new Date(dateFrom)
      }
      if (dateTo) {
        timestampFilter.$lte = new Date(dateTo)
      }
      dateFilter.timestamp = timestampFilter
    }

    // Get total quotes
    const totalQuotes = await quotes.countDocuments(dateFilter)

    // Get quotes this month
    const now = new Date()
    const startOfMonth = new Date(now.getFullYear(), now.getMonth(), 1)
    const endOfMonth = new Date(
      now.getFullYear(),
      now.getMonth() + 1,
      0,
      23,
      59,
      59,
      999
    )

    // Merge month filter with user date filter
    const monthFilter: Record<string, unknown> = { ...dateFilter }
    const userTimestamp = dateFilter.timestamp as
      | { $gte?: Date; $lte?: Date }
      | undefined
    if (userTimestamp) {
      // Combine user date range with month range
      monthFilter.timestamp = {
        $gte:
          userTimestamp.$gte && userTimestamp.$gte > startOfMonth
            ? userTimestamp.$gte
            : startOfMonth,
        $lte:
          userTimestamp.$lte && userTimestamp.$lte < endOfMonth
            ? userTimestamp.$lte
            : endOfMonth,
      }
    } else {
      monthFilter.timestamp = {
        $gte: startOfMonth,
        $lte: endOfMonth,
      }
    }

    const quotesThisMonth = await quotes.countDocuments(monthFilter)

    // Get quotes last month
    const startOfLastMonth = new Date(now.getFullYear(), now.getMonth() - 1, 1)
    const endOfLastMonth = new Date(now.getFullYear(), now.getMonth(), 0)
    const quotesLastMonth = await quotes.countDocuments({
      timestamp: {
        $gte: startOfLastMonth,
        $lte: endOfLastMonth,
      },
    })

    // Calculate average quote value
    const quoteValues = await quotes
      .aggregate([
        { $match: dateFilter },
        {
          $group: {
            _id: null,
            avgValue: { $avg: '$total' },
            totalRevenue: { $sum: '$total' },
          },
        },
      ])
      .toArray()

    const averageQuoteValue = quoteValues[0]?.avgValue || 0
    const totalRevenue = quoteValues[0]?.totalRevenue || 0

    // Calculate revenue this month
    const revenueThisMonth = await quotes
      .aggregate([
        {
          $match: monthFilter,
        },
        {
          $group: {
            _id: null,
            total: { $sum: '$total' },
          },
        },
      ])
      .toArray()

    const revenueThisMonthValue = revenueThisMonth[0]?.total || 0

    // Calculate revenue last month
    const revenueLastMonth = await quotes
      .aggregate([
        {
          $match: {
            timestamp: {
              $gte: startOfLastMonth,
              $lte: endOfLastMonth,
            },
          },
        },
        {
          $group: {
            _id: null,
            total: { $sum: '$total' },
          },
        },
      ])
      .toArray()

    const revenueLastMonthValue = revenueLastMonth[0]?.total || 0
    const revenueGrowth =
      revenueLastMonthValue > 0
        ? (revenueThisMonthValue - revenueLastMonthValue) /
          revenueLastMonthValue
        : 0

    // Get top products
    const topProducts = await quotes
      .aggregate([
        { $match: dateFilter },
        { $unwind: { path: '$items', preserveNullAndEmptyArrays: true } },
        {
          $group: {
            _id: '$items.product',
            count: { $sum: 1 },
          },
        },
        { $sort: { count: -1 } },
        { $limit: 10 },
      ])
      .toArray()

    const totalProductQuotes = topProducts.reduce((sum, p) => sum + p.count, 0)
    const topProductsFormatted = topProducts.map(p => ({
      name: p._id || 'Unknown',
      count: p.count,
      percentage: totalProductQuotes > 0 ? p.count / totalProductQuotes : 0,
    }))

    // Get quotes by status
    const quotesByStatus = await quotes
      .aggregate([
        { $match: dateFilter },
        {
          $group: {
            _id: '$estado',
            count: { $sum: 1 },
          },
        },
      ])
      .toArray()

    const totalStatusQuotes = quotesByStatus.reduce(
      (sum, s) => sum + s.count,
      0
    )
    const quotesByStatusFormatted = quotesByStatus.map(s => ({
      status: s._id || 'Unknown',
      count: s.count,
      percentage: totalStatusQuotes > 0 ? s.count / totalStatusQuotes : 0,
    }))

    // Get quotes by hour
    const quotesByHour = await quotes
      .aggregate([
        { $match: dateFilter },
        {
          $group: {
            _id: { $hour: '$timestamp' },
            count: { $sum: 1 },
          },
        },
        { $sort: { _id: 1 } },
      ])
      .toArray()

    const quotesByTimeFormatted = Array.from({ length: 24 }, (_, i) => {
      const hourData = quotesByHour.find(h => h._id === i)
      return {
        hour: i,
        count: hourData?.count || 0,
      }
    })

    // Calculate conversion rate (quotes with estado 'Confirmado' / total quotes)
    const confirmedQuotes = await quotes.countDocuments({
      ...dateFilter,
      estado: 'Confirmado',
    })
    const conversionRate = totalQuotes > 0 ? confirmedQuotes / totalQuotes : 0

    // Calculate average response time from conversations
    const avgResponseTime = await conversations
      .aggregate([
        { $match: dateFilter },
        {
          $group: {
            _id: null,
            avgTime: {
              $avg: {
                $subtract: [
                  { $arrayElemAt: ['$messages.timestamp', -1] },
                  { $arrayElemAt: ['$messages.timestamp', 0] },
                ],
              },
            },
          },
        },
      ])
      .toArray()

    const averageResponseTimeMinutes = avgResponseTime[0]?.avgTime
      ? Math.round(avgResponseTime[0].avgTime / (1000 * 60))
      : 0

    return successResponse({
      totalQuotes,
      quotesThisMonth,
      quotesLastMonth,
      averageQuoteValue,
      conversionRate,
      averageResponseTime: averageResponseTimeMinutes,
      topProducts: topProductsFormatted,
      quotesByStatus: quotesByStatusFormatted,
      quotesByTime: quotesByTimeFormatted,
      revenue: {
        total: totalRevenue,
        thisMonth: revenueThisMonthValue,
        lastMonth: revenueLastMonthValue,
        growth: revenueGrowth,
      },
    })
  } catch (error: unknown) {
    console.error('Analytics Quotes API Error:', error)
    const errorMessage =
      error instanceof Error ? error.message : 'Internal server error'
    return errorResponse(errorMessage, 500)
  }
}
