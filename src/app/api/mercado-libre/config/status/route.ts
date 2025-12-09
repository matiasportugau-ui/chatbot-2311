import { NextRequest } from 'next/server'
import {
  errorResponse,
  successResponse,
} from '@/lib/api-response'
import {
  validateMercadoLibreConfig,
  getConfigValidationSummary,
} from '@/lib/mercado-libre/config-validator'
import { getGrantStatus } from '@/lib/mercado-libre/client'

export async function GET(request: NextRequest) {
  try {
    const validation = validateMercadoLibreConfig()
    const grantStatus = await getGrantStatus()

    return successResponse({
      config: {
        isValid: validation.isValid,
        errors: validation.errors,
        warnings: validation.warnings,
        missing: validation.missing,
        configured: validation.configured,
        summary: getConfigValidationSummary(validation),
      },
      connection: grantStatus,
      timestamp: new Date().toISOString(),
    })
  } catch (error: unknown) {
    const errorMessage =
      error instanceof Error ? error.message : 'Error desconocido'
    
    console.error(
      '[MercadoLibre Config] Error al verificar configuración:',
      JSON.stringify({
        error: errorMessage,
        stack: error instanceof Error ? error.stack : undefined,
      }, null, 2)
    )
    
    return errorResponse(errorMessage, 500)
  }
}

