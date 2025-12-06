/**
 * Recovery Type Definitions
 */

export interface RecoveryResult {
  success: boolean
  message: string
  data?: unknown
}

export interface RecoveryReport {
  summary: {
    totalConversations: number
    totalQuotes: number
    totalSessions: number
  }
  collections: Array<{
    name: string
    count: number
    size: number
  }>
  backups: Array<{
    filename: string
    size: number
    date: string
  }>
}

export interface BackupData {
  timestamp: string
  collections: Record<string, unknown[]>
}
