import { initializeSecureConfig } from './secure-config'
import { GoogleSheetsClient } from './google-sheets'
import { quoteEngine } from './quote-engine'

// Inicializar todo el sistema BMC de forma segura
export async function initializeBMCSystem(credentialsPath?: string): Promise<{
  success: boolean
  error?: string
  configSummary?: any
}> {
  try {
    console.log('🚀 Inicializando Sistema BMC de Cotización...')
    
    // 1. Inicializar configuración segura
    console.log('🔐 Cargando credenciales...')
    await initializeSecureConfig(credentialsPath)
    
    // 2. Validar credenciales
    console.log('✅ Validando credenciales...')
    const validation = secureConfig.validateAllCredentials()
    
    if (!validation.isValid) {
      console.warn('⚠️ Credenciales faltantes:', validation.missing)
      return {
        success: false,
        error: `Credenciales faltantes: ${validation.missing.join(', ')}`
      }
    }
    
    // 3. Probar conexión a Google Sheets
    console.log('📊 Probando conexión a Google Sheets...')
    try {
      const sheetsClient = new GoogleSheetsClient()
      await sheetsClient.getStats()
      console.log('✅ Google Sheets conectado correctamente')
    } catch (error) {
      console.warn('⚠️ Error conectando a Google Sheets:', error.message)
    }
    
    // 4. Probar motor de cotización
    console.log('🤖 Probando motor de cotización...')
    try {
      const testResponse = await quoteEngine.procesarConsulta('Test de conexión')
      console.log('✅ Motor de cotización funcionando')
    } catch (error) {
      console.warn('⚠️ Error en motor de cotización:', error.message)
    }
    
    // 5. Obtener resumen de configuración
    const configSummary = secureConfig.getConfigSummary()
    
    console.log('🎉 Sistema BMC inicializado correctamente')
    
    return {
      success: true,
      configSummary
    }
    
  } catch (error: any) {
    console.error('❌ Error inicializando sistema BMC:', error)
    return {
      success: false,
      error: error.message
    }
  }
}

// Función para verificar estado del sistema
export function getSystemStatus() {
  return {
    isInitialized: secureConfig.isReady(),
    configSummary: secureConfig.isReady() ? secureConfig.getConfigSummary() : null,
    validation: secureConfig.isReady() ? secureConfig.validateAllCredentials() : null
  }
}

// Función para reinicializar el sistema
export async function reinitializeSystem(credentialsPath?: string) {
  console.log('🔄 Reinicializando sistema BMC...')
  return await initializeBMCSystem(credentialsPath)
}
