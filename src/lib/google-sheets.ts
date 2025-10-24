import { google } from 'googleapis'
import { secureConfig } from './secure-config'

export interface AdminRow {
  rowNumber: number
  arg: string
  estado: string
  fecha: string
  cliente: string
  origen: string
  telefono: string
  direccion: string
  consulta: string
}

export interface QuoteData {
  arg: string
  estado: string
  fecha: string
  cliente: string
  origen: string
  telefono: string
  direccion: string
  consulta: string
}

export class GoogleSheetsClient {
  private sheets: any
  private spreadsheetId: string
  
  constructor() {
    if (!secureConfig.isReady()) {
      throw new Error('SecureConfig not initialized. Call initializeSecureConfig() first.')
    }

    const config = secureConfig.getGoogleSheetsConfig()
    this.spreadsheetId = config.sheetId

    if (!this.spreadsheetId) {
      throw new Error('Google Sheet ID is not configured')
    }

    const auth = new google.auth.GoogleAuth({
      credentials: {
        client_email: config.serviceAccountEmail,
        private_key: config.privateKey?.replace(/\\n/g, '\n')
      },
      scopes: config.scopes
    })
    
    this.sheets = google.sheets({ version: 'v4', auth })
  }
  
  // Leer pestaña "Admin." completa
  async readAdminTab(): Promise<AdminRow[]> {
    try {
      const response = await this.sheets.spreadsheets.values.get({
        spreadsheetId: this.spreadsheetId,
        range: 'Admin.!A:H' // Columnas A-H
      })
      return this.parseAdminRows(response.data.values || [])
    } catch (error) {
      console.error('Error reading Admin tab:', error)
      throw new Error(`Failed to read Admin tab: ${error.message}`)
    }
  }
  
  // Leer pestaña "Enviados"
  async readEnviadosTab(): Promise<AdminRow[]> {
    try {
      const response = await this.sheets.spreadsheets.values.get({
        spreadsheetId: this.spreadsheetId,
        range: 'Enviados!A:H'
      })
      return this.parseAdminRows(response.data.values || [])
    } catch (error) {
      console.error('Error reading Enviados tab:', error)
      throw new Error(`Failed to read Enviados tab: ${error.message}`)
    }
  }
  
  // Leer pestaña "Confirmado"
  async readConfirmadoTab(): Promise<AdminRow[]> {
    try {
      const response = await this.sheets.spreadsheets.values.get({
        spreadsheetId: this.spreadsheetId,
        range: 'Confirmado!A:H'
      })
      return this.parseAdminRows(response.data.values || [])
    } catch (error) {
      console.error('Error reading Confirmado tab:', error)
      throw new Error(`Failed to read Confirmado tab: ${error.message}`)
    }
  }
  
  // Parsear filas del sheet
  private parseAdminRows(rows: any[][]): AdminRow[] {
    if (!rows || rows.length === 0) return []
    
    // Primera fila son headers, saltarla
    return rows.slice(1).map((row, index) => ({
      rowNumber: index + 2, // +2 porque Excel empieza en 1 y saltamos header
      arg: row[0] || '',
      estado: row[1] || '',
      fecha: row[2] || '',
      cliente: row[3] || '',
      origen: row[4] || '',
      telefono: row[5] || '',
      direccion: row[6] || '',
      consulta: row[7] || '',
    }))
  }
  
  // Agregar nueva cotización a "Admin."
  async addQuoteToAdmin(quoteData: QuoteData): Promise<void> {
    try {
      const values = [[
        quoteData.arg,
        quoteData.estado,
        quoteData.fecha,
        quoteData.cliente,
        quoteData.origen,
        quoteData.telefono,
        quoteData.direccion,
        quoteData.consulta
      ]]
      
      await this.sheets.spreadsheets.values.append({
        spreadsheetId: this.spreadsheetId,
        range: 'Admin.!A:H',
        valueInputOption: 'USER_ENTERED',
        resource: { values }
      })
    } catch (error) {
      console.error('Error adding quote to Admin:', error)
      throw new Error(`Failed to add quote to Admin: ${error.message}`)
    }
  }
  
  // Leer fila específica
  async readSpecificRow(sheetName: string, rowNumber: number): Promise<string[]> {
    try {
      const response = await this.sheets.spreadsheets.values.get({
        spreadsheetId: this.spreadsheetId,
        range: `${sheetName}!A${rowNumber}:H${rowNumber}`
      })
      return response.data.values?.[0] || []
    } catch (error) {
      console.error(`Error reading specific row ${rowNumber} from ${sheetName}:`, error)
      throw new Error(`Failed to read row ${rowNumber} from ${sheetName}: ${error.message}`)
    }
  }
  
  // Mover cotización de "Admin." a "Enviados"
  async moveToEnviados(rowNumber: number, additionalData?: any): Promise<void> {
    try {
      // 1. Leer la fila específica
      const row = await this.readSpecificRow('Admin.', rowNumber)
      
      // 2. Agregar a "Enviados"
      await this.sheets.spreadsheets.values.append({
        spreadsheetId: this.spreadsheetId,
        range: 'Enviados!A:H',
        valueInputOption: 'USER_ENTERED',
        resource: { values: [row] }
      })
      
      // 3. Cambiar estado en "Admin." en lugar de eliminar
      await this.updateCellValue('Admin.', rowNumber, 'B', 'Enviado')
    } catch (error) {
      console.error('Error moving to Enviados:', error)
      throw new Error(`Failed to move to Enviados: ${error.message}`)
    }
  }
  
  // Mover cotización de "Enviados" a "Confirmado"
  async moveToConfirmado(rowNumber: number): Promise<void> {
    try {
      // 1. Leer la fila específica de Enviados
      const row = await this.readSpecificRow('Enviados', rowNumber)
      
      // 2. Agregar a "Confirmado"
      await this.sheets.spreadsheets.values.append({
        spreadsheetId: this.spreadsheetId,
        range: 'Confirmado!A:H',
        valueInputOption: 'USER_ENTERED',
        resource: { values: [row] }
      })
      
      // 3. Cambiar estado en "Enviados"
      await this.updateCellValue('Enviados', rowNumber, 'B', 'Confirmado')
    } catch (error) {
      console.error('Error moving to Confirmado:', error)
      throw new Error(`Failed to move to Confirmado: ${error.message}`)
    }
  }
  
  // Actualizar valor de una celda específica
  async updateCellValue(sheetName: string, row: number, column: string, value: string): Promise<void> {
    try {
      await this.sheets.spreadsheets.values.update({
        spreadsheetId: this.spreadsheetId,
        range: `${sheetName}!${column}${row}`,
        valueInputOption: 'USER_ENTERED',
        resource: { values: [[value]] }
      })
    } catch (error) {
      console.error(`Error updating cell ${column}${row} in ${sheetName}:`, error)
      throw new Error(`Failed to update cell: ${error.message}`)
    }
  }
  
  // Buscar cotización por teléfono
  async findByPhone(phone: string): Promise<{
    pendientes: AdminRow[]
    enviados: AdminRow[]
    confirmados: AdminRow[]
  }> {
    try {
      const [adminRows, enviadosRows, confirmadosRows] = await Promise.all([
        this.readAdminTab(),
        this.readEnviadosTab(),
        this.readConfirmadoTab()
      ])
      
      return {
        pendientes: adminRows.filter(r => r.telefono.includes(phone)),
        enviados: enviadosRows.filter(r => r.telefono.includes(phone)),
        confirmados: confirmadosRows.filter(r => r.telefono.includes(phone))
      }
    } catch (error) {
      console.error('Error finding by phone:', error)
      throw new Error(`Failed to find by phone: ${error.message}`)
    }
  }
  
  // Obtener estadísticas generales
  async getStats(): Promise<{
    totalPendientes: number
    totalEnviados: number
    totalConfirmados: number
    totalGeneral: number
  }> {
    try {
      const [adminRows, enviadosRows, confirmadosRows] = await Promise.all([
        this.readAdminTab(),
        this.readEnviadosTab(),
        this.readConfirmadoTab()
      ])
      
      return {
        totalPendientes: adminRows.length,
        totalEnviados: enviadosRows.length,
        totalConfirmados: confirmadosRows.length,
        totalGeneral: adminRows.length + enviadosRows.length + confirmadosRows.length
      }
    } catch (error) {
      console.error('Error getting stats:', error)
      throw new Error(`Failed to get stats: ${error.message}`)
    }
  }
  
  // Generar código Arg automático
  generateArgCode(phone: string, origen: string = 'WA'): string {
    const prefix = phone.slice(-4)
    const date = new Date().getDate()
    const month = new Date().getMonth() + 1
    return `${origen}${month}${date}${prefix}`
  }
}
