/**
 * Import/Export Type Definitions
 */

export type ImportType = 'conversations' | 'quotes' | 'products'
export type ExportType = 'conversations' | 'quotes' | 'analytics'
export type ExportFormat = 'CSV' | 'JSON' | 'Excel'

export interface ImportRecord {
  [key: string]: unknown
  timestamp?: Date
  createdAt?: Date
  updatedAt?: Date
}

export interface ConversationRecord extends ImportRecord {
  user_phone: string
  [key: string]: unknown
}

export interface QuoteRecord extends ImportRecord {
  cliente: string
  telefono: string
  [key: string]: unknown
}

export interface ProductRecord extends ImportRecord {
  name?: string
  product?: string
  [key: string]: unknown
}

export interface ExportFilters {
  dateFrom?: string
  dateTo?: string
  status?: string
  userPhone?: string
}

export interface ImportRequest {
  file: File
  type: ImportType
  validateOnly?: boolean
}

export interface ExportRequest {
  type: ExportType
  format?: ExportFormat
  filters?: ExportFilters
}

export interface ImportResponse {
  success: boolean
  data?: {
    imported: number
    failed: number
    total: number
    errors: string[]
  }
  message?: string
  recordCount?: number
  validated?: boolean
  error?: string
  validationErrors?: string[]
}

export interface ExportResponse {
  success: boolean
  data?: {
    filename: string
    format: string
    recordCount: number
    content: unknown[]
  }
  error?: string
}

export interface ValidationResult {
  valid: boolean
  errors: string[]
}
