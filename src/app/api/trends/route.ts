export const dynamic = 'force-dynamic'

import { connectDB } from '@/lib/mongodb'
import { NextRequest, NextResponse } from 'next/server'

/**
 * Trends API Endpoint
 * GET /api/trends
 *
 * Analyzes conversation and quote trends
 *
 * Query parameters:
 * - type: 'quotes' | 'revenue' | 'users' (default: 'quotes')
 * - period: 'day' | 'week' | 'month' (default: 'month')
 */
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const type = searchParams.get('type') || 'quotes'
    const period = searchParams.get('period') || 'month'

    const db = await connectDB()
    const conversations = db.collection('conversations')
    const quotes = db.collection('quotes')

    const now = new Date()
    let startDate: Date
    let previousStartDate: Date
    let previousEndDate: Date

    // Calculate date ranges based on period
    switch (period) {
      case 'day':
        startDate = new Date(now.getFullYear(), now.getMonth(), now.getDate())
        previousStartDate = new Date(startDate)
        previousStartDate.setDate(previousStartDate.getDate() - 1)
        previousEndDate = new Date(startDate)
        break
      case 'week':
        const dayOfWeek = now.getDay()
        startDate = new Date(now)
        startDate.setDate(now.getDate() - dayOfWeek)
        startDate.setHours(0, 0, 0, 0)
        previousStartDate = new Date(startDate)
        previousStartDate.setDate(previousStartDate.getDate() - 7)
        previousEndDate = new Date(startDate)
        break
      case 'month':
      default:
        startDate = new Date(now.getFullYear(), now.getMonth(), 1)
        previousStartDate = new Date(now.getFullYear(), now.getMonth() - 1, 1)
        previousEndDate = new Date(now.getFullYear(), now.getMonth(), 0)
        break
    }

    let currentValue: number
    let previousValue: number
    let data: Array<{
      period: string
      value: number
      change: number
      changePercentage: number
    }>
    let insights: string[]
    let recommendations: string[]

    switch (type) {
      case 'quotes':
        currentValue = await quotes.countDocuments({
          timestamp: { $gte: startDate },
        })
        previousValue = await quotes.countDocuments({
          timestamp: {
            $gte: previousStartDate,
            $lt: previousEndDate,
          },
        })

        // Get daily/weekly/monthly breakdown
        const quoteBreakdown = await quotes
          .aggregate([
            {
              $match: {
                timestamp: { $gte: startDate },
              },
            },
            {
              $group: {
                _id:
                  period === 'day'
                    ? { $dateToString: { format: '%H:00', date: '$timestamp' } }
                    : period === 'week'
                    ? {
                        $dateToString: {
                          format: '%Y-%m-%d',
                          date: '$timestamp',
                        },
                      }
                    : {
                        $dateToString: {
                          format: '%Y-%m-%d',
                          date: '$timestamp',
                        },
                      },
                count: { $sum: 1 },
              },
            },
            { $sort: { _id: 1 } },
          ])
          .toArray()

        data = quoteBreakdown.map((item, index) => {
          const prevItem = index > 0 ? quoteBreakdown[index - 1] : null
          const change = prevItem ? item.count - prevItem.count : 0
          const changePercentage =
            prevItem && prevItem.count > 0 ? (change / prevItem.count) * 100 : 0

          return {
            period: item._id,
            value: item.count,
            change,
            changePercentage,
          }
        })

        insights = [
          currentValue > previousValue
            ? `Quote volume increased by ${(
                ((currentValue - previousValue) / previousValue) *
                100
              ).toFixed(1)}% compared to previous period`
            : `Quote volume decreased by ${(
                ((previousValue - currentValue) / previousValue) *
                100
              ).toFixed(1)}% compared to previous period`,
          `Average ${(
            currentValue / (period === 'day' ? 1 : period === 'week' ? 7 : 30)
          ).toFixed(1)} quotes per ${period === 'day' ? 'hour' : 'day'}`,
        ]

        recommendations = [
          currentValue > previousValue
            ? 'Consider scaling resources to handle increased demand'
            : 'Review marketing strategies to increase quote generation',
          'Analyze peak hours to optimize response times',
        ]
        break

      case 'revenue':
        const currentRevenue = await quotes
          .aggregate([
            {
              $match: {
                timestamp: { $gte: startDate },
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

        const previousRevenue = await quotes
          .aggregate([
            {
              $match: {
                timestamp: {
                  $gte: previousStartDate,
                  $lt: previousEndDate,
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

        currentValue = currentRevenue[0]?.total || 0
        previousValue = previousRevenue[0]?.total || 0

        const revenueBreakdown = await quotes
          .aggregate([
            {
              $match: {
                timestamp: { $gte: startDate },
              },
            },
            {
              $group: {
                _id:
                  period === 'day'
                    ? { $dateToString: { format: '%H:00', date: '$timestamp' } }
                    : {
                        $dateToString: {
                          format: '%Y-%m-%d',
                          date: '$timestamp',
                        },
                      },
                total: { $sum: '$total' },
              },
            },
            { $sort: { _id: 1 } },
          ])
          .toArray()

        data = revenueBreakdown.map((item, index) => {
          const prevItem = index > 0 ? revenueBreakdown[index - 1] : null
          const change = prevItem ? item.total - prevItem.total : 0
          const changePercentage =
            prevItem && prevItem.total > 0 ? (change / prevItem.total) * 100 : 0

          return {
            period: item._id,
            value: item.total,
            change,
            changePercentage,
          }
        })

        // Calculate average revenue per quote before constructing insights
        const quotesCount = await quotes.countDocuments({
          timestamp: { $gte: startDate },
        })
        const averageRevenuePerQuote =
          quotesCount > 0
            ? (currentValue / quotesCount).toFixed(2)
            : '0'

        insights = [
          currentValue > previousValue
            ? `Revenue increased by ${(
                ((currentValue - previousValue) / previousValue) *
                100
              ).toFixed(1)}%`
            : `Revenue decreased by ${(
                ((previousValue - currentValue) / previousValue) *
                100
              ).toFixed(1)}%`,
          `Average revenue per quote: ${averageRevenuePerQuote}`,
        ]

        recommendations = [
          'Focus on high-value quote conversions',
          'Analyze revenue patterns to optimize pricing strategies',
        ]
        break

      case 'users':
      default:
        currentValue = await conversations
          .distinct('user_phone', {
            timestamp: { $gte: startDate },
          })
          .then(phones => phones.length)

        previousValue = await conversations
          .distinct('user_phone', {
            timestamp: {
              $gte: previousStartDate,
              $lt: previousEndDate,
            },
          })
          .then(phones => phones.length)

        const userBreakdown = await conversations
          .aggregate([
            {
              $match: {
                timestamp: { $gte: startDate },
              },
            },
            {
              $group: {
                _id:
                  period === 'day'
                    ? { $dateToString: { format: '%H:00', date: '$timestamp' } }
                    : {
                        $dateToString: {
                          format: '%Y-%m-%d',
                          date: '$timestamp',
                        },
                      },
                uniqueUsers: { $addToSet: '$user_phone' },
              },
            },
            {
              $project: {
                _id: 1,
                count: { $size: '$uniqueUsers' },
              },
            },
            { $sort: { _id: 1 } },
          ])
          .toArray()

        data = userBreakdown.map((item, index) => {
          const prevItem = index > 0 ? userBreakdown[index - 1] : null
          const change = prevItem ? item.count - prevItem.count : 0
          const changePercentage =
            prevItem && prevItem.count > 0 ? (change / prevItem.count) * 100 : 0

          return {
            period: item._id,
            value: item.count,
            change,
            changePercentage,
          }
        })

        insights = [
          currentValue > previousValue
            ? `Active users increased by ${(
                ((currentValue - previousValue) / previousValue) *
                100
              ).toFixed(1)}%`
            : `Active users decreased by ${(
                ((previousValue - currentValue) / previousValue) *
                100
              ).toFixed(1)}%`,
          `User engagement is ${currentValue > 0 ? 'increasing' : 'stable'}`,
        ]

        recommendations = [
          'Improve user retention strategies',
          'Analyze user behavior patterns',
        ]
        break
    }

    const change = currentValue - previousValue
    const changePercentage =
      previousValue > 0
        ? (change / previousValue) * 100
        : currentValue > 0
        ? 100
        : 0

    const trend: 'up' | 'down' | 'stable' =
      changePercentage > 5 ? 'up' : changePercentage < -5 ? 'down' : 'stable'

    const confidence = Math.min(
      100,
      Math.max(0, 100 - Math.abs(changePercentage) / 2)
    )

    return NextResponse.json({
      success: true,
      data: [
        {
          metric: type,
          description: `${
            type.charAt(0).toUpperCase() + type.slice(1)
          } trends for ${period}`,
          currentValue,
          previousValue,
          change,
          changePercentage,
          trend,
          confidence,
          data,
          insights,
          recommendations,
        },
      ],
    })
  } catch (error: any) {
    console.error('Trends API Error:', error)
    return NextResponse.json(
      {
        success: false,
        error: error.message || 'Internal server error',
        data: [],
      },
      { status: 500 }
    )
  }
}
