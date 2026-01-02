import { callMercadoLibreAPI } from './client'
import { MercadoLibreQuestion } from './types'

/**
 * Obtiene los detalles de una pregunta específica por su ID
 */
export async function getQuestionById(questionId: number): Promise<MercadoLibreQuestion> {
  return callMercadoLibreAPI<MercadoLibreQuestion>({
    path: `/questions/${questionId}`,
  })
}

/**
 * Responde a una pregunta específica
 */
export async function answerQuestion(questionId: number, text: string): Promise<any> {
  return callMercadoLibreAPI({
    method: 'POST',
    path: '/answers',
    body: {
      question_id: questionId,
      text: text,
    },
  })
}

/**
 * Obtiene todas las preguntas recibidas, opcionalmente filtradas por estado o ítem
 */
export async function fetchQuestions(options: {
  status?: 'UNANSWERED' | 'ANSWERED' | 'BANNED' | 'DELETED'
  item?: string
  seller?: string
  limit?: number
  offset?: number
} = {}): Promise<{ questions: MercadoLibreQuestion[], total: number }> {
  return callMercadoLibreAPI({
    path: '/questions/search',
    query: {
      seller: options.seller,
      item: options.item,
      status: options.status,
      limit: options.limit || 50,
      offset: options.offset || 0,
    },
  })
}

/**
 * Obtiene las preguntas no respondidas para el vendedor configurado
 */
export async function getUnansweredQuestions(sellerId: string): Promise<MercadoLibreQuestion[]> {
  const response = await fetchQuestions({
    status: 'UNANSWERED',
    seller: sellerId,
  })
  return response.questions
}
