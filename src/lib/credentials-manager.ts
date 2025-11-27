import crypto from 'crypto'

interface Credentials {
  openai: {
    api_key: string
    model: string
    max_tokens: number
    temperature: number
  }
  google_sheets: {
    sheet_id: string
    service_account_email: string
    private_key: string
    scopes: string[]
  }
  mongodb: {
    uri: string
    database: string
    collections: {
      quotes: string
      sessions: string
      context: string
      analytics: string
    }
  }
  whatsapp: {
    access_token: string
    phone_number_id: string
    verify_token: string
    webhook_url: string
  }
  n8n: {
    webhook_url: string
    api_key: string
    base_url: string
  }
  mercado_libre: {
    app_id: string
    client_secret: string
    redirect_uri: string
    seller_id: string
    webhook_secret: string
    auth_base_url: string
    api_base_url: string
    scopes: string[]
    pkce_enabled: boolean
  }
  system: {
    environment: string
    max_context_tokens: number
    max_messages_per_session: number
    inactivity_timeout_minutes: number
    default_zone: string
    encryption_key: string
  }
}

class CredentialsManager {
  private credentials: Credentials | null = null
  private encryptionKey: string
  private isLoaded = false

  constructor() {
    // Usar clave de encriptación del sistema o generar una
    this.encryptionKey = process.env.CREDENTIALS_ENCRYPTION_KEY || 
      'bmc-default-encryption-key-32-chars'
  }

  // Cargar credenciales desde archivo JSON encriptado
  async loadCredentials(credentialsPath: string = './credentials.json'): Promise<void> {
    try {
      // En desarrollo, cargar desde archivo local
      if (process.env.NODE_ENV === 'development') {
        const fs = await import('fs/promises')
        const path = await import('path')
        
        const fullPath = path.resolve(process.cwd(), credentialsPath)
        const encryptedData = await fs.readFile(fullPath, 'utf-8')
        
        // Desencriptar datos
        const decryptedData = this.decrypt(encryptedData)
        this.credentials = JSON.parse(decryptedData)
      } else {
        // En producción, cargar desde variables de entorno
        this.loadFromEnvironment()
      }
      
      this.isLoaded = true
      console.log('✅ Credenciales cargadas exitosamente')
    } catch (error) {
      console.error('❌ Error cargando credenciales:', error)
      throw new Error('No se pudieron cargar las credenciales')
    }
  }

  // Cargar credenciales desde variables de entorno
  private loadFromEnvironment(): void {
    this.credentials = {
      openai: {
        api_key: process.env.OPENAI_API_KEY || '',
        model: process.env.OPENAI_MODEL || 'gpt-4',
        max_tokens: parseInt(process.env.OPENAI_MAX_TOKENS || '4000'),
        temperature: parseFloat(process.env.OPENAI_TEMPERATURE || '0.1')
      },
      google_sheets: {
        sheet_id: process.env.GOOGLE_SHEET_ID || '',
        service_account_email: process.env.GOOGLE_SERVICE_ACCOUNT_EMAIL || '',
        private_key: process.env.GOOGLE_PRIVATE_KEY || '',
        scopes: ['https://www.googleapis.com/auth/spreadsheets']
      },
      mongodb: {
        uri: process.env.MONGODB_URI || '',
        database: process.env.MONGODB_DATABASE || 'bmc_quotes',
        collections: {
          quotes: process.env.MONGODB_QUOTES_COLLECTION || 'quotes',
          sessions: process.env.MONGODB_SESSIONS_COLLECTION || 'sessions',
          context: process.env.MONGODB_CONTEXT_COLLECTION || 'context',
          analytics: process.env.MONGODB_ANALYTICS_COLLECTION || 'analytics'
        }
      },
      whatsapp: {
        access_token: process.env.WHATSAPP_ACCESS_TOKEN || '',
        phone_number_id: process.env.WHATSAPP_PHONE_NUMBER_ID || '',
        verify_token: process.env.WHATSAPP_VERIFY_TOKEN || 'bmc_whatsapp_verify_2024',
        webhook_url: process.env.WHATSAPP_WEBHOOK_URL || ''
      },
      n8n: {
        webhook_url: process.env.N8N_WEBHOOK_URL || 'http://localhost:5678/webhook/bmc-quotes',
        api_key: process.env.N8N_API_KEY || '',
        base_url: process.env.N8N_BASE_URL || 'http://localhost:5678'
      },
      mercado_libre: {
        app_id: process.env.MERCADO_LIBRE_APP_ID || process.env.MELI_APP_ID || '',
        client_secret: process.env.MERCADO_LIBRE_CLIENT_SECRET || process.env.MELI_CLIENT_SECRET || '',
        redirect_uri: process.env.MERCADO_LIBRE_REDIRECT_URI || process.env.MELI_REDIRECT_URI || '',
        seller_id: process.env.MERCADO_LIBRE_SELLER_ID || process.env.MELI_SELLER_ID || '',
        webhook_secret: process.env.MERCADO_LIBRE_WEBHOOK_SECRET || '',
        auth_base_url: process.env.MERCADO_LIBRE_AUTH_URL || 'https://auth.mercadolibre.com.ar',
        api_base_url: process.env.MERCADO_LIBRE_API_URL || 'https://api.mercadolibre.com',
        scopes: (process.env.MERCADO_LIBRE_SCOPES || 'offline_access read write')
          .split(/[ ,]+/)
          .filter(Boolean),
        pkce_enabled: (process.env.MERCADO_LIBRE_PKCE_ENABLED || 'true').toLowerCase() !== 'false'
      },
      system: {
        environment: process.env.NODE_ENV || 'development',
        max_context_tokens: parseInt(process.env.MAX_CONTEXT_TOKENS || '8000'),
        max_messages_per_session: parseInt(process.env.MAX_MESSAGES_PER_SESSION || '20'),
        inactivity_timeout_minutes: parseInt(process.env.INACTIVITY_TIMEOUT_MINUTES || '30'),
        default_zone: process.env.DEFAULT_ZONE || 'montevideo',
        encryption_key: this.encryptionKey
      }
    }
  }

  // Obtener credenciales específicas
  getOpenAI() {
    this.ensureLoaded()
    return this.credentials!.openai
  }

  getGoogleSheets() {
    this.ensureLoaded()
    return this.credentials!.google_sheets
  }

  getMongoDB() {
    this.ensureLoaded()
    return this.credentials!.mongodb
  }

  getWhatsApp() {
    this.ensureLoaded()
    return this.credentials!.whatsapp
  }

  getN8N() {
    this.ensureLoaded()
    return this.credentials!.n8n
  }

  getMercadoLibre() {
    this.ensureLoaded()
    return this.credentials!.mercado_libre
  }

  getSystem() {
    this.ensureLoaded()
    return this.credentials!.system
  }

  // Verificar si todas las credenciales están configuradas
  validateCredentials(): { isValid: boolean; missing: string[] } {
    this.ensureLoaded()
    
    const missing: string[] = []
    const creds = this.credentials!

    // Verificar OpenAI
    if (!creds.openai.api_key) missing.push('OPENAI_API_KEY')

    // Verificar Google Sheets
    if (!creds.google_sheets.sheet_id) missing.push('GOOGLE_SHEET_ID')
    if (!creds.google_sheets.service_account_email) missing.push('GOOGLE_SERVICE_ACCOUNT_EMAIL')
    if (!creds.google_sheets.private_key) missing.push('GOOGLE_PRIVATE_KEY')

    // Verificar MongoDB
    if (!creds.mongodb.uri) missing.push('MONGODB_URI')

    // Verificar WhatsApp (opcional)
    if (!creds.whatsapp.access_token) missing.push('WHATSAPP_ACCESS_TOKEN')
    if (!creds.whatsapp.phone_number_id) missing.push('WHATSAPP_PHONE_NUMBER_ID')

    // Verificar Mercado Libre
    if (!creds.mercado_libre.app_id) missing.push('MERCADO_LIBRE_APP_ID')
    if (!creds.mercado_libre.client_secret) missing.push('MERCADO_LIBRE_CLIENT_SECRET')
    if (!creds.mercado_libre.redirect_uri) missing.push('MERCADO_LIBRE_REDIRECT_URI')
    if (!creds.mercado_libre.seller_id) missing.push('MERCADO_LIBRE_SELLER_ID')

    return {
      isValid: missing.length === 0,
      missing
    }
  }

  // Encriptar datos sensibles
  private encrypt(text: string): string {
    const cipher = crypto.createCipher('aes-256-cbc', this.encryptionKey)
    let encrypted = cipher.update(text, 'utf8', 'hex')
    encrypted += cipher.final('hex')
    return encrypted
  }

  // Desencriptar datos sensibles
  private decrypt(encryptedText: string): string {
    const decipher = crypto.createDecipher('aes-256-cbc', this.encryptionKey)
    let decrypted = decipher.update(encryptedText, 'hex', 'utf8')
    decrypted += decipher.final('utf8')
    return decrypted
  }

  // Verificar que las credenciales estén cargadas
  private ensureLoaded(): void {
    if (!this.isLoaded || !this.credentials) {
      throw new Error('Las credenciales no han sido cargadas. Llama a loadCredentials() primero.')
    }
  }

  // Obtener resumen de credenciales (sin datos sensibles)
  getCredentialsSummary() {
    this.ensureLoaded()
    
    return {
      openai: {
        model: this.credentials!.openai.model,
        max_tokens: this.credentials!.openai.max_tokens,
        has_api_key: !!this.credentials!.openai.api_key
      },
      google_sheets: {
        sheet_id: this.credentials!.google_sheets.sheet_id,
        has_credentials: !!(this.credentials!.google_sheets.service_account_email && this.credentials!.google_sheets.private_key)
      },
      mongodb: {
        database: this.credentials!.mongodb.database,
        has_uri: !!this.credentials!.mongodb.uri
      },
      whatsapp: {
        has_credentials: !!(this.credentials!.whatsapp.access_token && this.credentials!.whatsapp.phone_number_id)
      },
      mercado_libre: {
        app_id: this.credentials!.mercado_libre.app_id,
        has_secret: !!this.credentials!.mercado_libre.client_secret,
        seller_id: this.credentials!.mercado_libre.seller_id,
        pkce_enabled: this.credentials!.mercado_libre.pkce_enabled,
        scopes: this.credentials!.mercado_libre.scopes
      },
      n8n: {
        webhook_url: this.credentials!.n8n.webhook_url,
        has_api_key: !!this.credentials!.n8n.api_key
      },
      system: {
        environment: this.credentials!.system.environment,
        max_context_tokens: this.credentials!.system.max_context_tokens
      }
    }
  }
}

// Instancia global del gestor de credenciales
export const credentialsManager = new CredentialsManager()

// Función de conveniencia para inicializar credenciales
export async function initializeCredentials(credentialsPath?: string): Promise<void> {
  await credentialsManager.loadCredentials(credentialsPath)
  
  const validation = credentialsManager.validateCredentials()
  if (!validation.isValid) {
    console.warn('⚠️ Credenciales faltantes:', validation.missing)
    console.log('💡 Usa el archivo credentials-template.json como guía')
  } else {
    console.log('✅ Todas las credenciales están configuradas correctamente')
  }
}
