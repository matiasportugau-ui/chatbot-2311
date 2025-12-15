import { credentialsManager } from './credentials-manager'

// Configuración centralizada y segura del sistema BMC
export class SecureConfig {
  private static instance: SecureConfig
  private isInitialized = false

  private constructor() { }

  static getInstance(): SecureConfig {
    if (!SecureConfig.instance) {
      SecureConfig.instance = new SecureConfig()
    }
    return SecureConfig.instance
  }

  // Inicializar configuración segura
  async initialize(credentialsPath?: string): Promise<void> {
    if (this.isInitialized) return

    try {
      await credentialsManager.loadCredentials(credentialsPath)
      this.isInitialized = true
      console.log('🔐 Configuración segura inicializada')
    } catch (error) {
      console.error('❌ Error inicializando configuración segura:', error)
      throw error
    }
  }

  // Obtener configuración de OpenAI / xAI
  getOpenAIConfig() {
    const config = credentialsManager.getOpenAI()

    // Support xAI (Grok) via standard OpenAI SDK compatibility
    const xaiKey = process.env.XAI_API_KEY;

    if (xaiKey) {
      return {
        apiKey: xaiKey,
        baseURL: process.env.XAI_BASE_URL || 'https://api.x.ai/v1',
        model: process.env.XAI_MODEL || 'grok-beta',
        maxTokens: config.max_tokens,
        temperature: config.temperature
      }
    }

    // Default to OpenAI
    return {
      apiKey: config.api_key,
      baseURL: 'https://api.openai.com/v1', // Standard OpenAI URL
      model: config.model || 'gpt-4o',
      maxTokens: config.max_tokens,
      temperature: config.temperature
    }
  }

  // Obtener configuración de Google Sheets
  getGoogleSheetsConfig() {
    const config = credentialsManager.getGoogleSheets()
    return {
      sheetId: config.sheet_id,
      serviceAccountEmail: config.service_account_email,
      privateKey: config.private_key,
      scopes: config.scopes
    }
  }

  // Obtener configuración de MongoDB
  getMongoDBConfig() {
    const config = credentialsManager.getMongoDB()
    return {
      uri: config.uri,
      database: config.database,
      collections: config.collections
    }
  }

  // Obtener configuración de WhatsApp
  getWhatsAppConfig() {
    const config = credentialsManager.getWhatsApp()
    return {
      accessToken: config.access_token,
      phoneNumberId: config.phone_number_id,
      verifyToken: config.verify_token,
      webhookUrl: config.webhook_url
    }
  }

  // Obtener configuración de n8n
  getN8NConfig() {
    const config = credentialsManager.getN8N()
    return {
      webhookUrl: config.webhook_url,
      apiKey: config.api_key,
      baseUrl: config.base_url
    }
  }

  // Obtener configuración de Mercado Libre
  getMercadoLibreConfig() {
    const config = credentialsManager.getMercadoLibre()
    return {
      appId: config.app_id,
      clientSecret: config.client_secret,
      redirectUri: config.redirect_uri,
      sellerId: config.seller_id,
      webhookSecret: config.webhook_secret,
      authBaseUrl: config.auth_base_url,
      apiBaseUrl: config.api_base_url,
      scopes: config.scopes,
      pkceEnabled: config.pkce_enabled
    }
  }

  // Obtener configuración de Dropbox
  getDropboxConfig() {
    const config = credentialsManager.getDropbox()
    return {
      appKey: config.app_key,
      appSecret: config.app_secret,
      accessToken: config.access_token,
      refreshToken: config.refresh_token
    }
  }

  // Obtener configuración del sistema
  getSystemConfig() {
    const config = credentialsManager.getSystem()
    return {
      environment: config.environment,
      maxContextTokens: config.max_context_tokens,
      maxMessagesPerSession: config.max_messages_per_session,
      inactivityTimeoutMinutes: config.inactivity_timeout_minutes,
      defaultZone: config.default_zone,
      encryptionKey: config.encryption_key
    }
  }

  // Validar todas las credenciales
  validateAllCredentials() {
    return credentialsManager.validateCredentials()
  }

  // Obtener resumen de configuración (sin datos sensibles)
  getConfigSummary() {
    return credentialsManager.getCredentialsSummary()
  }

  // Verificar si está inicializado
  isReady(): boolean {
    return this.isInitialized
  }
}

// Instancia global
export const secureConfig = SecureConfig.getInstance()

// Función de conveniencia para inicializar
export async function initializeSecureConfig(credentialsPath?: string): Promise<SecureConfig> {
  await secureConfig.initialize(credentialsPath)
  return secureConfig
}