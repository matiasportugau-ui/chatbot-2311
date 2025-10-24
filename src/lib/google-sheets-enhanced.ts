/**
 * 📊 Cliente Google Sheets Mejorado para Sistema BMC
 * 
 * Integración completa con el "Administrador de Cotizaciones" de BMC
 * Sheet ID: bs467N7FbLSHI7LpNor3wqrPZC9snqPphft8cEPHHl0
 */

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

export interface EnviadosRow {
  rowNumber: number
  arg: string
  estado: string
  fecha: string
  cliente: string
  origen: string
  telefono: string
  direccion: string
  consulta: string
  precio?: string
  fechaEnvio?: string
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
  precio?: string
  fechaEnvio?: string
}

export class GoogleSheetsEnhancedClient {
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
  
  /**
   * 📋 Leer pestaña "Admin." completa
   */
  async readAdminTab(): Promise<AdminRow[]> {
    try {
      const response = await this.sheets.spreadsheets.values.get({
        spreadsheetId: this.spreadsheetId,
        range: 'Admin.!A:H', // Columnas A-H
      })
      
      return this.parseAdminRows(response.data.values || [])
    } catch (error) {
      console.error('Error reading Admin tab:', error)
      throw new Error(`Error reading Admin tab: ${error.message}`)
    }
  }
  
  /**
   * 📤 Leer pestaña "Enviados"
   */
  async readEnviadosTab(): Promise<EnviadosRow[]> {
    try {
      const response = await this.sheets.spreadsheets.values.get({
        spreadsheetId: this.spreadsheetId,
        range: 'Enviados!A:J', // Columnas A-J (incluye precio y fecha envío)
      })
      
      return this.parseEnviadosRows(response.data.values || [])
    } catch (error) {
      console.error('Error reading Enviados tab:', error)
      throw new Error(`Error reading Enviados tab: ${error.message}`)
    }
  }
  
  /**
   * ✅ Leer pestaña "Confirmado"
   */
  async readConfirmadoTab(): Promise<EnviadosRow[]> {
    try {
      const response = await this.sheets.spreadsheets.values.get({
        spreadsheetId: this.spreadsheetId,
        range: 'Confirmado!A:J',
      })
      
      return this.parseEnviadosRows(response.data.values || [])
    } catch (error) {
      console.error('Error reading Confirmado tab:', error)
      throw new Error(`Error reading Confirmado tab: ${error.message}`)
    }
  }
  
  /**
   * ➕ Agregar nueva cotización a "Admin."
   */
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
      
      console.log(`✅ Cotización agregada a Admin: ${quoteData.arg}`)
    } catch (error) {
      console.error('Error adding quote to Admin:', error)
      throw new Error(`Error adding quote to Admin: ${error.message}`)
    }
  }
  
  /**
   * 📤 Mover cotización de "Admin." a "Enviados"
   */
  async moveToEnviados(rowNumber: number, additionalData?: any): Promise<void> {
    try {
      // 1. Leer la fila específica de Admin
      const row = await this.readSpecificRow('Admin.', rowNumber)
      
      // 2. Preparar datos para Enviados
      const enviadosData = [
        row.arg,
        'Enviado',
        row.fecha,
        row.cliente,
        row.origen,
        row.telefono,
        row.direccion,
        row.consulta,
        additionalData?.precio || '',
        additionalData?.fechaEnvio || new Date().toLocaleDateString('es-UY')
      ]
      
      // 3. Agregar a "Enviados"
      await this.sheets.spreadsheets.values.append({
        spreadsheetId: this.spreadsheetId,
        range: 'Enviados!A:J',
        valueInputOption: 'USER_ENTERED',
        resource: { values: [enviadosData] }
      })
      
      // 4. Cambiar estado en "Admin." en lugar de eliminar
      await this.updateCellValue('Admin.', rowNumber, 'B', 'Enviado')
      
      console.log(`✅ Cotización movida a Enviados: ${row.arg}`)
    } catch (error) {
      console.error('Error moving to Enviados:', error)
      throw new Error(`Error moving to Enviados: ${error.message}`)
    }
  }
  
  /**
   * ✅ Mover cotización de "Enviados" a "Confirmado"
   */
  async moveToConfirmado(rowNumber: number, additionalData?: any): Promise<void> {
    try {
      // 1. Leer la fila específica de Enviados
      const row = await this.readSpecificRow('Enviados', rowNumber)
      
      // 2. Preparar datos para Confirmado
      const confirmadoData = [
        row.arg,
        'Confirmado',
        row.fecha,
        row.cliente,
        row.origen,
        row.telefono,
        row.direccion,
        row.consulta,
        row.precio || '',
        row.fechaEnvio || '',
        additionalData?.fechaConfirmacion || new Date().toLocaleDateString('es-UY')
      ]
      
      // 3. Agregar a "Confirmado"
      await this.sheets.spreadsheets.values.append({
        spreadsheetId: this.spreadsheetId,
        range: 'Confirmado!A:K',
        valueInputOption: 'USER_ENTERED',
        resource: { values: [confirmadoData] }
      })
      
      // 4. Cambiar estado en "Enviados"
      await this.updateCellValue('Enviados', rowNumber, 'B', 'Confirmado')
      
      console.log(`✅ Cotización movida a Confirmado: ${row.arg}`)
    } catch (error) {
      console.error('Error moving to Confirmado:', error)
      throw new Error(`Error moving to Confirmado: ${error.message}`)
    }
  }
  
  /**
   * 🔍 Buscar cotización por teléfono
   */
  async findByPhone(phone: string): Promise<{
    pendientes: AdminRow[]
    enviados: EnviadosRow[]
    confirmados: EnviadosRow[]
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
      throw new Error(`Error finding by phone: ${error.message}`)
    }
  }
  
  /**
   * 🔍 Buscar cotización por código Arg
   */
  async findByArg(arg: string): Promise<{
    admin?: AdminRow
    enviados?: EnviadosRow
    confirmados?: EnviadosRow
  }> {
    try {
      const [adminRows, enviadosRows, confirmadosRows] = await Promise.all([
        this.readAdminTab(),
        this.readEnviadosTab(),
        this.readConfirmadoTab()
      ])
      
      return {
        admin: adminRows.find(r => r.arg === arg),
        enviados: enviadosRows.find(r => r.arg === arg),
        confirmados: confirmadosRows.find(r => r.arg === arg)
      }
    } catch (error) {
      console.error('Error finding by arg:', error)
      throw new Error(`Error finding by arg: ${error.message}`)
    }
  }
  
  /**
   * 📊 Obtener estadísticas del sistema
   */
  async getStatistics(): Promise<{
    totalPendientes: number
    totalEnviados: number
    totalConfirmados: number
    totalCotizaciones: number
    cotizacionesPorOrigen: Record<string, number>
    cotizacionesPorEstado: Record<string, number>
  }> {
    try {
      const [adminRows, enviadosRows, confirmadosRows] = await Promise.all([
        this.readAdminTab(),
        this.readEnviadosTab(),
        this.readConfirmadoTab()
      ])
      
      const totalPendientes = adminRows.length
      const totalEnviados = enviadosRows.length
      const totalConfirmados = confirmadosRows.length
      const totalCotizaciones = totalPendientes + totalEnviados + totalConfirmados
      
      // Estadísticas por origen
      const cotizacionesPorOrigen: Record<string, number> = {}
      ;[...adminRows, ...enviadosRows, ...confirmadosRows].forEach(row => {
        cotizacionesPorOrigen[row.origen] = (cotizacionesPorOrigen[row.origen] || 0) + 1
      })
      
      // Estadísticas por estado
      const cotizacionesPorEstado: Record<string, number> = {}
      ;[...adminRows, ...enviadosRows, ...confirmadosRows].forEach(row => {
        cotizacionesPorEstado[row.estado] = (cotizacionesPorEstado[row.estado] || 0) + 1
      })
      
      return {
        totalPendientes,
        totalEnviados,
        totalConfirmados,
        totalCotizaciones,
        cotizacionesPorOrigen,
        cotizacionesPorEstado
      }
    } catch (error) {
      console.error('Error getting statistics:', error)
      throw new Error(`Error getting statistics: ${error.message}`)
    }
  }
  
  /**
   * 🔧 Actualizar valor de una celda específica
   */
  async updateCellValue(sheetName: string, row: number, column: string, value: string): Promise<void> {
    try {
      await this.sheets.spreadsheets.values.update({
        spreadsheetId: this.spreadsheetId,
        range: `${sheetName}!${column}${row}`,
        valueInputOption: 'USER_ENTERED',
        resource: { values: [[value]] }
      })
    } catch (error) {
      console.error('Error updating cell value:', error)
      throw new Error(`Error updating cell value: ${error.message}`)
    }
  }
  
  /**
   * 📖 Leer fila específica
   */
  private async readSpecificRow(sheetName: string, rowNumber: number): Promise<any> {
    try {
      const response = await this.sheets.spreadsheets.values.get({
        spreadsheetId: this.spreadsheetId,
        range: `${sheetName}!A${rowNumber}:J${rowNumber}`,
      })
      
      const row = response.data.values?.[0] || []
      
      if (sheetName === 'Admin.') {
        return {
          arg: row[0] || '',
          estado: row[1] || '',
          fecha: row[2] || '',
          cliente: row[3] || '',
          origen: row[4] || '',
          telefono: row[5] || '',
          direccion: row[6] || '',
          consulta: row[7] || ''
        }
      } else {
        return {
          arg: row[0] || '',
          estado: row[1] || '',
          fecha: row[2] || '',
          cliente: row[3] || '',
          origen: row[4] || '',
          telefono: row[5] || '',
          direccion: row[6] || '',
          consulta: row[7] || '',
          precio: row[8] || '',
          fechaEnvio: row[9] || ''
        }
      }
    } catch (error) {
      console.error('Error reading specific row:', error)
      throw new Error(`Error reading specific row: ${error.message}`)
    }
  }
  
  /**
   * 🔄 Parsear filas de Admin
   */
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
  
  /**
   * 🔄 Parsear filas de Enviados/Confirmado
   */
  private parseEnviadosRows(rows: any[][]): EnviadosRow[] {
    if (!rows || rows.length === 0) return []
    
    return rows.slice(1).map((row, index) => ({
      rowNumber: index + 2,
      arg: row[0] || '',
      estado: row[1] || '',
      fecha: row[2] || '',
      cliente: row[3] || '',
      origen: row[4] || '',
      telefono: row[5] || '',
      direccion: row[6] || '',
      consulta: row[7] || '',
      precio: row[8] || '',
      fechaEnvio: row[9] || ''
    }))
  }
  
  /**
   * 🆔 Generar código Arg único
   */
  generateArgCode(phone: string, origen: string = 'WA'): string {
    const prefix = phone.slice(-4)
    const date = new Date().getDate()
    const time = new Date().getHours()
    return `${origen}${date}${time}${prefix}`
  }
}
