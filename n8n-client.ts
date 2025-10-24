/**
 * Cliente TypeScript para integración con n8n
 * Sistema BMC de Cotización Inteligente
 */

export interface N8NWebhookPayload {
  action: 'procesar_mensaje' | 'procesar_fila_sheet' | 'obtener_insights' | 'analisis_conversiones'
  mensaje?: string
  telefono?: string
  sesion_id?: string
  fila?: {
    arg: string
    estado: string
    fecha: string
    cliente: string
    origen: string
    telefono: string
    direccion: string
    consulta: string
  }
}

export interface N8NResponse {
  success: boolean
  data?: any
  error?: string
  timestamp?: string
}

export interface ChatMessage {
  mensaje: string
  telefono?: string
  sesion_id?: string
  source?: 'whatsapp' | 'web' | 'api'
}

export interface WhatsAppMessage {
  from: string
  name: string
  text: string
  timestamp?: string
  messageId?: string
}

export interface SheetRow {
  arg: string
  estado: string
  fecha: string
  cliente: string
  origen: string
  telefono: string
  direccion: string
  consulta: string
}

export class N8NClient {
  private baseUrl: string
  private apiKey?: string

  constructor(baseUrl: string = 'http://localhost:5678', apiKey?: string) {
    this.baseUrl = baseUrl
    this.apiKey = apiKey
  }

  /**
   * Enviar mensaje al workflow de chat
   */
  async sendChatMessage(message: ChatMessage): Promise<N8NResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/webhook/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(this.apiKey && { 'Authorization': `Bearer ${this.apiKey}` })
        },
        body: JSON.stringify({
          action: 'procesar_mensaje',
          mensaje: message.mensaje,
          telefono: message.telefono,
          sesion_id: message.sesion_id,
          source: message.source || 'api'
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error('Error sending chat message to n8n:', error)
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      }
    }
  }

  /**
   * Procesar mensaje de WhatsApp
   */
  async processWhatsAppMessage(message: WhatsAppMessage): Promise<N8NResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/webhook/whatsapp`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(this.apiKey && { 'Authorization': `Bearer ${this.apiKey}` })
        },
        body: JSON.stringify({
          entry: [{
            changes: [{
              field: 'messages',
              value: {
                messages: [{
                  from: message.from,
                  text: { body: message.text },
                  id: message.messageId || `msg_${Date.now()}`,
                  timestamp: message.timestamp || Math.floor(Date.now() / 1000).toString()
                }],
                contacts: message.name ? [{
                  profile: { name: message.name }
                }] : []
              }
            }]
          }]
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error('Error processing WhatsApp message:', error)
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      }
    }
  }

  /**
   * Sincronizar fila de Google Sheets
   */
  async syncSheetRow(row: SheetRow): Promise<N8NResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/webhook/sheets-sync`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(this.apiKey && { 'Authorization': `Bearer ${this.apiKey}` })
        },
        body: JSON.stringify({
          action: 'procesar_fila_sheet',
          fila: row
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error('Error syncing sheet row:', error)
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      }
    }
  }

  /**
   * Obtener insights de la base de conocimiento
   */
  async getInsights(): Promise<N8NResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/webhook/analytics`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(this.apiKey && { 'Authorization': `Bearer ${this.apiKey}` })
        },
        body: JSON.stringify({
          action: 'obtener_insights'
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error('Error getting insights:', error)
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      }
    }
  }

  /**
   * Obtener análisis de conversiones
   */
  async getConversions(): Promise<N8NResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/webhook/analytics`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(this.apiKey && { 'Authorization': `Bearer ${this.apiKey}` })
        },
        body: JSON.stringify({
          action: 'analisis_conversiones'
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error('Error getting conversions:', error)
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      }
    }
  }

  /**
   * Verificar estado de n8n
   */
  async healthCheck(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/healthz`, {
        method: 'GET',
        headers: {
          ...(this.apiKey && { 'Authorization': `Bearer ${this.apiKey}` })
        }
      })

      return response.ok
    } catch (error) {
      console.error('n8n health check failed:', error)
      return false
    }
  }

  /**
   * Obtener workflows activos
   */
  async getActiveWorkflows(): Promise<any[]> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/workflows`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          ...(this.apiKey && { 'Authorization': `Bearer ${this.apiKey}` })
        }
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      return data.data || []
    } catch (error) {
      console.error('Error getting workflows:', error)
      return []
    }
  }

  /**
   * Activar/desactivar workflow
   */
  async toggleWorkflow(workflowId: string, active: boolean): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/workflows/${workflowId}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          ...(this.apiKey && { 'Authorization': `Bearer ${this.apiKey}` })
        },
        body: JSON.stringify({ active })
      })

      return response.ok
    } catch (error) {
      console.error('Error toggling workflow:', error)
      return false
    }
  }
}

// Instancia singleton para uso global
export const n8nClient = new N8NClient(
  process.env.N8N_BASE_URL || 'http://localhost:5678',
  process.env.N8N_API_KEY
)

// Funciones de utilidad para integración directa
export async function sendChatToN8N(message: string, phone?: string, sessionId?: string): Promise<N8NResponse> {
  return n8nClient.sendChatMessage({
    mensaje: message,
    telefono: phone,
    sesion_id: sessionId,
    source: 'api'
  })
}

export async function processWhatsAppViaN8N(from: string, text: string, name?: string): Promise<N8NResponse> {
  return n8nClient.processWhatsAppMessage({
    from,
    text,
    name,
    timestamp: Math.floor(Date.now() / 1000).toString(),
    messageId: `msg_${Date.now()}`
  })
}

export async function syncSheetRowViaN8N(row: SheetRow): Promise<N8NResponse> {
  return n8nClient.syncSheetRow(row)
}

export async function getInsightsViaN8N(): Promise<N8NResponse> {
  return n8nClient.getInsights()
}

export async function getConversionsViaN8N(): Promise<N8NResponse> {
  return n8nClient.getConversions()
}

// Exportar tipos para uso externo
export type { N8NWebhookPayload, N8NResponse, ChatMessage, WhatsAppMessage, SheetRow }
