/**
 * Notification Type Definitions
 */

export interface Notification {
  _id?: string
  userId: string
  type: string
  title: string
  message: string
  read: boolean
  timestamp: Date
  metadata?: Record<string, unknown>
}

export interface NotificationQuery {
  userId?: string
  type?: string
  read?: boolean
  timestamp?: {
    $gte?: Date
    $lte?: Date
  }
}

export interface CreateNotificationRequest {
  userId: string
  type: string
  title: string
  message: string
  metadata?: Record<string, unknown>
}

export interface NotificationResponse {
  success: boolean
  data?: Notification | Notification[]
  error?: string
  total?: number
  page?: number
  limit?: number
}

