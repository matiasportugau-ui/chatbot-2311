/**
 * Validador de configuración para integración con MercadoLibre
 * Verifica que todas las variables de entorno requeridas estén presentes
 * y valida sus formatos básicos.
 */

export interface ConfigValidationResult {
  isValid: boolean
  errors: string[]
  warnings: string[]
  missing: string[]
  configured: string[]
}

export interface VariableDefinition {
  key: string
  required: boolean
  description: string
  validator?: (value: string) => boolean | string
}

const REQUIRED_VARIABLES: VariableDefinition[] = [
  {
    key: 'MERCADO_LIBRE_APP_ID',
    required: true,
    description: 'ID de la aplicación en MercadoLibre',
    validator: (value) => value.length > 0 || 'No puede estar vacío',
  },
  {
    key: 'MERCADO_LIBRE_CLIENT_SECRET',
    required: true,
    description: 'Client Secret de la aplicación',
    validator: (value) => value.length > 0 || 'No puede estar vacío',
  },
  {
    key: 'MERCADO_LIBRE_REDIRECT_URI',
    required: true,
    description: 'URI de redirección configurada en la app',
    validator: (value) => {
      try {
        new URL(value)
        return true
      } catch {
        return 'Debe ser una URL válida'
      }
    },
  },
  {
    key: 'MERCADO_LIBRE_SELLER_ID',
    required: true,
    description: 'ID del vendedor en MercadoLibre',
    validator: (value) => value.length > 0 || 'No puede estar vacío',
  },
]

const OPTIONAL_VARIABLES: VariableDefinition[] = [
  {
    key: 'MERCADO_LIBRE_AUTH_URL',
    required: false,
    description: 'URL base de autenticación (por defecto: auth.mercadolibre.com.ar)',
    validator: (value) => {
      try {
        new URL(value)
        return true
      } catch {
        return 'Debe ser una URL válida'
      }
    },
  },
  {
    key: 'MERCADO_LIBRE_API_URL',
    required: false,
    description: 'URL base de la API (por defecto: api.mercadolibre.com)',
    validator: (value) => {
      try {
        new URL(value)
        return true
      } catch {
        return 'Debe ser una URL válida'
      }
    },
  },
  {
    key: 'MERCADO_LIBRE_SCOPES',
    required: false,
    description: 'Scopes OAuth separados por espacios',
  },
  {
    key: 'MERCADO_LIBRE_PKCE_ENABLED',
    required: false,
    description: 'Habilitar PKCE (por defecto: true)',
    validator: (value) => {
      const lower = value.toLowerCase()
      return lower === 'true' || lower === 'false' || 'Debe ser "true" o "false"'
    },
  },
  {
    key: 'MERCADO_LIBRE_WEBHOOK_SECRET',
    required: false,
    description: 'Secret para validar webhooks de MercadoLibre',
  },
]

/**
 * Valida la configuración de MercadoLibre
 * @returns Resultado de la validación con detalles
 */
export function validateMercadoLibreConfig(): ConfigValidationResult {
  const errors: string[] = []
  const warnings: string[] = []
  const missing: string[] = []
  const configured: string[] = []

  // Validar variables requeridas
  for (const variable of REQUIRED_VARIABLES) {
    const value = process.env[variable.key]
    if (!value) {
      missing.push(variable.key)
      errors.push(
        `Variable requerida faltante: ${variable.key} - ${variable.description}`
      )
    } else {
      configured.push(variable.key)
      if (variable.validator) {
        const validationResult = variable.validator(value)
        if (validationResult !== true) {
          errors.push(
            `Variable ${variable.key}: ${validationResult || 'Valor inválido'}`
          )
        }
      }
    }
  }

  // Validar variables opcionales (solo si están presentes)
  for (const variable of OPTIONAL_VARIABLES) {
    const value = process.env[variable.key]
    if (value) {
      configured.push(variable.key)
      if (variable.validator) {
        const validationResult = variable.validator(value)
        if (validationResult !== true) {
          warnings.push(
            `Variable opcional ${variable.key}: ${validationResult || 'Valor inválido'}`
          )
        }
      }
    }
  }

  // Verificar compatibilidad con nombres antiguos (MELI_*)
  const legacyVars = [
    'MELI_ACCESS_TOKEN',
    'MELI_REFRESH_TOKEN',
    'MELI_SELLER_ID',
    'MELI_PAGE_SIZE',
  ]
  const hasLegacyVars = legacyVars.some((key) => process.env[key])
  if (hasLegacyVars) {
    warnings.push(
      'Se detectaron variables con prefijo MELI_*. Se recomienda migrar a MERCADO_LIBRE_* para consistencia.'
    )
  }

  return {
    isValid: errors.length === 0,
    errors,
    warnings,
    missing,
    configured,
  }
}

/**
 * Obtiene un resumen legible de la validación
 */
export function getConfigValidationSummary(
  result: ConfigValidationResult
): string {
  if (result.isValid) {
    return `✅ Configuración válida (${result.configured.length} variables configuradas)`
  }

  const parts: string[] = []
  parts.push(`❌ Configuración inválida:`)
  parts.push(`   - ${result.errors.length} error(es)`)
  parts.push(`   - ${result.missing.length} variable(s) faltante(s)`)
  if (result.warnings.length > 0) {
    parts.push(`   - ${result.warnings.length} advertencia(s)`)
  }
  return parts.join('\n')
}

/**
 * Valida y lanza error si la configuración es inválida
 * Útil para validar al inicio de la aplicación
 */
export function requireValidConfig(): void {
  const result = validateMercadoLibreConfig()
  if (!result.isValid) {
    const summary = getConfigValidationSummary(result)
    const details = result.errors.join('\n')
    throw new Error(
      `Configuración de MercadoLibre inválida:\n${summary}\n\nDetalles:\n${details}`
    )
  }
}

