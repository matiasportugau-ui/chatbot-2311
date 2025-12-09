/**
 * Analytics Type Definitions
 */

export interface QuoteAnalytics {
  total: number
  byStatus: Record<string, number>
  byDate: Array<{
    date: string
    count: number
  }>
  averageValue: number
  topProducts: Array<{
    product: string
    count: number
  }>
}

export interface TrendData {
  period: string
  value: number
  change?: number
}

export interface AnalyticsResponse {
  success: boolean
  data?: QuoteAnalytics | TrendData[]
  error?: string
}
