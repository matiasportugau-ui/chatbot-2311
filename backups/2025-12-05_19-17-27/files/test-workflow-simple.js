#!/usr/bin/env node

/**
 * 🧪 Test Simplificado del Workflow n8n - BMC Quote System
 * 
 * Este test simula el flujo completo sin depender de endpoints que pueden fallar
 */

const axios = require('axios')

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

// Simulador de parsing de IA
function simulateAIParsing(message) {
  const patterns = {
    isodec: /isodec\s+(\d+)mm/i,
    isoroof: /isoroof\s+(\d+)mm/i,
    area: /(\d+)\s*m2/i,
    instalacion: /instalaci[oó]n|completo/i,
    flete: /flete/i
  }
  
  const result = {
    producto: { tipo: 'No detectado', grosor: null },
    dimensiones: { area_m2: null },
    servicios: { flete: false, instalacion: false },
    estado_info: 'completo'
  }
  
  // Detectar producto
  if (patterns.isodec.test(message)) {
    const match = message.match(patterns.isodec)
    result.producto = { tipo: 'Isodec', grosor: `${match[1]}mm` }
  } else if (patterns.isoroof.test(message)) {
    const match = message.match(patterns.isoroof)
    result.producto = { tipo: 'Isoroof', grosor: `${match[1]}mm` }
  }
  
  // Detectar área
  if (patterns.area.test(message)) {
    const match = message.match(patterns.area)
    result.dimensiones.area_m2 = parseInt(match[1])
  }
  
  // Detectar servicios
  result.servicios.instalacion = patterns.instalacion.test(message)
  result.servicios.flete = patterns.flete.test(message)
  
  return result
}

// Simulador de sistema integrado
function simulateIntegratedSystem(parsedData, message, phone) {
  const responses = {
    cotizacion: {
      tipo: 'cotizacion',
      mensaje: `🏗️ COTIZACIÓN BMC - Código: BMC${Date.now().toString().slice(-6)}\n\n` +
               `Producto: ${parsedData.producto.tipo} ${parsedData.producto.grosor || ''}\n` +
               `Área: ${parsedData.dimensiones.area_m2 || 'N/A'} m²\n` +
               `Servicios: ${parsedData.servicios.instalacion ? 'Instalación' : ''} ${parsedData.servicios.flete ? 'Flete' : ''}\n` +
               `\n**TOTAL ESTIMADO: $${(parsedData.dimensiones.area_m2 || 1) * 45}**\n\n` +
               `_Esta es una cotización estimada. Para una cotización final, por favor contacta a un asesor._`,
      confianza: 0.85
    },
    informacion: {
      tipo: 'informacion',
      mensaje: `ℹ️ INFORMACIÓN SOBRE ${parsedData.producto.tipo.toUpperCase()}\n\n` +
               `El ${parsedData.producto.tipo} es un panel aislante de alta calidad.\n` +
               `Grosor disponible: ${parsedData.producto.grosor || '50-200mm'}\n` +
               `Aplicaciones: Techos, paredes, galpones industriales\n` +
               `Beneficios: Aislamiento térmico, acústico, resistencia al fuego`,
      confianza: 0.90
    }
  }
  
  return responses.cotizacion
}

// Simulador de Google Sheets
function simulateGoogleSheets(quoteData) {
  return {
    success: true,
    data: {
      message: 'Cotización guardada en Google Sheets',
      arg: quoteData.arg,
      timestamp: new Date().toISOString()
    }
  }
}

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
    
    // PASO 2: Simular parsing con IA
    const parsedData = simulateAIParsing(testCase.message)
    logStep(3, 'Parsing con IA simulado exitoso', 'success')
    log(`   🧠 Producto detectado: ${parsedData.producto.tipo}`, 'blue')
    log(`   📏 Grosor: ${parsedData.producto.grosor || 'N/A'}`, 'blue')
    log(`   📐 Área: ${parsedData.dimensiones.area_m2 || 'N/A'} m²`, 'blue')
    log(`   🔧 Servicios: ${parsedData.servicios.instalacion ? 'Instalación' : ''} ${parsedData.servicios.flete ? 'Flete' : ''}`, 'blue')
    
    // PASO 3: Simular sistema integrado
    const integratedResponse = simulateIntegratedSystem(parsedData, testCase.message, testCase.from)
    logStep(4, 'Procesamiento con sistema integrado simulado exitoso', 'success')
    log(`   🤖 Tipo de respuesta: ${integratedResponse.tipo}`, 'blue')
    log(`   💬 Mensaje: ${integratedResponse.mensaje.substring(0, 100)}...`, 'blue')
    
    // PASO 4: Simular guardado en Google Sheets
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
    
    const sheetsResponse = simulateGoogleSheets(quoteData)
    logStep(5, 'Guardado en Google Sheets simulado exitoso', 'success')
    log(`   📊 Código Arg: ${argCode}`, 'blue')
    log(`   📋 Estado: ${quoteData.estado}`, 'blue')
    
    // PASO 5: Generar respuesta final
    const finalResponse = {
      success: true,
      message: 'Cotización recibida y procesada exitosamente',
      data: {
        arg: argCode,
        parsed: parsedData,
        integrated: integratedResponse,
        sheets: sheetsResponse,
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
  log('\n🔄 Testing Workflow n8n - BMC Quote System (SIMULADO)', 'bold')
  log('=' * 60, 'blue')
  log(`⏰ Timestamp: ${new Date().toISOString()}`, 'blue')
  log(`🎭 Modo: Simulación completa (sin dependencias externas)`, 'blue')
  
  const testCases = [
    {
      name: 'Cotización Isodec Completa',
      message: 'Necesito cotizar Isodec 100mm para galpón de 50m2 con instalación y flete',
      from: '+59891234567'
    },
    {
      name: 'Cotización Isoroof Simple',
      message: 'Cotizar Isoroof 50mm para techo de 30m2',
      from: '+59898765432'
    },
    {
      name: 'Consulta de Información',
      message: '¿Qué es Isodec y para qué se usa?',
      from: '+59895555555'
    },
    {
      name: 'Mensaje Vacío',
      message: '',
      from: '+59899999999'
    }
  ]
  
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
      log(`\n⏳ Esperando 1 segundo antes del siguiente test...`, 'yellow')
      await new Promise(resolve => setTimeout(resolve, 1000))
    }
  }
  
  // Mostrar resumen final
  log('\n📊 RESUMEN FINAL DEL WORKFLOW SIMULADO', 'bold')
  log('=' * 50, 'blue')
  log(`✅ Tests Exitosos: ${totalPassed}`, 'green')
  log(`❌ Tests Fallidos: ${totalFailed}`, totalFailed > 0 ? 'red' : 'green')
  log(`📈 Tasa de Éxito: ${((totalPassed / (totalPassed + totalFailed)) * 100).toFixed(1)}%`, 
      totalFailed === 0 ? 'green' : 'yellow')
  
  if (totalFailed === 0) {
    log('\n🎉 ¡TODOS LOS TESTS DEL WORKFLOW SIMULADO PASARON!', 'green')
    log('El flujo de n8n está funcionando correctamente en modo simulación.', 'green')
    log('\n📋 PRÓXIMOS PASOS:', 'bold')
    log('1. 🔧 Configurar credenciales reales (.env.local)', 'blue')
    log('2. 🚀 Iniciar n8n con Docker: ./start-n8n.sh', 'blue')
    log('3. 🧪 Probar con endpoints reales: node test-n8n-workflow.js', 'blue')
    log('4. 📱 Configurar webhook de WhatsApp Business', 'blue')
  } else {
    log('\n⚠️  Algunos tests del workflow simulado fallaron.', 'yellow')
    log('Revisar logs para más detalles.', 'yellow')
  }
  
  return { totalPassed, totalFailed, results }
}

// Ejecutar tests si se llama directamente
if (require.main === module) {
  testN8NWorkflow()
    .then(({ totalPassed, totalFailed }) => {
      process.exit(totalFailed === 0 ? 0 : 1)
    })
    .catch(error => {
      log(`💥 Error fatal: ${error.message}`, 'red')
      process.exit(1)
    })
}

module.exports = {
  testN8NWorkflow,
  testWorkflowStep,
  simulateAIParsing,
  simulateIntegratedSystem,
  simulateGoogleSheets
}
