#!/usr/bin/env node

/**
 * 🧪 Script de Testing para Workflow n8n - BMC Quote System
 * 
 * Este script simula el flujo completo de n8n para probar la integración
 * sin necesidad de tener n8n corriendo.
 */

const axios = require('axios')

const BASE_URL = 'http://localhost:3000'
const N8N_WEBHOOK_URL = 'http://localhost:5678/webhook/whatsapp-quote'

// Colores para output
const colors = {
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m',
  reset: '\x1b[0m',
  bold: '\x1b[1m'
}

function log(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`)
}

function logStep(step, message, status = 'info') {
  const statusIcon = status === 'success' ? '✅' : status === 'error' ? '❌' : status === 'warning' ? '⚠️' : '🔄'
  const statusColor = status === 'success' ? 'green' : status === 'error' ? 'red' : status === 'warning' ? 'yellow' : 'blue'
  
  log(`${statusIcon} [PASO ${step}] ${message}`, statusColor)
}

// Casos de prueba para el workflow
const testCases = [
  {
    name: 'Cotización Isodec Completa',
    message: 'Necesito cotizar Isodec 100mm para galpón de 50m2 con instalación y flete',
    from: '+59891234567',
    expected: {
      producto: 'Isodec',
      grosor: '100mm',
      area: 50,
      servicios: ['instalacion', 'flete']
    }
  },
  {
    name: 'Cotización Isoroof Simple',
    message: 'Cotizar Isoroof 50mm para techo de 30m2',
    from: '+59898765432',
    expected: {
      producto: 'Isoroof',
      grosor: '50mm',
      area: 30,
      servicios: []
    }
  },
  {
    name: 'Consulta de Información',
    message: '¿Qué es Isodec y para qué se usa?',
    from: '+59895555555',
    expected: {
      tipo: 'informacion'
    }
  },
  {
    name: 'Mensaje Vacío',
    message: '',
    from: '+59899999999',
    expected: {
      error: 'Mensaje vacío'
    }
  }
]

async function testWorkflowStep(stepName, testCase) {
  logStep(1, `Iniciando prueba: ${testCase.name}`, 'info')
  
  try {
    // Simular webhook de WhatsApp
    const webhookData = {
      body: {
        message: testCase.message,
        from: testCase.from,
        timestamp: new Date().toISOString()
      }
    }
    
    log(`📱 Mensaje recibido: "${testCase.message}"`, 'cyan')
    log(`📞 De: ${testCase.from}`, 'cyan')
    
    // PASO 1: Verificar que el mensaje no esté vacío
    if (!testCase.message || testCase.message.trim() === '') {
      logStep(2, 'Mensaje vacío detectado - Enviando respuesta de error', 'warning')
      return {
        success: false,
        error: 'Mensaje vacío o inválido',
        step: 'message_validation'
      }
    }
    
    logStep(2, 'Mensaje válido - Procesando con IA', 'success')
    
    // PASO 2: Parsear con IA (simular llamada a n8n)
    let parsedData = null
    try {
      const parseResponse = await axios.post(`${BASE_URL}/api/parse-quote`, {
        consulta: testCase.message
      }, { timeout: 10000 })
      
      if (parseResponse.data.success) {
        parsedData = parseResponse.data.data
        logStep(3, 'Parsing con IA exitoso', 'success')
        log(`   🧠 Producto detectado: ${parsedData.producto?.tipo || 'N/A'}`, 'blue')
        log(`   📏 Grosor: ${parsedData.producto?.grosor || 'N/A'}`, 'blue')
        log(`   📐 Área: ${parsedData.dimensiones?.area_m2 || 'N/A'} m²`, 'blue')
      } else {
        throw new Error('Error en parsing con IA')
      }
    } catch (error) {
      logStep(3, `Error en parsing con IA: ${error.message}`, 'error')
      return { success: false, error: error.message, step: 'ai_parsing' }
    }
    
    // PASO 3: Procesar con sistema integrado
    let integratedResponse = null
    try {
      const integratedResponse = await axios.post(`${BASE_URL}/api/integrated-quote`, {
        action: 'process',
        consulta: testCase.message,
        userPhone: testCase.from,
        userName: 'Cliente WhatsApp'
      }, { timeout: 15000 })
      
      if (integratedResponse.data.success) {
        logStep(4, 'Procesamiento con sistema integrado exitoso', 'success')
        log(`   🤖 Tipo de respuesta: ${integratedResponse.data.data.tipo}`, 'blue')
        log(`   💬 Mensaje: ${integratedResponse.data.data.mensaje.substring(0, 100)}...`, 'blue')
      } else {
        throw new Error('Error en sistema integrado')
      }
    } catch (error) {
      logStep(4, `Error en sistema integrado: ${error.message}`, 'error')
      return { success: false, error: error.message, step: 'integrated_processing' }
    }
    
    // PASO 4: Guardar en Google Sheets
    try {
      const argCode = `WA${new Date().getDate()}${testCase.from.slice(-4)}`
      const quoteData = {
        arg: argCode,
        estado: 'Pendiente',
        fecha: new Date().toLocaleDateString('es-UY'),
        cliente: testCase.from,
        origen: 'WA',
        telefono: testCase.from,
        direccion: 'A confirmar',
        consulta: testCase.message
      }
      
      const sheetsResponse = await axios.post(`${BASE_URL}/api/sheets/enhanced-sync`, {
        action: 'add_quote',
        data: quoteData
      }, { timeout: 10000 })
      
      if (sheetsResponse.data.success) {
        logStep(5, 'Guardado en Google Sheets exitoso', 'success')
        log(`   📊 Código Arg: ${argCode}`, 'blue')
        log(`   📋 Estado: ${quoteData.estado}`, 'blue')
      } else {
        throw new Error('Error guardando en Google Sheets')
      }
    } catch (error) {
      logStep(5, `Error guardando en Google Sheets: ${error.message}`, 'error')
      return { success: false, error: error.message, step: 'google_sheets' }
    }
    
    // PASO 5: Generar respuesta final
    const finalResponse = {
      success: true,
      message: 'Cotización recibida y procesada exitosamente',
      data: {
        arg: `WA${new Date().getDate()}${testCase.from.slice(-4)}`,
        parsed: parsedData,
        integrated: integratedResponse?.data?.data,
        timestamp: new Date().toISOString()
      }
    }
    
    logStep(6, 'Respuesta final generada', 'success')
    log(`   ✅ Éxito: ${finalResponse.success}`, 'green')
    log(`   📝 Mensaje: ${finalResponse.message}`, 'green')
    
    return finalResponse
    
  } catch (error) {
    logStep('ERROR', `Error general: ${error.message}`, 'error')
    return { success: false, error: error.message, step: 'general' }
  }
}

async function testN8NWorkflow() {
  log('\n🔄 Testing Workflow n8n - BMC Quote System', 'bold')
  log('=' * 50, 'blue')
  log(`🌐 URL Base: ${BASE_URL}`, 'blue')
  log(`⏰ Timestamp: ${new Date().toISOString()}`, 'blue')
  log(`📱 Webhook URL: ${N8N_WEBHOOK_URL}`, 'blue')
  
  let totalPassed = 0
  let totalFailed = 0
  const results = []
  
  for (let i = 0; i < testCases.length; i++) {
    const testCase = testCases[i]
    log(`\n${'='.repeat(60)}`, 'magenta')
    
    const result = await testWorkflowStep(i + 1, testCase)
    results.push({ testCase, result })
    
    if (result.success) {
      totalPassed++
      log(`\n✅ TEST ${i + 1} PASÓ: ${testCase.name}`, 'green')
    } else {
      totalFailed++
      log(`\n❌ TEST ${i + 1} FALLÓ: ${testCase.name}`, 'red')
      log(`   Error: ${result.error}`, 'red')
      log(`   Paso: ${result.step}`, 'red')
    }
    
    // Pausa entre tests
    if (i < testCases.length - 1) {
      log(`\n⏳ Esperando 2 segundos antes del siguiente test...`, 'yellow')
      await new Promise(resolve => setTimeout(resolve, 2000))
    }
  }
  
  // Mostrar resumen final
  log('\n📊 RESUMEN FINAL DEL WORKFLOW', 'bold')
  log('=' * 40, 'blue')
  log(`✅ Tests Exitosos: ${totalPassed}`, 'green')
  log(`❌ Tests Fallidos: ${totalFailed}`, totalFailed > 0 ? 'red' : 'green')
  log(`📈 Tasa de Éxito: ${((totalPassed / (totalPassed + totalFailed)) * 100).toFixed(1)}%`, 
      totalFailed === 0 ? 'green' : 'yellow')
  
  // Mostrar detalles de errores
  if (totalFailed > 0) {
    log('\n🔍 DETALLES DE ERRORES:', 'bold')
    results.forEach(({ testCase, result }, index) => {
      if (!result.success) {
        log(`\n${index + 1}. ${testCase.name}:`, 'red')
        log(`   Error: ${result.error}`, 'red')
        log(`   Paso: ${result.step}`, 'red')
      }
    })
  }
  
  if (totalFailed === 0) {
    log('\n🎉 ¡TODOS LOS TESTS DEL WORKFLOW PASARON!', 'green')
    log('El flujo de n8n está funcionando correctamente.', 'green')
  } else {
    log('\n⚠️  Algunos tests del workflow fallaron.', 'yellow')
    log('Revisar logs para más detalles.', 'yellow')
  }
  
  return { totalPassed, totalFailed, results }
}

// Función para probar webhook específico
async function testWebhookDirectly() {
  log('\n🔗 Testing Webhook Directamente', 'bold')
  log('=' * 35, 'blue')
  
  try {
    const testMessage = {
      body: {
        message: 'Test directo del webhook - Isodec 100mm para 50m2',
        from: '+59891234567',
        timestamp: new Date().toISOString()
      }
    }
    
    log(`📤 Enviando mensaje de prueba al webhook...`, 'cyan')
    log(`URL: ${N8N_WEBHOOK_URL}`, 'cyan')
    
    const response = await axios.post(N8N_WEBHOOK_URL, testMessage, {
      timeout: 10000,
      headers: { 'Content-Type': 'application/json' }
    })
    
    log(`✅ Respuesta del webhook:`, 'green')
    log(`   Status: ${response.status}`, 'blue')
    log(`   Data: ${JSON.stringify(response.data, null, 2)}`, 'blue')
    
    return { success: true, response: response.data }
    
  } catch (error) {
    log(`❌ Error en webhook: ${error.message}`, 'red')
    if (error.response) {
      log(`   Status: ${error.response.status}`, 'red')
      log(`   Data: ${JSON.stringify(error.response.data, null, 2)}`, 'red')
    }
    return { success: false, error: error.message }
  }
}

// Ejecutar tests si se llama directamente
if (require.main === module) {
  const args = process.argv.slice(2)
  
  if (args.includes('--webhook')) {
    testWebhookDirectly()
      .then(({ success }) => {
        process.exit(success ? 0 : 1)
      })
      .catch(error => {
        log(`💥 Error fatal: ${error.message}`, 'red')
        process.exit(1)
      })
  } else {
    testN8NWorkflow()
      .then(({ totalPassed, totalFailed }) => {
        process.exit(totalFailed === 0 ? 0 : 1)
      })
      .catch(error => {
        log(`💥 Error fatal: ${error.message}`, 'red')
        process.exit(1)
      })
  }
}

module.exports = {
  testN8NWorkflow,
  testWebhookDirectly,
  testWorkflowStep
}
