#!/usr/bin/env node

/**
 * 🧪 Script de Testing para la Integración del Módulo Cotizador
 * 
 * Este script prueba la integración completa del sistema de cotización
 * con la base de conocimiento evolutiva.
 */

const axios = require('axios')

const BASE_URL = 'http://localhost:3000'
const API_ENDPOINTS = {
  integratedQuote: `${BASE_URL}/api/integrated-quote`,
  chat: `${BASE_URL}/api/chat`,
  parseQuote: `${BASE_URL}/api/parse-quote`,
  sheetsSync: `${BASE_URL}/api/sheets/sync`
}

// Colores para output
const colors = {
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  reset: '\x1b[0m',
  bold: '\x1b[1m'
}

function log(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`)
}

function logTest(testName, status, details = '') {
  const statusIcon = status === 'PASS' ? '✅' : status === 'FAIL' ? '❌' : '⏳'
  const statusColor = status === 'PASS' ? 'green' : status === 'FAIL' ? 'red' : 'yellow'
  
  log(`${statusIcon} ${testName}`, statusColor)
  if (details) {
    log(`   ${details}`, 'blue')
  }
}

// Casos de prueba
const testCases = [
  {
    name: 'Consulta de Cotización - Isodec',
    data: {
      action: 'process',
      consulta: 'Necesito cotizar Isodec 100mm para galpón de 50m2 con instalación en Montevideo',
      userPhone: '+59891234567',
      userName: 'Cliente Test'
    },
    expectedType: 'cotizacion'
  },
  {
    name: 'Consulta de Información - Producto',
    data: {
      action: 'process',
      consulta: '¿Qué es Isoroof y para qué se usa?',
      userPhone: '+59891234568',
      userName: 'Cliente Info'
    },
    expectedType: 'informacion'
  },
  {
    name: 'Consulta de Objeción - Precio',
    data: {
      action: 'process',
      consulta: 'El precio me parece muy caro, ¿tienen descuentos?',
      userPhone: '+59891234569',
      userName: 'Cliente Objeción'
    },
    expectedType: 'objeccion'
  },
  {
    name: 'Consulta Compleja - Múltiples Productos',
    data: {
      action: 'process',
      consulta: 'Necesito cotizar galpón completo: Isodec 100mm para techo, Isowall 50mm para paredes, chapas galvanizadas para estructura, con instalación y flete a Canelones',
      userPhone: '+59891234570',
      userName: 'Cliente Complejo'
    },
    expectedType: 'cotizacion'
  }
]

async function testIntegratedQuote() {
  log('\n🧠 Testing Motor de Cotización Integrado', 'bold')
  log('=' * 50, 'blue')
  
  let passed = 0
  let failed = 0
  
  for (const testCase of testCases) {
    try {
      log(`\n📝 ${testCase.name}`, 'yellow')
      
      const response = await axios.post(API_ENDPOINTS.integratedQuote, testCase.data, {
        headers: { 'Content-Type': 'application/json' },
        timeout: 30000
      })
      
      if (response.data.success && response.data.data?.respuesta) {
        const respuesta = response.data.data.respuesta
        
        // Verificar tipo de respuesta
        if (respuesta.tipo === testCase.expectedType) {
          logTest(testCase.name, 'PASS', `Tipo: ${respuesta.tipo}, Confianza: ${(respuesta.confianza * 100).toFixed(1)}%`)
          passed++
        } else {
          logTest(testCase.name, 'FAIL', `Esperado: ${testCase.expectedType}, Obtenido: ${respuesta.tipo}`)
          failed++
        }
        
        // Mostrar detalles de la respuesta
        log(`   Mensaje: ${respuesta.mensaje.substring(0, 100)}...`, 'blue')
        
        if (respuesta.patrones_aplicados && respuesta.patrones_aplicados.length > 0) {
          log(`   Patrones: ${respuesta.patrones_aplicados.join(', ')}`, 'blue')
        }
        
        if (respuesta.conocimiento_utilizado && respuesta.conocimiento_utilizado.length > 0) {
          log(`   Conocimiento: ${respuesta.conocimiento_utilizado.join(', ')}`, 'blue')
        }
        
      } else {
        logTest(testCase.name, 'FAIL', 'Respuesta inválida del servidor')
        failed++
      }
      
    } catch (error) {
      logTest(testCase.name, 'FAIL', `Error: ${error.message}`)
      failed++
    }
  }
  
  return { passed, failed }
}

async function testMetrics() {
  log('\n📊 Testing Métricas del Sistema', 'bold')
  log('=' * 30, 'blue')
  
  try {
    const response = await axios.post(API_ENDPOINTS.integratedQuote, {
      action: 'metrics'
    }, {
      headers: { 'Content-Type': 'application/json' },
      timeout: 10000
    })
    
    if (response.data.success && response.data.data?.metricas) {
      const metricas = response.data.data.metricas
      
      logTest('Obtener Métricas', 'PASS', `Interacciones: ${metricas.total_interacciones}`)
      
      log(`   📈 Interacciones Totales: ${metricas.total_interacciones}`, 'blue')
      log(`   💰 Cotizaciones Generadas: ${metricas.cotizaciones_generadas}`, 'blue')
      log(`   🎯 Conversiones: ${metricas.conversiones}`, 'blue')
      log(`   📊 Tasa de Conversión: ${(metricas.tasa_conversion * 100).toFixed(1)}%`, 'blue')
      log(`   🧠 Patrones Identificados: ${metricas.patrones_identificados}`, 'blue')
      log(`   📚 Productos Conocidos: ${metricas.productos_conocidos}`, 'blue')
      log(`   ⚡ Confianza Promedio: ${(metricas.confianza_promedio * 100).toFixed(1)}%`, 'blue')
      
      return { passed: 1, failed: 0 }
    } else {
      logTest('Obtener Métricas', 'FAIL', 'Respuesta inválida')
      return { passed: 0, failed: 1 }
    }
    
  } catch (error) {
    logTest('Obtener Métricas', 'FAIL', `Error: ${error.message}`)
    return { passed: 0, failed: 1 }
  }
}

async function testKnowledgeUpdate() {
  log('\n🧠 Testing Actualización de Base de Conocimiento', 'bold')
  log('=' * 45, 'blue')
  
  try {
    const response = await axios.post(API_ENDPOINTS.integratedQuote, {
      action: 'update_knowledge'
    }, {
      headers: { 'Content-Type': 'application/json' },
      timeout: 30000
    })
    
    if (response.data.success) {
      logTest('Actualizar Conocimiento', 'PASS', response.data.message)
      return { passed: 1, failed: 0 }
    } else {
      logTest('Actualizar Conocimiento', 'FAIL', 'Error en la actualización')
      return { passed: 0, failed: 1 }
    }
    
  } catch (error) {
    logTest('Actualizar Conocimiento', 'FAIL', `Error: ${error.message}`)
    return { passed: 0, failed: 1 }
  }
}

async function testPatternAnalysis() {
  log('\n🔍 Testing Análisis de Patrones', 'bold')
  log('=' * 30, 'blue')
  
  try {
    const response = await axios.post(API_ENDPOINTS.integratedQuote, {
      action: 'analyze_patterns'
    }, {
      headers: { 'Content-Type': 'application/json' },
      timeout: 15000
    })
    
    if (response.data.success && response.data.data) {
      const data = response.data.data
      
      logTest('Análisis de Patrones', 'PASS', `Patrones: ${data.patrones_identificados}`)
      
      log(`   🎯 Patrones Identificados: ${data.patrones_identificados}`, 'blue')
      log(`   📦 Productos Más Consultados: ${data.productos_mas_consultados}`, 'blue')
      log(`   🌍 Zonas Más Activas: ${data.zonas_mas_activas}`, 'blue')
      log(`   ⏰ Horarios Pico: ${data.horarios_pico}`, 'blue')
      
      return { passed: 1, failed: 0 }
    } else {
      logTest('Análisis de Patrones', 'FAIL', 'Respuesta inválida')
      return { passed: 0, failed: 1 }
    }
    
  } catch (error) {
    logTest('Análisis de Patrones', 'FAIL', `Error: ${error.message}`)
    return { passed: 0, failed: 1 }
  }
}

async function testSystemHealth() {
  log('\n🏥 Testing Salud del Sistema', 'bold')
  log('=' * 25, 'blue')
  
  try {
    const response = await axios.get(`${API_ENDPOINTS.integratedQuote}?action=health`, {
      timeout: 5000
    })
    
    if (response.data.success && response.data.data?.status === 'healthy') {
      logTest('Salud del Sistema', 'PASS', 'Sistema funcionando correctamente')
      
      const data = response.data.data
      log(`   🟢 Estado: ${data.status}`, 'blue')
      log(`   ⏱️  Uptime: ${Math.round(data.uptime)}s`, 'blue')
      log(`   💾 Memoria: ${Math.round(data.memory.used / 1024 / 1024)}MB`, 'blue')
      
      return { passed: 1, failed: 0 }
    } else {
      logTest('Salud del Sistema', 'FAIL', 'Sistema no saludable')
      return { passed: 0, failed: 1 }
    }
    
  } catch (error) {
    logTest('Salud del Sistema', 'FAIL', `Error: ${error.message}`)
    return { passed: 0, failed: 1 }
  }
}

async function runAllTests() {
  log('🚀 Iniciando Tests de Integración del Módulo Cotizador', 'bold')
  log('=' * 60, 'blue')
  log(`🌐 URL Base: ${BASE_URL}`, 'blue')
  log(`⏰ Timestamp: ${new Date().toISOString()}`, 'blue')
  
  let totalPassed = 0
  let totalFailed = 0
  
  // Ejecutar todos los tests
  const results = await Promise.all([
    testIntegratedQuote(),
    testMetrics(),
    testKnowledgeUpdate(),
    testPatternAnalysis(),
    testSystemHealth()
  ])
  
  // Sumar resultados
  results.forEach(result => {
    totalPassed += result.passed
    totalFailed += result.failed
  })
  
  // Mostrar resumen final
  log('\n📊 RESUMEN FINAL', 'bold')
  log('=' * 20, 'blue')
  log(`✅ Tests Exitosos: ${totalPassed}`, 'green')
  log(`❌ Tests Fallidos: ${totalFailed}`, totalFailed > 0 ? 'red' : 'green')
  log(`📈 Tasa de Éxito: ${((totalPassed / (totalPassed + totalFailed)) * 100).toFixed(1)}%`, 
      totalFailed === 0 ? 'green' : 'yellow')
  
  if (totalFailed === 0) {
    log('\n🎉 ¡TODOS LOS TESTS PASARON! La integración está funcionando correctamente.', 'green')
  } else {
    log('\n⚠️  Algunos tests fallaron. Revisar logs para más detalles.', 'yellow')
  }
  
  return { totalPassed, totalFailed }
}

// Ejecutar tests si se llama directamente
if (require.main === module) {
  runAllTests()
    .then(({ totalPassed, totalFailed }) => {
      process.exit(totalFailed === 0 ? 0 : 1)
    })
    .catch(error => {
      log(`\n💥 Error fatal: ${error.message}`, 'red')
      process.exit(1)
    })
}

module.exports = {
  runAllTests,
  testIntegratedQuote,
  testMetrics,
  testKnowledgeUpdate,
  testPatternAnalysis,
  testSystemHealth
}