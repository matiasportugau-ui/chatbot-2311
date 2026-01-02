import { getQuestionById, answerQuestion } from './questions'
import { MercadoLibreQuestion } from './types'

const PY_API_URL = process.env.PY_CHAT_SERVICE_URL || 'http://localhost:8000'
const INTERNAL_API_KEY = process.env.INTERNAL_API_KEY

/**
 * Procesa una pregunta de Mercado Libre y genera una respuesta automática usando la IA
 */
export async function processQuestionAutoAnswer(questionId: number): Promise<{ success: boolean, answer?: string, error?: string }> {
  try {
    console.log(`[AutoAnswer] Iniciando proceso para pregunta ${questionId}`)

    // 1. Obtener detalles de la pregunta
    const question = await getQuestionById(questionId)

    if (question.status !== 'UNANSWERED') {
      console.log(`[AutoAnswer] La pregunta ${questionId} ya no está en estado UNANSWERED (status: ${question.status})`)
      return { success: false, error: 'Question already answered or closed' }
    }

    // 2. Llamar al servicio de IA (FastAPI)
    console.log(`[AutoAnswer] Generando respuesta para: "${question.text}"`)

    // Using /api/chat endpoint which expects ChatMessage schema
    const aiResponse = await fetch(`${PY_API_URL}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': INTERNAL_API_KEY || '',
      },
      body: JSON.stringify({
        message: question.text,
        session_id: `meli_session_${question.item_id}_${question.from.id}`,
      }),
    })

    if (!aiResponse.ok) {
      const errorData = await aiResponse.json().catch(() => ({}))
      throw new Error(`AI Service error: ${aiResponse.status} - ${JSON.stringify(errorData)}`)
    }

    const aiData = await aiResponse.json()
    // Python API /api/chat returns { response: string, session_id: string }
    const answerText = aiData.response

    // 3. Validar confianza (Not returned by current /api/chat, skipping check)
    // If the API evolves to return confidence, we can add it back here.

    // 4. Enviar respuesta a Mercado Libre
    console.log(`[AutoAnswer] Enviando respuesta a ML: "${answerText}"`)

    if (process.env.MELI_AUTO_ANSWER_ENABLED === 'true') {
      await answerQuestion(questionId, answerText)
      console.log(`[AutoAnswer] Pregunta ${questionId} respondida exitosamente en Mercado Libre.`)
    } else {
      console.log(`[AutoAnswer] Modo simulación activo. No se envió la respuesta a ML. (Para habilitar, setea MELI_AUTO_ANSWER_ENABLED=true)`)
    }

    return {
      success: true,
      answer: answerText
    }

  } catch (error) {
    console.error(`[AutoAnswer] Error al procesar la pregunta ${questionId}:`, error)
    return {
      success: false,
      error: error instanceof Error ? error.message : String(error)
    }
  }
}
