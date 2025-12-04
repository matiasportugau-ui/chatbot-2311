export const dynamic = 'force-dynamic';

<<<<<<< Updated upstream
=======
import {
  errorResponse,
  successResponse,
  validationErrorResponse,
} from '@/lib/api-response'
import { withRateLimit } from '@/lib/rate-limit'
import {
  WhatsAppMessage,
  processAndRespondToWhatsApp,
} from '@/lib/whatsapp-to-sheets'
import { RATE_LIMITS } from '@/types/api'
>>>>>>> Stashed changes
import { NextRequest, NextResponse } from 'next/server'
import { processAndRespondToWhatsApp, WhatsAppMessage } from '@/lib/whatsapp-to-sheets'

const VERIFY_TOKEN = process.env.WHATSAPP_VERIFY_TOKEN || 'bmc_whatsapp_verify_2024'

// Verificar webhook de WhatsApp
export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url)
  const mode = searchParams.get('hub.mode')
  const token = searchParams.get('hub.verify_token')
  const challenge = searchParams.get('hub.challenge')
  
  if (mode === 'subscribe' && token === VERIFY_TOKEN) {
    console.log('WhatsApp webhook verified successfully')
    return new NextResponse(challenge, { status: 200 })
  } else {
    console.log('WhatsApp webhook verification failed')
    return new NextResponse('Forbidden', { status: 403 })
  }
}

// Procesar mensajes entrantes de WhatsApp
export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    
    // Verificar que es un evento de WhatsApp
    if (body.object !== 'whatsapp_business_account') {
<<<<<<< Updated upstream
      return NextResponse.json({ error: 'Invalid object type' }, { status: 400 })
=======
      return validationErrorResponse(
        ['Invalid object type'],
        'Expected whatsapp_business_account object'
      )
>>>>>>> Stashed changes
    }
    
    // Procesar cada entrada
    for (const entry of body.entry || []) {
      for (const change of entry.changes || []) {
        if (change.field === 'messages') {
          await processMessages(change.value)
        }
      }
    }
<<<<<<< Updated upstream
    
    return NextResponse.json({ status: 'ok' })
  } catch (error) {
    console.error('Error processing WhatsApp webhook:', error)
    return NextResponse.json({ error: error instanceof Error ? error.message : 'Unknown error' }, { status: 500 })
=======

    return successResponse({ status: 'ok' })
  } catch (error: unknown) {
    console.error('Error processing WhatsApp webhook:', error)
    const errorMessage =
      error instanceof Error ? error.message : 'Unknown error'
    return errorResponse(errorMessage, 500)
>>>>>>> Stashed changes
  }
}

async function processMessages(value: any) {
  const messages = value.messages || []
  const contacts = value.contacts || []
  
  for (const message of messages) {
    try {
      // Obtener información del contacto
      const contact = contacts.find((c: any) => c.wa_id === message.from)
      const contactName = contact?.profile?.name || 'Usuario'
      
      // Preparar mensaje para procesamiento
      const whatsappMessage: WhatsAppMessage = {
        from: message.from,
        name: contactName,
        text: message.text?.body || '',
        timestamp: new Date().toISOString(),
        messageId: message.id
      }
      
      // Solo procesar mensajes de texto
      if (message.type === 'text' && whatsappMessage.text.trim()) {
        console.log(`Processing WhatsApp message from ${whatsappMessage.from}: ${whatsappMessage.text}`)
        
        // Procesar y responder automáticamente
        const result = await processAndRespondToWhatsApp(whatsappMessage)
        
        if (result.success && result.response) {
          // Enviar respuesta automática
          await sendWhatsAppMessage(whatsappMessage.from, result.response)
          console.log(`Auto-response sent to ${whatsappMessage.from}`)
        }
      }
    } catch (error) {
      console.error('Error processing individual message:', error)
      
      // Enviar mensaje de error al usuario
      try {
        await sendWhatsAppMessage(
          message.from, 
          'Lo siento, hubo un error procesando tu mensaje. Por favor, intenta de nuevo.'
        )
      } catch (sendError) {
        console.error('Error sending error message:', sendError)
      }
    }
  }
}

// Función para enviar mensajes por WhatsApp (implementación básica)
async function sendWhatsAppMessage(to: string, message: string): Promise<void> {
  const accessToken = process.env.WHATSAPP_ACCESS_TOKEN
  const phoneNumberId = process.env.WHATSAPP_PHONE_NUMBER_ID
  
  if (!accessToken || !phoneNumberId) {
    console.error('WhatsApp credentials not configured')
    return
  }
  
  try {
    const response = await fetch(`https://graph.facebook.com/v18.0/${phoneNumberId}/messages`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        messaging_product: 'whatsapp',
        to: to,
        type: 'text',
        text: {
          body: message
        }
      })
    })
    
    if (!response.ok) {
      const errorData = await response.json()
      console.error('WhatsApp API error:', errorData)
      throw new Error(`WhatsApp API error: ${response.status}`)
    }
    
    const result = await response.json()
    console.log('WhatsApp message sent successfully:', result)
  } catch (error) {
    console.error('Error sending WhatsApp message:', error)
    throw error
  }
}

// Función para marcar mensaje como leído
async function markMessageAsRead(messageId: string): Promise<void> {
  const accessToken = process.env.WHATSAPP_ACCESS_TOKEN
  const phoneNumberId = process.env.WHATSAPP_PHONE_NUMBER_ID
  
  if (!accessToken || !phoneNumberId) {
    return
  }
  
  try {
    await fetch(`https://graph.facebook.com/v18.0/${phoneNumberId}/messages`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        messaging_product: 'whatsapp',
        status: 'read',
        message_id: messageId
      })
    })
  } catch (error) {
    console.error('Error marking message as read:', error)
  }
}
