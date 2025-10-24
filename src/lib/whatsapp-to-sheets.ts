import { GoogleSheetsClient, QuoteData } from './google-sheets'
import { parseQuoteConsulta, isValidQuoteRequest, extractContactInfo } from './quote-parser'

export interface WhatsAppMessage {
  from: string
  name: string
  text: string
  timestamp?: string
  messageId?: string
}

export interface ProcessedQuote {
  quoteData: QuoteData
  parsed: any
  contactInfo: any
  isValid: boolean
  messageId: string
}

export async function processWhatsAppQuote(message: WhatsAppMessage): Promise<ProcessedQuote> {
  const sheetsClient = new GoogleSheetsClient()
  
  // 1. Validar si es una consulta válida
  const isValid = isValidQuoteRequest(message.text)
  
  if (!isValid) {
    throw new Error('El mensaje no parece ser una consulta de cotización válida')
  }
  
  // 2. Extraer información de contacto
  const contactInfo = extractContactInfo(message.text)
  
  // 3. Parsear consulta con IA
  const parsed = await parseQuoteConsulta(message.text)
  
  // 4. Generar código Arg automático
  const arg = generateArgCode(message.from, 'WA')
  
  // 5. Preparar datos para Sheet
  const quoteData: QuoteData = {
    arg: arg,
    estado: 'Pendiente',
    fecha: new Date().toLocaleDateString('es-UY', { 
      day: '2-digit', 
      month: '2-digit' 
    }),
    cliente: message.name || contactInfo.name || 'Cliente WhatsApp',
    origen: 'WA',
    telefono: message.from,
    direccion: parsed.dimensiones?.largo ? 'A confirmar' : 'A confirmar',
    consulta: message.text
  }
  
  // 6. Agregar a Google Sheets
  await sheetsClient.addQuoteToAdmin(quoteData)
  
  // 7. Retornar datos procesados
  return {
    quoteData,
    parsed,
    contactInfo,
    isValid,
    messageId: message.messageId || generateMessageId()
  }
}

// Procesar mensaje de WhatsApp y responder automáticamente
export async function processAndRespondToWhatsApp(message: WhatsAppMessage): Promise<{
  success: boolean
  response?: string
  error?: string
  quoteData?: QuoteData
}> {
  try {
    // Procesar la cotización
    const processed = await processWhatsAppQuote(message)
    
    // Generar respuesta automática
    const response = generateAutoResponse(processed)
    
    return {
      success: true,
      response,
      quoteData: processed.quoteData
    }
  } catch (error) {
    console.error('Error processing WhatsApp quote:', error)
    
    // Respuesta de error amigable
    const errorResponse = `Hola ${message.name || 'cliente'}! 

Gracias por tu mensaje. He recibido tu consulta pero necesito más información para poder cotizarte correctamente.

Por favor, incluye en tu mensaje:
• Tipo de producto (Isodec, Isoroof, Chapas, etc.)
• Dimensiones aproximadas
• Si necesitas instalación y flete

¡Estaré aquí para ayudarte! 🏗️`

    return {
      success: false,
      error: error.message,
      response: errorResponse
    }
  }
}

// Generar respuesta automática basada en la cotización procesada
function generateAutoResponse(processed: ProcessedQuote): string {
  const { parsed, quoteData } = processed
  
  let response = `¡Hola ${quoteData.cliente}! 👋

He recibido tu consulta de cotización y la he registrado con el código ${quoteData.arg}.

📋 **Resumen de tu consulta:**
• Producto: ${parsed.producto.tipo}${parsed.producto.grosor ? ` (${parsed.producto.grosor})` : ''}
• Estado: ${parsed.estado_info === 'completo' ? 'Información completa' : 'Necesito más detalles'}`

  if (parsed.dimensiones?.area_m2) {
    response += `\n• Área: ${parsed.dimensiones.area_m2} m²`
  }
  
  if (parsed.servicios.flete || parsed.servicios.instalacion) {
    response += `\n• Servicios: ${parsed.servicios.flete ? 'Flete incluido' : ''}${parsed.servicios.instalacion ? ' + Instalación' : ''}`
  }
  
  if (parsed.estado_info === 'pendiente_info') {
    response += `\n\n⚠️ **Necesito más información:**
Por favor, proporciona más detalles sobre tu proyecto para poder cotizarte correctamente.`
  } else if (parsed.estado_info === 'ver_plano') {
    response += `\n\n📐 **Plano requerido:**
Necesito revisar el plano de tu proyecto. Por favor, compártelo cuando esté disponible.`
  } else {
    response += `\n\n✅ **Información completa:**
Procesaré tu cotización y te enviaré el presupuesto en las próximas horas.`
  }
  
  response += `\n\n📞 **Contacto:** ${quoteData.telefono}
🆔 **Código:** ${quoteData.arg}

¡Gracias por elegirnos! 🏗️`
  
  return response
}

// Generar código Arg único
function generateArgCode(phone: string, origen: string = 'WA'): string {
  const prefix = phone.slice(-4)
  const date = new Date().getDate()
  const month = new Date().getMonth() + 1
  const hour = new Date().getHours()
  return `${origen}${month}${date}${hour}${prefix}`
}

// Generar ID único para mensaje
function generateMessageId(): string {
  return `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
}

// Buscar cotizaciones existentes por teléfono
export async function findExistingQuotes(phone: string) {
  const sheetsClient = new GoogleSheetsClient()
  return await sheetsClient.findByPhone(phone)
}

// Actualizar estado de cotización
export async function updateQuoteStatus(arg: string, newStatus: string, targetSheet: 'Admin' | 'Enviados' | 'Confirmado' = 'Admin') {
  const sheetsClient = new GoogleSheetsClient()
  
  // Buscar la fila por código Arg
  const quotes = await sheetsClient.readAdminTab()
  const quote = quotes.find(q => q.arg === arg)
  
  if (!quote) {
    throw new Error(`Quote with code ${arg} not found`)
  }
  
  // Actualizar estado
  await sheetsClient.updateCellValue(targetSheet, quote.rowNumber, 'B', newStatus)
  
  return { success: true, message: `Quote ${arg} status updated to ${newStatus}` }
}

// Mover cotización entre pestañas
export async function moveQuote(arg: string, fromSheet: 'Admin' | 'Enviados', toSheet: 'Enviados' | 'Confirmado') {
  const sheetsClient = new GoogleSheetsClient()
  
  // Buscar la fila por código Arg
  const quotes = await sheetsClient.readAdminTab()
  const quote = quotes.find(q => q.arg === arg)
  
  if (!quote) {
    throw new Error(`Quote with code ${arg} not found`)
  }
  
  if (toSheet === 'Enviados') {
    await sheetsClient.moveToEnviados(quote.rowNumber)
  } else if (toSheet === 'Confirmado') {
    await sheetsClient.moveToConfirmado(quote.rowNumber)
  }
  
  return { success: true, message: `Quote ${arg} moved from ${fromSheet} to ${toSheet}` }
}
