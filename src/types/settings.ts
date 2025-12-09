/**
 * Settings Type Definitions
 */

export interface AppSettings {
  [key: string]: unknown
}

export interface SettingsDocument {
  _id?: string
  key: string
  value: unknown
  updatedAt: Date
  updatedBy?: string
}

export interface UpdateSettingsRequest {
  settings: Record<string, unknown>
}

export interface SettingsResponse {
  success: boolean
  data?: AppSettings | SettingsDocument
  error?: string
}

